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
        # Validate file size (10MB limit)
        file_content = await file.read()
        max_size = 10 * 1024 * 1024  # 10MB
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
