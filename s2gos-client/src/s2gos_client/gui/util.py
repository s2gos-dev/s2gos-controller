#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import datetime
from typing import Any


def json_serialize(value: Any):
    # check if there are more cases to be handled
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value


class JsonDict(dict):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name

    def _repr_json_(self):
        return self, {"root": f"{self._name}:"}
