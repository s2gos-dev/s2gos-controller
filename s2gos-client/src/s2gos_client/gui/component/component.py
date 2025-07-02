#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any, Callable, Optional

import panel as pn
import param

from .types import (
    JsonCodec,
    JsonIdentityCodec,
    JsonValue,
)


class Component(param.Parameterized):
    def __init__(
        self, viewable: pn.viewable.Viewable, json_codec: Optional[JsonCodec] = None
    ):
        super().__init__()
        self.viewable = viewable
        self.json_codec = JsonIdentityCodec() if json_codec is None else json_codec

    def __panel__(self) -> pn.viewable.Viewable:
        return self.viewable

    def get_json_value(self) -> Any:
        """Get the viewable's value as a json value."""
        return self.json_codec.encode(self.get_value())

    def set_json_value(self, json_value: JsonValue):
        """Sets the viewable's value from a json value."""
        self.set_value(self.json_codec.decode(json_value))

    def get_value(self) -> Any:
        """Get the viewable's value."""

    def set_value(self, value: Any):
        """Sets the viewable's value."""

    def watch_value(self, callback: Callable[[Any, Any], Any]):
        """Watch for value changes in the viewable."""


class WidgetComponent(Component):
    def __init__(self, widget: pn.widgets.Widget, json_codec: JsonCodec | None = None):
        super().__init__(widget, json_codec=json_codec)

    @property
    def widget(self) -> pn.widgets.Widget:
        # noinspection PyTypeChecker
        return self.viewable

    def watch_value(self, callback: Callable[[Any, Any], Any]):
        """Watch for value changes in the viewable."""
        self.widget.param.watch(callback, "value")

    def get_value(self) -> Any:
        """Get the viewable's value."""
        return self.widget.value

    def set_value(self, value: Any):
        """Sets the viewable's value."""
        self.widget.value = value
