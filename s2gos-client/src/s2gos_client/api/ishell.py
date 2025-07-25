#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import importlib.util

has_ishell = importlib.util.find_spec("IPython.core.interactiveshell")

__all__ = ["has_ishell"]


def _register_client_exception_handler():
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.display import JSON, display

    from .exceptions import ClientException

    # noinspection PyUnusedLocal
    def client_exception_handler(
        self: InteractiveShell, exc_type, exc_value, tb, tb_offset=None
    ):
        if isinstance(exc_value, ClientException):
            display(
                JSON(
                    exc_value.api_error.model_dump(mode="json", exclude_none=True),
                    root="Client error",
                    expanded=True,
                )
            )
            return None, None, None  # prevents default traceback

        return None

    # Register handler for MyCustomError
    InteractiveShell.instance().set_custom_exc(
        (ClientException,), client_exception_handler
    )


if has_ishell:
    _register_client_exception_handler()
