# Working with results

Job results describe what a process produced. Some outputs are inline JSON
values; others are links to data. `get_job_results(job_id)` retrieves this
description. `open_job_result(job_id, ...)` selects a reader and opens an output,
for example as an `xarray.Dataset`.

## Generate a small dataset locally

Start the [local test service](index.md#run-the-examples-locally). The supplied
request for `simulate_scene` contains:

```json
--8<-- "examples/guides/simulate-scene-request.json"
```

The bounding box is `[west, south, east, north]` in degrees. With a resolution of
`0.5`, this two-degree box gives four latitude and four longitude cells. The date
interval produces two time slices; the variables `a` and `b` contain zeros. These
small dimensions make it easy to verify the complete data-access workflow.

The service writes `guide-scene.zarr` relative to **its own working directory**.
This example assumes server and client run on the same machine and can access
that path. Repeating it overwrites that example dataset. Choose a different
`output_path` to keep separate outputs.

Run the maintained example from the repository root:

```bash
python -m examples.guides.results
```

It submits one job, prints the job ID, waits up to 60 seconds for its output,
opens the dataset, prints a short summary, and closes both dataset and client.
Expected dimensions are `time: 2`, `lat: 4`, `lon: 4`, the variables are `a` and
`b`, and the first slice of `a` has mean `0.0`.

If waiting times out, the job can still be running. Check its status, then reopen
the **same** job without another submission:

```bash
python -m examples.guides.results --job-id YOUR_JOB_ID
```

## Open a selected output

The local dataset example uses `open_local_dataset`, defined below, to open the
output, then inspects and closes it:

```python
--8<-- "examples/guides/results.py:open"
```

`output_name` is a key in the returned results, not a filename. The local test
process uses `return_value`; a deployed process may use names such as `dataset`
or `image`. Inspect `get_job_results(job_id)` before choosing a name.
`data_type=xr.Dataset` constrains the reader to produce a dataset. The link's media
type helps select a reader; it does not turn an arbitrary file into a dataset.

Xarray may load data lazily. Inspecting dimensions and variable names is cheap;
calling `.compute()` reads the selected data. Start with a small spatial or time
subset for large scientific outputs, and close the dataset when finished.

## Handle local file URLs portably

Some reader versions interpret `file:///C:/...` as a path with a leading slash
on Windows. The local example includes a small custom opener that converts the
URI to a native path before calling Xarray. It also handles URL-encoded spaces.
The opener accepts only local Zarr links and the requested dataset type, leaving
other outputs to the built-in readers.

```python
from urllib.parse import urlsplit
from urllib.request import url2pathname

import xarray as xr
from cuiman.api.opener import JobResultOpenContext, JobResultOpener
from s2gos_client import Client

--8<-- "examples/guides/results.py:custom"
--8<-- "examples/guides/results.py:registration"
```

Registration temporarily gives this opener priority in the S2GOS configuration's
registry. The returned callback removes the registration even when opening fails.
Keep the registration around the open operation; the returned dataset remains
usable afterward and must still be closed. For hosted storage, use the built-in
readers as shown next rather than this local-filesystem example.

## Access data from a hosted service

There are two connections to consider: the client authenticates to the processing
API to get job metadata, then a result reader accesses the output's storage.
Your S2GOS API login does not automatically grant access to an S3 bucket or another
storage endpoint.

For an output that requires storage settings, obtain the supported settings from
the service operator and pass them as `storage_options` to `open_job_result`.
For example, in an existing client session, after setting `job_id`, `output_name`,
and `storage_options` for that output:

```python
dataset = client.open_job_result(
    job_id,
    output_name=output_name,
    data_type=xr.Dataset,
    storage_options=storage_options,
    timeout=300,
)
try:
    print(dataset.sizes)
finally:
    dataset.close()
```

The settings are specific to the storage backend: endpoint URL, anonymous access,
or credentials may be needed. Keep secrets outside request files committed to
version control. A `file://` URL points to a filesystem path; a path on a remote
worker is not directly readable from your laptop. Ask for an accessible storage
URL or use the deployment's supported download mechanism.

## Diagnose result-access failures

| Symptom | Likely next step |
| --- | --- |
| Job is still `accepted` or `running` | Check it later using the same ID; increase the wait limit if appropriate. |
| Job is `failed` or `dismissed` | Inspect its status and message; waiting longer will not make it successful. |
| Requested output is missing | Inspect result keys and the process's output description. |
| Reader cannot handle the output | Check the media type, desired Python type, and installed reader dependencies. |
| Storage returns an authorization error | Check storage credentials separately from your S2GOS login. |
| A local file does not exist | Check the server's working directory and whether client and server share the filesystem. |

The client inherits its result readers from Cuiman. See the
[Cuiman result-opener guide](https://eo-tools.github.io/eozilla/cuiman/guides/openers/)
when you need to implement a reader for an additional output format.
