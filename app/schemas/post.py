from pydantic import BaseModel, Field


class PostCandidate(BaseModel):
    post_id: str
    author_name: str
    author_headline: str | None = None
    post_text: str
    post_url: str
    published_at: str | None = None

    relevance_hint: str | None = None

    source: str = Field(default="linkedin")