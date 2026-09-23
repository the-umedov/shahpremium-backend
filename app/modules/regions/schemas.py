from pydantic import BaseModel


class RegionCreateRequest(BaseModel):
    name: str
    code: str


class RegionUpdateRequest(BaseModel):
    name: str | None = None
    code: str | None = None
