#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
import os
import unittest
from unittest.mock import patch

from s2gos_client.cli.config import configure_client

CONFIG_PATH = "test.cfg"


class ConfigTest(unittest.TestCase):
    def tearDown(self):
        os.remove(CONFIG_PATH)

    @patch("typer.prompt")
    def test_configure_client(self, mock_prompt):
        # Simulate sequential responses to typer.prompt
        mock_prompt.side_effect = ["test-user", "s3cr3t", "http://localhorst:9090"]
        configure_client(
            user_name=None, access_token=None, server_url=None, config_path="test.cfg"
        )
        self.assertTrue(os.path.exists(CONFIG_PATH))
