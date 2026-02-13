from __future__ import annotations

from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import Any, List, Dict


class AuditLogBaseResponse(BaseModel):
    id: str
    table_name: str | None
    date_time: datetime
    type: str
    user_id: uuid.UUID | None
    user_full_name: str | None

class AuditLogListResponse(AuditLogBaseResponse):
    pass


class AuditLogDetailResponse(AuditLogBaseResponse):
    old_values: Dict[str, Any] | None = None
    new_values: Dict[str, Any] | None = None
    affected_columns: List[str] | None = None
    primary_key: Dict[str, Any] | None = None