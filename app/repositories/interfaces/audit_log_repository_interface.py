from abc import ABC, abstractmethod
from typing import Tuple, List
from datetime import datetime
from uuid import UUID

from app.models.audit_log import AuditLog


class IAuditLogRepository(ABC):
    @abstractmethod
    async def get_all_paginated(
        self,
        skip: int = 0,
        limit: int = 20,
        type: str | None = None,
        table_name: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        user_id: UUID | None = None,
    ) -> Tuple[List[AuditLog], int]:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> AuditLog | None:
        """Get audit log by id with user relationship loaded."""
        pass
