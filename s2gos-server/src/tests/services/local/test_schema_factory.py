#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
from typing import Any, Dict, List, Optional, Tuple
from unittest import TestCase

import pytest

from s2gos.common.models import Link, Schema
from s2gos.server.services.local.schema_factory import SchemaFactory
from tests.helpers import BaseModelMixin


class SchemaFactoryTest(BaseModelMixin, TestCase):
    def assertSchemaOk(
        self, expected_schema_dict, annotation, default=..., is_return=False
    ):
        self.maxDiff = None
        factory = SchemaFactory(
            "f", "x", annotation, default=default, is_return=is_return
        )
        schema_dict = factory.get_schema_dict()
        self.assertDictEqual(expected_schema_dict, schema_dict)

        expected_schema = Schema.model_validate(expected_schema_dict)
        schema = factory.get_schema()
        self.assertBaseModelEqual(expected_schema, schema)

    def test_with_default(self):
        self.assertSchemaOk({"type": "number", "default": 42.0}, float, default=42.0)

    def test_any(self):
        self.assertSchemaOk({}, Any)

    def test_float(self):
        self.assertSchemaOk({"type": "number"}, float)

    def test_tuple(self):
        self.assertSchemaOk({"type": "array"}, tuple)
        self.assertSchemaOk({"type": "array"}, Tuple)

    def test_tuple_with_args(self):
        expected_schema_dict = {
            "type": "array",
            "items": [{"type": "string"}, {"type": "integer"}],
            "minItems": 2,
            "maxItems": 2,
        }
        self.assertSchemaOk(expected_schema_dict, tuple[str, int])
        self.assertSchemaOk(expected_schema_dict, Tuple[str, int])

    def test_list(self):
        self.assertSchemaOk({"type": "array"}, list)
        self.assertSchemaOk({"type": "array"}, List)

    def test_list_with_args(self):
        expected_schema_dict = {
            "type": "array",
            "items": {"type": "string"},
        }
        self.assertSchemaOk(expected_schema_dict, list[str])
        self.assertSchemaOk(expected_schema_dict, List[str])

    def test_dict(self):
        self.assertSchemaOk({"type": "object"}, dict)
        self.assertSchemaOk({"type": "object"}, Dict)

    def test_dict_with_args(self):
        expected_schema_dict = {
            "type": "object",
            "additionalProperties": {"type": "integer"},
        }
        self.assertSchemaOk(expected_schema_dict, dict[str, int])
        self.assertSchemaOk(expected_schema_dict, Dict[str, int])

    def test_union(self):
        self.assertSchemaOk(
            {
                "oneOf": [{"type": "number"}, {"type": "string"}],
            },
            float | str,
        )

    def test_union_with_none(self):
        self.assertSchemaOk(
            {
                "type": "number",
                "nullable": True,
            },
            float | None,
        )
        self.assertSchemaOk(
            {
                "oneOf": [{"type": "number"}, {"type": "string"}],
                "nullable": True,
            },
            float | None | str,
        )

    def test_optional(self):
        self.assertSchemaOk({"type": "string", "nullable": True}, Optional[str])

    def test_base_model(self):
        self.assertSchemaOk(
            {
                "type": "object",
                "title": "Link",
                "required": ["href"],
                "properties": {
                    "href": {
                        "type": "string",
                        "title": "Href",
                    },
                    "hreflang": {
                        "type": "string",
                        "title": "Hreflang",
                        "default": None,
                        "examples": ["en"],
                        "nullable": True,
                    },
                    "rel": {
                        "type": "string",
                        "title": "Rel",
                        "default": None,
                        "examples": ["service"],
                        "nullable": True,
                    },
                    "title": {
                        "type": "string",
                        "title": "Title",
                        "default": None,
                        "nullable": True,
                    },
                    "type": {
                        "type": "string",
                        "title": "Type",
                        "default": None,
                        "examples": ["application/json"],
                        "nullable": True,
                    },
                },
            },
            Link,
            is_return=True,
        )

    def test_param_fail(self):
        with pytest.raises(
            ValueError,
            match="Unhandled annotation '<class 'object'>' for parameter 'x' of 'f'",
        ):
            self.assertSchemaOk({}, object)

    def test_return_fail(self):
        with pytest.raises(
            ValueError,
            match="Unhandled annotation '<class 'object'>' for return value 'x' of 'f'",
        ):
            self.assertSchemaOk({}, object, is_return=True)
