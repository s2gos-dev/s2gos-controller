#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from s2gos_common.models import ApiError


class ClientError(Exception):
    """Raised if a web API call failed with a status code that is not 2xx."""

    def __init__(self, message: str, status_code: int, api_error: ApiError):
        super().__init__(message)
        self.status_code = status_code
        self.api_error = api_error
