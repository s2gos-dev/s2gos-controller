from abc import abstractmethod, ABC
from typing import Literal, Any, overload

from s2gos_common.models import ProcessDescription
from s2gos_common.process import ExecutionRequest


# noinspection PyShadowingBuiltins
class AsyncClientMixin(ABC):
    """
    Extra methods for the API client (synchronous mode).
    """

    @abstractmethod
    async def get_process(self, process_id: str, **kwargs: Any) -> ProcessDescription:
        """Will be overridden by actual client class."""

    @overload
    async def create_execution_request_template(
        self,
        process_description: ProcessDescription,
        format: Literal["obj"] | None = None,
    ) -> ExecutionRequest: ...
    @overload
    async def create_execution_request_template(
        self,
        process_description: ProcessDescription,
        format: Literal["dict"],
    ) -> dict[str, Any]: ...
    @overload
    async def create_execution_request_template(
        self,
        process_description: ProcessDescription,
        format: Literal["yaml", "json"],
    ) -> str: ...
    async def create_execution_request_template(
        self,
        process_id: str,
        format: Literal["obj", "dict", "json", "yaml"] | None = None,
    ) -> ExecutionRequest | dict | str:
        """
        Create a template for an execution request
        generated from the process description of the
        given process identifier.

        Args:
            process_id: The process identifier
            format: The format of the returned value.

        Returns:
            The returned type and form depends on the `format` argument:
                - `"obj"` or `None`: type `ExecutionRequest` (the default),
                - `"dict"`: type `dict`, plain dictionary,
                - `"yaml"`: type `str` using YAML format,
                - `"json"`: type `str` using JSON format.

        Raises:
            ClientException: if an error occurs
        """
        process_description = await self.get_process(process_id)
        # noinspection PyTypeChecker
        return ExecutionRequest.from_process_description(
            process_description, format=format
        )
