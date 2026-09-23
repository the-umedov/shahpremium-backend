from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile

from app.core.database import DbSession
from app.core.deps import CurrentUser, require_permissions
from app.core.storage import storage_service
from app.models.enums import DocumentAccess
from app.modules.documents import service
from app.modules.documents.allowed_files import mime_for_ext
from app.modules.documents.schemas import DocumentQuery

router = APIRouter(tags=["documents"])

# Asl documents.controller.js'da @Public() bilan belgilangan (faqat HMAC imzo
# bilan himoyalangan, autentifikatsiyasiz ochiq havola — masalan mijozga SMS/email
# orqali yuborilgan yuklab olish havolasi). Shu xatti-harakatni saqlash uchun
# ALOHIDA router: main.py buni `dependencies=[Depends(get_current_user)]` SIZ
# ulaydi, qolgan `router`dagi marshrutlar esa login talab qiladi.
public_router = APIRouter(tags=["documents"])


@public_router.get("/download")
async def download(key: str = Query(...), exp: str = Query(...), sig: str = Query(...)) -> Response:
    if not storage_service.verify_signature(key, int(exp), sig):
        return Response(content='{"message": "Havola yaroqsiz yoki muddati o\'tgan"}', status_code=403, media_type="application/json")
    try:
        buf = storage_service.read(key)
    except (FileNotFoundError, OSError):
        return Response(content='{"message": "Fayl topilmadi"}', status_code=404, media_type="application/json")
    ext = "." + key.rsplit(".", 1)[-1] if "." in key else ""
    mime = mime_for_ext(ext)
    return Response(content=buf, media_type=mime)


@router.get("", dependencies=[Depends(require_permissions("documents.read"))])
async def list_documents(db: DbSession, user: CurrentUser, query: DocumentQuery = Depends()) -> dict:
    return await service.list_documents(db, query, user)


@router.post("", status_code=201, dependencies=[Depends(require_permissions("documents.upload"))])
async def create_document(
    db: DbSession,
    user: CurrentUser,
    file: UploadFile = File(...),
    title: str = Form(...),
    doc_type: str | None = Form(None),
    case_id: str | None = Form(None),
    contract_id: str | None = Form(None),
    client_id: str | None = Form(None),
    access_level: DocumentAccess | None = Form(None),
) -> dict:
    data = await file.read()
    return await service.create_document(
        db,
        title=title,
        doc_type=doc_type,
        case_id=case_id,
        contract_id=contract_id,
        client_id=client_id,
        access_level=access_level,
        data=data,
        mime_type=file.content_type or "",
        user=user,
    )


@router.get("/{document_id}", dependencies=[Depends(require_permissions("documents.read"))])
async def get_document(document_id: str, db: DbSession, user: CurrentUser) -> dict:
    return await service.get_document(db, document_id, user)


@router.get("/{document_id}/link", dependencies=[Depends(require_permissions("documents.read"))])
async def get_download_link(document_id: str, db: DbSession, user: CurrentUser) -> dict:
    return await service.create_download_link(db, document_id, user)


@router.post("/{document_id}/versions", status_code=201, dependencies=[Depends(require_permissions("documents.update"))])
async def add_version(
    document_id: str,
    db: DbSession,
    user: CurrentUser,
    file: UploadFile = File(...),
    comment: str | None = Form(None),
) -> dict:
    data = await file.read()
    return await service.add_version(
        db,
        document_id,
        data=data,
        mime_type=file.content_type or "",
        comment=comment,
        user=user,
    )


@router.delete("/{document_id}", dependencies=[Depends(require_permissions("documents.delete"))])
async def remove_document(document_id: str, db: DbSession, user: CurrentUser) -> dict:
    return await service.remove_document(db, document_id, user)
