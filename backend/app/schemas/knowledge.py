from pydantic import BaseModel, Field, field_validator


class IngestTextRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=500000)

    @field_validator("title", "content")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class DocumentInfo(BaseModel):
    id: str
    title: str
    filename: str
    chunk_count: int
    created_at: str


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]
    total: int


class SearchResult(BaseModel):
    content: str
    title: str
    doc_id: str
    chunk_index: int
    distance: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
