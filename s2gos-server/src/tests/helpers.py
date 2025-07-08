#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
import contextlib
import os

from pydantic import BaseModel


# noinspection PyAttributeOutsideInit,PyUnresolvedReferences,PyPep8Naming
class BaseModelMixin:
    def assertBaseModelEqual(self, a: BaseModel, b: BaseModel):
        self.maxDiff = None
        self.assertIsInstance(a, BaseModel)
        self.assertIsInstance(b, BaseModel)
        self.assertIs(b.__class__, a.__class__)
        a_dict = a.model_dump(
            mode="json", by_alias=True, exclude_none=True, exclude_defaults=True
        )
        b_dict = b.model_dump(
            mode="json", by_alias=True, exclude_none=True, exclude_defaults=True
        )
        self.assertDictEqual(a_dict, b_dict)


@contextlib.contextmanager
def set_env_var(name: str, value: str | None):
    old_value = os.environ.get(name)
    try:
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value
        yield
    finally:
        if old_value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = old_value
