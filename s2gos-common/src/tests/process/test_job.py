#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

import pytest

from s2gos_common.models import JobResults, JobStatus
from s2gos_common.process import Process
from s2gos_common.process.job import (
    Job,
    JobCancelledException,
    NullJobContext,
    get_job_context,
)

from .test_process import f1


def fn_success(x: int, y: int) -> int:
    return x * y


def fn_success_report(path: str) -> str:
    ctx = get_job_context()
    ctx.check_cancelled()
    ctx.report_progress(progress=0)
    ctx.report_progress(progress=50, message="Almost done")
    ctx.report_progress(progress=100)
    return path + "/result.zarr"


# noinspection PyUnusedLocal
def fn_cancel_exc(path: str) -> str:
    raise JobCancelledException


# noinspection PyUnusedLocal
def fn_exc(path: str) -> str:
    raise OSError("File not found")


class JobTest(TestCase):
    def test_ctor(self):
        job = Job(
            process=Process.create(fn_success, id="process_54"),
            job_id="job_27",
            function_kwargs={"x": True, "y": 2},
        )
        self.assertEqual("process_54", job.job_info.processID)
        self.assertEqual("job_27", job.job_info.jobID)
        self.assertEqual(None, job.job_info.progress)
        self.assertEqual({"x": True, "y": 2}, job.function_kwargs)

    def test_context(self):
        job = Job(
            process=Process.create(fn_success, id="process_54"),
            job_id="job_27",
            function_kwargs={"x": False, "y": 2},
        )
        self.assertEqual(False, job.is_cancelled())
        self.assertEqual(None, job.check_cancelled())
        job.report_progress(progress=35, message="2/6 input files downloaded")
        self.assertEqual(35, job.job_info.progress)
        self.assertEqual("2/6 input files downloaded", job.job_info.message)
        job.report_progress(message="3/6 input files downloaded")
        self.assertEqual(35, job.job_info.progress)
        self.assertEqual("3/6 input files downloaded", job.job_info.message)
        job.report_progress(progress=40)
        self.assertEqual(40, job.job_info.progress)
        self.assertEqual("3/6 input files downloaded", job.job_info.message)

        job.cancel()
        self.assertEqual(True, job.is_cancelled())
        with pytest.raises(JobCancelledException):
            job.check_cancelled()
        self.assertEqual(40, job.job_info.progress)
        self.assertEqual("3/6 input files downloaded", job.job_info.message)

    def test_run_success(self):
        job = Job(
            process=Process.create(fn_success, id="process_8"),
            job_id="job_41",
            function_kwargs={"x": 3, "y": 9},
        )
        job_results = job.run()
        # noinspection PyArgumentList
        self.assertEqual(JobResults({"return_value": 27}), job_results)
        self.assertEqual(JobStatus.successful, job.job_info.status)
        self.assertEqual(None, job.job_info.progress)
        self.assertEqual(None, job.job_info.message)

    def test_run_success_report(self):
        job = Job(
            process=Process.create(fn_success_report, id="process_8"),
            job_id="job_41",
            function_kwargs={"path": "outputs"},
        )
        job_results = job.run()
        # noinspection PyArgumentList
        self.assertEqual(
            JobResults({"return_value": "outputs/result.zarr"}), job_results
        )
        self.assertEqual(JobStatus.successful, job.job_info.status)
        self.assertEqual(100, job.job_info.progress)
        self.assertEqual("Almost done", job.job_info.message)

    def test_run_exc(self):
        job = Job(
            process=Process.create(fn_exc, id="process_8"),
            job_id="job_41",
            function_kwargs={"path": "outputs"},
        )
        result = job.run()
        self.assertEqual(None, result)
        self.assertEqual(JobStatus.failed, job.job_info.status)

    def test_run_failed(self):
        job = Job(
            process=Process.create(fn_cancel_exc, id="process_8"),
            job_id="job_41",
            function_kwargs={"path": "outputs"},
        )
        result = job.run()
        self.assertEqual(None, result)
        self.assertEqual(JobStatus.dismissed, job.job_info.status)


class GetJobContextTest(TestCase):
    def test_null(self):
        job_context = get_job_context()
        self.assertIsInstance(job_context, NullJobContext)

    def test_valid(self):
        __job_context__ = Job(  # noqa: F841
            process=Process.create(f1),
            job_id="b",
            function_kwargs={"x": 4},
        )
        value = get_job_context()
        self.assertIs(__job_context__, value)


class NullJobContextTest(TestCase):
    def test_it(self):
        job_context = NullJobContext()
        self.assertFalse(job_context.report_progress(progress=85))
        self.assertFalse(job_context.is_cancelled())
        self.assertFalse(job_context.check_cancelled())
