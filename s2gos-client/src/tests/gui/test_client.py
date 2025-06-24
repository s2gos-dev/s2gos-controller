#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
from typing import Any, Literal
from unittest import TestCase

from s2gos_client.gui import Client as GuiClient
from s2gos_client.gui.jobs_form import JobsForm
from s2gos_client.gui.processes_form import ProcessesForm
from s2gos_client.transport import Transport
from s2gos_common.models import JobList, ProcessList


class ClientTest(TestCase):
    def test_show_processes(self):
        class _MockTransport(Transport):
            def call(
                self,
                path: str,
                method: Literal["get", "post", "put", "delete"],
                *args,
                **kwargs,
            ) -> Any:
                if (method, path) == ("get", "/processes"):
                    return ProcessList(processes=[], links=[])
                return None

        client = GuiClient(_transport=_MockTransport())
        processes_form = client.show_processes()
        self.assertIsInstance(processes_form, ProcessesForm)

    def test_show_jobs(self):
        class _MockTransport(Transport):
            def call(
                self,
                path: str,
                method: Literal["get", "post", "put", "delete"],
                *args,
                **kwargs,
            ) -> Any:
                if (method, path) == ("get", "/jobs"):
                    return JobList(jobs=[], links=[])
                return None

        client = GuiClient(_transport=_MockTransport())
        jobs_form = client.show_jobs()
        self.assertIsInstance(jobs_form, JobsForm)
