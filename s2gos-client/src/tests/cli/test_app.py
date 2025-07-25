#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

import typer.testing
from tests.helpers import MockTransport

from s2gos_client import Client, ClientConfig, __version__
from s2gos_client.cli.app import app


def invoke_app(*args: str) -> typer.testing.Result:
    def get_mock_client(_config_path: str | None):
        return Client(config=ClientConfig(), _transport=MockTransport())

    runner = typer.testing.CliRunner()
    return runner.invoke(app, args, obj={"get_client": get_mock_client})


class AppTest(TestCase):
    def test_help(self):
        result = invoke_app("--help")
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertIn("tool for the S2GOS service.", result.output)

    def test_version(self):
        result = invoke_app("--version")
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertEqual(__version__ + "\n", result.output)

    def test_configure(self):
        result = invoke_app("configure")
        self.assertEqual(1, result.exit_code, msg=self.get_result_msg(result))

    def test_get_processes(self):
        result = invoke_app("list-processes")
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertEqual("links: []\nprocesses: []\n\n", result.output)

    def test_get_process(self):
        result = invoke_app("get-process", "sleep_a_while")
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertEqual("id: ''\nversion: ''\n\n", result.output)

    def test_validate_request(self):
        result = invoke_app(
            "validate-request", "sleep_a_while", "-i", "duration=120", "-i", "fail=true"
        )
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertEqual(
            "inputs:\n  duration: 120\n  fail: true\nprocess_id: sleep_a_while\n\n",
            result.output,
        )

    def test_execute_process(self):
        result = invoke_app(
            "execute-process", "sleep_a_while", "-i", "duration=120", "-i", "fail=true"
        )
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertEqual(
            "jobID: ''\nstatus: accepted\ntype: process\n\n", result.output
        )

    def test_list_jobs(self):
        result = invoke_app("list-jobs")
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertEqual("jobs: []\nlinks: []\n\n", result.output)

    def test_get_job(self):
        result = invoke_app("get-job", "job_4")
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertEqual(
            "jobID: ''\nstatus: accepted\ntype: process\n\n", result.output
        )

    def test_dismiss_job(self):
        result = invoke_app("dismiss-job", "job_4")
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertEqual(
            "jobID: ''\nstatus: accepted\ntype: process\n\n", result.output
        )

    def test_get_job_results(self):
        result = invoke_app("get-job-results", "job_4")
        self.assertEqual(0, result.exit_code, msg=self.get_result_msg(result))
        self.assertEqual("null\n...\n\n", result.output)

    @classmethod
    def get_result_msg(cls, result: typer.testing.Result):
        if result.exit_code != 0:
            return f"output was: [{result.output}]\nstderr was: [{result.stderr}]"
        else:
            return None


class AppWithRealClientTest(TestCase):
    def test_get_processes(self):
        """Test code in app so that the non-mocked Client is used."""
        runner = typer.testing.CliRunner()
        result = runner.invoke(app, ["list-processes"])
        # May succeed if dev server is running
        self.assertTrue(
            result.exit_code in (0, 1), msg=f"exit code was {result.exit_code}"
        )
        if result.exit_code != 0:
            print(result.output)
