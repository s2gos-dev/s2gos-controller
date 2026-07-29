# DTE-S2GOS controller server

The gateway server for the ESA DTE-S2GOS synthetic scene generator service.
Python gateway server for the ESA DTE-S2GOS synthetic scene generator service.

## Airflow service

Start by running a local Airflow instance with some test DAGs:
```commandline
cd s2gos-airflow
pixi install
pixi run airflow standalone
```

Then run the S2GOS gateway server with the local Airflow instance (assuming
the local Airflow webserver runs on http://localhost:8080):

```commandline
pixi shell
s2gos-server run -- wraptile.services.airflow:service --airflow-password=a8e7f4bb230
```

> **Note:** `s2gos-server` does not ship its own Airflow service yet, so the
> generic `wraptile.services.airflow:service` is used.

The S2GOS server is basically a branded 
[Eozilla wraptile server](https://eo-tools.github.io/eozilla/wraptile/).

## API authentication

`s2gos-server` does not authenticate requests to its OGC API itself. In a
deployment, place the server behind the platform's authentication gateway or
reverse proxy, which validates client credentials before forwarding requests.
Configure the client to send the appropriate credentials as described in the
[authentication guide](../docs/auth.md).

This is separate from the `--airflow-username` and `--airflow-password`
options below: those credentials authenticate the gateway to Airflow.

The possible options are

* `--airflow-base-url=TEXT`: The base URL of the Airflow web API, defaults to
  `http://localhost:8080`.
* `--airflow-username=TEXT`: The Airflow username, defaults to `admin`.
* `--airflow-password=TEXT`: The Airflow password.
  For an Airflow installation with the simple Auth manager, use the one from
  `.airflow/simple_auth_manager_passwords.json.generated`.

### Running against a deployed Airflow

To run the gateway against a live, deployed Airflow instead of a local one,
point `--airflow-base-url` at the deployed Airflow API and provide the
credentials. The service authenticates with the username/password to obtain a
bearer token and refreshes it on expiry, so this assumes Airflow's
username/password (JWT) login is reachable at that base URL.

```commandline
s2gos-server run -- wraptile.services.airflow:service \
    --airflow-base-url=https://airflow.your-domain.example \
    --airflow-username=admin \
    --airflow-password="$AIRFLOW_PASSWORD"
```

Pass the password via an environment variable (as above) rather than inline, so
it does not end up in your shell history.

### Running with Docker

The server image (`quay.io/s2gos/s2gos-server`) sets
`EOZILLA_SERVICE=wraptile.services.airflow:service` by default and binds to
`0.0.0.0:8008`. Provide the Airflow connection details at run time. Options may
be passed after `--`:

```commandline
docker run --rm -p 8008:8008 \
    quay.io/s2gos/s2gos-server:0.2.0.dev1 \
    s2gos-server run -- wraptile.services.airflow:service \
      --airflow-base-url=https://airflow.your-domain.example \
      --airflow-username=admin \
      --airflow-password="$AIRFLOW_PASSWORD"
```

Alternatively, supply the whole service specification via the `EOZILLA_SERVICE`
environment variable and run the default command:

```commandline
docker run --rm -p 8008:8008 \
    -e EOZILLA_SERVICE="wraptile.services.airflow:service --airflow-base-url=https://airflow.your-domain.example --airflow-username=admin --airflow-password=${AIRFLOW_PASSWORD}" \
    quay.io/s2gos/s2gos-server:0.2.0.dev1
```

Once running, `GET http://localhost:8008/processes` lists the DAGs exposed by
that Airflow instance.


## Local service

Running the S2GOS gateway server with a local service:

```commandline
pixi shell
s2gos-server run -- s2gos_server.services.testing:service --processes --max-workers=5
```

The possible options are

* `--processes` /  `--no-processes`: Whether to use processes or threads, defaults
  to threads.
* `--max-workers=INTEGER`: Maximum number of processes or threads, defaults to 3.
