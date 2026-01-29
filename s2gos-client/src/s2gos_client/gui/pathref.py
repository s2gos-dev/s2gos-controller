#  Copyright (c) 2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
from typing import Any, Callable

import panel as pn
import param

from cuiman.gui.component import (
    Component,
    ComponentContainer,
    ComponentFactoryBase,
    JsonValue,
    JsonSchemaDict,
)


class PathRefEditor(pn.viewable.Viewer):
    title = param.String(default="")
    tooltip = param.String(default=None, allow_None=True)

    value = param.String(default="")
    cid = param.String(default="")

    disabled = param.Boolean(default=False)

    def __init__(self, **params):
        super().__init__(**params)

        self._value_input = pn.widgets.TextInput(
            name=f"{self.title} URI",
            placeholder="URI or rel. path...",
            value=self.value,
            disabled=self.param.disabled,
            width=300,
        )

        self._cid_input = pn.widgets.TextInput(
            name=f"{self.title} CID (optional)",
            placeholder="Credentials ID...",
            value=self.cid,
            disabled=self.param.disabled,
            width=120,
        )

        # widget ↔ param (two-way, explicit)
        self._value_input.link(self, value="value")
        self._cid_input.link(self, value="cid")

        # TODO: set tooltip (how?)
        self.view = pn.Row(
            self._value_input,
            self._cid_input,
        )

    def __panel__(self):
        return self.view


class PathRefComponent(Component):
    def __init__(self, editor: PathRefEditor):
        # noinspection PyTypeChecker
        super().__init__(editor)

    @property
    def path_ref_editor(self) -> PathRefEditor:
        # noinspection PyTypeChecker
        return self.viewable

    def get_value(self) -> dict[str, Any] | None:
        value = self.path_ref_editor.value
        cid = self.path_ref_editor.cid
        if not (value and cid):
            return None
        return {"value": value, "cid": cid or None}

    def set_value(self, value: dict[str, Any] | None):
        self.path_ref_editor.value = value.get("value") or ""
        self.path_ref_editor.cid = value.get("cid") or ""

    def watch_value(self, callback: Callable[[Any], Any]):
        self.path_ref_editor.param.watch(callback, ["value", "cid"])


class PathRefEditorFactory(ComponentFactoryBase):
    type = "object"
    format = "PathRef"

    def create_component(
        self, value: JsonValue, title: str, schema: JsonSchemaDict
    ) -> Component:
        path_ref: dict[str, Any] | None = value
        return PathRefComponent(
            PathRefEditor(
                title=title,
                value=(path_ref and path_ref.get("value")) or "",
                cid=(path_ref and path_ref.get("cid")) or "",
                tooltip=schema.get("description"),
            )
        )


def register_component():
    PathRefEditorFactory.register_in(ComponentContainer.registry)
