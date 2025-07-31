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
def my_process_1(path: str, threshold: float) -> str:
    ctx = get_job_context()
    ...
    ctx.report_progress(progress=15, message="Initialized sources")
    ...

@registry.process(id="my-process-2")
def my_process_2(path: str, factor: float) -> str:
    ...
```

(2) Create an instance of a common processor CLI and pass it a function that returns
your process registry. In `my_package/cli.py`:

```python
from s2gos_common.cli.cli import get_cli

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

::: s2gos_common.process.get_job_context

::: s2gos_common.process.JobContext

::: s2gos_common.cli.cli.get_cli
