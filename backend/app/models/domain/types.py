from typing import Any, Optional, Union
from uuid import UUID

from sqlalchemy import String, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeEngine


class SQLiteUUID(TypeDecorator[UUID]):
    """Platform-independent UUID type.
    Uses PostgreSQL's UUID type, if available, otherwise uses String(32)
    """

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgUUID())
        else:
            return dialect.type_descriptor(String(32))

    def process_bind_param(
        self, value: Union[str, UUID, None], dialect: Dialect
    ) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            # Remove hyphens if they exist
            return value.replace("-", "")
        return value.hex if dialect.name != "postgresql" else str(value)

    def process_result_value(
        self, value: Optional[str], dialect: Dialect
    ) -> Optional[UUID]:
        if value is None:
            return None
        if len(str(value)) == 32:  # If no hyphens
            value = (
                f"{value[:8]}-{value[8:12]}-{value[12:16]}-{value[16:20]}-{value[20:]}"
            )
        try:
            return UUID(str(value))
        except (TypeError, ValueError):
            return None
