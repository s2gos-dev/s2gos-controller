# Installation

## Using pip

The S2GOS controller packages can be installed from PyPI using `pip` into an existing
Python environment with Python >= 3.11. 

To install the S2GOS client

```bash
pip install s2gos-client
```

and to install the S2GOS server (e.g., for local testing)

```bash
pip install s2gos-server
```

## Using conda/mamba 

The S2GOS controller packages are not yet deployed on conda-forge, therefore
installing it using as a conda package using `conda` or `mamba` is not yet available. 

## Using pixi

Since the S2GOS controller packages are not yet deployed on conda-forge, 
use `pixi add --pypi s2gos-{client|server}` to add them to an existing 
[pixi](https://pixi.prefix.dev/latest/) project.

## Using GitHub

To install the S2GOS controller packages from their sources on GitHub you'll 
need to both [install git](https://git-scm.com/install/) and 
[install pixi](https://pixi.sh/latest/installation/) first. Then:

```bash
git clone https://github.com/s2gos-dev/s2gos-controller.git
cd s2gos-controller
pixi install
```

The environment includes both controller packages, JupyterLab, and the
requirements for the local demonstration processes.

## Getting started

Follow the [user guide](guide/index.md) to start a local test service,
configure the client, and submit your first job. The guide covers the Python API,
App, command line, authentication, and result access.

The original notebooks remain in the repository for independent exploration;
the maintained walkthroughs and reusable examples are in the user guide.

## Development

Install the S2GOS controller packages as described in 
[Installation / Using GitHub](#using-github) above.

## Code Checking and Testing

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

* `s2gos-client` is a branded version of 
  [cuiman](https://github.com/eo-tools/eozilla/tree/main/cuiman),
  which provides the client CLI, GUI, and API implementations, and 
* `s2gos-server` is a branded version of
  [wraptile](https://github.com/eo-tools/eozilla/tree/main/wraptile),
  which provides the gateway server implementation, 
* [gavicore](https://github.com/eo-tools/eozilla/tree/main/gavicore)
  which provides common OGC model classes and basic utilities for 
  Eozilla packages.  

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
