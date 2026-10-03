"""Private trainer accounts and transactional adventure state."""
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE trainers (
            id uuid PRIMARY KEY, username text NOT NULL UNIQUE,
            password_hash text NOT NULL, credits integer NOT NULL DEFAULT 1000 CHECK(credits >= 0),
            team jsonb NOT NULL DEFAULT '[]', created_at timestamptz NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE TABLE invitations (
            code_hash text PRIMARY KEY, expires_at timestamptz NOT NULL,
            used_by uuid REFERENCES trainers(id), revoked boolean NOT NULL DEFAULT false
        )
    """)
    op.execute("""
        CREATE TABLE trainer_sessions (
            token_hash text PRIMARY KEY, trainer_id uuid NOT NULL REFERENCES trainers(id) ON DELETE CASCADE,
            expires_at timestamptz NOT NULL
        )
    """)
    op.execute("CREATE INDEX sessions_trainer ON trainer_sessions(trainer_id)")
    op.execute("""
        CREATE TABLE trainer_collection (
            trainer_id uuid REFERENCES trainers(id) ON DELETE CASCADE,
            pokemon_id integer REFERENCES pokemon(id), price integer NOT NULL CHECK(price > 0),
            purchased_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(trainer_id, pokemon_id)
        )
    """)
    op.execute("""
        CREATE TABLE gym_medals (
            trainer_id uuid REFERENCES trainers(id) ON DELETE CASCADE,
            gym_id integer NOT NULL CHECK(gym_id BETWEEN 1 AND 6),
            reward integer NOT NULL CHECK(reward > 0), earned_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY(trainer_id, gym_id)
        )
    """)
    op.execute("""
        CREATE TABLE trainer_battles (
            id uuid PRIMARY KEY, trainer_id uuid NOT NULL REFERENCES trainers(id) ON DELETE CASCADE,
            gym_id integer NOT NULL CHECK(gym_id BETWEEN 1 AND 6),
            status text NOT NULL CHECK(status IN ('active','won','lost','surrendered')),
            revision integer NOT NULL DEFAULT 0, state jsonb NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE UNIQUE INDEX one_active_battle ON trainer_battles(trainer_id) WHERE status='active'")
    op.execute("CREATE INDEX battles_trainer ON trainer_battles(trainer_id, created_at DESC)")
    op.execute("""
        CREATE TABLE auth_attempts (
            key text PRIMARY KEY, attempts integer NOT NULL,
            window_start timestamptz NOT NULL DEFAULT now()
        )
    """)


def downgrade():
    op.execute("DROP TABLE auth_attempts, trainer_battles, gym_medals, trainer_collection, trainer_sessions, invitations, trainers")
