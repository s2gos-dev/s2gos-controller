#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import IsolatedAsyncioTestCase, TestCase

from s2gos_common.models import InputDescription, Link, ProcessDescription, ProcessList
from s2gos_server.services.local.testing import service as testing_service
from s2gos_server.services.local.testing import simulate_scene


class TestingFunctionsTest(TestCase):
    def test_simulate_scene(self):
        kwargs = {
            "var_names": "a, b",
            "bbox": [-10, 30, 5, 45],
            "resolution": 1,
            "start_date": "2025-01-01",
            "end_date": "2025-01-03",
            "periodicity": 1,
            "output_path": None,
        }
        link = simulate_scene(**kwargs)
        self.assertIsInstance(link, Link)
        self.assertIsInstance(link.href, str)
        self.assertTrue(link.href.startswith("memory://"))
        self.assertTrue(link.href.endswith(".zarr"))
        try:
            import xarray as xr

            ds = xr.open_dataset(link.href)
            self.assertIsInstance(ds, xr.Dataset)
            self.assertEqual({"time": 2, "lat": 15, "lon": 15}, ds.sizes)
            self.assertEqual({"time", "lat", "lon"}, set(ds.coords.keys()))
            self.assertEqual({"a", "b"}, set(ds.data_vars.keys()))
        except ImportError:
            pass


class TestingServiceTest(IsolatedAsyncioTestCase):
    async def test_get_processes(self):
        class MockRequest:
            # noinspection PyMethodMayBeStatic
            def url_for(self, name, **_params):
                return f"https://api.com/{name}"

        process_list = await testing_service.get_processes(request=MockRequest())
        self.assertIsInstance(process_list, ProcessList)
        self.assertEqual(3, len(process_list.processes))
        process_dict = {v.id: v for v in process_list.processes}
        self.assertEqual(3, len(process_dict))

        self.assertEqual(
            {"sleep_a_while", "primes_between", "simulate_scene"},
            set(process_dict.keys()),
        )

    async def test_get_process(self):
        process = await testing_service.get_process(process_id="simulate_scene")
        self.assertIsInstance(process, ProcessDescription)
        self.assertIsInstance(process.inputs, dict)

        bbox_input = process.inputs.get("bbox")
        self.assertIsInstance(bbox_input, InputDescription)
        self.assertEqual("Bounding box", bbox_input.title)
        self.assertEqual(
            "Bounding box in geographical coordinates.", bbox_input.description
        )
        self.assertEqual(
            {
                "type": "array",
                "default": [-180, -90, 180, 90],
                "format": "bbox",
                "items": {"type": "number"},
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
        self.assertEqual("Start date", start_date_input.title)
        self.assertEqual(None, start_date_input.description)
        self.assertEqual(
            {
                "type": "string",
                "format": "date",
                "default": "2025-01-01",
            },
            start_date_input.schema_.model_dump(
                mode="json",
                exclude_defaults=True,
                exclude_none=True,
            ),
        )
