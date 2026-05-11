#  Copyright (c) 2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import panel as pn

from gavicore.models import Schema
from gavicore.ui import FieldContext, FieldGenerator, FieldMeta
from gavicore.ui.panel import PanelField
from gavicore.ui.vm import PrimitiveViewModel

from s2gos_client.gui.pathref import PathRefEditor, PathRefEditorFactory

pn.extension()


def _path_ref_meta(
    properties: dict | None = None,
    *,
    title: str = "Aux file",
    description: str = "Auxiliary input file",
) -> FieldMeta:
    return FieldMeta.from_schema(
        "aux_file",
        Schema(
            **{
                "type": "object",
                "title": title,
                "description": description,
                "properties": properties
                if properties is not None
                else {
                    "value": {"type": "string"},
                    "cid": {"type": "string"},
                },
                "required": ["value"],
            }
        ),
    )


def _path_ref_context(initial_value: dict) -> FieldContext:
    return FieldContext(
        generator=FieldGenerator(),
        meta=_path_ref_meta(),
        initial_value=initial_value,
    )


def test_path_ref_editor_initializes_inputs_from_value():
    editor = PathRefEditor(
        name="Aux file",
        description="Auxiliary input file",
        value={"value": "data/aux.bin", "cid": "ABC123"},
    )

    assert editor.value == {"value": "data/aux.bin", "cid": "ABC123"}
    assert editor._uri_input.name == "Aux file URI"
    assert editor._uri_input.description == "Auxiliary input file"
    assert editor._uri_input.value == "data/aux.bin"
    assert editor._cid_input.name == "Credentials ID"
    assert editor._cid_input.value == "ABC123"


def test_path_ref_editor_uses_empty_strings_for_missing_value_parts():
    editor = PathRefEditor(value={})

    assert editor.value == {"value": "", "cid": ""}
    assert editor._uri_input.value == ""
    assert editor._cid_input.value == ""


def test_path_ref_editor_updates_value_when_uri_input_changes():
    editor = PathRefEditor(value={"value": "data/old.bin", "cid": "ABC123"})

    editor._uri_input.value = "data/new.bin"

    assert editor.value == {"value": "data/new.bin", "cid": "ABC123"}
    assert editor._cid_input.value == "ABC123"


def test_path_ref_editor_updates_value_when_cid_input_changes():
    editor = PathRefEditor(value={"value": "data/aux.bin", "cid": ""})

    editor._cid_input.value = "DEF456"

    assert editor.value == {"value": "data/aux.bin", "cid": "DEF456"}
    assert editor._uri_input.value == "data/aux.bin"


def test_path_ref_editor_updates_inputs_when_value_changes():
    editor = PathRefEditor(value={"value": "data/old.bin", "cid": "ABC123"})

    editor.value = {"value": "data/new.bin", "cid": "DEF456"}

    assert editor._uri_input.value == "data/new.bin"
    assert editor._cid_input.value == "DEF456"


def test_path_ref_editor_renders_uri_and_cid_inputs():
    editor = PathRefEditor(value={"value": "data/aux.bin", "cid": "ABC123"})

    layout = editor.__panel__()

    assert isinstance(layout, pn.Column)
    assert list(layout) == [editor._uri_input, editor._cid_input]
    assert layout.margin == (6, 0, 6, 0)


def test_path_ref_editor_factory_scores_path_ref_object_schema():
    factory = PathRefEditorFactory()

    assert factory.get_score(_path_ref_meta()) == 10


def test_path_ref_editor_factory_scores_zero_for_other_object_schemas():
    factory = PathRefEditorFactory()

    assert factory.get_score(_path_ref_meta({"value": {"type": "string"}})) == 0
    assert factory.get_score(_path_ref_meta({"cid": {"type": "string"}})) == 0
    assert factory.get_score(_path_ref_meta({"href": {"type": "string"}})) == 0


def test_path_ref_editor_factory_creates_bound_panel_field():
    factory = PathRefEditorFactory()
    initial_value = {"value": "data/aux.bin", "cid": "ABC123"}

    field = factory.create_field(_path_ref_context(initial_value))

    assert isinstance(field, PanelField)
    assert isinstance(field.view_model, PrimitiveViewModel)
    assert isinstance(field.view, PathRefEditor)
    assert field.view_model.value == initial_value
    assert field.view.value == initial_value
    assert field.view._uri_input.name == "Aux file URI"
    assert field.view._uri_input.description == "Auxiliary input file"

    field.view._uri_input.value = "data/updated.bin"
    field.view._cid_input.value = "DEF456"

    assert field.view_model.value == {"value": "data/updated.bin", "cid": "DEF456"}


def test_path_ref_editor_factory_uses_empty_value_for_empty_initial_value():
    factory = PathRefEditorFactory()

    field = factory.create_field(_path_ref_context({}))

    assert field.view_model.value == {"value": "", "cid": ""}
    assert field.view.value == {"value": "", "cid": ""}
