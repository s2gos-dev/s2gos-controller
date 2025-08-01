# generated by gen_client.py:
#   filename:  client.py:
#   timestamp: 2025-07-25T15:55:10.509531


from typing import Any, Optional

from s2gos_common.models import (
    ApiError,
    Capabilities,
    ConformanceDeclaration,
    JobInfo,
    JobList,
    JobResults,
    ProcessDescription,
    ProcessList,
    ProcessRequest,
)

from .config import ClientConfig
from .ishell import has_ishell as _  # noqa F401
from .transport import Transport, TransportArgs
from .transport.httpx import HttpxTransport


class Client:
    """
    The client API for the web service (synchronous mode).

    Args:
      config: Optional client configuration object. If given,
        other configuration arguments are ignored.
      config_path: Optional path of the configuration file to be loaded
      server_url: Optional server URL
      user_name: Optional username
      access_token: Optional private access token
    """

    def __init__(
        self,
        *,
        config: Optional[ClientConfig] = None,
        config_path: Optional[str] = None,
        server_url: Optional[str] = None,
        user_name: Optional[str] = None,
        access_token: Optional[str] = None,
        _debug: bool = False,
        _transport: Optional[Transport] = None,
    ):
        self._config = ClientConfig.create(
            config=config,
            config_path=config_path,
            server_url=server_url,
            user_name=user_name,
            access_token=access_token,
        )
        assert self._config.server_url is not None
        self._transport = (
            HttpxTransport(
                server_url=self._config.server_url,
                debug=_debug,
            )
            if _transport is None
            else _transport
        )

    @property
    def config(self) -> ClientConfig:
        return self._config

    def _repr_json_(self):
        # noinspection PyProtectedMember
        return self._config._repr_json_()

    def get_capabilities(self, **kwargs: Any) -> Capabilities:
        """
        The landing page provides links to the:
          * The OpenAPI-definition (no fixed path),
          * The Conformance statements (path /conformance),
          * The processes metadata (path /processes),
          * The endpoint for job monitoring (path /jobs).

        For more information, see [Section
        7.2](https://docs.ogc.org/is/18-062/18-062.html#sc_landing_page).

        Returns:
          Capabilities: The landing page provides links to the API definition
            (link relations `service-desc` and `service-doc`),
            the Conformance declaration (path `/conformance`,
            link relation `http://www.opengis.net/def/rel/ogc/1.0/conformance`),
        and to other resources.

        Raises:
          ClientError: if the call to the web service fails
            with a status code != `2xx`.
            - `500`: A server error occurred.
        """
        return self._transport.call(
            TransportArgs(
                path="/",
                method="get",
                return_types={"200": Capabilities},
                error_types={"500": ApiError},
                extra_kwargs=kwargs,
            )
        )

    def get_conformance(self, **kwargs: Any) -> ConformanceDeclaration:
        """
        A list of all conformance classes, specified in a standard, that the
        server conforms to.

        | Conformance class | URI |
        |-----------|-------|
        |Core|http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/core|
        |OGC Process Description|http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/ogc-process-description|
        |JSON|http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/json|
        |HTML|http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/html|
        |OpenAPI Specification 3.0|http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/oas30|
        |Job list|http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/job-list|
        |Callback|http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/callback|
        |Dismiss|http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/dismiss|

        For more information, see [Section
        7.4](https://docs.ogc.org/is/18-062/18-062.html#sc_conformance_classes).


        Returns:
          ConformanceDeclaration: The URIs of all conformance classes supported
        by the server.
            To support "generic" clients that want to access multiple
            OGC API - Processes implementations - and not "just" a specific
            API / server, the server declares the conformance
            classes it implements and conforms to.

        Raises:
          ClientError: if the call to the web service fails
            with a status code != `2xx`.
            - `500`: A server error occurred.
        """
        return self._transport.call(
            TransportArgs(
                path="/conformance",
                method="get",
                return_types={"200": ConformanceDeclaration},
                error_types={"500": ApiError},
                extra_kwargs=kwargs,
            )
        )

    def get_processes(self, **kwargs: Any) -> ProcessList:
        """
        The list of processes contains a summary of each process the OGC API -
        Processes offers, including the link to a more detailed description of
        the process.

        For more information, see [Section
        7.9](https://docs.ogc.org/is/18-062/18-062.html#sc_process_list).


        Returns:
          ProcessList: Information about the available processes

        Raises:
          ClientError: if the call to the web service fails
            with a status code != `2xx`.
        """
        return self._transport.call(
            TransportArgs(
                path="/processes",
                method="get",
                return_types={"200": ProcessList},
                extra_kwargs=kwargs,
            )
        )

    def get_process(self, process_id: str, **kwargs: Any) -> ProcessDescription:
        """
        The process description contains information about inputs and outputs
        and a link to the execution-endpoint for the process. The Core does not
        mandate the use of a specific process description to specify the
        interface of a process. That said, the Core requirements class makes the
        following recommendation:

        Implementations SHOULD consider supporting the OGC process description.

        For more information, see [Section 7.10](https://docs.ogc.org/is/18-
        062/18-062.html#sc_process_description).

        Args:
          process_id:
          kwargs: Optional keyword arguments that may be
            used by the underlying transport.

        Returns:
          ProcessDescription: A process description.

        Raises:
          ClientError: if the call to the web service fails
            with a status code != `2xx`.
            - `404`: The requested URI was not found.
        """
        return self._transport.call(
            TransportArgs(
                path="/processes/{processID}",
                method="get",
                path_params={"processID": process_id},
                return_types={"200": ProcessDescription},
                error_types={"404": ApiError},
                extra_kwargs=kwargs,
            )
        )

    def execute_process(
        self, process_id: str, request: ProcessRequest, **kwargs: Any
    ) -> JobInfo:
        """
        Create a new job.

        For more information, see [Section
        7.11](https://docs.ogc.org/is/18-062/18-062.html#sc_create_job).

        Args:
          process_id:
          kwargs: Optional keyword arguments that may be
            used by the underlying transport.
          request: Mandatory request JSON

        Returns:
          JobInfo: Started asynchronous execution. Created job.

        Raises:
          ClientError: if the call to the web service fails
            with a status code != `2xx`.
            - `404`: The requested URI was not found.
            - `500`: A server error occurred.
        """
        return self._transport.call(
            TransportArgs(
                path="/processes/{processID}/execution",
                method="post",
                path_params={"processID": process_id},
                request=request,
                return_types={"201": JobInfo},
                error_types={"404": ApiError, "500": ApiError},
                extra_kwargs=kwargs,
            )
        )

    def get_jobs(self, **kwargs: Any) -> JobList:
        """
        Lists available jobs.

        For more information, see [Section
        11](https://docs.ogc.org/is/18-062/18-062.html#sc_job_list).


        Returns:
          JobList: A list of jobs for this process.

        Raises:
          ClientError: if the call to the web service fails
            with a status code != `2xx`.
            - `404`: The requested URI was not found.
        """
        return self._transport.call(
            TransportArgs(
                path="/jobs",
                method="get",
                return_types={"200": JobList},
                error_types={"404": ApiError},
                extra_kwargs=kwargs,
            )
        )

    def get_job(self, job_id: str, **kwargs: Any) -> JobInfo:
        """
        Shows the status of a job.

        For more information, see [Section 7.12](https://docs.ogc.org/is/18-
        062/18-062.html#sc_retrieve_status_info).

        Args:
          job_id: local identifier of a job
          kwargs: Optional keyword arguments that may be
            used by the underlying transport.

        Returns:
          JobInfo: The status of a job.

        Raises:
          ClientError: if the call to the web service fails
            with a status code != `2xx`.
            - `404`: The requested URI was not found.
            - `500`: A server error occurred.
        """
        return self._transport.call(
            TransportArgs(
                path="/jobs/{jobId}",
                method="get",
                path_params={"jobId": job_id},
                return_types={"200": JobInfo},
                error_types={"404": ApiError, "500": ApiError},
                extra_kwargs=kwargs,
            )
        )

    def dismiss_job(self, job_id: str, **kwargs: Any) -> JobInfo:
        """
        Cancel a job execution and remove it from the jobs list.

        For more information, see [Section
        13](https://docs.ogc.org/is/18-062/18-062.html#Dismiss).

        Args:
          job_id: local identifier of a job
          kwargs: Optional keyword arguments that may be
            used by the underlying transport.

        Returns:
          JobInfo: Information about the job.

        Raises:
          ClientError: if the call to the web service fails
            with a status code != `2xx`.
            - `404`: The requested URI was not found.
            - `500`: A server error occurred.
        """
        return self._transport.call(
            TransportArgs(
                path="/jobs/{jobId}",
                method="delete",
                path_params={"jobId": job_id},
                return_types={"200": JobInfo},
                error_types={"404": ApiError, "500": ApiError},
                extra_kwargs=kwargs,
            )
        )

    def get_job_results(self, job_id: str, **kwargs: Any) -> JobResults:
        """
        Lists available results of a job. In case of a failure, lists errors
        instead.

        For more information, see [Section 7.13](https://docs.ogc.org/is/18-
        062/18-062.html#sc_retrieve_job_results).

        Args:
          job_id: local identifier of a job
          kwargs: Optional keyword arguments that may be
            used by the underlying transport.

        Returns:
          JobResults: The results of a job.

        Raises:
          ClientError: if the call to the web service fails
            with a status code != `2xx`.
            - `404`: The requested URI was not found.
            - `500`: A server error occurred.
        """
        return self._transport.call(
            TransportArgs(
                path="/jobs/{jobId}/results",
                method="get",
                path_params={"jobId": job_id},
                return_types={"200": JobResults},
                error_types={"404": ApiError, "500": ApiError},
                extra_kwargs=kwargs,
            )
        )

    def close(self):
        """Closes this client."""
        if self._transport is not None:
            self._transport.close()
