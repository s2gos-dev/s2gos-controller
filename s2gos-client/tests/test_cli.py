#  Copyright (c) 2025-2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest.mock import patch

from typer.testing import CliRunner

import s2gos_client.cli
from s2gos_client.api import S2GOSConfig


def test_cli_ok():
    assert {"cli"}.issubset(dir(s2gos_client.cli))


def test_cli_login_uses_s2gos_config():
    with patch("cuiman.cli.config.login_client_with_prompt") as login:
        result = CliRunner().invoke(s2gos_client.cli.cli, ["login", "--no-input"])

    assert result.exit_code == 0, result.output
    login.assert_called_once_with(
        None,
        config_type=S2GOSConfig,
        no_browser=False,
        force=False,
        interactive=False,
    )
