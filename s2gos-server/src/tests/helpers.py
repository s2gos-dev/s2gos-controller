#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

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
