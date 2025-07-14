#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import pydantic

from .airflow_service import DEFAULT_AIRFLOW_BASE_URL, AirflowService

service = AirflowService(
    title="Airflow Dev Service",
    airflow_base_url=DEFAULT_AIRFLOW_BASE_URL,
    airflow_username="admin",
    airflow_user_package="s2gos_server.services.local.testing",
)


# noinspection PyUnusedLocal
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
    pass


# noinspection PyUnusedLocal
@service.process(
    id="primes_between",
    title="Prime Processor",
    description=(
        "Returns the list of prime numbers between a `min_val` and `max_val`. "
    ),
)
def primes_between(
    min_val: int = pydantic.Field(0, ge=0), max_val: int = pydantic.Field(100, le=100)
) -> list[int]:
    pass
