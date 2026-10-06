from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..models.models import User, Organisation, Partner
from ..schemas.schemas import LoginRequest, TokenResponse, UserResponse
from ..core.auth import verify_password, create_access_token, get_current_user, UserContext

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "organisation_id": user.organisation_id
    }
    access_token = create_access_token(data=token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organisation_id": user.organisation_id,
            "partner_id": user.partner_id
        }
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserContext = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
