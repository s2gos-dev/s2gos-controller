#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
import os
import unittest
from pathlib import Path
from unittest.mock import patch

import click
import pytest

from s2gos_client import ClientConfig
from s2gos_client.api.defaults import DEFAULT_CONFIG_PATH
from s2gos_client.cli.config import configure_client, read_config
from s2gos_common.testing import set_env

CONFIG_PATH = "test.cfg"

DEFAULT_CONFIG_BACKUP_PATH = DEFAULT_CONFIG_PATH.parent / (
    str(DEFAULT_CONFIG_PATH.name) + ".backup"
)


class ReadConfigTest(unittest.TestCase):
    def setUp(self):
        self.restore_env = set_env(
            **{k: None for k, v in os.environ.items() if k.startswith("S2GOS_")}
        )
        if DEFAULT_CONFIG_BACKUP_PATH.exists():
            os.remove(DEFAULT_CONFIG_BACKUP_PATH)
        if DEFAULT_CONFIG_PATH.exists():
            DEFAULT_CONFIG_PATH.rename(DEFAULT_CONFIG_BACKUP_PATH)

    def tearDown(self):
        self.restore_env()
        if DEFAULT_CONFIG_BACKUP_PATH.exists():
            if DEFAULT_CONFIG_PATH.exists():
                os.remove(DEFAULT_CONFIG_BACKUP_PATH)
            else:
                DEFAULT_CONFIG_BACKUP_PATH.rename(DEFAULT_CONFIG_PATH)

    def test_read_config_custom(self):
        with pytest.raises(
            click.ClickException,
            match="Configuration file fantasia.cfg not found or empty.",
        ):
            read_config("fantasia.cfg")

    def test_read_config_no_default(self):
        with pytest.raises(
            click.ClickException,
            match="The client tool is not yet configured, please use the",
        ):
            read_config(None)

    def test_read_config_default(self):
        with DEFAULT_CONFIG_PATH.open("wt") as stream:
            stream.write("server_url: https://test.api.com")

        config = read_config(None)
        self.assertEqual(ClientConfig(server_url="https://test.api.com"), config)


class ConfigTest(unittest.TestCase):
    def tearDown(self):
        os.remove(CONFIG_PATH)

    @patch("typer.prompt")
    def test_configure_client(self, mock_prompt):
        # Simulate sequential responses to typer.prompt
        mock_prompt.side_effect = ["test-user", "s3cr3t", "http://localhorst:9090"]
        self.assertEqual(
            Path(CONFIG_PATH),
            configure_client(
                user_name=None,
                access_token=None,
                server_url=None,
                config_path=CONFIG_PATH,
            ),
        )
        self.assertTrue(os.path.exists(CONFIG_PATH))
