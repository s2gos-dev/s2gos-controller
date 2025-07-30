#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import os
import unittest
from io import StringIO
from unittest.mock import patch

import click
import pytest

from s2gos_common.cli.request import ProcessingRequest, parse_processing_request
from s2gos_common.models import Subscriber

REQUEST_PATH = "test-request.yaml"


class RequestTest(unittest.TestCase):
    def tearDown(self):
        if os.path.exists(REQUEST_PATH):
            os.remove(REQUEST_PATH)

    def test_read_processing_request_from_yaml_stdin(self):
        stream = StringIO("process_id: test_func\ninputs:\n  x: 7\n  y: 9")
        with patch("sys.stdin", new=stream):
            request = parse_processing_request(request_file="-")
            self.assertEqual(
                ProcessingRequest(process_id="test_func", inputs={"x": 7, "y": 9}),
                request,
            )

    def test_read_processing_request_from_json_stdin(self):
        stream = StringIO(
            "{\n"
            '  "process_id": "test_func_2",\n'
            '  "inputs": {\n'
            '    "x": 0,\n'
            '    "y": -4'
            "  }\n"
            "}"
        )
        with patch("sys.stdin", new=stream):
            request = parse_processing_request(request_file="-")
            self.assertEqual(
                ProcessingRequest(process_id="test_func_2", inputs={"x": 0, "y": -4}),
                request,
            )

    def test_read_processing_request_from_file(self):
        with open(REQUEST_PATH, mode="w") as stream:
            stream.write("process_id: test_func\ninputs:\n  x: 5\n  y: 2\n")

        request = parse_processing_request(request_file=REQUEST_PATH)
        self.assertEqual(
            ProcessingRequest(process_id="test_func", inputs={"x": 5, "y": 2}),
            request,
        )

    # noinspection PyPep8Naming
    def test_read_processing_request_from_inputs_and_subscribers(self):
        successUri = "https://myhost/api/v1/subscriptions/success"
        failedUri = "https://myhost/api/v1/subscriptions/failed"
        inProgressUri = "https://myhost/api/v1/subscriptions/progress"
        request = parse_processing_request(
            process_id="test_func",
            inputs=[
                "flag",
                "x=false",
                "y=13.8",
                "z=string",
            ],
            subscribers=[
                f"success={successUri}",
                f"failed={failedUri}",
                f"progress={inProgressUri}",
            ],
        )
        # noinspection PyTypeChecker
        self.assertEqual(
            ProcessingRequest(
                process_id="test_func",
                inputs={"flag": True, "x": False, "y": 13.8, "z": "string"},
                outputs=None,
                subscriber=Subscriber(
                    successUri=successUri,
                    failedUri=failedUri,
                    inProgressUri=inProgressUri,
                ),
            ),
            request,
        )

    def test_read_processing_request_from_file_and_inputs(self):
        with open(REQUEST_PATH, mode="w") as stream:
            stream.write("process_id: test_func\ninputs:\n  x: 5\n  y: 2\n")

        request = parse_processing_request(request_file=REQUEST_PATH, inputs=["x=13"])
        self.assertEqual(
            ProcessingRequest(process_id="test_func", inputs={"x": 13, "y": 2}),
            request,
        )

    # noinspection PyMethodMayBeStatic
    def test_read_processing_request_from_nothing(self):
        with pytest.raises(
            click.ClickException, match="Processing request is invalid:"
        ):
            parse_processing_request()

    # noinspection PyMethodMayBeStatic
    def test_read_processing_request_from_invalid_file(self):
        with open(REQUEST_PATH, mode="w") as stream:
            stream.write("42\n")
        with pytest.raises(
            click.ClickException, match="Request must be an object, but was type int"
        ):
            parse_processing_request(request_file=REQUEST_PATH)

    # noinspection PyMethodMayBeStatic
    def test_read_processing_request_from_invalid_input(self):
        with pytest.raises(click.ClickException, match="Invalid request NAME: '2x'"):
            parse_processing_request(process_id="my_func", inputs=["2x=20'"])

    def test_read_processing_request_from_invalid_subscription(self):
        with pytest.raises(
            click.ClickException,
            match=(
                r"Invalid subscriber item: must have form `EVENT=URL`, "
                r"but was 'success\:http\:\/\/localhost\/success'"
            ),
        ):
            parse_processing_request(
                process_id="my_func", subscribers=["success:http://localhost/success"]
            )

        with pytest.raises(
            click.ClickException,
            match=(
                r"Invalid subscriber EVENT: must be one of "
                r"\[success\|failed\|progress\], but was 'error'"
            ),
        ):
            parse_processing_request(
                process_id="my_func", subscribers=["error=http://localhost/error"]
            )

        with pytest.raises(
            click.ClickException,
            match="Invalid subscriber URL: 'localhorst'",
        ):
            parse_processing_request(
                process_id="my_func", subscribers=["failed=localhorst"]
            )
