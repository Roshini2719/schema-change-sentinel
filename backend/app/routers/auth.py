from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from ..models.models import get_db, User
from ..core.auth import verify_password, create_access_token
from ..core.config import settings
from ..schemas.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    email = None
    password = None
    
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            email = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            pass
    else:
        try:
            form = await request.form()
            email = form.get("username") or form.get("email")
            password = form.get("password")
        except Exception:
            pass

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        try:
            from app.models.user import User as OldUser
            user = db.query(OldUser).filter(OldUser.email == email).first()
        except Exception:
            pass

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    pwd_hash = getattr(user, "hashed_password", None) or getattr(user, "password_hash", None)
    if not pwd_hash or not verify_password(password, pwd_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    role_val = user.role.value if hasattr(user.role, "value") else str(user.role)
    org_id = str(getattr(user, "organisation_id", None) or getattr(user, "organization_id", None) or "")
    partner_id = str(getattr(user, "partner_id", None) or "")
    full_name = getattr(user, "full_name", None) or getattr(user, "name", None) or email.split("@")[0]

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": role_val,
        "organisation_id": org_id,
        "organization_id": org_id,
        "partner_id": partner_id,
    }
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": full_name,
            "role": role_val,
            "organisation_id": org_id,
            "partner_id": partner_id,
        },
    )

@router.get("/me")
async def me(token_data: dict = Depends(lambda: None)):
    """Echo current user context (handled client-side from JWT)."""
    return {"status": "authenticated"}
