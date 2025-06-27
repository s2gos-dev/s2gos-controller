#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from panel.layout import Panel

from s2gos_client.gui.jobs_form import JobsForm
from s2gos_common.models import JobInfo, JobList, JobStatus


class JobsFormTest(TestCase):
    def test_it(self):
        jobs_form = _create_jobs_form()
        self.assertIsInstance(jobs_form.__panel__(), Panel)


def _create_jobs_form() -> JobsForm:
    job_list = JobList(
        jobs=[
            JobInfo(
                type="process",
                processID="gen_scene",
                jobID="job_1",
                status=JobStatus.successful,
                progress=100,
            ),
            JobInfo(
                type="process",
                processID="gen_scene",
                jobID="job_2",
                status=JobStatus.running,
                progress=23,
            ),
            JobInfo(
                type="process",
                processID="gen_scene",
                jobID="job_3",
                status=JobStatus.failed,
                progress=97,
            ),
            JobInfo(
                type="process",
                processID="gen_scene",
                jobID="job_4",
                status=JobStatus.accepted,
            ),
        ],
        links=[],
    )
    job_list_error = None

    def on_delete_job(job_id: str):
        pass

    def on_cancel_job(job_id: str):
        pass

    def on_restart_job(job_id: str):
        pass

    def on_get_job_results(job_id: str):
        pass

    return JobsForm(
        job_list,
        job_list_error,
        on_delete_job=on_delete_job,
        on_cancel_job=on_cancel_job,
        on_restart_job=on_restart_job,
        on_get_job_results=on_get_job_results,
    )
