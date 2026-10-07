from fastapi import APIRouter, Depends
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.db import get_db
from app.response import err, ok
from app.schemas import LoginRequest
from app.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    verify_password,
)

router = APIRouter(tags=["Auth"])


def _user_out(user: models.User, building_ids: list[int] | None = None) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "building_ids": building_ids or [1],
    }


@router.post("/auth/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        return err("Invalid credentials", code=401, status_code=401)
    data = {
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(user),
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": _user_out(user),
    }
    return ok(data)


@router.post("/auth/logout")
def logout(_: models.User = Depends(get_current_user)):
    return ok({"logged_out": True})


@router.post("/auth/refresh")
def refresh(body: dict, db: Session = Depends(get_db)):
    token = body.get("refresh_token")
    if not token:
        return err("refresh_token required", 400)
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "refresh":
            return err("Invalid token type", 401, 401)
        user = db.query(models.User).filter_by(username=payload.get("sub")).first()
    except JWTError:
        return err("Invalid token", 401, 401)
    if not user:
        return err("User not found", 401, 401)
    data = {
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(user),
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": _user_out(user),
    }
    return ok(data)


@router.get("/auth/me")
def me(user: models.User = Depends(get_current_user)):
    return ok(_user_out(user))
