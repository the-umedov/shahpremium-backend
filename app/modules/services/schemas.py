from pydantic import BaseModel, Field

from app.models.enums import ServiceCategory


class ServiceCreateRequest(BaseModel):
    code: str
    name: str
    description: str | None = None
    category: ServiceCategory
    base_price: float | None = Field(default=None, ge=0)
    sort_order: int | None = None


class ServiceUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    category: ServiceCategory | None = None
    base_price: float | None = Field(default=None, ge=0)
    sort_order: int | None = None
    is_active: bool | None = None


class SetActiveRequest(BaseModel):
    is_active: bool


class ReorderItem(BaseModel):
    id: str
    sort_order: int


class ReorderRequest(BaseModel):
    items: list[ReorderItem]
