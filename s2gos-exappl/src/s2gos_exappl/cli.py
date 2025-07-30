#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import json
from typing import Annotated, Optional

import click
import typer


cli = typer.Typer(add_completion=False)

# See also s2gos-client/src/s2gos_client/cli/cli.py
process_id_arg = typer.Argument(
    help="Process identifier.",
)

# See also s2gos-client/src/s2gos_client/cli/cli.py
request_input_option = typer.Option(
    "--input",
    "-i",
    help="Process input value.",
    metavar="[NAME=VALUE]...",
)

# See also s2gos-client/src/s2gos_client/cli/cli.py
request_subscriber_option = typer.Option(
    "--subscriber",
    "-s",
    help="Process subscriber URL.",
    metavar="[NAME=URL]...",
)

# See also s2gos-client/src/s2gos_client/cli/cli.py
request_file_option = typer.Option(
    ...,
    "--request",
    "-r",
    help="Processing request file. Use `-` to read from <stdin>.",
    metavar="PATH",
)


@cli.command("execute-process")
def execute_process(
    process_id: Annotated[Optional[str], process_id_arg] = None,
    request_inputs: Annotated[Optional[list[str]], request_input_option] = None,
    request_subscribers: Annotated[
        Optional[list[str]], request_subscriber_option
    ] = None,
    request_file: Annotated[Optional[str], request_file_option] = None,
):
    """
    Execute a process.

    The processing request to be submitted may be read from a file given
    by `--request`, or from `stdin`, or from the `process_id` argument
    with zero, one, or more `--input` (or `-i`) options.

    The `process_id` argument and any given `--input` options will override
    settings with same name found in the given request file or `stdin`, if any.
    """
    from s2gos_common.cli.request import read_processing_request
    from s2gos_common.process import Job
    from s2gos_exappl.processors import registry

    processing_request = read_processing_request(
        process_id=process_id,
        request_inputs=request_inputs,
        request_subscribers=request_subscribers,
        request_file=request_file,
    )

    process_id_ = processing_request.process_id
    process = registry.get(process_id_)
    if process is None:
        raise click.ClickException(f"Process {process_id_!r} not found.")

    job = Job.create(process, process_request=processing_request)
    job_results = job.run()
    if job_results is not None:
        typer.echo(job_results.model_dump_json(indent=2))
    else:
        typer.echo(job.job_info.model_dump_json(indent=2))


@cli.command("list-processes", help="List all processes.")
def list_processes():
    from s2gos_exappl.processors import registry

    typer.echo(
        json.dumps(
            {
                k: v.description.model_dump(
                    mode="json",
                    by_alias=True,
                    exclude_none=True,
                    exclude_defaults=True,
                    exclude_unset=True,
                    exclude=["inputs", "outputs"],
                )
                for k, v in registry.items()
            },
            indent=2,
        )
    )


@cli.command("get-process", help="Get details of a process.")
def get_process(
    process_id: Annotated[str, typer.Argument(help="The process identifier")],
):
    import json
    from s2gos_exappl.processors import registry

    process = registry.get(process_id)
    if process is None:
        raise click.ClickException(f"Process {process_id!r} not found.")

    typer.echo(
        json.dumps(
            process.description.model_dump(
                mode="json",
                by_alias=True,
                exclude_defaults=True,
                exclude_none=True,
                exclude_unset=True,
            ),
            indent=2,
        )
    )
