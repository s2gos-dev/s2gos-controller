#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import datetime
import tempfile
import time
from pathlib import Path
from typing import Optional

from s2gos.common.models import Link
from s2gos.server.services.local import LocalService, get_job_context

service = LocalService(
    title="S2GOS API Server (local dummy for testing)",
    description="Local test server implementing the OGC API - Processes 1.0 Standard",
)


@service.process(
    id="create_datacube",
    title="Generate a dummy datacube for testing",
    description=(
        "Creates an xarray dataset and writes it as Zarr into a temporary location. "
        "Requires installed dask, xarray, and zarr packages."
    ),
    inputs={
        "var_names": {
            "title": "Variable names",
            "description": "Comma-separated list of variable names.",
        },
        "bbox": {
            "title": "Bounding box",
            "description": "Bounding box in geographical coordinates.",
            "format": "bbox",
        },
        "resolution": {
            "title": "Spatial resolution",
            "description": "Spatial resolution in degree.",
            "minimum": 0.01,
            "maximum": 10,
        },
        "start_date": {
            "title": "Start date",
            "format": "date",
        },
        "end_date": {
            "title": "End date",
            "format": "date",
        },
        "periodicity": {
            "title": "Periodicity",
            "description": "Size of time steps in days.",
            "minimum": 1,
            "maximum": 10,
        },
        "output_path": {
            "title": "Output path",
            "description": "Local output path or URI.",
        },
    },
)
def create_datacube(
    var_names: str = "a, b, c",
    bbox: tuple[float, float, float, float] = (-180, -90, 180, 90),
    resolution: float = 0.5,
    start_date: str = "2025-01-01",
    end_date: str = "2025-02-01",
    periodicity: int = 1,
    output_path: Optional[str] = None,
) -> Link:
    # dependencies only required for this operation
    import dask.array as da
    import numpy as np
    import xarray as xr

    print(
        dict(
            var_names=var_names,
            bbox=bbox,
            resolution=resolution,
            start_date=start_date,
            end_date=end_date,
            periodicity=periodicity,
        )
    )

    var_names = [name.strip() for name in var_names.split(",")]
    start_date = datetime.date.fromisoformat(start_date)
    end_date = datetime.date.fromisoformat(end_date)

    x1, y1, x2, y2 = bbox
    x_size = round((x2 - x1) / resolution)
    y_size = round((y2 - y1) / resolution)
    time_size = round((end_date - start_date).days / periodicity)
    r05 = resolution / 2

    dataset = xr.Dataset()
    dataset.coords["lon"] = xr.DataArray(
        np.linspace(x1 + r05, x2 - r05, x_size), dims="lon"
    )
    dataset.coords["lat"] = xr.DataArray(
        np.linspace(y1 + r05, y2 - r05, y_size), dims="lat"
    )
    dataset.coords["time"] = xr.DataArray(
        np.array(
            [start_date + datetime.timedelta(days=days) for days in range(time_size)],
            dtype=np.datetime64,
        ),
        dims="time",
    )
    for var_name in var_names:
        dataset[var_name] = xr.DataArray(
            da.zeros(shape=(time_size, y_size, x_size)), dims=("time", "lat", "lon")
        )

    if not output_path:
        output_path = tempfile.mkdtemp(prefix="datacube-", suffix=".zarr")

    dataset.to_zarr(output_path)
    if "://" in output_path:
        href = output_path
    else:
        href = Path(output_path).resolve().as_uri()
    return Link(href=href, type="application/zarr")


@service.process(
    id="sleep_a_while",
    title="Sleep Processor",
    description=(
        "Sleeps for `duration` seconds. "
        "Fails on purpose if `fail` is `True`. "
        "Returns the effective amount of sleep in seconds."
    ),
)
def sleep_a_while(
    duration: float = 10.0,
    fail: bool = False,
) -> float:
    ctx = get_job_context()

    t0 = time.time()
    for i in range(101):
        ctx.report_progress(progress=i)
        if fail and i == 50:
            raise RuntimeError("Woke up too early")
        time.sleep(duration / 100)
    return time.time() - t0


@service.process(
    id="primes_between",
    title="Prime Processor",
    description=(
        "Returns the list of prime numbers between a `min_val` and `max_val`. "
    ),
)
def primes_between(min_val: int, max_val: int) -> list[int]:
    ctx = get_job_context()

    if max_val < 2 or max_val <= min_val:
        raise ValueError("max_val must be greater 1 and greater min_val")

    ctx.report_progress(message="Step 1: Generate sieve up to sqrt(max_val)")
    limit = int(max_val**0.5) + 1
    is_prime_small = [True] * (limit + 1)
    is_prime_small[0:2] = [False, False]
    for i in range(2, int(limit**0.5) + 1):
        if is_prime_small[i]:
            for j in range(i * i, limit + 1, i):
                is_prime_small[j] = False
    small_primes = [i for i, prime in enumerate(is_prime_small) if prime]

    ctx.report_progress(
        message="Step 2: Create the sieve for the range [min_val, max_val]"
    )
    sieve_range = max_val - min_val + 1
    is_prime = [True] * sieve_range

    for p in small_primes:
        # Find the first multiple of p in the range [min_val, max_val]
        start = max(p * p, ((min_val + p - 1) // p) * p)
        for j in range(start, max_val + 1, p):
            is_prime[j - min_val] = False

    for n in range(min_val, min(min_val + 2, max_val + 1)):
        if n < 2:
            is_prime[n - min_val] = False

    ctx.report_progress(message="Done")
    return [min_val + i for i, prime in enumerate(is_prime) if prime]
