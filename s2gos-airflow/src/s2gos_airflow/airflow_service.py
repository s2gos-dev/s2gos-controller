#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Optional

import os
from pprint import pprint

from airflow_client.client import ApiClient, Configuration
from airflow_client.client.api import dag_api, auth_api
from airflow_client.client.models import LoginForm
import fastapi

from s2gos_common.models import (
    InputDescription,
    JobInfo,
    JobList,
    JobResults,
    OutputDescription,
    ProcessDescription,
    ProcessList,
    ProcessRequest,
    ProcessSummary
)
from s2gos_server.services.base import ServiceBase
from s2gos_server.exceptions import JSONContentException


# --- Configuration ---
AIRFLOW_API_BASE_URL = os.getenv("AIRFLOW_API_BASE_URL", "http://localhost:8080/api/v2")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "admin")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "admin")


class AirflowService(ServiceBase):
    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
    ):
        super().__init__(title=title, description=description)
            # Get the token from the base URL (without /api/v2)
        jwt_token = get_airflow_jwt_token(
            AIRFLOW_API_BASE_URL.replace("/api/v2", ""), AIRFLOW_USERNAME, AIRFLOW_PASSWORD
        )
        configuration = Configuration(host=AIRFLOW_API_BASE_URL, access_token=jwt_token)
        self.airflow_client = ApiClient(configuration)
        self.dags_api_instance = dag_api.DAGApi(self.api_client)

    async def get_processes(self, request: fastapi.Request, *args, **kwargs) -> ProcessList:
        processes: list[ProcessSummary] = []
        try:
            list_dags_response = self.dags_api_instance.get_dags(only_active=True, limit=None)
        except Exception as e:
            raise JSONContentException(500, detail=f"Error getting all Airflow DAGs: {e}")
        if list_dags_response and list_dags_response.dags:
            print(f"Found {len(list_dags_response.dags)} active DAGs:")
            for dag in list_dags_response.dags:
                print(
                    f"  - DAG ID: {dag.dag_id}, Is Paused: {dag.is_paused}, File Location: {dag.fileloc}"
                )
                # https://github.com/apache/airflow-client-python/blob/main/airflow_client/client/models/dag_response.py
                processes.append(
                    ProcessSummary(
                        id=dag.dag_id,
                        version="0.0.0",  # TODO 
                        title=dag.dag_display_name,
                        description=dag.description,
                        tags=[t.name for t in dag.tags],
                    )
                )
        return ProcessList(processes=[], links=[self._get_self_link(request, "get_processes")])

    
    async def get_process(self, process_id: str, *args, **kwargs) -> ProcessDescription:
        try:
            dag_details = self.dags_api_instance.get_dag(dag_id=process_id)
        except Exception as e:
            raise JSONContentException(
                500, 
                detail=f"Error getting details for Airflow DAG {process_id!r}: {e}", 
                e=e
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
            tags=[t.name for t in dag_details.tags],
            inputs=inputs,
            inputs=outputs,
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


def get_airflow_jwt_token(host: str, username: str, password: str) -> str:
    # This assumes the /auth/token endpoint is at the base URL, not /api/v2
    # Adjust if your setup places it differently.
    config = Configuration(host=host)
    with ApiClient(config) as api_client:
        auth_instance = auth_api.AuthApi(api_client)
        login_form = LoginForm(username=username, password=password)
        try:
            auth_response = auth_instance.login(login_form=login_form)
            return auth_response.access_token
        except Exception as e:
            print(f"Error obtaining JWT token: {e}")
            raise


# --- Airflow API Interactions ---

    # --- 2. Get details for a given DAG ---
    # Replace with a DAG_ID that exists in your Airflow instance
    target_dag_id = "example_bash_operator"  # Or one of the IDs from the list above

    print(f"\n--- Getting details for DAG: '{target_dag_id}' ---")
    try:
        dag_details = dags_api_instance.get_dag(dag_id=target_dag_id)

        print(f"Details for DAG ID: {dag_details.dag_id}")
        print(f"  Description: {dag_details.description}")
        print(f"  File Location: {dag_details.fileloc}")
        print(f"  Is Paused: {dag_details.is_paused}")
        print(
            f"  Schedule Interval: {dag_details.schedule_interval.to_dict() if dag_details.schedule_interval else 'None'}"
        )

        # Accessing parameters (new in Airflow 3.x - if defined in the DAG)
        if dag_details.params:
            print("  Defined Parameters (params):")
            for param_key, param_value in dag_details.params.items():
                print(f"    - {param_key}:")
                # 'param_value' will be an instance of 'Param' model
                print(
                    f"      Type: {param_value.type}, Default: {param_value.default}, Description: {param_value.description}"
                )
        else:
            print("  No parameters (params) defined for this DAG.")

        print("\nFull DAG details (as dictionary):")
        pprint(dag_details.to_dict())

    except Exception as e:
        print(f"Error getting details for DAG '{target_dag_id}': {e}")
        print(
            "Please ensure the DAG ID is correct and it exists in your Airflow instance."
        )
