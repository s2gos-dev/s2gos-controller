# DTE-S2GOS controller Airflow

Airflow DAGs for the ESA DTE-S2GOS synthetic scene generator service

A minimal local Airflow development environment using [pixi](https://pixi.sh).

## Setup

**THIS DOESN'T WORK! WHY?**
Copy file `.env-template.txt` and rename it to `.env`. Check it and optionally adjust it.

```bash
mv .env-template.txt .env
pixi install
pixi run install-airflow
```

## Run Airflow

```bash
pixi run webserver
```

## Develop

```bash
pixi run test
pixi run lint
pixi run typecheck
```

## Airflow

```bash
pixi run airflow db migrate
pixi run airflow dag-processor
pixi run airflow scheduler
pixi run airflow api-server
```

The Airflow API Server runs at URL http://localhost:8080.
To find login credentials search for the log entry:
```Simple auth manager | Password for user 'admin':```
