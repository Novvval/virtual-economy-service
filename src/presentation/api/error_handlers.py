from fastapi import HTTPException, FastAPI
from pydantic import ValidationError as PydanticValidationError
from slowapi.errors import RateLimitExceeded
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.application.errors import ValidationError, NotFound, AccessError

def unhandled_exception(details: list = None):
    content = {"error": "Internal server error"}
    if details is not None:
        content["details"] = details
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content,
    )

async def rate_limit_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Rate limit exceeded"},
    )


async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Bad request", "details": [{"description": f"Validation error: {str(exc)}"}]},
    )


async def not_found_error_handler(request: Request, exc: NotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Not found", "details": [{"description": str(exc)}]},
    )


async def access_error_error_handler(request: Request, exc: AccessError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"error": "Access denied"},
    )


async def http_error_handler(request: Request, exc: HTTPException):
    content = {"error": "Uncaught error"}
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        content["error"] = "Unauthorized"
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        content["error"] = "Access denied"
    elif exc.status_code == status.HTTP_404_NOT_FOUND:
        content["error"] = "Not found"
    elif exc.status_code == status.HTTP_400_BAD_REQUEST:
        content["error"] = "Bad request"
        content["details"] = exc.detail
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )


async def pydantic_req_validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    content = {"error": "Bad request"}
    for exc in exc.errors():
        if exc["type"] == "missing":
            errors.append({"description": f'Missing required field "{exc["loc"][1]}"'})
        elif exc["type"] == "value_error":
            errors.append({"description": f'Invalid value for field "{exc["loc"][1]}"'})
        elif exc["type"] == "greater_than":
            errors.append({"description": f'"{exc["loc"][1]}" should be greater than {exc["ctx"]["gt"]}'})
        elif exc["type"] == "less_than":
            errors.append({"description": f'"{exc["loc"][1]}" should be less than {exc["ctx"]["lt"]}'})
    if errors:
        content["details"] = errors
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)


async def pydantic_validation_error_handler(request: Request, exc: PydanticValidationError):
    return unhandled_exception()


async def unhandled_exception_handler(request: Request, exc: Exception):
    return unhandled_exception()


def init_error_handlers(app: FastAPI):
    app.add_exception_handler(RateLimitExceeded, rate_limit_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(NotFound, not_found_error_handler)
    app.add_exception_handler(AccessError, access_error_error_handler)
    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, pydantic_req_validation_error_handler)
    app.add_exception_handler(PydanticValidationError, unhandled_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
