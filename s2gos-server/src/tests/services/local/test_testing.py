#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import sys
from pathlib import Path
from unittest import IsolatedAsyncioTestCase, TestCase

from s2gos_common.models import InputDescription, Link, ProcessDescription, ProcessList
from s2gos_server.services.local.testing import create_datacube
from s2gos_server.services.local.testing import service as testing_service


class TestingFunctionsTest(TestCase):
    def test_create_datacube(self):
        kwargs = {
            "var_names": "a, b, c",
            "bbox": [-12.614059, 32.044123, 4.612504, 45.65913],
            "resolution": 0.5,
            "start_date": "2025-01-01",
            "end_date": "2025-02-03",
            "periodicity": 1,
        }
        link = create_datacube(**kwargs)
        self.assertIsInstance(link, Link)
        self.assertIsInstance(link.href, str)
        self.assertTrue(link.href.startswith("memory://"))
        self.assertTrue(link.href.endswith(".zarr"))
        try:
            import xarray as xr

            ds = xr.open_dataset(link.href)
            self.assertIsInstance(ds, xr.Dataset)
        except ImportError:
            pass


class TestingServiceTest(IsolatedAsyncioTestCase):
    async def test_get_processes(self):
        process_list = await testing_service.get_processes()
        self.assertIsInstance(process_list, ProcessList)
        self.assertEqual(3, len(process_list.processes))
        process_dict = {v.id: v for v in process_list.processes}
        self.assertEqual(3, len(process_dict))

        self.assertEqual(
            {"create_datacube", "sleep_a_while", "primes_between"},
            set(process_dict.keys()),
        )

    async def test_get_process(self):
        process = await testing_service.get_process(process_id="create_datacube")
        self.assertIsInstance(process, ProcessDescription)
        self.assertIsInstance(process.inputs, dict)

        bbox_input = process.inputs.get("bbox")
        self.assertIsInstance(bbox_input, InputDescription)
        self.assertEqual(
            {
                "type": "array",
                "title": "Bounding box",
                "description": "Bounding box in geographical coordinates.",
                "default": [-180, -90, 180, 90],
                "format": "bbox",
                "items": [
                    {"type": "number"},
                    {"type": "number"},
                    {"type": "number"},
                    {"type": "number"},
                ],
                "minItems": 4,
                "maxItems": 4,
            },
            bbox_input.schema_.model_dump(
                mode="json",
                exclude_defaults=True,
                exclude_none=True,
            ),
        )

        start_date_input = process.inputs.get("start_date")
        self.assertIsInstance(start_date_input, InputDescription)
        self.assertEqual(
            {
                "type": "string",
                "title": "Start date",
                "format": "date",
                "default": "2025-01-01",
            },
            start_date_input.schema_.model_dump(
                mode="json",
                exclude_defaults=True,
                exclude_none=True,
            ),
        )
