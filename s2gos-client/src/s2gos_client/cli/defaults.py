#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from enum import Enum
from typing import Final

# Important: this module shall have no s2gos dependencies


class OutputFormat(str, Enum):
    simple = "simple"
    json = "json"
    yaml = "yaml"


DEFAULT_OUTPUT_FORMAT = OutputFormat.yaml
DEFAULT_REQUEST_FILE: Final = "process-request.yaml"
