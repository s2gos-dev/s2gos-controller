# DTE-S2GOS controller server

Python gateway server for the ESA DTE-S2GOS synthetic scene generator service.

## Local

Running the S2GOS gateway server with a local service:

```commandline
pixi shell
s2gos-server run --service=s2gos_server.services.local.testing:service
```

## Airflow

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
export AIRFLOW_USERNAME admin
export AIRFLOW_PASSWORD ***********
s2gos-server run --service=s2gos_server.services.airflow.testing:service
```

Get the airflow user password from `s2gos-airflow/.airflow/simple_auth_manager_passwords.json.generated`.
