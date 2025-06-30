## Changes in version 0.0.2 (in development)

- `s2gos-client` package:
  - Moved top-level module in `s2gos_client` into package `s2gos_client.api`.
  - Generated `AsyncClient`, next to existing, synchronous `Client` in `s2gos_client.api`.
  - Added `show_job(job_id)` to `Client` of `s2gos_client.gui`. It displays job details.
  - Added `close()` methods to clients and transports.
  - Using `httpx` package instead of `requests`.

- `s2gos-server` package:
  - `LocalService` in `s2gos_server.services.local` now reports links to `self`
    and reports absolute capability URLs.
  - Now using `fastapi.Depends()` feature

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
