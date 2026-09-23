"""reports.service.js / reports.controller.js ekvivalenti."""

from __future__ import annotations

from pydantic import BaseModel

REPORT_TYPES: list[str] = [
    "payments",
    "income",
    "expense",
    "debt",
    "clients",
    "employees",
    "services",
    "cases",
]


class ReportQuery(BaseModel):
    """reports.controller.js#filters() bilan yig'iladigan filtrlar + eksport formati."""

    date_from: str | None = None
    date_to: str | None = None
    region_id: str | None = None
    employee_id: str | None = None
    client_id: str | None = None
    service_id: str | None = None
    format: str | None = None  # faqat /export endpointida: csv | xlsx | pdf


class ReportColumn(BaseModel):
    key: str
    header: str


class ReportData(BaseModel):
    title: str
    columns: list[ReportColumn]
    rows: list[dict]
