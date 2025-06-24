[![CI](https://github.com/s2gos-dev/s2gos-client/actions/workflows/tests.yml/badge.svg)](https://github.com/s2gos-dev/s2gos-client/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/s2gos-dev/s2gos-client/graph/badge.svg?token=GVKuJao97t)](https://codecov.io/gh/s2gos-dev/s2gos-client)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)
[![GitHub License](https://img.shields.io/github/license/s2gos-dev/s2gos-client)](https://github.com/s2gos-dev/s2gos-client)

# DTE-S2GOS Python client

A Python client for the ESA DTE-S2GOS synthetic scene generator service

## Development

Create a new environment using `conda` or `mamba`

```commandline
mamba env create -f ./environment.yml 
conda activate s2gos
pip install -ve . 
```
### Formatting

```commandline
isort .
```

```commandline
ruff format 
```

### Linting

```commandline
ruff check
```

### Testing & Coverage

```commandline
pytest --cov s2gos --cov-report html tests
```

### Code generation

Generate [pydantic](https://docs.pydantic.dev/) models in `s2gos/common/models.py` 
(uses [datamodel-code-generator](https://koxudaxi.github.io/datamodel-code-generator/)):

```commandline
python -m generators.gen_models
```

Generate client API in `s2gos/client/api/client.py`:

```commandline
python -m generators.gen_client
```

Generate server routes in `s2gos/server/routes.py` and 
service interface in `s2gos/server/service.py`:

```commandline
python -m generators.gen_server
```

### Documentation generation

Generate client CLI reference documentation in `docs/cli.md`:

```commandline
python -m generators.gen_client_cli_md
```

### Run server

```commandline
s2gos-server dev --service=s2gos.server.services.local.testing:service
```

or using FastAPI CLI

```commandline
$ fastapi dev s2gos/server/main.py
```

### Run client Python API

```python
from s2gos.client import Client

client = Client()
client.get_jobs()
```

### Run client GUI (in Jupyter notebooks)

```python
from s2gos.client.gui import Client

client = Client()
client.show_processes()
client.show_jobs()
```

### Run client CLI

```commandline
$ s2gos --help
```

### Run client GUI demo code 

Run via panel server:

```commandline
$ panel serve  --show --dev ./examples/demo.py
```
