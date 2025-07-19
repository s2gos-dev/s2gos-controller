# Client CLI Reference

`s2gos-client` is the client shell tool for the S2GOS service.

The tool provides commands for managing processing request templates,
processing requests, processing jobs, and gets processing results.

You can use shorter command name aliases, e.g., use command name `vr`
for `validate-request`, or `lp` for `list-processes`.

**Usage**:

```console
$ s2gos-client [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version`: Show version and exit
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `configure`: Configure the client tool.
* `list-processes`: List available processes.
* `get-process`: Get process details.
* `validate-request`: Validate a processing request.
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
* `-c, --config PATH`: Client configuration file
* `--help`: Show this message and exit.

## `s2gos-client list-processes`

List available processes.

**Usage**:

```console
$ s2gos-client list-processes [OPTIONS]
```

**Options**:

* `-c, --config PATH`: Client configuration file
* `-f, --format [simple|json|yaml]`: Output format  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client get-process`

Get process details.

**Usage**:

```console
$ s2gos-client get-process [OPTIONS] PROCESS_ID
```

**Arguments**:

* `PROCESS_ID`: Process identifier  [required]

**Options**:

* `-c, --config PATH`: Client configuration file
* `-f, --format [simple|json|yaml]`: Output format  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client validate-request`

Validate a processing request.

The processing request to be validated may be read from a file given
by `--request`, or from `stdin`, or from the `process_id` argument
with zero, one, or more `--input` (or `-i`) options.

The `process_id` argument and any given `--input` options will override
settings with same name found in the given request file or `stdin`, if any.

**Usage**:

```console
$ s2gos-client validate-request [OPTIONS] [PROCESS_ID]
```

**Arguments**:

* `[PROCESS_ID]`: Process identifier

**Options**:

* `-i, --input [NAME=VALUE]...`: Processing request input
* `-r, --request PATH`: Processing request file
* `-f, --format [simple|json|yaml]`: Output format  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client execute-process`

Execute a process in asynchronous mode.

The processing request to be submitted may be read from a file given
by `--request`, or from `stdin`, or from the `process_id` argument
with zero, one, or more `--input` (or `-i`) options.

The `process_id` argument and any given `--input` options will override
settings with same name found in the given request file or `stdin`, if any.

**Usage**:

```console
$ s2gos-client execute-process [OPTIONS] [PROCESS_ID]
```

**Arguments**:

* `[PROCESS_ID]`: Process identifier

**Options**:

* `-i, --input [NAME=VALUE]...`: Processing request input
* `-r, --request PATH`: Processing request file
* `-c, --config PATH`: Client configuration file
* `-f, --format [simple|json|yaml]`: Output format  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client list-jobs`

List all jobs.

**Usage**:

```console
$ s2gos-client list-jobs [OPTIONS]
```

**Options**:

* `-c, --config PATH`: Client configuration file
* `-f, --format [simple|json|yaml]`: Output format  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client get-job`

Get job details.

**Usage**:

```console
$ s2gos-client get-job [OPTIONS] JOB_ID
```

**Arguments**:

* `JOB_ID`: Job identifier  [required]

**Options**:

* `-c, --config PATH`: Client configuration file
* `-f, --format [simple|json|yaml]`: Output format  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client dismiss-job`

Cancel a running or delete a finished job.

**Usage**:

```console
$ s2gos-client dismiss-job [OPTIONS] JOB_ID
```

**Arguments**:

* `JOB_ID`: Job identifier  [required]

**Options**:

* `-c, --config PATH`: Client configuration file
* `-f, --format [simple|json|yaml]`: Output format  [default: yaml]
* `--help`: Show this message and exit.

## `s2gos-client get-job-results`

Get job results.

**Usage**:

```console
$ s2gos-client get-job-results [OPTIONS] JOB_ID
```

**Arguments**:

* `JOB_ID`: Job identifier  [required]

**Options**:

* `-c, --config PATH`: Client configuration file
* `-f, --format [simple|json|yaml]`: Output format  [default: yaml]
* `--help`: Show this message and exit.
