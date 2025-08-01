# Process Development

The package `s2gos_common` provides a simple processor development framework that

  - supports registration of processes from Python functions,  
  - supports progress reporting by subscriber callback URLs, and
  - provides a command-line interface (CLI) to query and execute the registered processes.

Processor packages developed using the provided CLI can later on be used to
generate Docker images, Airflow DAGs, and optionally OGC Application Packages.

## Development Recipe

Framework usage is simple, it is a 3-step process: 

1. Write your processes as Python functions and register them in a process registry.
2. Create a CLI instance from that process registry.
3. Register the CLI instance as an entry point script for your package.

The steps are explained in more detail in the following.

(1) First, you'll create a process registry object of type `ProcessRegistry`.
Use the registry's `process` decorator to register your Python functions 
that should be exposed as processes. In `my_package/processes.py`:

```python
from s2gos_common.process import JobContext, ProcessRegistry

registry = ProcessRegistry()


@registry.process(id="my-process-1")
def my_process_1(path: str, threshold: float = 0.5) -> str:
    ctx = JobContext.get()
    ...
    ctx.report_progress(progress=15, message="Initialized sources")
    ...


@registry.process(id="my-process-2")
def my_process_2(ctx: JobContext, path: str, factor: float = 1.0) -> str:
    ...
```

The `ctx` object of type [JobContext][s2gos_common.process.JobContext]
can be used to report progress and to check for job cancellation.
You can get the job context inside the function body via `JobContext.get()` 
or declare it as a function argument of type `JobContext`.

Process inputs, such as the arguments `path` or `factor` above, 
can be further specified by 
[`pydantic.Field`](https://docs.pydantic.dev/latest/concepts/fields/) annotations.
Field annotations for an argument can be provided via the `input_fields` dictionary 
passed  to the [`process`][s2gos_common.process.ProcessRegistry.process] decorator, 
or preferably as part of the type declaration using the Python `Annotated` 
special form. An example for the latter is
`factor: Annotated[float, Field(title="Scaling factor", gt=0., le=10.)] = 1.0`.


(2) In a second step you create an instance of a common processor CLI and pass it 
a reference to your registry instance. In `my_package/cli.py`:

```python
from s2gos_common.process.cli.cli import get_cli

# The CLI with a basic set of commands.
# The `cli` is a Typer application of type `typer.Typer()`,
# so can use the instance to register your own commands.
cli = get_cli("my_package.processes:registry")
```

You could also pass the imported registry directly, but using a 
reference string defers importing the registry instance until it is 
needed. This makes the CLI much faster if it is just called with
the `--help` option and hence no processing takes place. 

(3) Expose the CLI as an entry point. In your `pyproject.toml`:

```toml
[project.scripts]
my-tool = "my_package.cli:cli"
```

## Application Example

An application example that can serve as a starting point is provided in the workspace 
[s2gos-app-ex](https://github.com/s2gos-dev/s2gos-controller/tree/main/s2gos-app-ex).


## Framework API

::: s2gos_common.process.ProcessRegistry
    options:
      show_source: false
      heading_level: 3

::: s2gos_common.process.JobContext
    options:
      show_source: false
      heading_level: 3

::: s2gos_common.process.JobCancelledException
    options:
      show_source: false
      heading_level: 3

::: s2gos_common.process.get_cli
    options:
      show_source: false
      heading_level: 3
