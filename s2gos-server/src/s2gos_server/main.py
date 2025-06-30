#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from . import routes
from .app import app
from .provider import get_service

"""
This module imports both, the FastAPI `app` instance and the application's 
path functions from the `routes` module. 
It also sets the server's service instance and exports the application as 
the `app` module attribute.
"""

__all__ = ["app", "routes"]

print(f"Using service of type {type(get_service()).__class__}")
