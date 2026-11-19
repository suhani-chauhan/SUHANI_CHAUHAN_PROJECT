from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.client import get_anon_client

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    user_id: UUID
    token: str


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=401, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def get_auth_context(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> AuthContext:
    if creds is None:
        raise _unauthorized("Missing bearer token")
    try:
        response = get_anon_client().auth.get_user(creds.credentials)
        user = response.user if response else None
    except Exception:
        user = None
    if user is None:
        raise _unauthorized("Invalid or expired token")
    return AuthContext(user_id=UUID(user.id), token=creds.credentials)
