#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

import click
import pytest
import typer

from s2gos_client import ClientException
from s2gos_client.api.client import Client
from s2gos_client.cli.cli import cli
from s2gos_client.cli.client import use_client
from s2gos_common.models import ApiError


class UseClientTest(TestCase):
    def test_success(self):
        with use_client(new_cli_context(), None) as client:
            self.assertIsInstance(client, Client)

    # noinspection PyMethodMayBeStatic
    def test_fail_with_client_error(self):
        with pytest.raises(
            click.ClickException,
            match=(
                "Not found\n"
                "Server-side error details:\n"
                "  title:  Not found\n"
                "  status: 404\n"
                "  type:   error\n"
                "  detail: Something was not found\n"
                "  traceback:\n"
            ),
        ):
            with use_client(new_cli_context(traceback=True), None):
                raise ClientException(
                    "Not found",
                    api_error=ApiError(
                        type="error",
                        title="Not found",
                        status=404,
                        detail="Something was not found",
                        traceback=["a", "b", "c"],
                    ),
                )

    # noinspection PyMethodMayBeStatic
    def test_fail_with_non_client_error(self):
        with pytest.raises(ValueError, match=r"path must be given"):
            with use_client(new_cli_context(), None):
                raise ValueError("path must be given")


def new_cli_context(traceback: bool = False):
    return typer.Context(
        cli,
        obj={
            "get_client": lambda config_path: Client(config_path=config_path),
            "traceback": traceback,
        },
        # the following have no special meaning for the tests,
        # but typer/click wants them to be given.
        allow_extra_args=False,
        allow_interspersed_args=False,
        ignore_unknown_options=False,
    )
