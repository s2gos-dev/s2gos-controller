# Process Development

The package `s2gos_common` provides a simple processor development framework that

  - supports registration of processes from python functions,  
  - supports progress reporting by subscriber callback URLs, and
  - provides a CLI to query and execute processes.

Processor packages developed using the provided CLI can later on be used to
generate Docker images, Airflow DAGs, and optionally OGC Application Packages.

## Development Recipe

Framework usage is simple, as described in the following three steps. 

(1) Create a process registry object of type `ProcessRegistry`.
Use the registry's `process` decorator to register your Python functions 
that should be exposed as processes. In `my_package/processes.py`:

```python
from s2gos_common.process import ProcessRegistry, get_job_context

registry = ProcessRegistry()

@registry.process(id="my-process-1")
def my_process_1(path: str, threshold: float = 0.5) -> str:
    ctx = get_job_context()
    ...
    ctx.report_progress(progress=15, message="Initialized sources")
    ...

@registry.process(id="my-process-2")
def my_process_2(path: str, factor: float = 1.0) -> str:
    ...
```

Process inputs, such as the arguments `path` or `factor` above, 
can be further specified by 
[`pydantic.Field`](https://docs.pydantic.dev/latest/concepts/fields/) annotations.
Field annotations for an argument can be provided via the `input_fields` dictionary 
passed  to the [`process`][s2gos_common.process.ProcessRegistry.process] decorator, 
or preferably as part of the type declaration using the Python `Annotated` 
special form. An example for the latter is
`factor: Annotated[float, Field(title="Scaling factor", gt=0., le=10.)] = 1.0`.


(2) Create an instance of a common processor CLI and pass it a function that returns
your process registry. In `my_package/cli.py`:

```python
from s2gos_common.process.cli.cli import get_cli


# By using a getter function, we defer importing the registry 
# until needed. This avoids early loading of all dependencies
# in the case where the CLI is invoked just with a`--help` option.
def get_registry():
    from my_package.processes import registry

    return registry


# The CLI with a basic set of commands.
# The `cli` is a Typer application of type `typer.Typer()`, 
# so you can use the instance to register your own commands.
cli = get_cli(get_registry)
```

(3) Expose the CLI as an entry point. In your `pyproject.toml`:

```toml
[project.scripts]
my-tool = "my_package.cli:cli"
```

## Process Development API

::: s2gos_common.process.ProcessRegistry
    options:
      show_source: false
      heading_level: 3

::: s2gos_common.process.get_job_context
    options:
      show_source: false
      heading_level: 3

::: s2gos_common.process.JobContext
    options:
      show_source: false
      heading_level: 3

::: s2gos_common.cli.cli.get_cli
    options:
      show_source: false
      heading_level: 3
