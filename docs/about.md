# About the DTE-S2GOS client project

## Changelog

You can find the complete S2GOS client's changelog 
[here](https://github.com/s2gos-dev/s2gos-client/blob/main/CHANGES.md). 

## Reporting

If you have suggestions, ideas, feature requests, or if you have identified
a malfunction or error, then please 
[post an issue](https://github.com/s2gos-dev/s2gos-client/issues). 

## Contributions

The S2GOS client project welcomes contributions of any form as long as you 
respect our 
[code of conduct](https://github.com/s2gos-dev/s2gos-client/blob/main/CODE_OF_CONDUCT.md)
and follow our 
[contribution guide](https://github.com/s2gos-dev/s2gos-client/blob/main/CONTRIBUTING.md).

If you'd like to submit code or documentation changes, we ask you to provide a 
pull request (PR) 
[here](https://github.com/s2gos-dev/s2gos-client/pulls). 
For code and configuration changes, your PR must be linked to a 
corresponding issue. 

## Development

To install theS2GOS client's development environment into an existing Python 
environment, do

```bash
pip install .[dev,doc]
```

or create a new environment using `conda` or `mamba`

```bash
mamba env create 
conda activate s2gos
```

### Testing and Coverage

The S2GOS client uses [pytest](https://docs.pytest.org/) for unit-level testing 
and code coverage analysis.

```bash
pytest tests/ --cov=s2gos --cov-report html
```

### Code Style

The S2GOS client's source code is formatted and quality-controlled 
using [ruff](https://docs.astral.sh/ruff/):

```bash
ruff format
ruff check
```

### Documentation

The S2GOS client's documentation is built using the 
[mkdocs](https://www.mkdocs.org/) tool.

With repository root as current working directory:

```bash
pip install .[doc]

mkdocs build
mkdocs serve
mkdocs gh-deploy
```

After changing the CLI code, always update its documentation `docs/cli.md` 
by running

```bash
python docs/scripts/gen_client_cli_md.py
```

## License

The S2GOS client is open source made available under the terms and conditions of the 
[Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0.html).
