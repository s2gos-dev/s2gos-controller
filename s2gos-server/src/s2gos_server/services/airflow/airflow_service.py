#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import os
from functools import cached_property
from pprint import pprint
from typing import Optional

import fastapi
import requests
from airflow_client.client import ApiClient, Configuration
from airflow_client.client.api import DAGApi

from s2gos_common.models import (
    InputDescription,
    JobInfo,
    JobList,
    JobResults,
    OutputDescription,
    ProcessDescription,
    ProcessList,
    ProcessRequest,
    ProcessSummary,
)
from s2gos_server.exceptions import JSONContentException
from s2gos_server.services.base import ServiceBase

DEFAULT_AIRFLOW_BASE_URL = "http://localhost:8080"


class AirflowService(ServiceBase):
    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        airflow_base_url: Optional[str] = None,
        airflow_username: Optional[str] = None,
        airflow_password: Optional[str] = None,
    ):
        super().__init__(title=title, description=description)
        self._airflow_base_url = airflow_base_url
        self._airflow_username = airflow_username
        self._airflow_password = airflow_password

    async def get_processes(
        self, request: fastapi.Request, *args, **kwargs
    ) -> ProcessList:
        processes: list[ProcessSummary] = []
        try:
            list_dags_response = self.airflow_dag_api.get_dags(
                exclude_stale=True, limit=None
            )
        except Exception as e:
            raise JSONContentException(
                500, detail=f"Error getting Airflow DAGs: {e}", exception=e
            )
        if list_dags_response and list_dags_response.dags:
            print(f"Found {len(list_dags_response.dags)} active DAGs:")
            for dag in list_dags_response.dags:
                print(
                    f"  - DAG ID: {dag.dag_id}, "
                    f"Is Paused: {dag.is_paused}, "
                    f"File Location: {dag.fileloc}"
                )
                # https://github.com/apache/airflow-client-python/blob/main/airflow_client/client/models/dag_response.py
                processes.append(
                    ProcessSummary(
                        id=dag.dag_id,
                        version="0.0.0",  # TODO
                        title=dag.dag_display_name,
                        description=dag.description,
                    )
                )
        return ProcessList(
            processes=processes,
            links=[self._get_self_link(request, "get_processes")],
        )

    async def get_process(self, process_id: str, *args, **kwargs) -> ProcessDescription:
        try:
            dag_details = self.airflow_dag_api.get_dag_details(dag_id=process_id)
        except Exception as e:
            raise JSONContentException(
                500,
                detail=f"Error getting details for Airflow DAG {process_id!r}: {e}",
                exception=e,
            )

        inputs: dict[str, InputDescription] = {}
        if dag_details.params:
            # TODO: check that 'param_value' will be an instance of 'Param' model
            for param_key, param_value in dag_details.params.items():
                # TODO: inputs[param_key] = InputDescription(param_value. ...)
                print(f"    - {param_key} = {param_value} (type {type(param_value)}):")
        else:
            print("  No parameters (params) defined for this DAG.")

        # TODO: where to get outputs from?
        outputs: dict[str, OutputDescription] = {}

        print("\nFull DAG details (as dictionary):")
        pprint(dag_details.to_dict())
        # https://github.com/apache/airflow-client-python/blob/main/airflow_client/client/models/dag_details_response.py
        return ProcessDescription(
            id=dag_details.dag_id,
            version="0.0.0",  # TODO
            title=dag_details.dag_display_name,
            description=dag_details.doc_md or dag_details.description,
            inputs=inputs,
            outputs=outputs,
        )

    async def execute_process(
        self, process_id: str, process_request: ProcessRequest, *args, **kwargs
    ) -> JobInfo:
        raise NotImplementedError

    async def get_jobs(self, *args, **kwargs) -> JobList:
        raise NotImplementedError

    async def get_job(self, job_id: str, *args, **kwargs) -> JobInfo:
        raise NotImplementedError

    async def dismiss_job(self, job_id: str, *args, **kwargs) -> JobInfo:
        raise NotImplementedError

    async def get_job_results(self, job_id: str, *args, **kwargs) -> JobResults:
        raise NotImplementedError

    @cached_property
    def airflow_dag_api(self) -> DAGApi:
        return DAGApi(self.airflow_client)

    @cached_property
    def airflow_client(self) -> ApiClient:
        airflow_base_url = self._airflow_base_url or os.getenv(
            "AIRFLOW_API_BASE_URL", DEFAULT_AIRFLOW_BASE_URL
        )
        airflow_username = self._airflow_username or os.getenv(
            "AIRFLOW_USERNAME", "admin"
        )
        airflow_password = self._airflow_password or os.getenv("AIRFLOW_PASSWORD")
        if not airflow_password:
            raise RuntimeError(
                "missing Airflow password; please set env var AIRFLOW_PASSWORD"
            )
        access_token = self.fetch_access_token(
            airflow_base_url,
            username=airflow_username,
            password=airflow_password,
        )
        configuration = Configuration(host=airflow_base_url, access_token=access_token)
        return ApiClient(configuration)

    @classmethod
    def fetch_access_token(
        cls,
        base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> str:
        response = requests.post(
            f"{base_url}/auth/token",
            json={"username": username, "password": password},
        )
        try:
            response.raise_for_status()
            token_data = response.json()
            return token_data.get("access_token")
        except requests.exceptions.HTTPError as e:
            raise JSONContentException(
                response.status_code, detail=response.reason, exception=e
            )
