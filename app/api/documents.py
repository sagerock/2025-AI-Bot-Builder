from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Request
from typing import List, Optional
from pydantic import BaseModel
from app.services.document_service import document_service
from app.services.qdrant_service import qdrant_service
from app.services.embedding_service import embedding_service
from app import auth

router = APIRouter(prefix="/api/documents", tags=["documents"])


def require_auth_dependency(request: Request) -> str:
    """Dependency to require authentication"""
    return auth.require_auth(request)


class UploadResponse(BaseModel):
    success: bool
    message: str
    chunks_count: int
    point_ids: List[str]
    collection: str


class FileUploadResult(BaseModel):
    filename: str
    success: bool
    chunks_count: int
    point_ids: List[str]
    error: Optional[str] = None


class MultiUploadResponse(BaseModel):
    success: bool
    message: str
    total_files: int
    successful_files: int
    failed_files: int
    results: List[FileUploadResult]
    collection: str


class CreateCollectionRequest(BaseModel):
    name: str
    vector_size: int = 1536
    distance: str = "Cosine"


class CreateCollectionResponse(BaseModel):
    success: bool
    message: str
    collection_name: str


class PointResponse(BaseModel):
    id: str
    payload: dict
    vector: Optional[List[float]] = None


class ScrollResponse(BaseModel):
    points: List[PointResponse]
    next_offset: Optional[str]
    total_returned: int


class DeletePointsRequest(BaseModel):
    point_ids: List[str]


class DeleteResponse(BaseModel):
    success: bool
    message: str


class CollectionInfo(BaseModel):
    name: str
    points_count: int
    vectors_count: int
    indexed_vectors_count: int
    status: str


class ListCollectionsResponse(BaseModel):
    collections: List[CollectionInfo]
    total_collections: int


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection: str = Form(...),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    create_if_missing: bool = Form(False),
    username: str = Depends(require_auth_dependency)
):
    """
    Upload a document, process it, and store chunks in Qdrant

    Args:
        file: Document file (PDF, TXT, MD, HTML)
        collection: Target Qdrant collection
        chunk_size: Size of each text chunk
        chunk_overlap: Overlap between chunks
        create_if_missing: Create collection if it doesn't exist
    """
    try:
        # Validate file size (25MB limit for scanned documents)
        file_content = await file.read()
        max_size = 25 * 1024 * 1024  # 25MB
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {max_size / (1024*1024)}MB"
            )

        # Check if collection exists
        collection_exists = qdrant_service.collection_exists(collection)

        if not collection_exists:
            if create_if_missing:
                # Create the collection
                qdrant_service.create_collection(collection)
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Collection '{collection}' does not exist. Set create_if_missing=true to create it."
                )

        # Process document into chunks
        documents = document_service.process_document(
            filename=file.filename,
            file_content=file_content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No content could be extracted from the document"
            )

        # Generate embeddings for each chunk
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        embeddings = []
        for text in texts:
            embedding = embedding_service.generate_embedding(text)
            embeddings.append(embedding)

        # Upload to Qdrant
        point_ids = qdrant_service.upload_points(
            collection_name=collection,
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return UploadResponse(
            success=True,
            message=f"Successfully uploaded {len(point_ids)} chunks from {file.filename}",
            chunks_count=len(point_ids),
            point_ids=point_ids,
            collection=collection
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload-multiple", response_model=MultiUploadResponse)
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    collection: str = Form(...),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    create_if_missing: bool = Form(False),
    username: str = Depends(require_auth_dependency)
):
    """
    Upload multiple documents at once, process them, and store chunks in Qdrant

    Args:
        files: List of document files (PDF, TXT, MD, HTML)
        collection: Target Qdrant collection
        chunk_size: Size of each text chunk
        chunk_overlap: Overlap between chunks
        create_if_missing: Create collection if it doesn't exist
    """
    try:
        # Check if collection exists
        collection_exists = qdrant_service.collection_exists(collection)

        if not collection_exists:
            if create_if_missing:
                # Create the collection
                qdrant_service.create_collection(collection)
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Collection '{collection}' does not exist. Set create_if_missing=true to create it."
                )

        results = []
        successful_files = 0
        failed_files = 0
        max_size = 25 * 1024 * 1024  # 25MB per file

        # Process each file
        for file in files:
            try:
                # Validate file size
                file_content = await file.read()
                if len(file_content) > max_size:
                    results.append(FileUploadResult(
                        filename=file.filename,
                        success=False,
                        chunks_count=0,
                        point_ids=[],
                        error=f"File too large. Maximum size is {max_size / (1024*1024)}MB"
                    ))
                    failed_files += 1
                    continue

                # Process document into chunks
                documents = document_service.process_document(
                    filename=file.filename,
                    file_content=file_content,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )

                if not documents:
                    results.append(FileUploadResult(
                        filename=file.filename,
                        success=False,
                        chunks_count=0,
                        point_ids=[],
                        error="No content could be extracted from the document"
                    ))
                    failed_files += 1
                    continue

                # Generate embeddings for each chunk
                texts = [doc.page_content for doc in documents]
                metadatas = [doc.metadata for doc in documents]

                embeddings = []
                for text in texts:
                    embedding = embedding_service.generate_embedding(text)
                    embeddings.append(embedding)

                # Upload to Qdrant
                point_ids = qdrant_service.upload_points(
                    collection_name=collection,
                    texts=texts,
                    embeddings=embeddings,
                    metadatas=metadatas
                )

                results.append(FileUploadResult(
                    filename=file.filename,
                    success=True,
                    chunks_count=len(point_ids),
                    point_ids=point_ids
                ))
                successful_files += 1

            except ValueError as e:
                results.append(FileUploadResult(
                    filename=file.filename,
                    success=False,
                    chunks_count=0,
                    point_ids=[],
                    error=str(e)
                ))
                failed_files += 1
            except Exception as e:
                print(f"Upload error for {file.filename}: {e}")
                results.append(FileUploadResult(
                    filename=file.filename,
                    success=False,
                    chunks_count=0,
                    point_ids=[],
                    error=str(e)
                ))
                failed_files += 1

        total_chunks = sum(r.chunks_count for r in results if r.success)

        return MultiUploadResponse(
            success=successful_files > 0,
            message=f"Processed {len(files)} files: {successful_files} successful, {failed_files} failed. Total chunks: {total_chunks}",
            total_files=len(files),
            successful_files=successful_files,
            failed_files=failed_files,
            results=results,
            collection=collection
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Multi-upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Multi-upload failed: {str(e)}")


@router.post("/collections/create", response_model=CreateCollectionResponse)
async def create_collection(request: CreateCollectionRequest, username: str = Depends(require_auth_dependency)):
    """Create a new Qdrant collection"""
    try:
        # Check if collection already exists
        if qdrant_service.collection_exists(request.name):
            raise HTTPException(
                status_code=400,
                detail=f"Collection '{request.name}' already exists"
            )

        # Create the collection
        qdrant_service.create_collection(
            collection_name=request.name,
            vector_size=request.vector_size,
            distance=request.distance
        )

        return CreateCollectionResponse(
            success=True,
            message=f"Collection '{request.name}' created successfully",
            collection_name=request.name
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Create collection error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create collection: {str(e)}"
        )


@router.get("/collections/{collection_name}/points", response_model=ScrollResponse)
async def list_collection_points(
    collection_name: str,
    limit: int = 100,
    offset: Optional[str] = None,
    with_vectors: bool = False,
    username: str = Depends(require_auth_dependency)
):
    """List points in a collection with pagination"""
    try:
        result = qdrant_service.scroll_points(
            collection_name=collection_name,
            limit=limit,
            offset=offset,
            with_vectors=with_vectors
        )

        return ScrollResponse(
            points=[PointResponse(**p) for p in result["points"]],
            next_offset=result["next_offset"],
            total_returned=len(result["points"])
        )

    except Exception as e:
        print(f"List points error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list points: {str(e)}"
        )


@router.delete("/collections/{collection_name}/points", response_model=DeleteResponse)
async def delete_points(collection_name: str, request: DeletePointsRequest, username: str = Depends(require_auth_dependency)):
    """Delete specific points from a collection"""
    try:
        if not request.point_ids:
            raise HTTPException(
                status_code=400,
                detail="No point IDs provided"
            )

        qdrant_service.delete_points(
            collection_name=collection_name,
            point_ids=request.point_ids
        )

        return DeleteResponse(
            success=True,
            message=f"Successfully deleted {len(request.point_ids)} points"
        )

    except Exception as e:
        print(f"Delete points error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete points: {str(e)}"
        )


@router.delete("/collections/{collection_name}", response_model=DeleteResponse)
async def delete_collection(collection_name: str, username: str = Depends(require_auth_dependency)):
    """Delete an entire collection"""
    try:
        # Check if collection exists
        if not qdrant_service.collection_exists(collection_name):
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_name}' not found"
            )

        qdrant_service.delete_collection(collection_name)

        return DeleteResponse(
            success=True,
            message=f"Collection '{collection_name}' deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete collection error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete collection: {str(e)}"
        )


@router.get("/collections/{collection_name}/search")
async def search_by_metadata(
    collection_name: str,
    key: str,
    value: str,
    limit: int = 100,
    username: str = Depends(require_auth_dependency)
):
    """Search for points by metadata field"""
    try:
        points = qdrant_service.search_points_by_metadata(
            collection_name=collection_name,
            metadata_key=key,
            metadata_value=value,
            limit=limit
        )

        return {
            "points": points,
            "total_found": len(points)
        }

    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/collections/{collection_name}/documents")
async def list_documents(
    collection_name: str,
    username: str = Depends(require_auth_dependency)
):
    """Get list of unique documents in a collection (grouped by source filename)"""
    try:
        # Get all points from the collection
        all_points = []
        offset = None

        while True:
            result = qdrant_service.scroll_points(
                collection_name=collection_name,
                limit=100,
                offset=offset,
                with_vectors=False
            )
            all_points.extend(result["points"])

            if not result["next_offset"]:
                break
            offset = result["next_offset"]

        # Group by source filename
        documents_map = {}
        for point in all_points:
            source = point["payload"].get("source", "Unknown")

            if source not in documents_map:
                documents_map[source] = {
                    "filename": source,
                    "file_type": point["payload"].get("file_type", "unknown"),
                    "uploaded_at": point["payload"].get("uploaded_at"),
                    "chunk_count": 0,
                    "point_ids": []
                }

            documents_map[source]["chunk_count"] += 1
            documents_map[source]["point_ids"].append(point["id"])

        # Convert to list and sort by upload date (newest first)
        documents = list(documents_map.values())
        documents.sort(key=lambda x: x.get("uploaded_at") or "", reverse=True)

        return {
            "documents": documents,
            "total_documents": len(documents),
            "total_chunks": len(all_points)
        }

    except Exception as e:
        print(f"List documents error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.delete("/collections/{collection_name}/documents/{filename}")
async def delete_document(
    collection_name: str,
    filename: str,
    username: str = Depends(require_auth_dependency)
):
    """Delete all chunks of a specific document by filename"""
    try:
        # Get all points for this document
        points = qdrant_service.search_points_by_metadata(
            collection_name=collection_name,
            metadata_key="source",
            metadata_value=filename,
            limit=10000  # High limit to get all chunks
        )

        if not points:
            raise HTTPException(
                status_code=404,
                detail=f"No chunks found for document '{filename}'"
            )

        # Extract point IDs
        point_ids = [p["id"] for p in points]

        # Delete all points
        qdrant_service.delete_points(
            collection_name=collection_name,
            point_ids=point_ids
        )

        return DeleteResponse(
            success=True,
            message=f"Successfully deleted document '{filename}' ({len(point_ids)} chunks)"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete document error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.get("/collections", response_model=ListCollectionsResponse)
async def list_collections(username: str = Depends(require_auth_dependency)):
    """List all available Qdrant collections"""
    try:
        collections_data = qdrant_service.list_collections()

        collections = [
            CollectionInfo(
                name=col["name"],
                points_count=col["points_count"],
                vectors_count=col.get("vectors_count", col["points_count"]),
                indexed_vectors_count=col.get("indexed_vectors_count", col["points_count"]),
                status=col.get("status", "ready")
            )
            for col in collections_data
        ]

        return ListCollectionsResponse(
            collections=collections,
            total_collections=len(collections)
        )

    except Exception as e:
        print(f"List collections error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list collections: {str(e)}"
        )


@router.get("/collections/{collection_name}/info", response_model=CollectionInfo)
async def get_collection_info(
    collection_name: str,
    username: str = Depends(require_auth_dependency)
):
    """Get detailed information about a specific collection"""
    try:
        if not qdrant_service.collection_exists(collection_name):
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_name}' not found"
            )

        info = qdrant_service.get_collection_info(collection_name)

        return CollectionInfo(
            name=collection_name,
            points_count=info["points_count"],
            vectors_count=info.get("vectors_count", info["points_count"]),
            indexed_vectors_count=info.get("indexed_vectors_count", info["points_count"]),
            status=info.get("status", "ready")
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Get collection info error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get collection info: {str(e)}"
        )
