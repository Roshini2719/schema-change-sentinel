from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from enum import Enum
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class Roles(str, Enum):
    ADMIN = "ADMIN"
    DATA_ENGINEER = "DATA_ENGINEER"
    ANALYST = "ANALYST"
    PARTNER = "PARTNER"

class UserContext:
    def __init__(self, user_id: str, email: str, role: str, organisation_id: str, partner_id: Optional[str] = None):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.organisation_id = organisation_id
        self.partner_id = partner_id

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserContext:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        organisation_id: str = payload.get("organisation_id")
        partner_id: Optional[str] = payload.get("partner_id")
        if user_id is None or email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return UserContext(
        user_id=user_id,
        email=email,
        role=role,
        organisation_id=organisation_id,
        partner_id=partner_id,
    )

def require_roles(*roles: Roles):
    """Dependency factory that restricts access to specific roles."""
    async def _check(current_user: UserContext = Depends(get_current_user)) -> UserContext:
        if current_user.role not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action requires one of: {[r.value for r in roles]}"
            )
        return current_user
    return _check