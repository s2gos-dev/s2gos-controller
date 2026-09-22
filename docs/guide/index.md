# Getting started

The S2GOS Controller connects your Python session, browser, or terminal to a
processing service. You select a **process** (a reusable operation), supply an
**execution request** (its inputs and optional output settings), and receive a
**job** (one execution with its own ID). After that job succeeds, you can retrieve
its results. A result can be an inline value or a link to data in storage.

The same service and jobs are accessible through all three interfaces. You can
submit a job in the App, inspect it from the CLI, and open its dataset in Python.
Use the same service configuration and user account when moving between them.

## Choose an interface

| You want to…                                         | Start here |
|------------------------------------------------------| --- |
| Explore processes and use a graphical user interface | [App](client-gui.md) |
| Repeat requests from a terminal or script            | [Command line](client-cli.md) |
| Integrate processing with a scientific workflow      | [Python API](client-api.md) |
| Read a job's dataset or troubleshoot storage access  | [Working with results](results.md) |

## Connect to S2GOS

To work with the remote S2GOS service, you need its API URL, access to the service,
and the authentication details supplied by its operator. Follow
[Configuration and authentication](../auth.md) to configure and log in. 

By default, the S2GOS client is configured to use a free tier demo service 
on [DestinE](https://platform.destine.eu/).

For a scene-generation workflow, carefully inspect its process description, 
prepare the required scene inputs and output locations, submit once, then monitor 
the returned job ID. Storage access may require additional credentials; see
[Working with results](results.md#access-data-from-a-hosted-service).

## Testing the client locally

!!! note

    This section will be rewritten to work with the 
    [`s2gos-mono`](https://github.com/s2gos-dev/s2gos-mono) 
    repo. 

Follow [Installation](../installation.md#using-github) to create the development
environment. Open two terminals in the repository root and run `pixi shell` in
each. The examples below assume that environment is active and commands run from
the repository root.

In the first terminal, start the test service:

```bash
--8<-- "examples/guides/cli.sh:server"
```

Leave this terminal running. By default, the gateway listens at
`http://127.0.0.1:8008`. This service needs no S2GOS account and includes small
demonstration processes: `primes_between`, `sleep_a_while`, and `simulate_scene`.
The simulated scene is a small dataset of zeros for testing data access; it does
not run the scientific S2GOS scene generator.

In the second terminal, create a separate local client profile:

```bash
--8<-- "examples/guides/cli.sh:configure"
--8<-- "examples/guides/cli.sh:inspect"
```

The list should include `primes_between`; its description tells you the accepted
inputs and outputs. `local-client.yaml` holds this tutorial's settings. Pass it
with `--config` on commands that connect to the server. This keeps your default
S2GOS profile available for hosted work. The Python examples select the local URL
and no authentication explicitly.

For a complete first submission, run:

```bash
python -m examples.guides.api
```

The script submits one prime-number calculation, prints the returned job ID,
checks its status once, and closes the client. Follow the
[Python walkthrough](client-api.md) to understand each step or the
[CLI walkthrough](client-cli.md) to perform it from the terminal.

## Understand the job lifecycle

| Status | Meaning | Next step |
| --- | --- | --- |
| `accepted` | The service has accepted the request. | Retain the job ID and check again later. |
| `running` | Processing is in progress. | Check progress and messages, if provided. |
| `successful` | Processing finished successfully. | Retrieve results, then open the outputs you need. |
| `failed` | Processing ended with an error. | Read the job message and correct the cause before resubmitting. |
| `dismissed` | The job was dismissed. | Do not expect results to remain available. |

A successful submission is not the same as a successful computation. Calling
`execute_process` again creates another job; use `get_job` to check an existing
one. Keep the job ID, the service URL, and a copy of the submitted request with
your experiment so you can return to it later.

## Common first-run problems

| Symptom | Check |
| --- | --- |
| `s2gos-client` or `s2gos-server` is not found | Activate the environment with `pixi shell`. |
| Connection refused | Keep the server terminal open and check the URL and port. |
| Local examples ask for login | Select `auth_type: none`; changing only the URL retains S2GOS authentication defaults. |
| A command reports that the client is not configured | Create a profile and pass the same `--config` path on subsequent commands. |
| A process or job is not found | Check the service URL, account, and ID. A job ID belongs to the service that created it. |
| Old job IDs stop working after restarting the test server | The local test service is for experimentation; do not rely on it for durable job history. |

We also provide example [notebooks](https://github.com/s2gos-dev/s2gos-controller/tree/main/notebooks) 
available for exploration. 