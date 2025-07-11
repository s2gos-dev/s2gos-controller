#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from s2gos_server.services.local.flatten_props import (
    flatten_1st_level_schema_properties,
    normalize_name_set,
    unflatten_1st_level_dict_properties,
)


class FlattenPropsTest(TestCase):
    def test_unflatten_1st_level_dict_properties(self):
        mapping = {
            "job_title": "My first Job",
            "scene_params.threshold": 0.6,
            "scene_params.bbox": [-10, 10, 20, 20],
            "output_spec.output_path": "/data/test.zarr",
        }
        self.assertIs(
            mapping,
            unflatten_1st_level_dict_properties(mapping, property_names=""),
        )

        mapping = {
            "job_title": "My first Job",
            "scene_params.threshold": 0.6,
            "scene_params.bbox": [-10, 10, 20, 20],
            "output_spec.output_path": "/data/test.zarr",
        }
        self.assertEqual(
            {
                "job_title": "My first Job",
                "scene_params": {"threshold": 0.6, "bbox": [-10, 10, 20, 20]},
                "output_spec": {"output_path": "/data/test.zarr"},
            },
            unflatten_1st_level_dict_properties(
                mapping,
                property_names=("scene_params", "output_spec"),
            ),
        )

    def test_flatten_1st_level_schema_properties(self):
        schema = {"type": "object", "properties": {"job_title": {"type": "string"}}}
        self.assertIs(
            schema,
            flatten_1st_level_schema_properties(schema, property_names=[]),
        )

        schema = {
            "type": "object",
            "properties": {
                "job_title": {"type": "string"},
                "scene_params": {
                    "type": "object",
                    "properties": {
                        "threshold": {"type": "number"},
                        "bbox": {"type": "array", "minItems": 4, "maxItems": 4},
                    },
                    "required": ["bbox"],
                },
                "output_spec": {
                    "type": "object",
                    "properties": {
                        "output_path": {"type": "string"},
                    },
                    "required": ["output_path"],
                },
            },
            "required": ["job_title", "scene_params"],
        }
        self.assertEqual(
            {
                "type": "object",
                "properties": {
                    "job_title": {"type": "string"},
                    "scene_params.threshold": {"type": "number"},
                    "scene_params.bbox": {
                        "type": "array",
                        "minItems": 4,
                        "maxItems": 4,
                    },
                    "output_spec.output_path": {"type": "string"},
                },
                "required": [
                    "job_title",
                    "output_spec.output_path",
                    "scene_params.bbox",
                ],
            },
            flatten_1st_level_schema_properties(
                schema=schema,
                property_names=["scene_params", "output_spec"],
            ),
        )

    def test_normalize_name_set(self):
        self.assertEqual(set(), normalize_name_set(""))
        self.assertEqual(set(), normalize_name_set(()))
        self.assertEqual({"x"}, normalize_name_set("x"))
        self.assertEqual({"x", "y", "z"}, normalize_name_set({"x", "y", "z"}))
        self.assertEqual({"x", "y", "z"}, normalize_name_set(["x", "y", "z"]))
        self.assertEqual({"x", "y"}, normalize_name_set(("x", "y", "")))
