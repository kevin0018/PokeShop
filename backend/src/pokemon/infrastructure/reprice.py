"""Preview by default: python -m src.pokemon.infrastructure.reprice [--apply]."""
import argparse
import asyncio
import json
from sqlalchemy import text
from .postgres_repository import engine
from ..application.pricing import calculate_price

async def reprice(apply=False):
    async with engine.begin() as conn:
        # Serialize commercial changes while building and applying one consistent calculation.
        rows = (await conn.execute(text('SELECT p.id,p.data,o.price_cents,o.base_cents FROM pokemon p JOIN offers o ON o.pokemon_id=p.id ORDER BY p.id FOR UPDATE OF o'))).mappings().all()
        changes=[]
        for row in rows:
            offer=calculate_price(row['data'],row['base_cents'])
            changes.append(dict(id=row['id'],**offer))
            if row['id'] in (1,3,6,11) or offer['pricing_breakdown']['missing']:
                print(json.dumps({'id':row['id'],'before_cents':row['price_cents'],**offer}),flush=True)
        print(f'{"APPLY" if apply else "PREVIEW"}: {len(changes)} offers; stock unchanged',flush=True)
        if apply and changes:
            await conn.execute(text('UPDATE offers SET price_cents=:price_cents,base_cents=:base_cents,pricing_version=:pricing_version,pricing_breakdown=CAST(:pricing_breakdown AS jsonb) WHERE pokemon_id=:id'),[dict(c,pricing_breakdown=json.dumps(c['pricing_breakdown'])) for c in changes])
    await engine.dispose()

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    asyncio.run(reprice(parser.parse_args().apply))
