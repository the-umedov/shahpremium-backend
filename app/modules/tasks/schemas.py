"""tasks/dto/task.dto.js ekvivalenti."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.core.pagination import PaginationQuery
from app.models.enums import TaskPriority, TaskStatus


class CreateTaskRequest(BaseModel):
    title: str
    description: str | None = None
    assignee_id: str | None = None
    case_id: str | None = None
    client_id: str | None = None
    due_date: datetime | None = None
    priority: TaskPriority | None = None


class UpdateTaskRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: str | None = None
    due_date: datetime | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None


class MoveTaskRequest(BaseModel):
    status: TaskStatus


class TaskQuery(PaginationQuery):
    status: TaskStatus | None = None
    case_id: str | None = None
    assignee_id: str | None = None
