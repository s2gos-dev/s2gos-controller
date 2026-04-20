#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from gavicore.models import Schema
from gavicore.ui import FieldMeta, FieldGenerator, FieldContext
from gavicore.ui.providers.panel import PanelField
from gavicore.ui.vm import PrimitiveViewModel

import s2gos_client.gui
from s2gos_client.gui import ClientConfig
from s2gos_client.gui.pathref import PathRefEditorFactory, PathRefEditor


def test_gui_ok():
    assert {"Client", "ClientConfig"}.issubset(dir(s2gos_client.gui))


def test_extra_panel_field_registered():
    config = ClientConfig.default_config
    field_factory_registry = config.get_field_factory_registry()
    field_meta = FieldMeta.from_schema(
        "aux_file",
        Schema(
            **{
                "type": "object",
                "properties": {
                    "uri": {"type": "string"},
                    "cid": {"type": "string"},
                },
                "required": ["uri"],
            }
        ),
    )
    factory = field_factory_registry.lookup(field_meta)
    assert isinstance(factory, PathRefEditorFactory)

    assert factory.get_score(field_meta) == 10

    initial_value = {"uri": "data/aux-2.bin", "cid": ""}
    ctx = FieldContext(
        generator=FieldGenerator(),
        meta=field_meta,
        initial_value=initial_value,
    )
    field = factory.create_field(ctx)

    assert isinstance(field, PanelField)
    assert isinstance(field.view_model, PrimitiveViewModel)
    assert isinstance(field.view, PathRefEditor)

    assert field.view_model.value == initial_value
    assert field.view.value == initial_value

    field.view._uri_input.value = "data/aux-1.bin"
    field.view._cid_input.value = "EF8DA78A001F17387B"
    assert field.view_model.value == {
        "uri": "data/aux-1.bin",
        "cid": "EF8DA78A001F17387B",
    }
