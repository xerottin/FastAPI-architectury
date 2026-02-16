from fastapi import HTTPException
from typing import Any, Dict, Optional
from starlette.status import HTTP_400_BAD_REQUEST


class AppException(HTTPException):
    def __init__(
        self,
        *,
        code: str,
        i18n_key: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        status_code: int = HTTP_400_BAD_REQUEST,
        detail: Optional[str] = None,
    ):
        i18n_key = i18n_key or f"errors.{code}"
        payload = {
            "code": code,
            "i18n_key": i18n_key,
            "params": params or {},
            "message": detail or i18n_key,
        }
        super().__init__(status_code=status_code, detail=payload)
