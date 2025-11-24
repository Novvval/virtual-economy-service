from typing import Annotated

from dependency_injector.wiring import Provide
from fastapi import Depends, status, Header, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.infrastructure.config import Settings
from src.infrastructure.container import Container
from src.infrastructure.utils.helpers import generate_hash
from src.interfaces.context import WriteContext, ReadContext

security = HTTPBearer(scheme_name="Bearer Token", description="JWT token for user authentication")
settings = Settings()


def get_authenticated_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int | JSONResponse:
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])

        return payload["id"]
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )


async def get_idempotency_deps(
    request: Request,
    idempotency_key: str = Header(
        alias="Idempotency-Key", description="Unique idempotency key. Use the same key for retries"
    ),
    user_id: int = Depends(get_authenticated_user_id),
) -> dict:
    if idempotency_key:
        try:
            body = await request.json()
        except Exception:
            body = {}
        key = f"{user_id}:{idempotency_key}:{str(body)}"
        return {
            "user_id": user_id,
            "idempotency_hash": generate_hash(key),
        }
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail={"details": [{"description": "Missing idempotency key"}]}
    )


def get_user_id_for_rate_limit(request: Request) -> str:
    auth_header = request.headers.get("authorization", False)
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        return f"token:{generate_hash(token)}"
    return get_remote_address(request)


AuthenticatedUserDep = Annotated[int, Depends(get_authenticated_user_id)]
IdempotentRequestDep = Annotated[dict, Depends(get_idempotency_deps)]
WriteContextDep = Annotated[WriteContext, Depends(Provide[Container.write_context])]
ReadContextDep = Annotated[ReadContext, Depends(Provide[Container.read_context])]
limiter = Limiter(key_func=get_user_id_for_rate_limit)
