## Changes in version 0.0.2 (in development)

* Moved top-level module in `s2gos_client` into package `s2gos_client.api`
* Generated `AsyncClient`, next to existing, synchronous `s2gos_client.api.Client`
* Updated `tools/openapi.yaml` to rename some unintuitive names.
  Regenerated and adjusted remaining code for following classes 
  renamed in `s2gos_common.models`:
  - `Response` into `ResponseType`
  - `StatusCode` into `JobStatus`
  - `Type` into `JobType`
  - `Type1` into `DataType`

## Changes in version 0.0.1

* Started from `https://github.com/s2gos-dev/s2gos-client`, which is now archived.
  Using multi-workspace setup with [pixi](https://pixi.sh).
