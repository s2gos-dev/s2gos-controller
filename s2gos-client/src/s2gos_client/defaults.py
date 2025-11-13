#  Copyright (c) 2025 by ESA Sen4CAP team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import os
from typing import Final


# TODO: adjust defaults
DEFAULT_SERVER_URL: Final = (
    os.environ.get("S2GOS_SERVER_URL") or "http://localhost:8008"
)
DEFAULT_USER_NAME: Final = os.environ.get("S2GOS_USERNAME") or "testuser"
DEFAULT_ACCESS_TOKEN: Final = os.environ.get("S2GOS_PASSWORD") or "1234"
