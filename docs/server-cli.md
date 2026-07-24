# S2GOS Server CLI

`s2gos-server` is a web server made for wrapping workflow 
orchestration systems providing an API compliant with the OGC API - Processes,
Part 1: Core Standard (https://ogcapi.ogc.org/processes/).


The SERVICE argument may be followed by a `--` to pass one or more 
service-specific arguments and options.

Note that the service arguments may also be given by the 
environment variable `EOZILLA_SERVICE`.

**Usage**:

```console
$ s2gos-server [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version`: Show version and exit.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `run`: Run server in production mode.
* `dev`: Run server in development mode.

## `s2gos-server run`

Run server in production mode.

**Usage**:

```console
$ s2gos-server run [OPTIONS] [SERVICE [-- SERVICE-OPTIONS]]
```

**Arguments**:

* `[SERVICE [-- SERVICE-OPTIONS]]`: Service instance optionally followed by `--` to pass service-specific arguments and options. SERVICE should have the form `path.to.module:service`.  [env var: EOZILLA_SERVICE]

**Options**:

* `--host TEXT`: Host address.  [env var: EOZILLA_SERVER_HOST; default: 127.0.0.1]
* `--port INTEGER`: Port number.  [env var: EOZILLA_SERVER_PORT; default: 8008]
* `--help`: Show this message and exit.

## `s2gos-server dev`

Run server in development mode.

**Usage**:

```console
$ s2gos-server dev [OPTIONS] [SERVICE [-- SERVICE-OPTIONS]]
```

**Arguments**:

* `[SERVICE [-- SERVICE-OPTIONS]]`: Service instance optionally followed by `--` to pass service-specific arguments and options. SERVICE should have the form `path.to.module:service`.  [env var: EOZILLA_SERVICE]

**Options**:

* `--host TEXT`: Host address.  [env var: EOZILLA_SERVER_HOST; default: 127.0.0.1]
* `--port INTEGER`: Port number.  [env var: EOZILLA_SERVER_PORT; default: 8008]
* `--help`: Show this message and exit.
