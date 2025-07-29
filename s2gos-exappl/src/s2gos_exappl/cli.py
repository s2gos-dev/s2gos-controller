#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import json
from typing import Annotated, Optional

import typer

from s2gos_common.models import ProcessRequest

cli = typer.Typer(add_completion=False)


@cli.command("execute-process", help="Execute a process.")
def execute_process(
    process_id: Annotated[str, typer.Argument(help="The process identifier")],
    request_path: Annotated[
        Optional[str], typer.Option("--request", "-r", help="The process request file")
    ] = None,
):
    from s2gos_common.process import Job
    from s2gos_exappl.processors import registry

    process_request_dict = {}
    if request_path:
        with open(request_path, "rt") as fp:
            process_request_dict = json.load(fp)
    process = registry.get(process_id)
    job = Job.create(process, process_request=ProcessRequest(**process_request_dict))
    job_results = job.run()
    typer.echo(job_results.model_dump_json(indent=2))


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
