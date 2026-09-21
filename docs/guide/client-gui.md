# App

The S2GOS App provides a graphical interface for discovering processes, editing
requests, submitting jobs, and inspecting their progress and results. It is
bundled with `s2gos-client` and runs in a browser or inside Jupyter. Start with the
[local test service](index.md#run-the-examples-locally) to learn the workflow.

## Open from a terminal

After creating `local-client.yaml` as described in Getting started:

```bash
--8<-- "examples/guides/cli.sh:app"
```

Keep the terminal open while using the App. Stop it with Ctrl+C when finished.
For hosted work, use your hosted profile instead and complete
[authentication](../auth.md) for that service. Check the selected service in the
App before submitting a request, especially when you switch between deployments.

## Open from Python or Jupyter

The following helper returns both the client and App handles so you can update
request forms and stop the local App server later:

```python
--8<-- "examples/guides/app.py:open"

client, app = open_app(display="browser")
```

In a notebook, use `open_app(display="notebook")` instead. The `height` setting
controls the embedded display height. Keep the notebook kernel or Python process
alive while using the App. For a standalone browser session, run
`python -m examples.guides.app`; it remains active until Ctrl+C.

For S2GOS, adapt the helper to use `create_client()` with your configured profile
or `create_client(config_path="s2gos-client.yaml")`. The client uses Cuiman's App
implementation; its appearance depends on the installed App build and any
`EOZILLA_APP_DIST` override. The process and job workflow is the same.

## Complete a first job

1. Open the process catalogue and select `primes_between` on the local service.
   Read its description and input constraints.
2. In its request form, set `min_val` to `10` and `max_val` to `80`. Review the
   values before executing the request.
3. Click the **Execute process** arrow once. Record the job ID shown for that execution.
4. In **JOBS**, select that job and inspect the **JOB** panel. Wait for `successful`; for a failure,
   read the message rather than immediately resubmitting.
5. Expand **RESULTS** if needed. The `return_value` contains the calculated primes.

The catalogue and forms come from the selected service's process descriptions.
A hosted S2GOS deployment may offer different processes and more complex inputs,
including paths, scene specifications, or output locations. Read their field
descriptions and use paths accessible to the processing service. A path on your
laptop is not automatically uploaded to a remote worker.

For longer jobs, you can return later using the same service and account. Closing
the App tab does not dismiss a submitted job. To continue analysis in Python,
copy the job ID and follow [Working with results](results.md).

## Update a request from Python

Open the local `sleep_a_while` process in the App first, then define and call:

```python
--8<-- "examples/guides/app.py:update"

set_duration(app, duration=2)
```

The helper reads the current form request, changes its duration, and writes it
back. Other inputs and output settings are preserved. This changes the draft
request; it does not submit a job or change the inputs of an existing job. Review
the updated form and execute it in the App when ready.

## Stop the App server

When you are done with a Python or notebook session:

```python
--8<-- "examples/guides/app.py:close"

close_app(client, app)
```

Closing a browser tab alone leaves the local App server running. Stop it before
repeatedly launching new instances from a notebook. This cleanup closes local
resources and does not cancel processing jobs.

If an embedded App does not display, try browser mode with the same configuration.
If the App opens but cannot list processes, verify the gateway URL and
authentication. For a notebook running on a remote machine, `127.0.0.1` refers
to that machine; the service must be reachable from the notebook environment.
