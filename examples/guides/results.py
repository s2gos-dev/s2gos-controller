"""Submit a small local dataset example, or reopen it using a saved job ID."""

# --8<-- [start:imports]
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import url2pathname

import xarray as xr
from cuiman.api.opener import JobResultOpenContext, JobResultOpener
from gavicore.models import ProcessRequest

from s2gos_client import Client

from .api import connect, submit

# --8<-- [end:imports]


# --8<-- [start:submit]
def submit_scene(client: Client, request_path: Path) -> str:
    request = ProcessRequest.model_validate_json(
        request_path.read_text(encoding="utf-8")
    )
    return submit(client, "simulate_scene", request)


# --8<-- [end:submit]


# --8<-- [start:custom]
class LocalZarrOpener(JobResultOpener):
    """Convert local file URIs to native paths, including Windows drive letters."""

    async def accept_job_result(self, ctx: JobResultOpenContext) -> bool:
        link = ctx.output_link
        if link is None or ctx.data_type not in (None, xr.Dataset):
            return False
        url = urlsplit(link.href)
        return (
            ctx.output_media_type == "application/zarr"
            and url.scheme == "file"
            and url.netloc in ("", "localhost")
        )

    async def open_job_result(self, ctx: JobResultOpenContext) -> xr.Dataset:
        link = ctx.output_link
        assert link is not None
        path = url2pathname(urlsplit(link.href).path)
        return xr.open_zarr(path, **ctx.options)


# --8<-- [end:custom]


# --8<-- [start:registration]
def open_local_dataset(client: Client, job_id: str) -> xr.Dataset:
    unregister = client.config.register_job_result_opener(LocalZarrOpener)
    try:
        return client.open_job_result(
            job_id,
            output_name="return_value",
            data_type=xr.Dataset,
            poll_interval=1,
            timeout=60,
        )
    finally:
        unregister()


# --8<-- [end:registration]


# --8<-- [start:open]
def inspect_dataset(client: Client, job_id: str) -> None:
    dataset = open_local_dataset(client, job_id)
    try:
        print(dict(dataset.sizes))
        print(list(dataset.data_vars))
        print(dataset["a"].isel(time=0).mean().compute().item())
    finally:
        dataset.close()


# --8<-- [end:open]


def main(job_id: str | None = None) -> str:
    client = connect()
    try:
        if job_id is None:
            request_path = Path(__file__).with_name("simulate-scene-request.json")
            job_id = submit_scene(client, request_path)
        print(f"Keep this job ID: {job_id}")
        inspect_dataset(client, job_id)
        return job_id
    finally:
        client.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--job-id", help="Reopen an existing job instead of submitting."
    )
    main(parser.parse_args().job_id)
