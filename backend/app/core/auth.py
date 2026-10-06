from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from enum import Enum
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class Roles(str, Enum):
    ADMIN = "ADMIN"
    DATA_ENGINEER = "DATA_ENGINEER"
    ANALYST = "ANALYST"
    PARTNER = "PARTNER"

class UserContext:
    def __init__(self, user_id: str, email: str, role: str, organisation_id: str):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.organisation_id = organisation_id

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

def get_password_hash(password: str) -> str:
    return hashlib.sha256((password + settings.SECRET_KEY).encode('utf-8')).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=480)
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
        if user_id is None or email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    return UserContext(user_id=user_id, email=email, role=role, organisation_id=organisation_id)

def role_required(allowed_roles: List[Roles]):
    def role_checker(current_user: UserContext = Depends(get_current_user)):
        if current_user.role not in [r.value for r in allowed_roles]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user
    return role_checker