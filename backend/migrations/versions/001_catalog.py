"""Persistent biological catalog, separate offers and HTTP cache."""
from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE TABLE pokemon (id integer PRIMARY KEY, data jsonb NOT NULL)")
    op.execute(
        "CREATE TABLE offers (pokemon_id integer PRIMARY KEY REFERENCES pokemon(id), price_cents integer NOT NULL CHECK(price_cents > 0), stock integer NOT NULL CHECK(stock >= 0))"
    )
    op.execute(
        "CREATE TABLE api_cache (url text PRIMARY KEY, data jsonb NOT NULL, fetched_at timestamptz NOT NULL DEFAULT now())"
    )
    op.execute("CREATE INDEX pokemon_species ON pokemon ((data->>'species_id'))")
    op.execute("CREATE INDEX pokemon_generation ON pokemon ((data->>'generation'))")


def downgrade():
    op.execute("DROP TABLE api_cache, offers, pokemon")
