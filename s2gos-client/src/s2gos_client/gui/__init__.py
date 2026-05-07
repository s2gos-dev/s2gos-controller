#  Copyright (c) 2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from cuiman.gui import Client

from s2gos_client.api import ClientConfig
from .pathref import PathRefEditorFactory


config = ClientConfig.default_config
config.get_field_factory_registry().register(PathRefEditorFactory())

__all__ = [
    "Client",
    "ClientConfig",
]
