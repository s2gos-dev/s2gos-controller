# Command line

The CLI is useful for inspecting a service, keeping execution requests in files,
and integrating submissions into scripts. This walkthrough uses the
[local test service](index.md#run-the-examples-locally), an active `pixi shell`,
and the repository root as the working directory.

The commands are maintained in
[examples/guides/cli.sh](https://github.com/s2gos-dev/s2gos-controller/blob/main/examples/guides/cli.sh).
Copy individual recipes; running that file does not submit jobs. Commands shown
on a single line work in Bash and PowerShell.

## Configure and inspect the service

```bash
--8<-- "examples/guides/cli.sh:configure"
--8<-- "examples/guides/cli.sh:inspect"
```

The profile contains the API URL and authentication settings. `--config` belongs
to the individual command, after its name. For a hosted deployment, create and
log in to a separate profile as described in [Authentication](../auth.md).

Inspect the process description before submitting: it describes the valid input
names, types, defaults, and outputs. `s2gos-client --help` lists commands;
`s2gos-client execute-process --help` lists that command's options.

## Prepare a repeatable request

Generate a starting template from the service:

```bash
--8<-- "examples/guides/cli.sh:template"
```

Generated values are suggestions, and may need editing before the request is
valid for that process. Save your actual request as JSON or YAML. The supplied
`examples/guides/primes-request.json` contains:

```json
--8<-- "examples/guides/primes-request.json"
```

Keep request files with your analysis so the chosen inputs are recorded. See
[Execution requests](../execution-requests.md) for nested inputs, output settings,
and the distinction between CLI request files and Python `ProcessRequest` objects.

## Validate, then submit

```bash
--8<-- "examples/guides/cli.sh:validate"
```

`validate-request` works offline. It checks the execution-request structure and
parses inputs; it does **not** fetch the process schema, verify storage access, or
guarantee scientific validity. Compare inputs with `get-process` and review
service-side validation errors as well.

When the request is ready, submit it once:

```bash
--8<-- "examples/guides/cli.sh:submit"
```

Alternatively, for a small request you can supply inputs directly:

```bash
--8<-- "examples/guides/cli.sh:inputs"
```

These are alternative submissions: running both creates two jobs. Repeated `-i`
options set separate inputs. Values such as numbers, `true`, arrays, and objects
are parsed as JSON where possible. Use a request file for complex values to
avoid shell quoting problems. A process ID or input supplied on the command line
overrides the corresponding value in the file.

## Follow the returned job

The submission prints job information, including `jobID` and `status`. Copy that
ID and replace `YOUR_JOB_ID` in the remaining commands:

```bash
--8<-- "examples/guides/cli.sh:jobs"
```

For `accepted` or `running`, check the same job later. For `failed`, read its
message before retrying. When status is `successful`, retrieve the results:

```bash
--8<-- "examples/guides/cli.sh:results"
```

Prime-number results are inline values. Scene results may be links to storage;
this command displays the result metadata rather than downloading every linked
file. Use the [results guide](results.md) to open datasets in Python.

For machine-readable output, add `--format json` to discovery, submission, job,
and result commands. Save the returned `jobID` in your script. A zero exit code
from submission means the API call succeeded; it does not mean the job finished.

## Dismiss a selected job

Only when you intend to cancel or discard that job:

```bash
--8<-- "examples/guides/cli.sh:dismiss"
```

Backend dismissal policies vary, and results may become unavailable afterward.
Download or open what you need first. Do not dismiss every job in a shared
service as part of tutorial cleanup.

## Errors in scripts

The CLI normally returns `0` for success, `1` for input or configuration errors,
`2` for remote API errors, and `3` for network transport errors. Stop your script
when submission fails instead of trying to parse a job ID from an error message.
The global `--traceback` option provides diagnostic details and changes error
exit codes to `1`:

```bash
s2gos-client --traceback list-processes --config local-client.yaml
```

Consult the generated [CLI reference](../client-cli.md) for all commands and
options. Regenerate it after upgrading the underlying client implementation.
