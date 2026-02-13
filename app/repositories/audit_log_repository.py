from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Tuple, List
from datetime import datetime
from uuid import UUID

from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.audit_log_repository_interface import IAuditLogRepository
from app.models.audit_log import AuditLog


class AuditLogRepository(IAuditLogRepository):
    def __init__(self, db_factory):
        self.db_factory = db_factory

    async def get_all_paginated(self, skip: int = 0, limit: int = 20, type: str | None = None, table_name: str | None = None, start_date: datetime | None = None, end_date: datetime | None = None, user_id: UUID | None = None) -> Tuple[List[AuditLog], int]:
        base_query = select(AuditLog)
        if type is not None:
            t = type.strip().lower()
            base_query = base_query.where(func.lower(AuditLog.type) == t)
        if table_name is not None:
            tn = table_name.strip().lower()
            base_query = base_query.where(func.lower(AuditLog.table_name) == tn)
        if start_date is not None:
            base_query = base_query.where(AuditLog.date_time >= start_date)
        if end_date is not None:
            base_query = base_query.where(AuditLog.date_time <= end_date)
        if user_id is not None:
            base_query = base_query.where(AuditLog.user_id == user_id)

        count_query = select(func.count()).select_from(base_query.subquery())
        async with self.db_factory() as session:
            total_result = await session.execute(count_query)
            total = total_result.scalar()

            result = await session.execute(
                base_query.options(selectinload(AuditLog.user)).order_by(AuditLog.date_time.desc()).offset(skip).limit(limit)
            )
            items = list(result.scalars().all())

            return items, total

    async def get_by_id(self, id: UUID) -> AuditLog | None:
        """Get audit log by id and eagerly load the `user` relationship."""
        async with self.db_factory() as session:
            result = await session.execute(
                select(AuditLog).options(selectinload(AuditLog.user)).where(AuditLog.id == str(id))
            )
            return result.scalars().first()
