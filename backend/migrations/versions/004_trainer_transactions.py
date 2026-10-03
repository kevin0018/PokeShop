"""Idempotent trainer checkout and sales receipts."""
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE trainer_transactions (
            trainer_id uuid NOT NULL REFERENCES trainers(id) ON DELETE CASCADE,
            request_id uuid NOT NULL,
            kind text NOT NULL CHECK (kind IN ('checkout','sale')),
            pokemon_ids jsonb NOT NULL,
            result jsonb NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (trainer_id, request_id)
        )
    """
    )


def downgrade():
    op.execute("DROP TABLE trainer_transactions")
