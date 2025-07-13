#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.process import ProcessPoolExecutor
from typing import Any, Callable, Optional

import fastapi
import pydantic

from s2gos_common.models import (
    JobInfo,
    JobList,
    JobResults,
    JobStatus,
    ProcessDescription,
    ProcessList,
    ProcessRequest,
    ProcessSummary,
    Schema,
)
from s2gos_server.exceptions import JSONContentException
from s2gos_server.services.base import ServiceBase

from .job import Job
from .process_registry import ProcessRegistry


class LocalService(ServiceBase):
    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        executor: Optional[ThreadPoolExecutor | ProcessPoolExecutor] = None,
    ):
        super().__init__(title=title, description=description)
        self.executor = executor or ThreadPoolExecutor(max_workers=3)
        self.process_registry = ProcessRegistry()
        self.jobs: dict[str, Job] = {}

    async def get_processes(self, request: fastapi.Request, **_kwargs) -> ProcessList:
        return ProcessList(
            processes=[
                ProcessSummary(
                    **p.model_dump(
                        mode="python",
                        exclude={"inputs", "outputs"},
                    )
                )
                for p in self.process_registry.get_process_list()
            ],
            links=[self.get_self_link(request, "get_processes")],
        )

    async def get_process(self, process_id: str, **kwargs) -> ProcessDescription:
        process_entry = self._get_process_entry(process_id)
        return process_entry.process

    async def execute_process(
        self, process_id: str, process_request: ProcessRequest, **_kwargs
    ) -> JobInfo:
        process_entry = self._get_process_entry(process_id)
        process_desc = process_entry.process
        input_params = _nest_dict(process_request.inputs or {})
        input_default_params = {
            input_name: input_info.schema_.default
            for input_name, input_info in (process_desc.inputs or {}).items()
            if isinstance(input_info.schema_, Schema)
            and input_info.schema_.default is not None
        }
        input_values: dict[str, Any] = {}
        for input_name in (process_desc.inputs or {}).keys():
            if input_name in input_params:
                input_values[input_name] = input_params[input_name]
            elif input_name in input_default_params:
                input_values[input_name] = input_default_params[input_name]

        model_instance: pydantic.BaseModel
        try:
            model_instance = process_entry.model_class(**input_values)
        except pydantic.ValidationError as e:
            raise JSONContentException(
                400,
                detail=f"Invalid parameterization for process {process_id!r}: {e}",
                exception=e,
            )

        function_kwargs = {
            k: getattr(model_instance, k)
            for k in model_instance.model_fields.keys()
            if k in input_values
        }

        # print("input_params:", input_params)
        # print("input_default_params:", input_default_params)
        # print("params:", function_kwargs)

        job_id = f"job_{len(self.jobs)}"
        job = Job(
            process_id=process_desc.id,
            job_id=job_id,
            function=process_entry.function,
            function_kwargs=function_kwargs,
        )
        self.jobs[job_id] = job
        job.future = self.executor.submit(job.run)
        # 201 means, async execution started
        return job.job_info

    async def get_jobs(self, request: fastapi.Request, **_kwargs) -> JobList:
        return JobList(
            jobs=[job.job_info for job in self.jobs.values()],
            links=[self.get_self_link(request, "get_jobs")],
        )

    async def get_job(self, job_id: str, *args, **kwargs) -> JobInfo:
        job = self._get_job(job_id, forbidden_status_codes={})
        return job.job_info

    async def dismiss_job(self, job_id: str, *args, **_kwargs) -> JobInfo:
        job = self._get_job(job_id, forbidden_status_codes={})
        if job.job_info.status in (JobStatus.accepted, JobStatus.running):
            job.cancel()
        elif job.job_info.status in (
            JobStatus.dismissed,
            JobStatus.successful,
            JobStatus.failed,
        ):
            del self.jobs[job_id]
        return job.job_info

    async def get_job_results(self, job_id: str, *args, **_kwargs) -> JobResults:
        job = self._get_job(
            job_id,
            forbidden_status_codes={
                JobStatus.accepted: "has not started yet",
                JobStatus.running: "is still running",
                JobStatus.dismissed: "has been cancelled",
                JobStatus.failed: "has failed",
            },
        )
        assert job.future is not None
        assert job.job_info.processID is not None
        result = job.future.result()
        entry = self.process_registry.get_entry(job.job_info.processID)
        assert entry is not None
        outputs = entry.process.outputs or {}
        output_count = len(outputs)
        return JobResults.model_validate(
            {
                output_name: result if output_count == 1 else result[i]
                for i, output_name in enumerate(outputs.keys())
            }
        )

    # noinspection PyShadowingBuiltins
    def process(
        self,
        id: Optional[str] = None,
        version: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        input_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
        output_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
    ) -> Callable[[Callable], Callable]:
        """A decorator for user functions to be registered as processes."""

        def _factory(function: Callable):
            self.process_registry.register_function(
                function,
                id=id,
                version=version,
                title=title,
                description=description,
                input_fields=input_fields,
                output_fields=output_fields,
            )
            return function

        return _factory

    def _get_process_entry(self, process_id: str) -> ProcessRegistry.Entry:
        process_entry = self.process_registry.get_entry(process_id)
        if process_entry is None:
            raise JSONContentException(
                404, detail=f"Process {process_id!r} does not exist"
            )
        return process_entry

    def _get_job(
        self, job_id: str, forbidden_status_codes: dict[JobStatus, str]
    ) -> Job:
        job = self.jobs.get(job_id)
        if job is None:
            raise JSONContentException(404, detail=f"Job {job_id!r} does not exist")
        message = forbidden_status_codes.get(job.job_info.status)
        if message:
            raise JSONContentException(403, detail=f"Job {job_id!r} {message}")
        return job


def _nest_dict(flat_dict: dict[str, Any]) -> dict[str, Any]:
    nested_dict: dict[str, Any] = {}
    for key, value in flat_dict.items():
        path = key.split(".")
        current = nested_dict
        for name in path[:-1]:
            current = current.setdefault(name, {})
        current[path[-1]] = value
    return nested_dict
