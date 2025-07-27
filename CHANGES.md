## Changes in version 0.0.3 (in development)

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
