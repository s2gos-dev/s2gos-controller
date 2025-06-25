#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import datetime
import inspect
import traceback
import warnings
from abc import ABC, abstractmethod
from concurrent.futures import Future
from typing import Any, Callable, Optional

from s2gos_common.models import JobInfo, JobStatus, JobType


class JobCancelledException(Exception):
    """Raised if a job's cancellation has been requested."""


class JobContext(ABC):
    """Report task progress and check for task cancellation."""

    @abstractmethod
    def report_progress(
        self,
        progress: Optional[int] = None,
        message: Optional[str] = None,
    ) -> None:
        """Report task progress.

        Args:
            progress: Progress in percent
            message: Detail progress message

        Raises:
            JobCancellationException: if an attempt has been made
                to cancel this job.
        """

    @abstractmethod
    def is_cancelled(self) -> bool:
        """Test whether an attempt has been made to cancel this job.
        It may still be running though.

        Returns:
            `True` if so, `False` otherwise.
        """

    @abstractmethod
    def check_cancelled(self) -> None:
        """Raise a `JobCancellationException`,
        an attempt has been made to cancel this job.
        """


class Job(JobContext):
    """Represents an execution of a user function.

    Args:
        process_id: The process identifier.
        job_id: A job identifier.
        function: The user function.
        function_kwargs: The user function's keyword arguments.
    """

    def __init__(
        self,
        *,
        process_id: str,
        job_id: str,
        function: Callable[..., Any],
        function_kwargs: dict[str, Any],
    ):
        self.job_info = JobInfo(
            type=JobType.process,
            processID=process_id,
            jobID=job_id,
            status=JobStatus.accepted,
            created=datetime.datetime.now(),
        )
        self.function = function
        self.function_kwargs = function_kwargs
        self.cancelled = False
        self.future: Optional[Future] = None

    def report_progress(
        self, progress: Optional[int] = None, message: Optional[str] = None
    ):
        self.check_cancelled()
        self.job_info.updated = datetime.datetime.now()
        if progress is not None:
            self.job_info.progress = progress
        if message is not None:
            self.job_info.message = message

    def is_cancelled(self) -> bool:
        return self.cancelled

    def check_cancelled(self):
        if self.cancelled:
            raise JobCancelledException

    def cancel(self):
        """Request job cancellation.
        Note, actual cancellation will happen
        only from within the user function.
        """
        self.cancelled = True

    def run(self):
        """Run this job."""

        # Make the job (context) findable by get_job_context()
        # through the local variable __job_context__
        __job_context__ = self  # noqa: F841

        self._start_job()

        result = None
        try:
            self.check_cancelled()
            result = self.function(**self.function_kwargs)
            self._finish_job(JobStatus.successful)
        except JobCancelledException:
            self._finish_job(JobStatus.dismissed)
        except Exception as e:
            self._finish_job(JobStatus.failed, exception=e)
        return result

    def _start_job(self):
        self.job_info.started = datetime.datetime.now()
        self.job_info.status = JobStatus.running

    def _finish_job(self, job_status: JobStatus, exception: Optional[Exception] = None):
        self.job_info.finished = datetime.datetime.now()
        self.job_info.status = job_status
        if exception is not None:
            self.job_info.message = f"{exception}"
            self.job_info.traceback = traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )


def get_job_context() -> JobContext:
    """Get the current job context."""
    frame = inspect.currentframe()
    try:
        while frame:
            job_context = frame.f_locals.get("__job_context__")
            if isinstance(job_context, JobContext):
                return job_context
            frame = frame.f_back
    finally:
        # Always free alive frame-references
        del frame
    # noinspection PyUnreachableCode
    warnings.warn("cannot determine current job context; using non-functional dummy")
    return NullJobContext()


class NullJobContext(JobContext):
    """A job context used if a real one could not be provided."""

    def report_progress(
        self, progress: Optional[int] = None, message: Optional[str] = None
    ) -> None:
        """Does nothing."""

    def is_cancelled(self) -> bool:
        """Returns `False`."""
        return False

    def check_cancelled(self) -> None:
        """Does nothing."""
