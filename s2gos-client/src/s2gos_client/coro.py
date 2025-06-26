#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import asyncio
import threading

from collections.abc import Awaitable
from typing import TypeVar

T = TypeVar("T")


def await_sync(coro: Awaitable[T]) -> T:
    """
    Safely run an async coroutine from synchronous code.

    Works with Python 3.10+, with or without a running event loop and
    works for the following situations:

    - From a normal script or test (__main__)
    - From within a Jupyter notebook
    - In a sync function that's part of a web app or GUI with a running loop
    - In Python 3.10+ where asyncio.get_event_loop() behaves differently
    """
    try:
        # If there's no running loop, just use asyncio.run
        return asyncio.run(coro)
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" not in str(e):
            raise

        # Fall back: run in a new thread with its own loop
        result_container = {}

        def runner():
            loop = None
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result_container["result"] = loop.run_until_complete(coro)
            except Exception as inner_exc:
                result_container["exception"] = inner_exc
            finally:
                if loop is not None:
                    loop.close()

        thread = threading.Thread(target=runner)
        thread.start()
        thread.join()

        if "exception" in result_container:
            raise result_container["exception"]
        return result_container["result"]
