"""Audit Logs endpoints

Endpoints:
 - GET /logs/audits  -> paged list (minimal fields)
 - GET /logs/audits/{id} -> detail (full fields)
"""

from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from app.core.container import Container
from app.services.interfaces.audit_log_service_interface import IAuditLogService
from uuid import UUID
from datetime import datetime

from app.schema.response.audit_log import AuditLogListResponse, AuditLogDetailResponse
from app.schema.response.pagination import PagedData
from app.core.constants.pagination import PAGE, PAGE_SIZE
from app.core.jwt_security import JWTBearer


router = APIRouter(
    prefix="/logs",
    tags=["Logs"],
    dependencies=[Depends(JWTBearer())],
)


@router.get(
        "/audits", 
        summary="Search audit logs",
        response_model=PagedData[AuditLogListResponse])
@inject
async def search_audits(
    type: str | None = None,
    table_name: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    user_id: UUID | None = None,
    page: int = PAGE,
    page_size: int = PAGE_SIZE,
    audit_log_service: IAuditLogService = Depends(Provide[Container.audit_log_service]),
):
    """Return paged audit logs (minimal fields).

        Filters supported:
        - `type`: one of `Insert`, `Update`, `Delete`
        - `table_name`
        - `start_date` / `end_date`: optional range. When provided the
            results will include records with `date_time >= start_date` and
            `date_time <= end_date`.
            Use ISO 8601 / RFC3339 format, e.g. `2026-02-13T10:30:00Z`.
            Example: `/logs/audits?start_date=2026-02-13T10:30:00Z&end_date=2026-02-14T00:00:00Z`
        - `user_id`
    """
    return await audit_log_service.search(page, page_size, type=type, table_name=table_name, start_date=start_date, end_date=end_date, user_id=user_id)


@router.get(
        "/audits/{id}",
        summary="Get audit log details by id",
        response_model=AuditLogDetailResponse)
@inject
async def get_audit(id: UUID, audit_log_service: IAuditLogService = Depends(Provide[Container.audit_log_service])):
    """Return full audit log details for given id."""

    return await audit_log_service.get_by_id(id)
