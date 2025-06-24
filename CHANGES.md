## Changes in version 0.0.6 (in development)


## Changes in version 0.0.5 (not released)

- Added a more realistic example in `create_datacube` to
  `s2gos.server.services.local.testing.service`
- Changed `s2gos/common/openapi.yaml`
  - renamed `exception` schema component into `apiError`
  - renamed `statusInfo` schema component into `jobInfo`
  - renamed `execute` schema component into `processRequest`
  - renamed `process` schema component into `processDescription`
  - renamed `results` schema component into `jobResults`
  - renamed `landingPage` schema component into `capabilities`
  - renamed `confClasses` schema component into `conformanceDeclaration`
  - renamed `inline_response_200` schema component into `inlineValue`
  - renamed `inlineOrRefData` schema component into `inlineOrRefValue`
  - renamed `qualifiedInputValue` schema component into `qualifiedValue`
  - renamed `getConformance` operationId into `getConformance`
  - renamed `getProcessDescription` operationId into `getProcess`
  - renamed `execute` operationId into `executeProcess`
  - renamed `getStatus` operationId into `getJob`
  - renamed `dismiss` operationId into `dismissJob`
  - renamed `getResults` operationId into `getJobResults`
  - extended `StatusInfo` schema component by `traceback` property
  - regenerated code
  - adjusted non-generated code accordingly


## Changes in version 0.0.4 (not released)

* Added basic submit form to GUI client: `s2gos.client.gui.Client.show_submitter()`

## Changes in version 0.0.3 (not released)

* Server now has a new option `--service` to specify the service implementation.
  It specifies an instance of an implementation of `s2gos.server.service.Service`, 
  e.g., `s2gos.server.services.testing:service`. Or use env var `S2GOS_SERVICE`.
* Added a useful process server impl. `LocalService` for local Python user
  functions in `s2gos.server.services.local`:
  * Uses a new decorator `@service.process_info` to register user functions.
  * Find example in  `s2gos/server/services/testing.py`.
* In GUI client prototype, changed job table to have an action row instead 
  of action table columns.
* Added `docs/todo.md`

## Changes in version 0.0.2 (not released)

* Reorganized package
* Started code generation for models, client, and server
* Added basic FastAPI server, added server CLI `s2gos-server`
* Using dummy implementation for the S2GOS service
* Using `Typer` instead of `Click`
* Added pretty rendering of model object in Jupyter notebooks

## Version 0.0.1 (not released) 

Initial setup.
