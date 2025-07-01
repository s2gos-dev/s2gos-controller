#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import panel as pn

from .provider import JsonSchema, JsonValue, WidgetViewableProvider


class BooleanViewableProvider(WidgetViewableProvider):
    type = "boolean"
    nullable = False

    def get_widget(self, schema: JsonSchema, **extras: JsonValue) -> pn.widgets.Widget:
        return pn.widgets.Checkbox(name=extras["title"], value=extras["value"])
