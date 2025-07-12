#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
import traceback
from typing import Optional

from fastapi import HTTPException

from s2gos_common.models import ApiError


class JSONContentException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        exception: Optional[Exception] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.content = ApiError(
            type="error",
            status=status_code,
            detail=detail,
            traceback=(
                traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                )
                if exception is not None
                else None
            ),
        )
