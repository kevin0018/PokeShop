"""Same-origin JSON API. The browser submits intentions, never prices/results."""
import json
import os
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text

from src.pokemon.infrastructure.postgres_repository import engine
from . import service
from .content import GYMS, SHOP_IDS
from .security import COOKIE, SESSION_SECONDS, digest

router = APIRouter()


def get_engine():
    return engine


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=24, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=10, max_length=128)

    @field_validator("username")
    @classmethod
    def normalize(cls, value):
        return value.lower()


class Registration(Credentials):
    invitation: str = Field(min_length=20, max_length=128)


class Purchase(BaseModel):
    pokemon_id: int = Field(gt=0)


class Team(BaseModel):
    ids: list[int] = Field(max_length=6)


class Challenge(BaseModel):
    gym_id: int = Field(ge=1, le=6)


class Turn(BaseModel):
    revision: int = Field(ge=0)
    kind: Literal["move", "switch", "surrender"]
    move: str | None = Field(default=None, max_length=40)
    slot: int | None = Field(default=None, ge=0, le=5)


def check_origin(request):
    origin = request.headers.get("origin")
    allowed = json.loads(os.getenv("ALLOWED_ORIGINS", '["http://localhost:5173", "http://127.0.0.1:5173"]'))
    if origin and origin not in allowed:
        service.fail("invalidOrigin", 403)


def token_from(request):
    return request.cookies.get(COOKIE, "")


def mutation(request):
    check_origin(request)
    service.require_csrf(token_from(request), request.headers.get("x-csrf-token"))


def set_session(response, token):
    response.set_cookie(COOKIE, token, max_age=SESSION_SECONDS, httponly=True, secure=os.getenv("ENVIRONMENT") == "production", samesite="strict", path="/api/v1/adventure")
    response.headers["Cache-Control"] = "no-store"


@router.post("/register", status_code=201)
async def register(body: Registration, request: Request, response: Response, db=Depends(get_engine)):
    check_origin(request)
    await service.throttle(db, f"auth:{request.client.host}")
    await service.throttle(db, f"username:{body.username}")
    token = await service.register(db, body.username, body.password, body.invitation)
    set_session(response, token)
    return {"ok": True}


@router.post("/login")
async def login(body: Credentials, request: Request, response: Response, db=Depends(get_engine)):
    check_origin(request)
    await service.throttle(db, f"auth:{request.client.host}")
    await service.throttle(db, f"username:{body.username}")
    token = await service.login(db, body.username, body.password)
    set_session(response, token)
    return {"ok": True}


@router.get("/me")
async def me(request: Request, response: Response, db=Depends(get_engine)):
    response.headers["Cache-Control"] = "no-store"
    async with db.begin() as conn:
        trainer = await service.session(conn, token_from(request), lock=True)
        return await service.profile(conn, trainer, token_from(request))


@router.post("/logout")
async def logout(request: Request, response: Response, db=Depends(get_engine)):
    mutation(request)
    async with db.begin() as conn:
        await conn.execute(text("DELETE FROM trainer_sessions WHERE token_hash=:token"), {"token": digest(token_from(request))})
    response.delete_cookie(COOKIE, path="/api/v1/adventure", httponly=True, secure=os.getenv("ENVIRONMENT") == "production", samesite="strict")
    return {"ok": True}


@router.get("/shop")
async def shop(db=Depends(get_engine)):
    async with db.connect() as conn:
        return {"items": [service.shop_item(p) for p in await service.pokemon_data(conn, SHOP_IDS)]}


@router.get("/gyms")
async def gyms():
    return {"items": GYMS}


@router.post("/purchases")
async def buy(body: Purchase, request: Request, db=Depends(get_engine)):
    mutation(request)
    async with db.begin() as conn:
        trainer = await service.session(conn, token_from(request), lock=True)
        await service.buy(conn, trainer, body.pokemon_id)
    return {"ok": True}


@router.put("/team")
async def team(body: Team, request: Request, db=Depends(get_engine)):
    mutation(request)
    async with db.begin() as conn:
        trainer = await service.session(conn, token_from(request), lock=True)
        await service.save_team(conn, trainer, body.ids)
    return {"ok": True}


@router.post("/battles", status_code=201)
async def challenge(body: Challenge, request: Request, db=Depends(get_engine)):
    mutation(request)
    async with db.begin() as conn:
        trainer = await service.session(conn, token_from(request), lock=True)
        return await service.start_battle(conn, trainer, body.gym_id)


@router.get("/battles/{battle_id}")
async def battle(battle_id: uuid.UUID, request: Request, response: Response, db=Depends(get_engine)):
    response.headers["Cache-Control"] = "no-store"
    async with db.connect() as conn:
        trainer = await service.session(conn, token_from(request))
        return service.battle_response(await service.battle_row(conn, trainer["id"], battle_id))


@router.post("/battles/{battle_id}/turns")
async def turn(battle_id: uuid.UUID, body: Turn, request: Request, db=Depends(get_engine)):
    mutation(request)
    async with db.begin() as conn:
        trainer = await service.session(conn, token_from(request), lock=True)
        return await service.turn(conn, trainer, battle_id, body.revision, body.model_dump())
