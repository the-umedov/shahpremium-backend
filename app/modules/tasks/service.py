"""tasks.service.js ekvivalenti.

Kanban-uslubidagi vazifa taxtasi: Task CRUD + holat o'tishlari (TODO ->
IN_PROGRESS -> DONE, muddati o'tganlar uchun OVERDUE), Case/Client bilan
bog'lanish, muddatlarni skanerlash orqali bildirishnoma yuborish.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from app.core.timeutils import utcnow

from fastapi import HTTPException, status
from sqlalchemy import ColumnElement, case, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import build_page, to_paginated
from app.core.security import AuthUser
from app.models.enums import NotificationChannel, RoleKey, TaskPriority, TaskStatus
from app.models.models import Case, Notification, Task
from app.modules.tasks.schemas import CreateTaskRequest, TaskQuery, UpdateTaskRequest

# Prisma'da TaskPriority - native enum, shu sababli "priority desc" ustuvorlik
# darajasi bo'yicha (LOW<MEDIUM<HIGH<URGENT) saralanadi. Bu yerda ustun oddiy
# string bo'lgani uchun xuddi shu tartibni CASE ifodasi bilan tiklaymiz.
_PRIORITY_RANK = case(
    (Task.priority == TaskPriority.LOW, 0),
    (Task.priority == TaskPriority.MEDIUM, 1),
    (Task.priority == TaskPriority.HIGH, 2),
    (Task.priority == TaskPriority.URGENT, 3),
    else_=0,
)


def _privileged(user: AuthUser) -> bool:
    privileged_roles = {RoleKey.SUPER_ADMIN.value, RoleKey.ADMIN.value, RoleKey.MANAGER.value}
    return any(r in privileged_roles for r in user.roles)


def _is_client(user: AuthUser) -> bool:
    return RoleKey.CLIENT.value in user.roles


def _scope(user: AuthUser) -> ColumnElement | None:
    """Object-level scope."""
    if _privileged(user):
        return None
    if _is_client(user):
        return Task.client_id == (user.client_id or "__none__")
    return or_(
        Task.assignee_id == user.id,
        Task.author_id == user.id,
        Task.case.has(Case.office_id == (user.office_id or "__none__")),
    )


def serialize(t: Task) -> dict:
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "assignee_id": t.assignee_id,
        "author_id": t.author_id,
        "case_id": t.case_id,
        "client_id": t.client_id,
        "due_date": t.due_date,
        "priority": t.priority,
        "status": t.status,
        "created_at": t.created_at,
        "updated_at": t.updated_at,
    }


async def list_tasks(db: AsyncSession, query: TaskQuery, user: AuthUser) -> dict:
    page_info = build_page(query, default_sort="created_at")

    filters = [Task.deleted_at.is_(None)]
    scope_filter = _scope(user)
    if scope_filter is not None:
        filters.append(scope_filter)
    if query.status:
        filters.append(Task.status == query.status)
    if query.case_id:
        filters.append(Task.case_id == query.case_id)
    if query.assignee_id:
        filters.append(Task.assignee_id == query.assignee_id)

    sort_col = getattr(Task, page_info["sort"], Task.created_at)
    order_col = sort_col.desc() if page_info["order"] == "desc" else sort_col.asc()

    total = (await db.execute(select(func.count()).select_from(Task).where(*filters))).scalar_one()
    items = (
        await db.execute(
            select(Task).where(*filters).order_by(order_col).offset(page_info["skip"]).limit(page_info["take"])
        )
    ).scalars().all()

    return to_paginated([serialize(t) for t in items], total, page_info["page"], page_info["limit"])


async def board(db: AsyncSession, user: AuthUser, case_id: str | None) -> dict[str, list[dict]]:
    """Kanban: Ochiq -> Jarayonda -> Bajarilgan ustunlari."""
    filters = [Task.deleted_at.is_(None)]
    scope_filter = _scope(user)
    if scope_filter is not None:
        filters.append(scope_filter)
    if case_id:
        filters.append(Task.case_id == case_id)

    columns = [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.DONE]
    result: dict[str, list[dict]] = {}
    for col in columns:
        stmt = (
            select(Task)
            .where(*filters, Task.status == col)
            .order_by(_PRIORITY_RANK.desc(), Task.due_date.asc())
        )
        rows = (await db.execute(stmt)).scalars().all()
        result[col.value] = [serialize(t) for t in rows]
    return result


async def create(db: AsyncSession, dto: CreateTaskRequest, user: AuthUser) -> Task:
    task = Task(
        title=dto.title,
        description=dto.description,
        assignee_id=dto.assignee_id,
        author_id=user.id,
        case_id=dto.case_id,
        client_id=dto.client_id,
        due_date=dto.due_date,
        priority=dto.priority or TaskPriority.MEDIUM,
        status=TaskStatus.TODO,
    )
    db.add(task)
    await db.commit()
    return task


async def _get_scoped(db: AsyncSession, id: str, user: AuthUser) -> Task:
    filters = [Task.id == id, Task.deleted_at.is_(None)]
    scope_filter = _scope(user)
    if scope_filter is not None:
        filters.append(scope_filter)
    task = (await db.execute(select(Task).where(*filters))).scalar_one_or_none()
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vazifa topilmadi")
    return task


async def update(db: AsyncSession, id: str, dto: UpdateTaskRequest, user: AuthUser) -> Task:
    task = await _get_scoped(db, id, user)
    for field, value in dto.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    return task


async def move(db: AsyncSession, id: str, new_status: TaskStatus, user: AuthUser) -> Task:
    """Kanban ustundan ustunga ko'chirish."""
    task = await _get_scoped(db, id, user)
    task.status = new_status
    await db.commit()
    return task


async def remove(db: AsyncSession, id: str, user: AuthUser) -> dict:
    task = await _get_scoped(db, id, user)
    task.deleted_at = utcnow()
    await db.commit()
    return {"ok": True}


async def scan_deadlines(db: AsyncSession) -> dict:
    """Muddatlarni skanerlash (cron o'rniga endpoint):

    - muddati o'tgan tugallanmagan vazifalarni OVERDUE qiladi;
    - 24 soat ichida muddati keladiganlar bo'yicha ijrochiga bildirishnoma.
    """
    now = utcnow()
    soon = now + timedelta(hours=24)

    overdue_result = await db.execute(
        update(Task)
        .where(
            Task.deleted_at.is_(None),
            Task.due_date < now,
            Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]),
        )
        .values(status=TaskStatus.OVERDUE)
    )
    marked_overdue = overdue_result.rowcount or 0

    due_soon = (
        await db.execute(
            select(Task.id, Task.title, Task.assignee_id, Task.due_date).where(
                Task.deleted_at.is_(None),
                Task.due_date >= now,
                Task.due_date <= soon,
                Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]),
                Task.assignee_id.is_not(None),
            )
        )
    ).all()

    for task in due_soon:
        db.add(
            Notification(
                user_id=task.assignee_id,
                channel=NotificationChannel.IN_APP,
                title="Vazifa muddati yaqinlashmoqda",
                body=f'"{task.title}" vazifasi muddati tugaydi.',
            )
        )

    await db.commit()
    return {"marked_overdue": marked_overdue, "notified": len(due_soon)}
