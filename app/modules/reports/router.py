"""reports.controller.js ekvivalenti."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.database import DbSession
from app.core.deps import require_permissions
from app.modules.reports import service
from app.modules.reports.exporter import export_report
from app.modules.reports.schemas import REPORT_TYPES, ReportData, ReportQuery

router = APIRouter(tags=["reports"])


def _parse_type(report_type: str) -> str:
    if report_type not in REPORT_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Noma'lum hisobot turi")
    return report_type


@router.get(
    "/{type}",
    response_model=ReportData,
    dependencies=[Depends(require_permissions("reports.read"))],
)
async def get_report(type: str, db: DbSession, query: ReportQuery = Depends()) -> ReportData:
    return await service.generate(db, _parse_type(type), query)


@router.get(
    "/{type}/export",
    # Eksport — permissions reports.export bilan himoyalangan
    dependencies=[Depends(require_permissions("reports.export"))],
)
async def export(type: str, db: DbSession, query: ReportQuery = Depends()) -> Response:
    fmt = query.format or "csv"
    if fmt not in ("csv", "xlsx", "pdf"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "format: csv | xlsx | pdf")
    data = await service.generate(db, _parse_type(type), query)
    buffer, content_type, filename = export_report(data, fmt)
    return Response(
        content=buffer,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
