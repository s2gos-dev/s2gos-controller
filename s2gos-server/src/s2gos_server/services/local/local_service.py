#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.process import ProcessPoolExecutor
from typing import Callable, Optional

from fastapi.responses import JSONResponse

from s2gos_common.models import (
    Capabilities,
    ConformanceDeclaration,
    JobInfo,
    JobList,
    JobResults,
    ProcessDescription,
    ProcessList,
    ProcessRequest,
    ProcessSummary,
    StatusCode,
)
from s2gos_server.exceptions import JSONContentException
from s2gos_server.service import Service

from .job import Job
from .process_registry import ProcessRegistry

model_dump_config = dict(
    exclude_none=True,
    exclude_unset=True,
    exclude_defaults=True,
)


class LocalService(Service):
    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        executor: Optional[ThreadPoolExecutor | ProcessPoolExecutor] = None,
    ):
        self.capabilities = Capabilities(title=title, description=description, links=[])
        self.executor = executor or ThreadPoolExecutor(max_workers=3)
        self.process_registry = ProcessRegistry()
        self.jobs: dict[str, Job] = {}

    async def get_capabilities(self) -> Capabilities:
        return self.capabilities

    async def get_conformance(self) -> ConformanceDeclaration:
        return ConformanceDeclaration(
            conformsTo=[
                "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/core",
                "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/"
                "ogc-process-description",
                "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/json",
                # "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/html",
                "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/oas30",
                "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/job-list",
                # "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/callback",
                "http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/dismiss",
            ]
        )

    async def get_processes(self) -> ProcessList:
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
            links=[],
        )

    async def get_process(self, process_id: str) -> ProcessDescription:
        process_entry = self._get_process_entry(process_id)
        return process_entry.process

    async def execute_process(
        self, process_id: str, request: ProcessRequest
    ) -> JSONResponse:
        process_entry = self._get_process_entry(process_id)
        process_info = process_entry.process

        input_params = (
            request.model_dump(mode="json", include={"inputs"}).get("inputs") or {}
        )
        input_default_params = {
            input_name: input_info.schema_.default
            for input_name, input_info in process_info.inputs.items()
            if input_info.schema_.default is not None
        }
        function_kwargs = {}
        for input_name in process_info.inputs.keys():
            if input_name in input_params:
                function_kwargs[input_name] = input_params[input_name]
            elif input_name in input_default_params:
                function_kwargs[input_name] = input_default_params[input_name]

        # print("input_params:", input_params)
        # print("input_default_params:", input_default_params)
        # print("params:", function_kwargs)

        job_id = f"job_{len(self.jobs)}"
        job = Job(
            process_id=process_info.id,
            job_id=job_id,
            function=process_entry.function,
            function_kwargs=function_kwargs,
        )
        self.jobs[job_id] = job
        job.future = self.executor.submit(job.run)
        # 201 means, async execution started
        return JSONResponse(
            status_code=201, content=job.status_info.model_dump(mode="json")
        )

    async def get_jobs(self) -> JobList:
        return JobList(jobs=[job.status_info for job in self.jobs.values()], links=[])

    async def get_job(self, job_id: str) -> JobInfo:
        job = self._get_job(job_id, forbidden_status_codes={})
        return job.status_info

    async def dismiss_job(self, job_id: str) -> JobInfo:
        job = self._get_job(job_id, forbidden_status_codes={})
        if job.status_info.status in (StatusCode.accepted, StatusCode.running):
            job.cancel()
        elif job.status_info.status in (
            StatusCode.dismissed,
            StatusCode.successful,
            StatusCode.failed,
        ):
            del self.jobs[job_id]
        return job.status_info

    async def get_job_results(self, job_id: str) -> JobResults:
        job = self._get_job(
            job_id,
            forbidden_status_codes={
                StatusCode.accepted: "has not started yet",
                StatusCode.running: "is still running",
                StatusCode.dismissed: "has been cancelled",
                StatusCode.failed: "has failed",
            },
        )
        result = job.future.result()
        entry = self.process_registry.get_entry(job.status_info.processID)
        outputs = entry.process.outputs or {}
        output_count = len(outputs)
        return JobResults.model_validate(
            {
                output_name: result if output_count == 1 else result[i]
                for i, output_name in enumerate(outputs.keys())
            }
        )

    # TODO: be user-friendly, turn kwargs into parameter list
    def process(self, **kwargs) -> Callable[[Callable], Callable]:
        """A decorator for user functions to be registered as processes."""

        def _factory(function: Callable):
            self.register_process(function, **kwargs)
            return function

        return _factory

    def register_process(self, function: Callable, **kwargs) -> ProcessRegistry.Entry:
        """Register a user function as process."""
        return self.process_registry.register_function(function, **kwargs)

    def _get_process_entry(self, process_id: str) -> ProcessRegistry.Entry:
        process_entry = self.process_registry.get_entry(process_id)
        if process_entry is None:
            raise JSONContentException(
                404, detail=f"Process {process_id!r} does not exist"
            )
        return process_entry

    def _get_job(
        self, job_id: str, forbidden_status_codes: dict[StatusCode, str]
    ) -> Job:
        job = self.jobs.get(job_id)
        if job is None:
            raise JSONContentException(404, detail=f"Job {job_id!r} does not exist")
        message = forbidden_status_codes.get(job.status_info.status)
        if message:
            raise JSONContentException(403, detail=f"Job {job_id!r} {message}")
        return job
