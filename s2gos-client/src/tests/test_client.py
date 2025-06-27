#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from tests.helpers import MockTransport

from s2gos_client.client import Client
from s2gos_common.models import (
    Capabilities,
    ConformanceDeclaration,
    JobInfo,
    JobList,
    JobResults,
    ProcessDescription,
    ProcessList,
    ProcessRequest,
)


class ClientTest(TestCase):
    def setUp(self):
        self.transport = MockTransport()
        self.client = Client(_transport=self.transport)

    def test_repr_json(self):
        result = self.client._repr_json_()
        self.assertIsInstance(result, tuple)
        self.assertEqual(2, len(result))
        data, metadata = result
        self.assertIsInstance(data, dict)
        self.assertIsInstance(metadata, dict)
        self.assertEqual({"root": "Configuration:"}, metadata)

    def test_get_capabilities(self):
        result = self.client.get_capabilities()
        self.assertIsInstance(result, Capabilities)

    def test_get_conformance(self):
        result = self.client.get_conformance()
        self.assertIsInstance(result, ConformanceDeclaration)

    def test_get_processes(self):
        result = self.client.get_processes()
        self.assertIsInstance(result, ProcessList)

    def test_get_process(self):
        result = self.client.get_process(process_id="gobabeb_1")
        self.assertIsInstance(result, ProcessDescription)

    def test_execute_process(self):
        result = self.client.execute_process(
            process_id="gobabeb_1",
            request=ProcessRequest(
                inputs={"bbox": [10, 20, 30, 40]},
                outputs={},
            ),
        )
        self.assertIsInstance(result, JobInfo)

    def test_get_jobs(self):
        result = self.client.get_jobs()
        self.assertIsInstance(result, JobList)

    def test_dismiss_job(self):
        result = self.client.dismiss_job("job_12")
        self.assertIsInstance(result, JobInfo)

    def test_get_job(self):
        result = self.client.get_job("job_12")
        self.assertIsInstance(result, JobInfo)

    def test_get_job_results(self):
        result = self.client.get_job_results("job_12")
        self.assertIsInstance(result, JobResults)
