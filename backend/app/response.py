from datetime import datetime
from typing import Any

from fastapi.responses import JSONResponse


def ok(data: Any = None, message: str = "success", code: int = 200, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


def err(message: str, code: int = 400, status_code: int = 400) -> JSONResponse:
    return ok(data=None, message=message, code=code, status_code=status_code)
