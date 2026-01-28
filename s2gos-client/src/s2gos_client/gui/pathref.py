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

    path = param.String(default="")
    cid = param.String(default="")

    disabled = param.Boolean(default=False)

    def __init__(self, **params):
        super().__init__(**params)

        self._path_input = pn.widgets.TextInput(
            name="Path",
            placeholder="Path or URL...",
            value=self.path,
            disabled=self.param.disabled,
        )

        self._cid_input = pn.widgets.TextInput(
            name="CID",
            placeholder="CID...",
            value=self.cid,
            disabled=self.param.disabled,
        )

        # widget ↔ param (two-way, explicit)
        self._path_input.link(self, value="path")
        self._cid_input.link(self, value="cid")

        header = (
            pn.pane.Markdown(
                f"**{self.title}**",
                tooltip=self.tooltip,
            )
            if self.title
            else None
        )

        self.view = pn.Column(
            *([header] if header else []),
            self._path_input,
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

    def get_value(self) -> dict[str, Any]:
        return {
            "value": self.path_ref_editor.path,
            "cid": self.path_ref_editor.cid or None,
        }

    def set_value(self, value: dict[str, Any]):
        self.path_ref_editor.path = value.get("value") or ""
        self.path_ref_editor.cid = value.get("cid") or ""

    def watch_value(self, callback: Callable[[Any], Any]):
        self.path_ref_editor.param.watch(callback, ["path", "cid"])


class PathRefEditorFactory(ComponentFactoryBase):
    type = "object"
    format = "path_ref"

    def create_component(
        self, value: JsonValue, title: str, schema: JsonSchemaDict
    ) -> Component:
        path_ref: dict[str, Any] = value
        return PathRefComponent(
            PathRefEditor(
                title=title,
                path=path_ref.get("value") or "",
                cid=path_ref.get("cid") or "",
            )
        )


def register_component():
    PathRefEditorFactory.register_in(ComponentContainer.registry)
