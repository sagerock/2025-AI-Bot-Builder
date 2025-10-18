# OCR + Qdrant Guide for Large Scanned Documents

## Overview

Your bot now supports OCR (Optical Character Recognition) for scanned documents up to 25 MB. This is perfect for handling your 11-19 MB scanned Torts textbook pages.

## How It Works

When you upload a PDF:
1. The system automatically detects if it's a scanned document (image-based) or has embedded text
2. If scanned, it uses OCR to extract text from the images
3. The text is chunked into manageable pieces
4. Each chunk is embedded and stored in Qdrant (vector database)
5. When you chat, relevant sections are retrieved using RAG (Retrieval Augmented Generation)

## Recommended Workflow for Your Torts Study Bot

### Step 1: Upload a Chapter to Qdrant

Use the document upload endpoint to process and store a chapter:

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -F "file=@torts-chapter-3.pdf" \
  -F "collection=torts-chapter-3" \
  -F "chunk_size=1000" \
  -F "chunk_overlap=200" \
  -F "create_if_missing=true"
```

This will:
- OCR the scanned pages (if needed)
- Extract all text
- Chunk it into ~1000 character pieces with 200 character overlap
- Create a collection named "torts-chapter-3"
- Upload all chunks to Qdrant

### Step 2: Configure Your Bot to Use RAG

Make sure your Torts bot has these settings enabled:
- `use_qdrant: true`
- `qdrant_collection: "torts-chapter-3"`
- `qdrant_top_k: 5` (retrieves top 5 most relevant chunks)

### Step 3: Chat with Your Bot

Now when you ask questions, the bot will:
1. Search the Qdrant collection for relevant text chunks
2. Include those chunks as context in the prompt
3. Answer based on your actual textbook content

Example questions:
- "What are the elements of negligence?"
- "Explain the doctrine of res ipsa loquitur"
- "What's the difference between battery and assault?"

### Step 4: Clean Up When Done (Optional)

After you're done studying that chapter, you can delete the collection:

```bash
curl -X DELETE "http://localhost:8000/api/documents/collections/torts-chapter-3" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

## API Endpoints Reference

### Upload Document
- **POST** `/api/documents/upload`
- Max size: 25 MB
- Supports: PDF (with OCR), TXT, MD, HTML
- Auto-detects if OCR is needed

### List All Collections
- **GET** `/api/documents/collections`
- Shows all your collections and their size

### Get Collection Info
- **GET** `/api/documents/collections/{name}/info`
- Shows point count and status for a specific collection

### List Documents in Collection
- **GET** `/api/documents/collections/{name}/documents`
- Shows all documents uploaded to this collection

### Delete Collection
- **DELETE** `/api/documents/collections/{name}`
- Removes the entire collection

### Delete Specific Document
- **DELETE** `/api/documents/collections/{name}/documents/{filename}`
- Removes just one document's chunks from a collection

## Why This Approach is Better Than Direct Upload

### ❌ Direct Upload (what we avoided):
- 50 pages × 15 MB = 750 MB of images
- Base64 encoded = ~1 GB payload (will fail)
- Uses 50,000-100,000 tokens just for images
- Slow processing
- Limited by API payload size

### ✅ OCR + Qdrant (what we implemented):
- Extracts text efficiently
- Only retrieves relevant sections (saves tokens)
- Can handle unlimited pages
- Reusable across multiple chat sessions
- Much faster responses
- Can search/query your textbook content

## Installation Requirements

Before using OCR features, install the Python dependencies:

```bash
pip install -r requirements.txt
```

### System Requirements for OCR

You'll also need Tesseract OCR installed on your system:

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

Also install poppler for PDF to image conversion:

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
Download from: http://blog.alivate.com.au/poppler-windows/

## Performance Tips

1. **DPI Settings**: The OCR service uses 300 DPI by default, which balances quality and speed. For better accuracy on small text, you could modify this in `app/services/ocr_service.py:82`

2. **Chunk Size**: Default is 1000 characters with 200 overlap. For legal texts with complex concepts, you might want larger chunks (1500-2000 characters)

3. **Processing Time**: Expect ~2-5 seconds per page for OCR processing of high-quality scans

4. **Storage**: Each 50-page chapter will use ~100-500 vectors in Qdrant (depending on text density)

## Example: Full Workflow for Torts Chapter

```bash
# 1. Upload chapter 3 (scanned PDF, 15 MB, 45 pages)
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@torts-chapter-3-negligence.pdf" \
  -F "collection=torts-chapter-3" \
  -F "create_if_missing=true"

# Response: Successfully uploaded 87 chunks from torts-chapter-3-negligence.pdf

# 2. Update your bot to use this collection
# (via UI or API - set use_qdrant=true, qdrant_collection="torts-chapter-3")

# 3. Start chatting!
# "What are the elements of negligence according to the textbook?"

# 4. When done, check what's stored
curl -X GET "http://localhost:8000/api/documents/collections/torts-chapter-3/info" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 5. Delete when done with this chapter
curl -X DELETE "http://localhost:8000/api/documents/collections/torts-chapter-3" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### OCR Returns Empty Text
- Check that Tesseract is installed: `tesseract --version`
- Verify the PDF pages are actually scanned (image-based)
- Try manually viewing the PDF - if you can select/copy text, it's not scanned

### "File too large" Error
- Current limit is 25 MB
- Try splitting very large PDFs into smaller sections
- Use PDF compression tools to reduce file size

### Poor OCR Accuracy
- Ensure scan quality is at least 300 DPI
- Check that pages are properly aligned/not skewed
- Dark or faded text may need image preprocessing

### Collection Not Found
- Make sure you created it with `create_if_missing=true`
- Check available collections: `GET /api/documents/collections`
- Verify collection name matches exactly (case-sensitive)

## Need Help?

Check the main README or contact support with questions about:
- OCR accuracy issues
- Collection management
- Bot configuration
- API usage
