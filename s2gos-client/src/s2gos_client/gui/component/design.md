The design used in this package:

```mermaid
classDiagram

Component : get_value()
Component : set_value()
Component: \_\_panel\_\_()
Component : viewable
Component : json_codec

Component <|-- WidgetComponent
panel.viewable.Viewable <|-- Component

ComponentFactory ..> Component : create

ComponentFactoryRegistry o-- ComponentFactory
```
