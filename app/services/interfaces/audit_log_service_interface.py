from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID
from app.schema.response.audit_log import AuditLogListResponse, AuditLogDetailResponse
from app.schema.response.pagination import PagedData


class IAuditLogService(ABC):
    @abstractmethod
    async def search(
        self,
        page: int,
        page_size: int,
        type: str | None = None,
        table_name: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        user_id: UUID | None = None,
    ) -> PagedData[AuditLogListResponse]:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> AuditLogDetailResponse:
        pass
