#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from typer.testing import CliRunner

from s2gos_client.cli.cli import cli

runner = CliRunner()


class CliTest(TestCase):
    def test_help(self):
        result = runner.invoke(cli, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("Client tool for the ESA synthetic", result.output)
