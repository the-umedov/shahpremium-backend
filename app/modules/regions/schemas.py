from pydantic import BaseModel, Field


class RegionCreateRequest(BaseModel):
    name: str
    code: str


class RegionUpdateRequest(BaseModel):
    name: str | None = None
    code: str | None = None


class DistrictCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
