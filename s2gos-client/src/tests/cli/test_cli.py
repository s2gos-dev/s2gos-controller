#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from typer.testing import Result
from typer.testing import CliRunner

from s2gos_client import __version__, Client, ClientConfig
from s2gos_client.cli.cli import cli
from tests.helpers import MockTransport

runner = CliRunner()


def get_mock_client():
    return Client(config=ClientConfig(), _transport=MockTransport())


class CliTest(TestCase):
    def test_help(self):
        result = runner.invoke(
            cli,
            ["--help"],
        )
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertIn("Client tool for the S2GOS service.", result.output)

    def test_version(self):
        result = runner.invoke(
            cli,
            ["version"],
        )
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertEqual(__version__ + "\n", result.output)

    def test_get_processes(self):
        result = runner.invoke(
            cli, ["list-processes"], obj={"get_client": get_mock_client}
        )
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertEqual("No processes available.\n", result.output)

    def test_get_process(self):
        result = runner.invoke(
            cli, ["get-process", "sleep_a_while"], obj={"get_client": get_mock_client}
        )
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertIn(":\n", result.output)

    @classmethod
    def get_result_msg(cls, result: Result):
        if result.exit_code != 0:
            return f"output was: [{result.output}]\nstderr was: [{result.stderr}]"
        else:
            return None
