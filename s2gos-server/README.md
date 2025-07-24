# DTE-S2GOS controller server

Python server for the ESA DTE-S2GOS synthetic scene generator service.

## Local

Running the S2GOS gateway server with a local service:

```commandline
pixi shell
s2gos-server run --service=s2gos_server.services.local.testing:service
```

## Airflow

Running a local Airflow instance with some test DAGs:
```commandline
cd s2gos-airflow
pixi install
pixi run airflow standalone
```

Running the S2GOS gateway server with a local Airflow instance:

```commandline
pixi shell
export AIRFLOW_USERNAME admin
export AIRFLOW_PASSWORD ***********
s2gos-server run --service=s2gos_server.services.airflow.testing:service
```

Get the airflow user password from `s2gos-airflow/.airflow/simple_auth_manager_passwords.json.generated`.
