#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
import datetime
from typing import Any, Callable, TypeAlias

import panel as pn
import param
from s2gos_client.exceptions import ClientException
from s2gos_client.gui.widget_factory import WidgetFactory
from s2gos_common.models import (
    Format,
    JobInfo,
    Output,
    ProcessDescription,
    ProcessList,
    ProcessRequest,
    TransmissionMode,
)

ExecuteProcessAction: TypeAlias = Callable[[str, ProcessRequest], JobInfo]
GetProcessAction: TypeAlias = Callable[[str], ProcessDescription]


class MainForm(pn.viewable.Viewer):
    _processes = param.List(default=[], doc="List of process summaries")
    _processes_dict = param.Dict(default={}, doc="Dictionary of cached processes")

    def __init__(
        self,
        process_list: ProcessList,
        process_list_error: ClientException | None,
        on_get_process: GetProcessAction,
        on_execute_process: ExecuteProcessAction,
    ):
        super().__init__()
        self._processes = process_list.processes
        self._process_list_error = process_list_error

        self._on_execute_process = on_execute_process
        self._on_get_process = on_get_process

        process_select_options = [p.id for p in process_list.processes]
        if process_select_options:
            process_id = process_select_options[0]
        else:
            process_id = process_select_options

        self._process_select = pn.widgets.Select(
            name="Process",
            options=process_select_options,
            value=process_select_options[0] if process_select_options else None,
        )
        self._process_select.param.watch(
            lambda e: self._on_process_id_changed(e.new), "value"
        )

        self._process_doc_markdown = pn.pane.Markdown("")
        process_panel = pn.Column(
            # pn.pane.Markdown("# Process"),
            self._process_select,
            self._process_doc_markdown,
        )

        self._execute_button = pn.widgets.Button(
            name="Execute",
            # tooltip="Executes the selected process with the current request",
            button_type="primary",
            on_click=self._on_execute_button_clicked,
            disabled=True,
        )
        self._open_button = pn.widgets.Button(
            name="Open",
            on_click=self._on_open_request_clicked,
            disabled=True,
        )
        self._save_button = pn.widgets.Button(
            name="Save",
            on_click=self._on_save_request_clicked,
            disabled=True,
        )
        self._save_as_button = pn.widgets.Button(
            name="Save As...",
            on_click=self._on_save_as_request_clicked,
            disabled=True,
        )
        self._request_button = pn.widgets.Button(
            name="Get Request",
            on_click=self._on_get_process_request,
            disabled=True,
        )

        action_panel = pn.Row(
            self._execute_button,
            self._open_button,
            self._save_button,
            self._save_as_button,
            self._request_button,
        )

        self._inputs_panel = pn.Column()
        self._outputs_panel = pn.Column()

        self._view = pn.Column(
            process_panel,
            self._inputs_panel,
            self._outputs_panel,
            action_panel,
        )

        self._input_widgets = {}
        self._output_widgets = {}

        self._on_process_id_changed(process_id)

    def __panel__(self) -> pn.viewable.Viewable:
        return self._view

    def _on_process_id_changed(self, process_id: str | None = None):
        process_description: ProcessDescription | None = None
        process_markdown: str | None = None
        if not process_id:
            process_markdown = "_No process selected._"
        else:
            if process_id in self._processes_dict:
                process_description = self._processes_dict[process_id]
            else:
                try:
                    process_description = self._on_get_process(process_id)
                    self._processes_dict[process_id] = process_description
                except ClientException as e:
                    process_description = None
                    process_markdown = (
                        f"**Error**: {e.title} (status `{e.status_code}`): {e.detail}"
                    )
            if process_description:
                process_markdown = (
                    f"**{process_description.title}**\n\n"
                    f"{process_description.description}"
                )

        self._process_doc_markdown.object = process_markdown
        if not process_description:
            self._execute_button.disabled = True
            self._request_button.disabled = True
            self._input_widgets = {}
            self._output_widgets = {}
        else:
            self._execute_button.disabled = False
            self._request_button.disabled = False
            self._input_widgets = {
                param_name: WidgetFactory().get_widget_for_schema(
                    param_name,
                    input_description.schema_.model_dump(
                        mode="json", exclude_defaults=True
                    ),
                    False,
                )
                for param_name, input_description in (
                    process_description.inputs or {}
                ).items()
            }
            self._output_widgets = {}

        self._inputs_panel[:] = self._input_widgets.values()
        self._outputs_panel[:] = self._output_widgets.values()

    def _on_execute_button_clicked(self, _event: Any = None):
        process_id, process_request = self._new_process_request()
        try:
            self._execute_button.disabled = True
            _job_info = self._on_execute_process(process_id, process_request)
            # TODO: Show status info in GUI
        except ClientException as e:
            # TODO: Show error in GUI
            print(f"error: {e}")
        finally:
            self._execute_button.disabled = False

    def _on_open_request_clicked(self, _event: Any = None):
        # TODO implement open request
        pass

    def _on_save_request_clicked(self, _event: Any = None):
        # TODO implement save request
        pass

    def _on_save_as_request_clicked(self, _event: Any = None):
        # TODO implement save request as
        pass

    def _on_get_process_request(self, _event: Any = None):
        # noinspection PyProtectedMember
        from IPython import get_ipython

        _, process_request = self._new_process_request()
        var_name = "_request"
        get_ipython().user_ns[var_name] = process_request

    def _update_buttons(self):
        # TODO implement action enablement
        pass

    def _new_process_request(self) -> tuple[str, ProcessRequest]:
        process_id = self._process_select.value
        assert process_id is not None
        process_description = self._processes_dict.get(process_id)
        assert process_description is not None
        return process_id, ProcessRequest(
            inputs={
                # TODO: This is not nice for several reasons
                #  (see WidgetFactory TODOs):
                #  1. v.value: we don't know if a widget has a `value`
                #     attribute
                #  2. _serialize_for_json(): we cannot know what value type
                #     a widget uses
                k: _serialize_for_json(v.value)
                for k, v in self._input_widgets.items()
            },
            outputs={
                k: Output(
                    format=Format(
                        mediaType="application/json",
                        encoding="UTF-8",
                        schema=v.schema_,
                    ),
                    transmissionMode=TransmissionMode.value,
                )
                for k, v in process_description.outputs.items()
            },
        )


def _serialize_for_json(value: Any):
    # check if there are more cases to be handled
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value
