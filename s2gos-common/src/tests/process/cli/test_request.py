#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import os
import unittest
from io import StringIO
from unittest.mock import patch

import click
import pytest

from s2gos_common.models import ProcessRequest, Subscriber
from s2gos_common.process.cli.request import ProcessingRequest

REQUEST_PATH = "test-request.yaml"


class RequestTest(unittest.TestCase):
    def tearDown(self):
        if os.path.exists(REQUEST_PATH):
            os.remove(REQUEST_PATH)

    def test_as_process_request(self):
        processing_request = ProcessingRequest(process_id="P16")
        process_request = processing_request.as_process_request()
        self.assertIsInstance(process_request, ProcessRequest)

    def test_as_process_request_dotpath(self):
        processing_request = ProcessingRequest(
            process_id="P16",
            dotpath=True,
            inputs={
                "scene.colors.bg": "blue",
                "scene.colors.opacity": 0.7,
                "scene.colors.fg": "white",
                "scene.models.path": "models/*",
                "log_file": "logs/*",
            },
        )
        process_request = processing_request.as_process_request()
        self.assertIsInstance(process_request, ProcessRequest)
        self.assertEqual(
            {
                "scene": {
                    "colors": {
                        "bg": "blue",
                        "opacity": 0.7,
                        "fg": "white",
                    },
                    "models": {
                        "path": "models/*",
                    },
                },
                "log_file": "logs/*",
            },
            process_request.inputs,
        )

    def test_create_processing_request_with_dotpath(self):
        request = ProcessingRequest.create(process_id="x15", dotpath=True)
        self.assertEqual(ProcessingRequest(process_id="x15", dotpath=True), request)

    def test_read_processing_request_from_yaml_stdin(self):
        stream = StringIO("process_id: test_func\ninputs:\n  x: 7\n  y: 9")
        with patch("sys.stdin", new=stream):
            request = ProcessingRequest.create(request_path="-")
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
            request = ProcessingRequest.create(request_path="-")
            self.assertEqual(
                ProcessingRequest(process_id="test_func_2", inputs={"x": 0, "y": -4}),
                request,
            )

    def test_read_processing_request_from_file(self):
        with open(REQUEST_PATH, mode="w") as stream:
            stream.write("process_id: test_func\ninputs:\n  x: 5\n  y: 2\n")

        request = ProcessingRequest.create(request_path=REQUEST_PATH)
        self.assertEqual(
            ProcessingRequest(process_id="test_func", inputs={"x": 5, "y": 2}),
            request,
        )

    # noinspection PyPep8Naming
    def test_read_processing_request_from_inputs_and_subscribers(self):
        successUri = "https://myhost/api/v1/subscriptions/success"
        failedUri = "https://myhost/api/v1/subscriptions/failed"
        inProgressUri = "https://myhost/api/v1/subscriptions/progress"
        request = ProcessingRequest.create(
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

        request = ProcessingRequest.create(request_path=REQUEST_PATH, inputs=["x=13"])
        self.assertEqual(
            ProcessingRequest(process_id="test_func", inputs={"x": 13, "y": 2}),
            request,
        )

    # noinspection PyMethodMayBeStatic
    def test_read_processing_request_from_nothing(self):
        with pytest.raises(
            click.ClickException, match="Processing request is invalid:"
        ):
            ProcessingRequest.create()

    # noinspection PyMethodMayBeStatic
    def test_read_processing_request_from_invalid_file(self):
        with open(REQUEST_PATH, mode="w") as stream:
            stream.write("42\n")
        with pytest.raises(
            click.ClickException, match="Request must be an object, but was type int"
        ):
            ProcessingRequest.create(request_path=REQUEST_PATH)

    # noinspection PyMethodMayBeStatic
    def test_read_processing_request_from_invalid_input(self):
        with pytest.raises(click.ClickException, match="Invalid request NAME: '2x'"):
            ProcessingRequest.create(process_id="my_func", inputs=["2x=20'"])

    # noinspection PyMethodMayBeStatic
    def test_read_processing_request_from_invalid_subscription(self):
        with pytest.raises(
            click.ClickException,
            match=(
                r"Invalid subscriber item: must have form `EVENT=URL`, "
                r"but was 'success\:http\:\/\/localhost\/success'"
            ),
        ):
            ProcessingRequest.create(
                process_id="my_func", subscribers=["success:http://localhost/success"]
            )

        with pytest.raises(
            click.ClickException,
            match=(
                r"Invalid subscriber EVENT: must be one of "
                r"\[success\|failed\|progress\], but was 'error'"
            ),
        ):
            ProcessingRequest.create(
                process_id="my_func", subscribers=["error=http://localhost/error"]
            )

        with pytest.raises(
            click.ClickException,
            match="Invalid subscriber URL: 'localhorst'",
        ):
            ProcessingRequest.create(
                process_id="my_func", subscribers=["failed=localhorst"]
            )


class ProcessingRequestHelpersTest(unittest.TestCase):
    def test_nest_dict(self):
        self.assertEqual(
            {"a": 1, "b": True}, ProcessingRequest._nest_dict({"a": 1, "b": True})
        )
        self.assertEqual(
            {"a": 1, "b": {"x": 0.3, "y": -0.1}},
            ProcessingRequest._nest_dict({"a": 1, "b.x": 0.3, "b.y": -0.1}),
        )
