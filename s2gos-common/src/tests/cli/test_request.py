#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import os
import unittest
from io import StringIO
from unittest.mock import patch

import click
import pytest

from s2gos_common.cli.request import ProcessingRequest, read_processing_request

REQUEST_PATH = "test-request.yaml"


class RequestTest(unittest.TestCase):
    def tearDown(self):
        if os.path.exists(REQUEST_PATH):
            os.remove(REQUEST_PATH)

    def test_read_processing_request_from_yaml_stdin(self):
        stream = StringIO("process_id: test_func\ninputs:\n  x: 7\n  y: 9")
        with patch("sys.stdin", new=stream):
            request = read_processing_request(request_file="-")
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
            request = read_processing_request(request_file="-")
            self.assertEqual(
                ProcessingRequest(process_id="test_func_2", inputs={"x": 0, "y": -4}),
                request,
            )

    def test_read_processing_request_from_file(self):
        with open(REQUEST_PATH, mode="w") as stream:
            stream.write("process_id: test_func\ninputs:\n  x: 5\n  y: 2\n")

        request = read_processing_request(request_file=REQUEST_PATH)
        self.assertEqual(
            ProcessingRequest(process_id="test_func", inputs={"x": 5, "y": 2}),
            request,
        )

    def test_read_processing_request_from_file_and_args(self):
        with open(REQUEST_PATH, mode="w") as stream:
            stream.write("process_id: test_func\ninputs:\n  x: 5\n  y: 2\n")

        request = read_processing_request(
            request_file=REQUEST_PATH, request_inputs=["x=13"]
        )
        self.assertEqual(
            ProcessingRequest(process_id="test_func", inputs={"x": 13, "y": 2}),
            request,
        )

    # noinspection PyMethodMayBeStatic
    def test_read_processing_request_from_nothing(self):
        with pytest.raises(
            click.ClickException, match="Processing request is invalid:"
        ):
            read_processing_request()

    # noinspection PyMethodMayBeStatic
    def test_read_processing_request_from_invalid_file(self):
        with open(REQUEST_PATH, mode="w") as stream:
            stream.write("42\n")
        with pytest.raises(
            click.ClickException, match="Request must be an object, but was type int"
        ):
            read_processing_request(request_file=REQUEST_PATH)

    # noinspection PyMethodMayBeStatic
    def test_read_processing_request_from_invalid_input(self):
        with pytest.raises(
            click.ClickException, match="Invalid request input argument: x='"
        ):
            read_processing_request(process_id="my_func", request_inputs=["x='"])
