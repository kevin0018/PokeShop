"""Owner-only CLI; no public invitation issuance endpoint."""
import argparse
import asyncio
import secrets

from sqlalchemy import text

from src.pokemon.infrastructure.postgres_repository import engine

from .security import digest


async def run(args):
    try:
        async with engine.begin() as conn:
            if args.revoke:
                await conn.execute(
                    text("UPDATE invitations SET revoked=true WHERE code_hash=:code"),
                    {"code": digest(args.revoke)},
                )
                print("Invitation revoked.")
            else:
                code = secrets.token_urlsafe(24)
                await conn.execute(
                    text(
                        "INSERT INTO invitations(code_hash,expires_at) VALUES (:code,now() + :hours * interval '1 hour')"
                    ),
                    {"code": digest(code), "hours": args.hours},
                )
                print(code)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a single-use trainer invitation."
    )
    parser.add_argument("--hours", type=int, default=72)
    parser.add_argument("--revoke", help="Revoke an unused invitation code.")
    args = parser.parse_args()
    if not 1 <= args.hours <= 720:
        parser.error("--hours must be between 1 and 720")
    asyncio.run(run(args))
