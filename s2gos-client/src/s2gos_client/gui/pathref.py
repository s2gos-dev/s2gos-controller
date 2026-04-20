#  Copyright (c) 2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import panel as pn
import param

from gavicore.ui import FieldMeta, FieldContext
from gavicore.ui.vm import ViewModel
from gavicore.ui.providers.panel import (
    PanelField,
    PanelFieldFactoryBase,
)


class PathRefEditor(pn.widgets.WidgetBase, pn.custom.PyComponent):
    value = param.Dict(default={"uri": "", "cid": ""})
    description = param.String(default="", allow_None=True)

    def __init__(self, **params):
        super().__init__(**params)

        self._uri_input = pn.widgets.TextInput(
            name=f"{self.name + ' ' if self.name else ''}URI",
            placeholder="URI or rel. path...",
            value=self.value["uri"],
            width=300,
            description=self.description or "",
        )

        self._cid_input = pn.widgets.TextInput(
            name="Credentials ID",
            value=self.value["cid"],
            width=300,
        )

        self._uri_input.link(self, value="uri")
        self._cid_input.link(self, value="cid")
        self._uri_input.param.watch(self._on_uri_change, "value")
        self._cid_input.param.watch(self._on_cid_change, "value")
        self.param.watch(self._on_value_change, "value")

    def __panel__(self):
        return pn.Column(
            self._uri_input,
            self._cid_input,
        )

    def _on_uri_change(self, e):
        self.value = dict(uri=e.new, cid=self.value["cid"])

    def _on_cid_change(self, e):
        self.value = dict(uri=self.value["uri"], cid=e.new)

    def _on_value_change(self, _e):
        uri, cid = self.value["uri"], self.value["cid"]
        if self._uri_input.value != uri:
            self._uri_input.value = uri
        if self._cid_input.value != cid:
            self._cid_input.value = cid


class PathRefEditorFactory(PanelFieldFactoryBase):
    def get_object_score(self, meta: FieldMeta) -> int:
        assert meta.properties is not None
        return 10 if {"uri", "cid"}.issubset(set(meta.properties.keys())) else 0

    def create_object_field(self, ctx: FieldContext) -> PanelField:
        view_model: ViewModel = ctx.vm.primitive()
        view = PathRefEditor(
            value=view_model.value, name=ctx.label, description=ctx.meta.description
        )
        return PanelField(view_model=view_model, view=view)
