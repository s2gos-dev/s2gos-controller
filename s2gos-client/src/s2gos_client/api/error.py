#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Optional


class ClientError(Exception):
    """Raised if a web API call failed with a status code that is not 2xx."""

    def __init__(
        self,
        message: str,
        status_code: int,
        title: Optional[str] = None,
        detail: Optional[str] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.title = title
        self.detail = detail
