#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Optional, get_args, get_origin, Literal

import pydantic

from s2gos_common.models import (
    InputDescription,
    OutputDescription,
    ProcessDescription,
)

from .schema import create_json_schema, create_schema_instance


@dataclass
class Process:
    """
    A process comprises a process description and executable code
    in form of a Python function.

    Instances of this class are be managed by the
    [ProcessRegistry][s2gos_common.process.ProcessRegistry].

    Attributes:
        function: The user's Python function.
        signature: The signature of `function`.
        job_ctx_arg: Names of `function` arguments of type `JobContext`.
        model_class: Pydantic model class for the arguments of `function`.
        description: Process description modelled after
            [OGC API - Processes - Part 1: Core](https://docs.ogc.org/is/18-062r2/18-062r2.html#toc37).
    """

    function: Callable
    signature: inspect.Signature
    model_class: type[pydantic.BaseModel]
    description: ProcessDescription
    # names of special arguments
    input_arg: str | None
    job_ctx_arg: str | None

    # noinspection PyShadowingBuiltins
    @classmethod
    def create(
        cls,
        function: Callable,
        id: Optional[str] = None,
        version: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        input_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
        output_fields: Optional[dict[str, pydantic.fields.FieldInfo]] = None,
        input_arg: bool | str = False,
    ) -> "Process":
        """Create a new instance of this dataclass.

        Called by the `ProcessRegistry.process()` decorator function.
        Not intended to be used by clients.
        """
        if not inspect.isfunction(function):
            raise TypeError("function argument must be callable")
        fn_name = f"{function.__module__}:{function.__qualname__}"
        id = id or fn_name
        version = version or "0.0.0"
        description = description or inspect.getdoc(function)
        signature = inspect.signature(function)
        inputs, model_class, input_arg, job_ctx_arg = _parse_inputs(
            fn_name, signature, input_fields, input_arg
        )
        outputs = _parse_outputs(fn_name, signature.return_annotation, output_fields)
        return Process(
            function=function,
            signature=signature,
            model_class=model_class,
            description=ProcessDescription(
                id=id,
                version=version,
                title=title,
                description=description,
                inputs=inputs,
                outputs=outputs,
                # Note, we may later add the following:
                # metadata=metadata,
                # keywords=keywords,
                # links=links,
                # outputTransmission=output_transmission,
                # jobControlOptions=job_control_options,
            ),
            input_arg=input_arg,
            job_ctx_arg=job_ctx_arg,
        )


def _parse_inputs(
    fn_name: str,
    signature: inspect.Signature,
    input_fields: Optional[dict[str, pydantic.fields.FieldInfo]] | None,
    input_arg: str | bool,
) -> tuple[
    dict[str, InputDescription], type[pydantic.BaseModel], str | None, str | None
]:
    from .job import JobContext

    model_class_name = "ProcessInputs"

    arg_parameters: dict[str, inspect.Parameter] = {}
    job_ctx_arg: str | None = None
    for param_name, parameter in signature.parameters.items():
        if parameter.annotation is JobContext:
            if job_ctx_arg:
                raise ValueError(
                    f"function {fn_name!r}: only one parameter can have type "
                    f"{JobContext.__name__}, but found {job_ctx_arg!r} "
                    f"and {param_name!r}"
                )
            job_ctx_arg = param_name
        else:
            arg_parameters[param_name] = parameter

    model_class: type[pydantic.BaseModel]
    input_arg_: str | None = None
    if input_arg:
        model_class, input_arg_ = _parse_input_arg(fn_name, arg_parameters, input_arg)
    else:
        model_field_definitions = {
            param_name: (
                (parameter.annotation, parameter.default)
                if parameter.default is not inspect.Parameter.empty
                else parameter.annotation
            )
            for param_name, parameter in arg_parameters.items()
        }
        model_class = pydantic.create_model(model_class_name, **model_field_definitions)

    if input_fields:
        invalid_inputs = [
            input_name
            for input_name in input_fields
            if input_name not in signature.parameters
        ]
        if invalid_inputs:
            raise ValueError(
                f"function {fn_name!r}: "
                "all input names must have corresponding parameter names; "
                f"invalid input name(s): {', '.join(map(repr, invalid_inputs))}"
            )
        # noinspection PyTypeChecker
        model_field_definitions = dict(model_class.model_fields)
        for input_name, field_info in input_fields.items():
            if input_name in model_field_definitions:
                old_field_info = model_field_definitions[input_name]
                parameter = signature.parameters[input_name]
                model_field_definitions[input_name] = (
                    parameter.annotation,
                    pydantic.fields.FieldInfo.merge_field_infos(
                        old_field_info, field_info
                    ),
                )
        model_class = pydantic.create_model(model_class_name, **model_field_definitions)

    model_class.model_rebuild()

    inputs_schema = create_json_schema(model_class)
    input_descriptions = {
        input_name: InputDescription(
            minOccurs=1 if input_name in inputs_schema.get("required", []) else 0,
            maxOccurs=None,
            title=schema.pop("title", None),
            description=schema.pop("description", None),
            schema=create_schema_instance(input_name, schema),
        )
        for input_name, schema in inputs_schema.get("properties", {}).items()
    }

    return input_descriptions, model_class, input_arg_, job_ctx_arg


def _parse_input_arg(
    fn_name: str,
    arg_parameters: dict[str, inspect.Parameter],
    input_arg: str | Literal[True],
) -> tuple[type[pydantic.BaseModel], str]:
    if len(arg_parameters) > 1:
        raise ValueError(
            f"function {fn_name!r}: the input argument must be the only "
            f"argument (input_arg={input_arg!r})"
        )

    arg_param: inspect.Parameter | None
    if isinstance(input_arg, str):
        arg_param = arg_parameters.get(input_arg)
    else:
        arg_param = (
            list(arg_parameters.values())[0] if len(arg_parameters) == 1 else None
        )

    if arg_param is None:
        raise ValueError(
            f"function {fn_name!r}: specified input argument "
            f"is not an argument of the function (input_arg={input_arg!r})"
        )

    model_class = arg_param.annotation
    # noinspection PyTypeChecker
    if isinstance(model_class, type) and issubclass(model_class, pydantic.BaseModel):
        return model_class, arg_param.name
    else:
        raise TypeError(
            f"function {fn_name!r}: type of argument parameter {arg_param.name!r} "
            f"must be a subclass of pydantic.BaseModel"
        )


def _parse_outputs(
    fn_name: str,
    annotation: type,
    output_fields: Optional[dict[str, pydantic.fields.FieldInfo]] | None,
) -> dict[str, OutputDescription]:
    model_field_definitions: dict[str, Any] = {}
    if not output_fields:
        model_field_definitions = {"return_value": annotation}
    elif len(output_fields) == 1:
        output_name, field_info = next(iter(output_fields.items()))
        model_field_definitions = {output_name: (annotation, field_info)}
    else:
        origin = get_origin(annotation)
        args = get_args(annotation)
        if not (origin is tuple and args):
            raise TypeError(
                f"function {fn_name!r}: return type must be tuple[] with arguments"
            )
        if len(args) != len(output_fields):
            raise ValueError(
                f"function {fn_name!r}: number of outputs must match number "
                f"of tuple[] arguments"
            )
        for arg_type, (output_name, field_info) in zip(args, output_fields.items()):
            model_field_definitions[output_name] = (arg_type, field_info)
    model_class = pydantic.create_model("Outputs", **model_field_definitions)
    outputs_schema = create_json_schema(model_class)
    output_descriptions = {}
    for output_name, schema in outputs_schema.get("properties", {}).items():
        output_descriptions[output_name] = OutputDescription(
            title=schema.pop("title", None),
            description=schema.pop("description", None),
            schema=create_schema_instance(output_name, schema),
        )
    return output_descriptions
