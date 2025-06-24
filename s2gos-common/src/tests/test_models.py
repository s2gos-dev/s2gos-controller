#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import inspect
from enum import Enum
from unittest import TestCase

from pydantic import BaseModel

import s2gos.common.models as s2g_models

REQUIRED_ENUMS = {
    "Crs",
    "JobControlOptions",
    "StatusCode",
}

REQUIRED_MODELS = {
    "ApiError",
    "Capabilities",
    "ConformanceDeclaration",
    "Format",
    "InputDescription",
    "JobInfo",
    "JobList",
    "Link",
    "Metadata",
    "Output",
    "OutputDescription",
    "ProcessDescription",
    "ProcessList",
    "ProcessRequest",
    "ProcessSummary",
    "Reference",
    "Schema",
}


class ModelsTest(TestCase):
    def test_enums(self):
        all_enums = set(
            name
            for name, obj in inspect.getmembers(s2g_models, inspect.isclass)
            if issubclass(obj, Enum)
        )
        self.assertSetEqual(set(), REQUIRED_ENUMS - all_enums)

    def test_models(self):
        all_models = set(
            name
            for name, obj in inspect.getmembers(s2g_models, inspect.isclass)
            if issubclass(obj, BaseModel)
        )

        self.assertSetEqual(set(), REQUIRED_MODELS - all_models)

    def test_models_have_repr_json(self):
        for name, obj in inspect.getmembers(s2g_models, inspect.isclass):
            if name in REQUIRED_MODELS and issubclass(obj, BaseModel):
                self.assertTrue(hasattr(obj, "_repr_json_"), msg=f"model {name}")

        obj = s2g_models.Bbox(bbox=[10, 20, 30, 40])
        json_repr = obj._repr_json_()
        self.assertEqual(
            (
                {"bbox": [10.0, 20.0, 30.0, 40.0]},
                {"root": "Bbox object:"},
            ),
            json_repr,
        )
