## Changes in version 0.1.0 (in development)

Added GUI component support for 
[PathRef](https://github.com/s2gos-dev/s2gos-utils/blob/MTR/src/s2gos_utils/io/paths.py) 
object (not yet used).

Major parts of the S2GOS controller packages have been generic with respect 
to the primary interface used between the client and the gateway server, 
which is the
[OGC API - Processes](https://github.com/opengeospatial/ogcapi-processes). 
Hence, S2GOS components can theoretically be used to work with any 
OGC-compliant processing service. Also, the old package names `s2gos-xxx` were
hard to remember and imply a special context as well was the name "S2GOS"
hard-coded into the package code, see #39. 

In consequence, we moved the existing repo to a new, dedicated GitHub 
organisation [eo-tools](https://github.com/eo-tools) and a new 
repo [Eozilla](https://github.com/eo-tools/eozilla) and gave credits to the 
[S2GOS project](https://dte-s2gos.rayference.eu/), which made Eozilla 
possible. We renamed the original packages so they are easy to remember and
convey a clear, general meaning and refactor out the S2GOS-specific parts.

The new Eozilla packages are 
- `appligator` (application packaging),
- `cuiman` (client user interfaces),
- `gavicore` (common core components),
- `procodile` (process dev framework), 
- `wraptile` (gateway server that wraps processing systems).

The S2GOS controller package `s2gos-client` now uses the Eozilla package 
`cuiman` and `s2gos-server` now uses the Eozilla package `wraptile`.


---

## Changes in version 0.0.5

- In `s2gos_client`:
  - Improved error handling (#54)
  - Renamed `ClientException` into `ClientError`. 
  - Renamed `TransportException` into `TransportError`. 


## Changes in version 0.0.4

- Prevent server from logging `/jobs` request, as they are used for polling. 
- Prevent client from logging at all if we are not debugging. 
- Client GUI uses `ExecutionRequest` rather than `ProcessRequest` to 
  allow users copying the processing request into a file for the CLI. 
  Therefore, `s2gos_common.process.ExecutionRequest` is now a 
  public API class.
- Added a keyword-argument `inputs_arg: str | bool` to the `ProcessRegistry.process`
  decorator. If specified, it defines an _inputs argument_, which is used to 
  define the process inputs in form of a dataclass derived from 
  `pydantic.BaseModel`. (#35)
- Now supporting the OpenAPI/JSON Schema `discriminator` property 
  in `tools/openapi.yaml/schemas/schema` and generated models. (#36)
- Renamed `s2gos_common.process.cli.ProcessingRequest` into
  `s2gos_common.process.cli.ExecutionRequest`.
- Replaced various occurrences of the term _processing_ by 
  _execution_ to be more precise.
- Developed a simple processor development framework that
  - provides a CLI to query and execute processes;  
  - supports registration of processes from python functions;  
  - supports progress reporting by subscriber callback URLs.
- Provided an application example that uses the framework in workspace 
  `s2gos-app-ex`.
- Added basic documentation for the process development framework
  in `docs/process-dev`.
- Moved process registry stuff from `s2gos_server.services.local` into 
  `s2gos_common.process` so it can be easier reused.
- Introduced `--dotpath` / `-d` flag in the CLI commands `validate-request` 
  and `execute-process` of `s2gos-client` and `s2gos-common`. 
  If set, allows for passing input names using a dot-path notion
  to encode nested values (e.g., `-i scene.colors.bg=red`).
- Added high level overview of various DevOps tools which will be used in the 
  development of services.
- Added Jupyter Notebooks to documentation.
- Fixed formatting and links for Client API documentation. (#48)


## Changes in version 0.0.3

- The client's CLI is now fully operable.
- Simplified generation of CLI reference documentation and improved general 
  styling significantly.
- Added a starting point for the documentation of the S2GOS control layer's 
  architecture. 
- Model class `Schema` now contains `ref`; removed `Reference` model. 
- Reverted addition of `inline_inputs` and `inline_sep` arguments to 
  `LocalService.process()` decorator. Instead, one can simply 
  use dotted property names to set values of nested objects in a 
  process request.
- Introduced custom client error rendering in notebooks.
- Renamed `ClientError` into `ClientException`.
- Server CLI now access has service as argument, which can have service-specific 
  arguments passed after `--`.
- Introduced `s2gos_server.services.base.ServiceBase` to serve as base 
  class for local and Airflow service implementations.
  - it can be configured by overriding `configure(args, kwargs)` 
  - it can log using `self.logger`


## Changes in version 0.0.2

- `s2gos-client` package:
  - Moved top-level module in `s2gos_client` into package `s2gos_client.api`.
  - Generated `AsyncClient`, next to existing, synchronous `Client` in `s2gos_client.api`.
  - Added `show_job(job_id)` to `Client` of `s2gos_client.gui`. It displays job details.
  - Added `close()` methods to clients and transports.
  - Using `httpx` package instead of `requests`.
  - Dedicated GUI widgets for given JSON schemas can now be registered in
    global registry `registry` of `s2gos_client.gui.component.ComponentContainer`.
  - Better widget selection for schema types `integer` and `number`.

- `s2gos-server` package:
  - `LocalService` in `s2gos_server.services.local` now reports links to `self`
    and reports absolute capability URLs.
  - `LocalService` now supports to more arguments for its `@process()` decorator:
    - `inline_inputs: bool | str | list[str] = False` - allows inlining all or named 
      object arguments, so that object properties become process inputs at top-level.
    - `inline_sep: str | None = "."` - In separator to used to create the top-level
      input names: `{arg}{sep}{prop}`. If `None`, the property names will be used.
  - Now using `fastapi.Depends()` feature
  - Renamed test process `create_datacube` into `simulate_scene`.

- `s2gos-common` package:
  - Updated `tools/openapi.yaml` to rename some unintuitive names.
    Regenerated and adjusted remaining code for following classes 
    renamed in `s2gos_common.models`:
    - `Response` into `ResponseType`
    - `StatusCode` into `JobStatus`
    - `Type` into `JobType`
    - `Type1` into `DataType`

- Project setup:
  - Excluded `s2gos_client.gui` from coverage as it is still experimental.


## Changes in version 0.0.1

- Started from `https://github.com/s2gos-dev/s2gos-client`, which is now archived.
  Using multi-workspace setup with [pixi](https://pixi.sh).
