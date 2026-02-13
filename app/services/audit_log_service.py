from datetime import datetime
from logging import log
from typing import List
from uuid import UUID

from app.core.constants.pagination import calculate_skip
from app.schema.response.audit_log import AuditLogListResponse, AuditLogDetailResponse
from app.schema.response.pagination import PagedData, create_paged_response
from app.services.interfaces.audit_log_service_interface import IAuditLogService
from app.repositories.interfaces.audit_log_repository_interface import IAuditLogRepository
from app.utils.exception_utils import NotFoundException


class AuditLogService(IAuditLogService):
    def __init__(self, audit_log_repository: IAuditLogRepository):
        self.audit_log_repository = audit_log_repository

    async def search(self, page: int, page_size: int, type: str | None = None, table_name: str | None = None, start_date: datetime | None = None, end_date: datetime | None = None, user_id: UUID | None = None) -> PagedData[AuditLogListResponse]:
        skip = calculate_skip(page, page_size)
        audit_logs, total = await self.audit_log_repository.get_all_paginated(skip=skip, limit=page_size, type=type, table_name=table_name, start_date=start_date, end_date=end_date, user_id=user_id)


        audit_logs_responses = [
            AuditLogListResponse(
                id=audit_log.id,
                table_name=audit_log.table_name,
                user_id=audit_log.user_id,
                user_full_name=(audit_log.user.full_name if getattr(audit_log, "user", None) else None),
                type=audit_log.type,
                date_time=audit_log.date_time,
            )
            for audit_log in audit_logs
        ]

        return create_paged_response(audit_logs_responses, total, page, page_size)

    async def get_by_id(self, id: UUID) -> AuditLogDetailResponse:
        audit_log = await self.audit_log_repository.get_by_id(id)
        if not audit_log:
            raise NotFoundException(
                "id",
                f"Audit Log with id {id} not found"
            )

        return AuditLogDetailResponse(
            id=audit_log.id,
            type=audit_log.type,
            table_name=audit_log.table_name,
            date_time=audit_log.date_time,
            old_values=audit_log.old_values,
            new_values=audit_log.new_values,
            affected_columns=audit_log.affected_columns,
            primary_key=audit_log.primary_key,
            user_id=audit_log.user_id,
            user_full_name=(audit_log.user.full_name if getattr(audit_log, "user", None) else None),
        )
