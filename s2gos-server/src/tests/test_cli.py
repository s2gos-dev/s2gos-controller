#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from s2gos_server.cli import cli

runner = CliRunner()


class CliTest(TestCase):
    def test_help(self):
        result = runner.invoke(cli, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("Server for the ESA synthetic", result.output)

    @patch("uvicorn.run")
    def test_run(self, mock: MagicMock):
        result = runner.invoke(
            cli,
            [
                "run",
                "--",
                "s2gos_server.services.local.testing:service",
                "--processes",
                "--max-workers=4",
            ],
        )
        self.assertEqual(0, result.exit_code)
        mock.assert_called_with(
            "s2gos_server.main:app", host="127.0.0.1", port=8008, reload=False
        )

    @patch("uvicorn.run")
    def test_dev(self, mock: MagicMock):
        result = runner.invoke(
            cli,
            [
                "dev",
                "--",
                "s2gos_server.services.local.testing:service",
                "--no-processes",
                "--max-workers=4",
            ],
        )
        self.assertEqual(0, result.exit_code)
        mock.assert_called_with(
            "s2gos_server.main:app", host="127.0.0.1", port=8008, reload=True
        )
