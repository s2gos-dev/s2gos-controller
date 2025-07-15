# Architecture

_Note, should the following diagram code not render, copy it 
into the [mermaid](https://www.mermaidchart.com/) editor._

## S2GOS Client - GUI

Given here is the design used in package `s2gos_client.gui.component`.
The package contains the code to generate widgets and panels from the 
JSON schema `s2gos_common.models.InputDescription` instances contained in
a `s2gos_common.models.ProcessDescription` instance.

The `ComponentContainer` maps every `InputDescription` to a visual 
`Component` that is created for a given JSON schema.  

```mermaid
---
config:
  class:
    hideEmptyMembersBox: true
  layout: elk
---
classDiagram
direction LR
    class models.InputDescription {
      title
      description
      schema
    }
    class ComponentContainer {
	    \_\_init\_\_(input_descriptions)
      get_components()
      get_viewables()
    }
    ComponentContainer ..> ComponentFactoryRegistry : use
    ComponentContainer o--> models.InputDescription : 1..n by name
    ComponentContainer o--> Component : 1..n
    ComponentFactory ..> Component : create
    ComponentFactoryRegistry *--> ComponentFactory
```

A suitable `ComponentFactory` is selected for a given JSON schema
and will create the `Component` when it is needed.
The possible `ComponentFactory` instances are registered in a
 `ComponentFactoryRegistry` singleton.

```mermaid
---
config:
  class:
    hideEmptyMembersBox: true
  layout: dagre
---
classDiagram
direction TB
    class panel.viewable.Viewable {
	    \_\_panel\_\_()
    }
    class Component {
	    viewable
	    json_codec
	    _get_value_()
	    _set_value_(val)
	    _watch_value_(cb)
    }
    class WidgetComponent {
    }
    class ComponentFactory {
	    _accept_(schema)
	    _create_component_(schema)
    }
    class ComponentFactoryRegistry {
      register_factory(factory, type, format)
      find_factory(schema)
    }
    class ComponentFactoryBase {
	    type
	    format
	    accept(schema)
    }
    class BooleanCF {
    }
    class IntegerCF {
    }
    class NumberCF {
    }
    class StringCF {
    }
    class DateCF {
    }
    class BboxCF {
    }
    Component <|-- WidgetComponent
    Component --> panel.viewable.Viewable : 1 
    ComponentFactory ..> Component : create
    ComponentFactoryRegistry *--> ComponentFactory : 0..N
    ComponentFactory <|-- ComponentFactoryBase
    ComponentFactoryBase <|-- BooleanCF
    ComponentFactoryBase <|-- IntegerCF
    ComponentFactoryBase <|-- NumberCF
    ComponentFactoryBase <|-- StringCF
    ComponentFactoryBase <|-- DateCF
    ComponentFactoryBase <|-- BboxCF
```

## S2GOS Common

Given here is the design used in package `s2gos_common.service`.

```mermaid
classDiagram
direction TB
    class Service {
        get_conformance()
        get_capabilities()
        get_processes()
        get_process(process_id)
        execute_process(process_id, process_request)
        get_jobs()
        get_job(job_id)
        get_job_result(job_id)
    }
    class ProcessList {
    }
    class ProcessSummary {
        process_id
    }
    class ProcessDescription {
    }
    class ProcessRequest {
        inputs
        outputs
        response
        subscriber
    }
    class JobList {
    }
    class JobInfo {
        process_id
        job_id
        status
        progress
    }
    class JobResult {
    }
    class InputDescription {
        schema
    }
    class Description {
        title
        description
    }
    ProcessList *--> ProcessSummary : 0 .. N 
    ProcessSummary --|> Description
    ProcessDescription --|> ProcessSummary
    ProcessDescription *--> InputDescription : 0 .. N by name
    ProcessDescription *--> OutputDescription : 0 .. N by name
    InputDescription --|> Description
    OutputDescription --|> Description
    JobList *--> JobInfo : 0 .. N 
    Service ..> ProcessList : obtain
    Service ..> ProcessDescription : obtain
    Service ..> JobList : obtain
    Service ..> JobInfo : obtain
    Service ..> JobResult : obtain   
    Service ..> ProcessRequest : use      
```

which may be refined like so:

```mermaid
classDiagram
direction TB
    class Service {
        get_conformance()
        get_capabilities()
    }
    class ProcessCatalog {
        get_processes()
        get_process(process_id)
    }
    class ProcessExecutor {
        execute_process(process_id, process_request)
        get_jobs()
        get_job(job_id)
        get_job_result(job_id)
    }
    Service o--> ProcessCatalog
    Service --|> ProcessCatalog
    ProcessCatalog ..> ProcessList : obtain
    ProcessCatalog ..> ProcessDescription : obtain
    Service o--> ProcessExecutor
    Service --|> ProcessExecutor
    ProcessExecutor ..> JobList : obtain
    ProcessExecutor ..> JobInfo : obtain
    ProcessExecutor ..> JobResult : obtain   
    ProcessExecutor ..> ProcessRequest : use      
```

## Code generation

```mermaid
---
config:
  theme: default
---
flowchart LR
    openapi@{ shape: lean-r, label: "openapi.yaml" }
    local_service@{ shape: stadium, label: "s2gos_server.services.local.testing:service" }
    dags@{ shape: stadium, label: "s2gos_airflow/dags" }
    sync_client@{ shape: stadium, label: "s2gos_client.api.Client" }
    async_client@{ shape: stadium, label: "s2gos_client.api.AsyncClient" }
    models@{ shape: stadium, label: "s2gos_common.models.*" }
    service@{ shape: stadium, label: "s2gos_common.service.Service" }
    routes@{ shape: stadium, label: "s2gos_server.routes" }
    openapi --> generate
    generate --> gen-client
    generate --> gen-common
    generate --> gen-server
    gen-client --> sync_client
    gen-client --> async_client
    gen-common --> models
    gen-common --> service
    gen-server --> routes
    local_service --> gen-dags
    gen-dags --> dags
```