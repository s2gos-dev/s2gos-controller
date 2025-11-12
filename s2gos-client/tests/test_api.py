#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import s2gos_client.api


def test_api_ok():
    assert {"AsyncClient", "Client", "ClientConfig", "ClientError"}.issubset(
        dir(s2gos_client.api)
    )
