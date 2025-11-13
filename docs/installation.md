# Installation

## Using pip

The S2GOS controller packages are not yet deployed on PyPI, therefore
installing it as a package using `pip` is not yet available. 

## Using conda/mamba 

The S2GOS controller packages are not yet deployed on conda-forge, therefore
installing it using as a conda package using `conda` or `mamba` is not yet available. 

## Using pixi

The S2GOS controller packages are not yet deployed on conda-forge, therefore
installing it as a conda package using `pixi` is not yet available. 

## Using GitHub

To install the S2GOS controller packages from their sources on GitHub you'll 
need to install both [git](https://git-scm.com/install/) and 
[pixi](https://pixi.sh/latest/installation/) first. Then:

```bash
git clone https://github.com/eo-tools/sen4cap-client.git
cd s2gos-controller
pixi install
pixi shell
```

The installed development environment includes also JupyterLab so the recommended
way to get started is to take a look at the notebooks in the `notebooks` folder.

```bash
cd notebooks
jupyter-lab
```

## Getting started

After installing the S2GOS controller packages in your Python environment
and activating it (conda/mamba: `conda activate <your-env>`, pixi: `pixi shell`)
make sure the respective command-line tools are accessible: Type

```bash
s2gos-server --help
```

and 

```bash
s2gos-client --help
```

to get an overview of the available commands and options. 

You can then run the S2GOS server with one of the development services
or use the deployed server. To run the development service with a local
process executor run

```bash
s2gos-server dev -- wraptile.services.local:service
```

To run the S2GOS gateway server with a local Airflow instance (assuming
the local Airflow webserver runs on http://localhost:8080):

```bash
s2gos-server dev -- wraptile.services.airflow:service --airflow-password=abcd1234
```

The next step is configure the client, which will also serve as default configuration 
for the client's Python API and its GUI:

```bash
s2gos-client configure
```

Test:

```bash
s2gos-client list-processes
```

## Development

Install the S2GOS controller packages as described in 
[Installation / Using GitHub](#using-github) above.

## Linting and Testing

To run all checks, execute

```bash
pixi run checks
```

To run all tests, execute

```bash
pixi run tests
```

To generate a coverage report, execute

```bash
pixi run coverage
```

## Implementing Enhancements

The S2GOS controller code relies heavily on the 
[Eozilla](https://eo-tools.github.io/eozilla/) packages 

* [wraptile](https://github.com/eo-tools/eozilla/tree/main/wraptile),
  which provides the gateway server implementation, 
* [cuiman](https://github.com/eo-tools/eozilla/tree/main/cuiman),
  which provides the client CLI, GUI, and API implementations, and 
* [gavicore](https://github.com/eo-tools/eozilla/tree/main/gavicore)
  which provides common OGC model classes and basic utilities.  

Should S2GOS controller require non-S2GOS-specific enhancements it 
would likely be best to implement the required changes in the respective 
Eozilla packages. For this, check out the Eozilla sources directly next 
to this project's sources to achieve this folder structure:

```
    <projects>/
    ├── s2gos-controller/
    │   ├── s2gos-client/
    │   ├── s2gos-server/
    │   └── ...
    └── eozilla/
        ├── appligator/
        ├── cuiman/
        ├── gavicore/
        ├── procodile/
        ├── wraptile/
        └── ...
```

For development, change the root `pyproject.toml` file as follows

1. Comment out the dependencies `cuiman`, `gavicore`, etc. in the 
   `[tool.pixi.dependencies]` table.

2. Uncomment the editable PyPI dependencies for `cuiman`, `gavicore`, etc. in 
   the `[tool.pixi.pypi-dependencies]` table.

The run

```bash
pixi i
```

to make the changes effective. Check with 

```bash
pixi ls
```

which should now list the Eozilla packages as editable.
