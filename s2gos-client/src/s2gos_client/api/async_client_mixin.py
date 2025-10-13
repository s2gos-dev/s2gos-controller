from abc import abstractmethod, ABC
from typing import Literal, Any, overload


from s2gos_common.models import ProcessDescription
from s2gos_common.process import ExecutionRequest, get_execution_request_template


# noinspection PyShadowingBuiltins
class AsyncClientMixin(ABC):
    """
    Extra methods for the API client (synchronous mode).
    """

    @abstractmethod
    async def get_process(self, process_id: str, **kwargs: Any) -> ProcessDescription:
        """Will be overridden by the actual client class."""

    @overload
    async def get_execution_request_template(
        self,
        process_id: str,
    ) -> ExecutionRequest: ...
    @overload
    async def get_execution_request_template(
        self,
        process_id: str,
        *,
        mode: Literal["python"],
    ) -> ExecutionRequest: ...
    @overload
    async def get_execution_request_template(
        self,
        process_id: str,
        *,
        mode: Literal["json"],
        dotpath: bool = False,
    ) -> dict[str, Any]: ...
    async def get_execution_request_template(
        self,
        process_id: str,
        *,
        mode: Literal["python", "json"] | None = None,
        dotpath: bool = False,
    ) -> ExecutionRequest | dict | str:
        """
        Create a template for an execution request
        generated from the process description of the
        given process identifier.

        Args:
            process_id: The process identifier
            mode: The mode which determines the type of the return value,
            dotpath: Applies to `mode=="json"` only:
                Whether to create dot-separated input
                names for nested object values

        Returns:
            The returned type and form depends on the `format` argument:
                - `"python"` or `None`: type `ExecutionRequest` (the default),
                - `"json"`: type `dict`, a JSON-serializable dictionary.

        Raises:
            ClientException: if an error occurs
        """
        process_description = await self.get_process(process_id)
        return get_execution_request_template(
            process_description, mode=mode, dotpath=dotpath
        )
