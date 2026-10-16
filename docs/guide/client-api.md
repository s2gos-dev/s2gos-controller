# Python API

Use the Python API when you want to construct requests programmatically, integrate
jobs into an analysis, or work directly with returned datasets. This walkthrough
uses the [local test service](index.md#run-the-examples-locally). Its complete
source is [examples/guides/api.py](https://github.com/s2gos-dev/s2gos-controller/blob/main/examples/guides/api.py).
Importing the example does not connect or submit work.

## Create a client

Use the S2GOS factory functions so the client uses the S2GOS configuration
namespace and defaults. Import the request and status models used below:

```python
--8<-- "examples/guides/api.py:imports"
--8<-- "examples/guides/api.py:connect"
```

`connect()` explicitly selects the local server and disables authentication.
For hosted work, replace its body with `return create_client()` after configuring
your [S2GOS profile](../auth.md), or use
`create_client(config_path="s2gos-client.yaml")` for a separate profile.
Use `client.login()` when interactive authentication is needed. Creating the
client itself does not log in or submit a request.

## Discover the process contract

```python
--8<-- "examples/guides/api.py:inspect"
```

The process list is a catalogue. The individual description gives you input names,
types, defaults, required values, constraints, and output descriptions. Read it
before constructing requests, particularly for deployed scene-generation
processes whose parameters may change between versions.

The returned objects are Pydantic models. Their attributes are convenient in
Python; `model_dump_json(indent=2)` produces readable JSON for inspection.
`client.get_capabilities()` and `client.get_conformance()` provide service-level
metadata when you need to identify a deployment or inspect its OGC capabilities.

## Submit once and keep the ID

```python
--8<-- "examples/guides/api.py:submit"
```

Input values belong inside `ProcessRequest(inputs={...})`. They are not top-level
fields of the request. The process ID is supplied separately to
`execute_process`. For the prime-number example, `min_val=10` and `max_val=80`
request the primes in that range.

The returned `JobInfo.jobID` identifies this execution. Always retain that
server-generated value. A response with `accepted` or `running` means the job
still needs monitoring. Do not repeat the submission to refresh its status.

## Check status before requesting results

```python
--8<-- "examples/guides/api.py:results"
```

This helper checks once. Call it again with the same job ID later if the job is
still active. In an automated workflow, poll at an interval suitable for the
computation and set an overall waiting limit. A client-side timeout does not
cancel the server job.

For a successful prime-number job, the results contain a `return_value` output
with a list starting at `11` and ending at `79`. For a scene-generation job,
results may instead contain links to files or datasets. Retrieving result
metadata does not necessarily download the data; see [Working with results](results.md).

## Run the complete session

After defining the functions above, run this session:

```python
--8<-- "examples/guides/api.py:session"

job_id = main()
```

The `finally` block releases network resources even if discovery or submission
fails. Closing the client leaves submitted server jobs running. To revisit the
job, create a new client for the same service and pass the saved ID to
`inspect_results(client, job_id)`, then close that client too.

You can also run the maintained example directly from the repository root:

```bash
python -m examples.guides.api
```

Each invocation submits one new job. If you only want to check an existing job,
use the helper with its saved ID or the CLI's `get-job` command instead.

## Failures and cancellation

A transport or HTTP error raises `ClientError`. A process that fails after
submission is represented by a job with status `failed`; inspect its `message`.
For a controlled local failure, submit `sleep_a_while` with
`ProcessRequest(inputs={"duration": 2, "fail": True})`, retain the returned ID,
and check that job after a few seconds.

To dismiss a selected job, call `client.dismiss_job(job_id)`. Dismissal can cancel
work or remove access to a completed job's results, depending on the backend.
Use only the ID of the job you intend to dismiss. Avoid dismissal loops over all
jobs, especially on a shared service.

## Asynchronous clients and Airflow-backed services

`create_async_client()` uses the same S2GOS settings and provides asynchronous
server calls. Await operations such as `get_processes()`, `execute_process()`,
`get_job()`, and `close()`. This is useful when your application already has an
event loop; it does not change the server job lifecycle. The synchronous client
also submits jobs for asynchronous execution on the service.

An Airflow-backed deployment exposes the same OGC interface through the S2GOS
gateway. Connect to the gateway's API URL, not the Airflow web UI, and discover
the processes it advertises. Your client does not need Airflow administrator
credentials. Operators configure the gateway's backend connection using the
[Server CLI](../server-cli.md). See the [Client API reference](../client-api.md)
for the full client interface.
