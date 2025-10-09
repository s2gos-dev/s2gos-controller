from abc import abstractmethod, ABC
from typing import Literal, Any, overload


from s2gos_common.models import ProcessDescription
from s2gos_common.process import ExecutionRequest
from s2gos_common.util.obj import flatten_obj


# noinspection PyShadowingBuiltins
class ClientMixin(ABC):
    """
    Extra methods for the API client (synchronous mode).
    """

    @abstractmethod
    def get_process(self, process_id: str, **kwargs: Any) -> ProcessDescription:
        """Will be overridden by actual client class."""

    @overload
    def get_execution_request_template(
        self,
        process_id: str,
    ) -> ExecutionRequest: ...
    @overload
    def get_execution_request_template(
        self,
        process_id: str,
        *,
        mode: Literal["python"],
    ) -> ExecutionRequest: ...
    @overload
    def get_execution_request_template(
        self,
        process_id: str,
        *,
        mode: Literal["json"],
        dotpath: bool = False,
    ) -> dict[str, Any]: ...
    def get_execution_request_template(
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
        process_description = self.get_process(process_id)
        request = ExecutionRequest.from_process_description(
            process_description, dotpath=dotpath
        )
        if mode is None or mode == "python":
            return request
        elif mode == "json":
            request_dict = request.model_dump(mode="json", exclude_unset=True)
            if request.dotpath:
                return flatten_obj(request_dict)
            return request_dict
        else:
            raise ValueError(f"unsupported mode {mode!r}")
