#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
import os
from collections.abc import Generator
from contextlib import contextmanager
from typing import Callable

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


@contextmanager
def set_env_cm(**new_env: str) -> Generator[dict[str, str]]:
    restore_env = set_env(**new_env)
    try:
        yield new_env
    finally:
        restore_env()


def set_env(**new_env: str) -> Callable[[], None]:
    old_env = {k: os.environ.get(k) for k in new_env.keys()}

    def restore_env():
        for ko, vo in old_env.items():
            if vo is not None:
                os.environ[ko] = vo
            elif ko in os.environ:
                del os.environ[ko]

    for kn, vn in new_env.items():
        if vn is not None:
            os.environ[kn] = vn
        elif kn in os.environ:
            del os.environ[kn]

    return restore_env
