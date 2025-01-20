"""
Service for DB reset endpoint
"""

from typing import Any

from sqlalchemy import MetaData, text
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings


class DBResetService:
    """Service for DB reset endpoint"""

    def __init__(self, db: Session, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()
        self.preserved_tables = {"users"}  # Tables to preserve during reset

    def reset_database(self) -> bool:
        """
        Reset the database while preserving user data.
        Only available in development/test environments.

        Returns:
            bool: True if reset was successful

        Raises:
            ValueError: If reset is attempted in production or if operation fails
            RuntimeError: If database operation fails
        """
        if self.settings.ENVIRONMENT not in ["development", "test"]:
            raise ValueError(
                "Database reset only allowed in development or test environment"
            )

        try:
            # Get metadata for all tables
            meta = MetaData()
            meta.reflect(bind=self.db.get_bind())

            # Get sorted tables to handle foreign key dependencies
            all_tables = list(reversed(meta.sorted_tables))

            # Filter out preserved tables
            tables_to_reset = [
                table for table in all_tables if table.name not in self.preserved_tables
            ]

            # Determine database type using engine name
            engine = self.db.get_bind()
            dialect_name = engine.dialect.name

            if dialect_name == "sqlite":
                self._reset_sqlite(tables_to_reset)
            elif dialect_name == "postgresql":
                self._reset_postgres(tables_to_reset)
            else:
                raise ValueError(f"Unsupported database type: {dialect_name}")

            self.db.commit()
            return True

        except Exception as e:  # pylint: disable=broad-exception-caught
            self._safe_rollback()
            raise RuntimeError(f"Failed to reset database: {str(e)}") from e

    def _safe_rollback(self) -> None:
        """Safely rollback the transaction and reset session state."""
        try:
            self.db.rollback()
        except Exception:  # pylint: disable=broad-exception-caught
            # If rollback fails, close and dispose the session
            self.db.close()

    def _reset_sqlite(self, tables: list[Any]) -> None:
        """Reset a SQLite database while preserving specified tables."""
        try:
            # Disable foreign key checks
            self.db.execute(text("PRAGMA foreign_keys = OFF"))

            # Delete from all non-preserved tables and reset sequences
            for table in tables:
                self.db.execute(text(f"DELETE FROM {table.name}"))
                try:
                    # Reset SQLite autoincrement counters for non-preserved tables
                    self.db.execute(
                        text(f"DELETE FROM sqlite_sequence WHERE name='{table.name}'")
                    )
                except Exception:  # pylint: disable=broad-exception-caught
                    # sqlite_sequence might not exist if no autoincrement fields
                    pass

        finally:
            # Re-enable foreign key checks
            try:
                self.db.execute(text("PRAGMA foreign_keys = ON"))
            except Exception:  # pylint: disable=broad-exception-caught
                self._safe_rollback()
                raise

    def _reset_postgres(self, tables: list[Any]) -> None:
        """Reset a PostgreSQL database while preserving specified tables."""
        try:
            # Start a new transaction
            self.db.execute(text("COMMIT"))  # Ensure we're in a clean state

            # Disable triggers
            self.db.execute(text("SET session_replication_role = replica"))

            # Build list of table names
            table_names = ", ".join(table.name for table in tables)
            if table_names:
                # Truncate all non-preserved tables in one statement
                self.db.execute(text(f"TRUNCATE TABLE {table_names} CASCADE"))

            # Reset sequences for non-preserved tables
            for table in tables:
                sequence_name = f"{table.name}_id_seq"
                try:
                    self.db.execute(
                        text(f"ALTER SEQUENCE {sequence_name} RESTART WITH 1")
                    )
                except Exception:  # pylint: disable=broad-exception-caught
                    # Sequence might not exist, which is fine
                    pass

            # Re-enable triggers
            self.db.execute(text("SET session_replication_role = DEFAULT"))

            # Commit the transaction
            self.db.commit()

        except Exception as e:  # pylint: disable=broad-exception-caught
            # If anything fails, try to clean up
            try:
                # Try to reset session_replication_role even if other commands failed
                self.db.execute(text("SET session_replication_role = DEFAULT"))
                self._safe_rollback()
            except Exception:  # pylint: disable=broad-exception-caught
                self._safe_rollback()
            raise RuntimeError(f"PostgreSQL reset failed: {str(e)}") from e
