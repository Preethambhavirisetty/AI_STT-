import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile

from app.core.config import settings
from app.core.security import get_current_user
from app.schemas.knowledge import (
    DocumentInfo,
    DocumentListResponse,
    IngestTextRequest,
    SearchResponse,
    SearchResult,
)
from app.schemas.users import CurrentUser
from app.services.doc_registry import get_doc, list_docs, register, remove_doc
from app.services.document_processor import chunk_text, extract_text
from app.services.vector_store import add_chunks, delete_doc_chunks, search, total_chunks

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/upload", response_model=DocumentInfo)
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    user: CurrentUser = Depends(get_current_user),
):
    file_bytes = await file.read()
    if len(file_bytes) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_BYTES} bytes",
        )
    filename = file.filename or "upload"
    doc_title = title.strip() if title and title.strip() else filename

    try:
        text = extract_text(file_bytes, filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No text could be extracted from the file")

    doc_id = str(uuid.uuid4())
    await add_chunks(user.id, doc_id, chunks, {"title": doc_title, "filename": filename})
    record = await register(user.id, doc_id, doc_title, filename, len(chunks))
    return DocumentInfo(**record)


@router.post("/ingest", response_model=DocumentInfo)
async def ingest_text(body: IngestTextRequest, user: CurrentUser = Depends(get_current_user)):
    chunks = chunk_text(body.content)
    if not chunks:
        raise HTTPException(status_code=400, detail="Content is empty")

    doc_id = str(uuid.uuid4())
    await add_chunks(user.id, doc_id, chunks, {"title": body.title, "filename": "text_input"})
    record = await register(user.id, doc_id, body.title, "text_input", len(chunks))
    return DocumentInfo(**record)


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(user: CurrentUser = Depends(get_current_user)):
    docs = await list_docs(user.id)
    return DocumentListResponse(
        documents=[DocumentInfo(**d) for d in docs],
        total=len(docs),
    )


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, user: CurrentUser = Depends(get_current_user)):
    doc = await get_doc(user.id, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await delete_doc_chunks(user.id, doc_id)
    await remove_doc(user.id, doc_id)
    return {"status": "deleted", "doc_id": doc_id}


@router.get("/search", response_model=SearchResponse)
async def search_knowledge(
    q: str,
    n: int = Query(default=5, ge=1, le=20),
    user: CurrentUser = Depends(get_current_user),
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    hits = await search(user.id, q, n_results=n)
    results = [
        SearchResult(
            content=h["content"],
            title=h["metadata"].get("title", ""),
            doc_id=h["metadata"].get("doc_id", ""),
            chunk_index=h["metadata"].get("chunk_index", 0),
            distance=round(h["distance"], 4),
        )
        for h in hits
    ]
    return SearchResponse(query=q, results=results)


@router.get("/stats")
async def knowledge_stats(user: CurrentUser = Depends(get_current_user)):
    docs = await list_docs(user.id)
    chunks = await total_chunks(user.id)
    return {"document_count": len(docs), "total_chunks": chunks}
