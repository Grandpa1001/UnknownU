from pydantic import BaseModel, Field


class CreateWorldRequest(BaseModel):
    name: str = "world"
    organism_count: int = Field(default=3, ge=1, le=20)
    seed: int | None = None
    max_tick: int | None = None
