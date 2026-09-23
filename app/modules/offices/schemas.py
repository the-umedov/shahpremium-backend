from pydantic import BaseModel


class OfficeCreateRequest(BaseModel):
    name: str
    address: str | None = None
    region_id: str


class OfficeUpdateRequest(BaseModel):
    name: str | None = None
    address: str | None = None
    region_id: str | None = None
