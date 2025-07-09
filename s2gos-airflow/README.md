# DTE-S2GOS controller Airflow

Airflow DAGs for the ESA DTE-S2GOS synthetic scene generator service

## Setup

This setup creates a minimal local Airflow development environment 
using [pixi](https://pixi.sh).
All packages are currently installed from PyPI as this is the only reliable
way to install Airflow 3.0.
Also, all Airflow configuration is local, namely in `./.airflow`, 
see `AIRFLOW_HOME` variable in `pyproject.toml`.

Windows users: this setup has been successfully tested with 
[WSL2](https://learn.microsoft.com/de-de/windows/wsl/) 2.4.11 
using Ubuntu 24.04.2 LTS. Airflow has no official Windows support. 

```bash
cd projects
git clone https://github.com/s2gos-dev/s2gos-controller.git
cd s2gos-controller/s2gos-airflow 
```

```bash
pixi install
pixi run install-airflow
```

## Start coding

```bash
pixi shell
```

Given that [VS Code](https://code.visualstudio.com/download) is installed 

```bash
code .
```

WSL users, see [VS Code with WSL](https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-vscode).

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
