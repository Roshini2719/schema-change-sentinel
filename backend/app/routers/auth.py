from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models.models import get_db, User
from ..core.auth import verify_password, create_access_token
from ..core.config import settings
from ..schemas.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email, User.is_active == True).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "organisation_id": user.organisation_id,
        "partner_id": user.partner_id,
    }
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organisation_id": user.organisation_id,
            "partner_id": user.partner_id,
        },
    )

@router.get("/me")
async def me(token_data: dict = Depends(lambda: None)):
    """Echo current user context (handled client-side from JWT)."""
    return {"status": "authenticated"}
