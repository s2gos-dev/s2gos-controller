#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import asyncio
from unittest import TestCase

import pytest

from s2gos_client.coro import await_sync


async def my_async_function(fail: bool = False):
    await asyncio.sleep(0.1)
    if fail:
        raise ValueError("intentionally failed")
    return "done"


class CoroTest(TestCase):
    def test_await_sync_ok(self):
        result = await_sync(my_async_function())
        self.assertEqual(result, "done")

    # noinspection PyMethodMayBeStatic
    def test_await_sync_fail(self):
        with pytest.raises(ValueError, match="intentionally failed"):
            await_sync(my_async_function(fail=True))
