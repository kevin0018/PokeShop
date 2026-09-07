"""Versioned commercial pricing and regional query index."""
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TABLE offers ADD COLUMN base_cents integer NOT NULL DEFAULT 3000 CHECK(base_cents > 0), ADD COLUMN pricing_version text NOT NULL DEFAULT 'legacy', ADD COLUMN pricing_breakdown jsonb NOT NULL DEFAULT '{}'::jsonb"
    )
    op.execute("CREATE INDEX pokemon_region ON pokemon ((data->>'region'))")


def downgrade():
    op.execute("DROP INDEX pokemon_region")
    op.execute(
        "ALTER TABLE offers DROP COLUMN base_cents, DROP COLUMN pricing_version, DROP COLUMN pricing_breakdown"
    )
