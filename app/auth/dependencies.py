from datetime import datetime

from auth.jwt import verify_token
from core.exceptions import AppException
from db.session import get_pg_db
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError
from models import User
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_pg_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    oauth_token: str | None = Depends(oauth2_scheme),
) -> User:
    """Allow authentication via either HTTPBearer or OAuth2PasswordBearer"""

    if credentials and credentials.credentials:
        token = credentials.credentials
    elif oauth_token:
        token = oauth_token
    else:
        raise AppException(
            code="MISSING_CREDENTIALS",
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
        )

    try:
        payload = verify_token(token)
        user_id = int(payload.get("sub"))
        role = payload.get("role")

        result = await db.scalars(select(User).where(User.id == user_id))
        user: User | None = result.one_or_none()

        if not user:
            raise AppException(
                code="USER_NOT_FOUND",
                status_code=HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        if not user.is_active:
            raise AppException(
                code="USER_INACTIVE",
                status_code=HTTP_403_FORBIDDEN,
                detail="User inactive",
            )

        request.state.current_user = user
        request.state.current_role = role or user.role
        return user

    except ExpiredSignatureError as e:
        raise AppException(
            code="TOKEN_EXPIRED",
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        ) from e
    except JWTError as e:
        print(e)
        raise AppException(
            code="INVALID_TOKEN",
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e

