"""Initial migration

Revision ID: 277af71fd561
Revises: 
Create Date: 2024-12-11 17:04:11.334843

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "277af71fd561"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Determine which type to use for UUID based on dialect
    is_postgresql = op.get_bind().dialect.name == "postgresql"
    uuid_type = postgresql.UUID(as_uuid=True) if is_postgresql else sa.String(32)

    # First create the users table
    op.create_table(
        "users",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("email", sa.LargeBinary(), nullable=False),  # For encrypted email
        sa.Column(
            "hashed_password", sa.String(), nullable=False
        ),  # Plain string for hashed password
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create a unique index on the encrypted email
    op.create_index(
        "ix_users_email_unique",
        "users",
        ["email"],
        unique=True,
    )

    # Then create the bank_accounts table
    op.create_table(
        "bank_accounts",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("user_id", uuid_type, nullable=False),
        sa.Column("account_type", sa.String(length=50), nullable=False),
        sa.Column("account_name", sa.LargeBinary(), nullable=True),  # Encrypted
        sa.Column("account_identifier", sa.LargeBinary(), nullable=True),  # Encrypted
        sa.Column("institution_name", sa.String(length=255), nullable=True),
        sa.Column("access_token", sa.LargeBinary(), nullable=True),  # Encrypted
        sa.Column("refresh_token", sa.LargeBinary(), nullable=True),  # Encrypted
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create index on user_id for better query performance
    op.create_index("ix_bank_accounts_user_id", "bank_accounts", ["user_id"])

    # Finally create the transactions table
    op.create_table(
        "transactions",
        sa.Column("id", uuid_type, nullable=False),
        sa.Column("user_id", uuid_type, nullable=False),
        sa.Column("bank_account_id", uuid_type, nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["bank_account_id"], ["bank_accounts.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for better query performance
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_index(
        "ix_transactions_bank_account_id", "transactions", ["bank_account_id"]
    )
    op.create_index("ix_transactions_created_at", "transactions", ["created_at"])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index("ix_transactions_created_at", table_name="transactions")
    op.drop_index("ix_transactions_bank_account_id", table_name="transactions")
    op.drop_index("ix_transactions_user_id", table_name="transactions")
    op.drop_index("ix_bank_accounts_user_id", table_name="bank_accounts")
    op.drop_index("ix_users_email_unique", table_name="users")

    # Drop tables in reverse order
    op.drop_table("transactions")
    op.drop_table("bank_accounts")
    op.drop_table("users")
