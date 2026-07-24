# S2GOS Client CLI

Interact with the ESA DTE S2GOS processing service.

`s2gos-client` can be used to get the available processes, get process 
details, execute processes, and manage the jobs originating from the latter. It 
herewith resembles the core functionality of the OGC API - Processes, Part 1.
For details see https://ogcapi.ogc.org/processes/.

You can use shorter command name aliases, e.g., use command name `vr`
for `validate-request`, or `lp` for `list-processes`.

The tool's exit codes are as follows:

* `0` - normal exit
* `1` - user errors, argument errors
* `2` - remote API errors 
* `3` - local network transport errors

If the `--traceback` flag is set, the original Python exception traceback
will be shown and the exit code will always be `1`. 
Otherwise, only the error message is shown. 

**Usage**:

```console
$ s2gos-client [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version`: Show version and exit.
* `--traceback, --tb`: Show server exception traceback, if any.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `configure`: Configure the client tool.
* `generate-client`: Generate the Python code for...
* `list-processes`: List available processes.
* `get-process`: Get process details.
* `create-request`: Create an execution request (template) for...
* `validate-request`: Validate a process execution request.
* `execute-process`: Execute a process in asynchronous mode.
* `list-jobs`: List all jobs.
* `get-job`: Get job details.
* `dismiss-job`: Cancel a running or delete a finished job.
* `get-job-results`: Get job results.
* `show-app`: Show the client app in a browser.

## `s2gos-client configure`

Configure the client tool.

**Usage**:

```console
$ s2gos-client configure [OPTIONS]
```

**Options**:

* `--api-url TEXT`: The URL of a service complying to the OGC API - Processes.
* `-a, --auth-type TEXT`: The authorisation method for the API (none|basic|token|login|api-key).
* `--auth-url TEXT`: The URL of the authorisation service for the API 
* `-u, --username TEXT`: Username.
* `-p, --password TEXT`: Password.
* `--client-id TEXT`: OAuth2 client ID for login authentication.
* `--client-secret TEXT`: OAuth2 client secret for login authentication.
* `-t, --token TEXT`: Access token.
* `--use-bearer`: Use bearer token?
* `--token-header TEXT`: Access token header
* `-c, --config PATH`: Client configuration file.
* `--help`: Show this message and exit.

## `s2gos-client generate-client`

Generate the Python code for service-specific, higher-level client functions.

The command generates classes for both sync and async clients, which
have methods that directly represent the processes of the currently configured
processing service.

**Usage**:

```console
$ s2gos-client generate-client [OPTIONS] NAME
```

**Arguments**:

* `NAME`: Service name used for generated module and class names.  [required]

**Options**:

* `-o, --output-dir TEXT`: Directory where generated modules will be written.  [default: .]
* `-c, --config PATH`: Client configuration file.
* `--help`: Show this message and exit.

## `s2gos-client list-processes`

List available processes.

**Usage**:

```console
$ s2gos-client list-processes [OPTIONS]
```

**Options**:

* `-c, --config PATH`: Client configuration file.
* `-f, --format [simple|json|yaml]`: Output format.  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client get-process`

Get process details.

**Usage**:

```console
$ s2gos-client get-process [OPTIONS] PROCESS_ID
```

**Arguments**:

* `PROCESS_ID`: Process identifier.  [required]

**Options**:

* `-c, --config PATH`: Client configuration file.
* `-f, --format [simple|json|yaml]`: Output format.  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client create-request`

Create an execution request (template) for a given process.

The generated template comprises generated default values for all inputs.
Note that they might not necessarily be valid.
The generated template request may serve as a starting point for the actual,
valid execution request.

**Usage**:

```console
$ s2gos-client create-request [OPTIONS] [PROCESS_ID]
```

**Arguments**:

* `[PROCESS_ID]`: Process identifier.

**Options**:

* `-d, --dotpath`: Input names use dot-path notion to encode nested values, e.g., `-i scene.colors.bg=red`.
* `-c, --config PATH`: Client configuration file.
* `-f, --format [simple|json|yaml]`: Output format.  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client validate-request`

Validate a process execution request.

The execution request to be validated may be read from a file given
by `--request`, or from `stdin`, or from the `process_id` argument
with zero, one, or more `--input` (or `-i`) options.

The `process_id` argument and any given `--input` options will override
settings with the same name found in the given request file or `stdin`, if any.

**Usage**:

```console
$ s2gos-client validate-request [OPTIONS] [PROCESS_ID]
```

**Arguments**:

* `[PROCESS_ID]`: Process identifier.

**Options**:

* `-d, --dotpath`: Input names use dot-path notion to encode nested values, e.g., `-i scene.colors.bg=red`.
* `-i, --input [NAME=VALUE]...`: Process input value.
* `-r, --request PATH`: Execution request file. Use `-` to read from <stdin>.
* `-f, --format [simple|json|yaml]`: Output format.  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client execute-process`

Execute a process in asynchronous mode.

The execution request to be submitted may be read from a file given
by `--request`, or from `stdin`, or from the `process_id` argument
with zero, one, or more `--input` (or `-i`) options.

The `process_id` argument and any given `--input` options will override
settings with same name found in the given request file or `stdin`, if any.

**Usage**:

```console
$ s2gos-client execute-process [OPTIONS] [PROCESS_ID]
```

**Arguments**:

* `[PROCESS_ID]`: Process identifier.

**Options**:

* `-d, --dotpath`: Input names use dot-path notion to encode nested values, e.g., `-i scene.colors.bg=red`.
* `-i, --input [NAME=VALUE]...`: Process input value.
* `-s, --subscriber [NAME=URL]...`: Process subscriber URL.
* `-r, --request PATH`: Execution request file. Use `-` to read from <stdin>.
* `-c, --config PATH`: Client configuration file.
* `-f, --format [simple|json|yaml]`: Output format.  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client list-jobs`

List all jobs.

**Usage**:

```console
$ s2gos-client list-jobs [OPTIONS]
```

**Options**:

* `-c, --config PATH`: Client configuration file.
* `-f, --format [simple|json|yaml]`: Output format.  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client get-job`

Get job details.

**Usage**:

```console
$ s2gos-client get-job [OPTIONS] JOB_ID
```

**Arguments**:

* `JOB_ID`: Job identifier.  [required]

**Options**:

* `-c, --config PATH`: Client configuration file.
* `-f, --format [simple|json|yaml]`: Output format.  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client dismiss-job`

Cancel a running or delete a finished job.

**Usage**:

```console
$ s2gos-client dismiss-job [OPTIONS] JOB_ID
```

**Arguments**:

* `JOB_ID`: Job identifier.  [required]

**Options**:

* `-c, --config PATH`: Client configuration file.
* `-f, --format [simple|json|yaml]`: Output format.  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client get-job-results`

Get job results.

**Usage**:

```console
$ s2gos-client get-job-results [OPTIONS] JOB_ID
```

**Arguments**:

* `JOB_ID`: Job identifier.  [required]

**Options**:

* `-c, --config PATH`: Client configuration file.
* `-f, --format [simple|json|yaml]`: Output format.  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client show-app`

Show the client app in a browser.

**Usage**:

```console
$ s2gos-client show-app [OPTIONS]
```

**Options**:

* `-c, --config PATH`: Client configuration file.
* `-d, --debug`: Output debugging information to the browser's dev console.
* `--help`: Show this message and exit.
