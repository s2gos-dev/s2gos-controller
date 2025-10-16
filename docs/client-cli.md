# Client CLI Reference

`s2gos-client` is the client shell tool for the S2GOS service.

The tool can be used to get the available processes, get process details,
execute processes, and manage the jobs originating from the latter. 
It herewith resembles the functionality of the OGC API Processes - Part 1.

You can use shorter command name aliases, e.g., use command name `vr`
for `validate-request`, or `lp` for `list-processes`.

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
* `list-processes`: List available processes.
* `get-process`: Get process details.
* `create-request`: Create an execution request (template) for...
* `validate-request`: Validate a process execution request.
* `execute-process`: Execute a process in asynchronous mode.
* `list-jobs`: List all jobs.
* `get-job`: Get job details.
* `dismiss-job`: Cancel a running or delete a finished job.
* `get-job-results`: Get job results.

## `s2gos-client configure`

Configure the client tool.

**Usage**:

```console
$ s2gos-client configure [OPTIONS]
```

**Options**:

* `-u, --user TEXT`: Your user name.
* `-t, --token TEXT`: Your personal access token.
* `-s, --server TEXT`: The S2GOS service API URL.
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
* `-r, --request PATH`: Execution request file. Use `-` to read from &lt;stdin&gt;.
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
* `-r, --request PATH`: Execution request file. Use `-` to read from &lt;stdin&gt;.
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
