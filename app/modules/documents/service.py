from __future__ import annotations

from datetime import datetime
from app.core.timeutils import utcnow

from fastapi import HTTPException, status
from sqlalchemy import and_, func, inspect, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.pagination import build_page, to_paginated
from app.core.security import AuthUser
from app.core.storage import storage_service
from app.models.enums import DocumentAccess, RoleKey
from app.models.models import Case, Document, DocumentVersion
from app.modules.documents.allowed_files import MAX_FILE_SIZE, ext_for_mime, is_allowed_mime
from app.modules.documents.schemas import DocumentQuery


def _is_privileged(user: AuthUser) -> bool:
    keys = {RoleKey.SUPER_ADMIN.value, RoleKey.ADMIN.value}
    return any(r in keys for r in user.roles)


def _is_client(user: AuthUser) -> bool:
    return RoleKey.CLIENT.value in user.roles


def _columns_dict(obj) -> dict:
    """Python-tomon snake_case atribut nomlari bilan (DB ustun nomi bilan EMAS)."""
    return {attr.key: getattr(obj, attr.key) for attr in inspect(obj).mapper.column_attrs}


def validate_file(mime_type: str | None, size: int) -> None:
    if not mime_type:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Fayl yuborilmadi")
    if not is_allowed_mime(mime_type):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Ruxsat etilmagan format: {mime_type}")
    if size > MAX_FILE_SIZE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Fayl hajmi 25 MB dan oshmasligi kerak")


async def _belongs_to_client(db: AsyncSession, user: AuthUser, doc: Document) -> bool:
    if doc.client_id and doc.client_id == user.client_id:
        return True
    if doc.case_id:
        case_client_id = (await db.execute(select(Case.client_id).where(Case.id == doc.case_id))).scalar_one_or_none()
        return case_client_id == user.client_id
    return False


async def assert_can_access(db: AsyncSession, user: AuthUser, doc: Document) -> None:
    """Object-level: foydalanuvchi shu hujjatni ko'ra oladimi (documents.service.js#assertCanAccess)."""
    if _is_privileged(user):
        return
    if doc.access_level == DocumentAccess.PRIVATE:
        if doc.uploaded_by_id != user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Topilmadi")
        return
    if doc.access_level == DocumentAccess.RESTRICTED:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Ruxsat yo'q")
    if doc.access_level == DocumentAccess.CLIENT_SHARED:
        if _is_client(user):
            if not await _belongs_to_client(db, user, doc):
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Topilmadi")
        return  # staff ham ko'radi
    # OFFICE (default)
    if _is_client(user):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topilmadi")


async def list_documents(db: AsyncSession, query: DocumentQuery, user: AuthUser) -> dict:
    page_info = build_page(query, default_sort="created_at")
    conditions = [Document.deleted_at.is_(None)]
    if query.case_id:
        conditions.append(Document.case_id == query.case_id)
    if query.client_id:
        conditions.append(Document.client_id == query.client_id)
    if query.contract_id:
        conditions.append(Document.contract_id == query.contract_id)
    if query.search:
        conditions.append(Document.title.ilike(f"%{query.search}%"))
    if _is_client(user):
        # mijozga faqat unga ochiq hujjatlar
        conditions.append(Document.access_level == DocumentAccess.CLIENT_SHARED)
        conditions.append(
            or_(
                Document.client_id == (user.client_id or "__none__"),
                Document.case_id.in_(select(Case.id).where(Case.client_id == (user.client_id or "__none__"))),
            )
        )
    where_clause = and_(*conditions)

    stmt = select(Document).where(where_clause)
    sort_col = getattr(Document, page_info["sort"], Document.created_at)
    stmt = stmt.order_by(sort_col.desc() if page_info["order"] == "desc" else sort_col.asc())
    stmt = stmt.offset(page_info["skip"]).limit(page_info["take"])

    total = (await db.execute(select(func.count()).select_from(Document).where(where_clause))).scalar_one()
    rows = (await db.execute(stmt)).scalars().all()
    return to_paginated([_columns_dict(d) for d in rows], total, page_info["page"], page_info["limit"])


async def _get_entity(db: AsyncSession, document_id: str, user: AuthUser) -> Document:
    doc = (
        await db.execute(
            select(Document)
            .options(selectinload(Document.versions))
            .where(Document.id == document_id, Document.deleted_at.is_(None))
        )
    ).scalar_one_or_none()
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hujjat topilmadi")
    await assert_can_access(db, user, doc)
    return doc


def _serialize(doc: Document) -> dict:
    data = _columns_dict(doc)
    versions = sorted(doc.versions, key=lambda v: v.version, reverse=True)
    data["versions"] = [_columns_dict(v) for v in versions]
    return data


async def get_document(db: AsyncSession, document_id: str, user: AuthUser) -> dict:
    doc = await _get_entity(db, document_id, user)
    return _serialize(doc)


async def create_document(
    db: AsyncSession,
    *,
    title: str,
    doc_type: str | None,
    case_id: str | None,
    contract_id: str | None,
    client_id: str | None,
    access_level: DocumentAccess | None,
    data: bytes,
    mime_type: str,
    user: AuthUser,
) -> dict:
    """Yangi hujjat + birinchi versiya (documents.service.js#create)."""
    validate_file(mime_type, len(data))
    stored = storage_service.save(data, mime_type, ext_for_mime(mime_type))

    doc = Document(
        title=title,
        doc_type=doc_type,
        case_id=case_id,
        contract_id=contract_id,
        client_id=client_id,
        access_level=access_level or DocumentAccess.OFFICE,
        storage_key=stored["storage_key"],
        mime_type=stored["mime_type"],
        size_bytes=stored["size_bytes"],
        checksum=stored["checksum"],
        current_version=1,
        uploaded_by_id=user.id,
    )
    db.add(doc)
    await db.flush()

    db.add(
        DocumentVersion(
            document_id=doc.id,
            version=1,
            storage_key=stored["storage_key"],
            mime_type=stored["mime_type"],
            size_bytes=stored["size_bytes"],
            checksum=stored["checksum"],
            uploaded_by_id=user.id,
            comment="Boshlang'ich versiya",
        )
    )
    await db.commit()
    return await get_document(db, doc.id, user)


async def add_version(
    db: AsyncSession,
    document_id: str,
    *,
    data: bytes,
    mime_type: str,
    comment: str | None,
    user: AuthUser,
) -> dict:
    """Yangi versiya — eskilari saqlanadi (documents.service.js#addVersion)."""
    doc = await _get_entity(db, document_id, user)
    validate_file(mime_type, len(data))
    stored = storage_service.save(data, mime_type, ext_for_mime(mime_type))
    next_version = doc.current_version + 1

    db.add(
        DocumentVersion(
            document_id=document_id,
            version=next_version,
            storage_key=stored["storage_key"],
            mime_type=stored["mime_type"],
            size_bytes=stored["size_bytes"],
            checksum=stored["checksum"],
            uploaded_by_id=user.id,
            comment=comment,
        )
    )
    doc.storage_key = stored["storage_key"]
    doc.mime_type = stored["mime_type"]
    doc.size_bytes = stored["size_bytes"]
    doc.checksum = stored["checksum"]
    doc.current_version = next_version
    await db.commit()
    return await get_document(db, document_id, user)


async def create_download_link(db: AsyncSession, document_id: str, user: AuthUser) -> dict:
    doc = await _get_entity(db, document_id, user)
    return {"url": storage_service.create_signed_path(doc.storage_key)}


async def remove_document(db: AsyncSession, document_id: str, user: AuthUser) -> dict:
    doc = await _get_entity(db, document_id, user)
    doc.deleted_at = utcnow()
    await db.commit()
    return {"ok": True}
