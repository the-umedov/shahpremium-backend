from pydantic import BaseModel


class UserUpdateRequest(BaseModel):
    is_active: bool | None = None
    region_id: str | None = None
    office_id: str | None = None
    locale: str | None = None


class SetRolesRequest(BaseModel):
    role_ids: list[str]
