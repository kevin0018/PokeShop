import asyncio

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from src.database import database_url


def migrate(connection):
    context.configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()


async def run():
    engine = create_async_engine(database_url())
    async with engine.connect() as connection:
        await connection.run_sync(migrate)
    await engine.dispose()


asyncio.run(run())
