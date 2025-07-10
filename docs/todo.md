# DTE-S2GOS client To-Dos

The DTE-S2GOS client is currently under development.
Given here are the issues that will be addressed next.

## Repo/package setup

* Setup CI with `pixi`
  - pixi run sync-versions
  - pixi run generate
  - **DONE** pixi run coverage
* **DONE** Move all source code into `src` folder.
* **DONE** Use either `uv` or `pixi` for package and environment management. <-- We use `pixi`
* **DONE**: We need three main packages in the end to avoid naming clashes:
  - `s2gos_client` (now `s2gos.client`)
  - `s2gos_common` (now `s2gos.common.models`)
  - `s2gos_server` (now `s2gos.server`)
* **DONE**: Find out and decide how to setup GitHub repo(s) for this
  - One repository with all three packages in `src`
  - One repository with three subdirectories  <-- This is the one!
  - Three repositories 
* **DONE**: Align `ruff` settings with other [S2GOS repos](https://github.com/s2gos-dev).

## Client implementation

General design

- **DOING**: We need two API client versions: sync and async
  - **DONE**: Generate `AsyncClient`, next to `Client` 
  - **DONE**: Generate them using [`httpx`](https://github.com/encode/httpx), which 
    should replace currently used `requests`
  - Use the async API client version in the GUI Client.
    `panel` widget handler that use the client can and should be async.
  - Use the sync API client version in the CLI Client. 

Enhance the API Client

- Consider generating a higher-level client from the 
  OGC API Processes descriptions
- Address the user-facing issues given under [Code generation](#code-generation)

Enhance the GUI Client

-  **DOING**: `show()` - show the main form where users can select a process 
  and submit process requests with inputs and outputs
  - **DONE**: select process
  - **DONE**: render input widgets
  - **DONE**: submit request
  - Actions
    - **DONE*: execute request 
    - open request 
    - save request 
    - save-as request
    - **DONE*: get request 
    - show success/failure
  - bug: process `gen_datacube`: if no bbox selected, client receives an error 
  - optional enhancements
    - integrate job status panel
    - show request as JSON
-  **DONE**: `show_jobs()` - show all jobs in a table and provide actions on job selection: 
  - **DONE**: use `Tabulator`
  - **DONE** Add an action row with actions applicable to the current table selection
  - Actions:
    - **DONE**: ✖️ cancel accepted/running job(s)
    - **DONE**: ❌ delete successful/dismissed/failed job(s)
    - ♻️️ restart dismissed/failed job(s)
    - **DONE**: ⬇️ get job result(s)
- `show_processes()` - get a nicely rendered overview of all processes 
- `show_process(process_id: str = None, job_id: str = None, editable: bool = True)`
- `show_job(job_id: str = None)`

Implement CLI commands
- `show_processes()`
- `show_process(process_id: str = None, job_id: str = None, editable: bool = True)`
- `show_jobs()` with cancel option
- `show_job(job_id: str = None)`

## Server implementation

Local service

- **DONE**: Implement local service that can invoke any Python function
- Path `/`:
  - Also provide a HTML version, support mimetype `text/html`
  - **DONE**: The landing page provides links to the:
    * **DONE**: The APIDefinition (no fixed path),
    * **DONE**: The Conformance statements (path `/conformance`),
    * **DONE**: The processes metadata (path `/processes`),
    * **DONE**: The endpoint for job monitoring (path `/jobs`).
  - **DONE**: Links should be absolute URL, hence we need `request: Request` as 1st function arg

Airflow-based service

- Implement Airflow-based service that connects to the Airflow web API

## Authentication

* Implement basic authentication using OAuth2, 
  use user_name/access_token from ClientConfig in
  - client 
  - server

## Authorisation

* Define roles & scopes
* Implement accordingly in
  - client 
  - server

## Error handling

* We currently have no error management in client. 
  Handle ClientException so users understand what went wrong:
  - Python API
  - CLI
  - GUI
* Include server traceback on internal server errors with 500 status

## Code generation

The output of `generators/gen_models` is not satisfying: 

1. Many generated classes are `RootModels` which are inconvenient for users, e.g.,
   `Input` requires passing values with `root` attributes.
2. Basic openAPI constructs like `Schema` or `Reference` should not be  
   generated but reused from predefined `BaseModel`s.
3. **DONE**: Generated class names like `Exception` clash with predefined Python names.
4. **DONE**: Some generated class names are rather unintuitive, e.g., 
   `Execute` instead of `Request`.
5. JSON generated from models is too verbose. Avoid including `None` fields and 
   fields that have default values.
6. Consider code generation from templates with `jinja2`

- **DONE**: Adjust `s2gos/common/openapi.yaml` to fix the above and/or
- **DONE**: Configure `datamodel-code-generator` to fix the above and/or
- Use [openapi-pydantic](https://github.com/mike-oakley/openapi-pydantic)
  - Use `openapi_pydantic.Schema`, `openapi_pydantic.Reference`, etc. in generated code
  - Use `openapi_pydantic.OpenAPI` for representing `s2gos/common/openapi.yaml` in 
    the generators
