#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase

from panel.layout import Panel

from s2gos_client.gui.main_form import MainForm
from s2gos_common.models import (
    InputDescription,
    JobInfo,
    JobStatus,
    JobType,
    ProcessDescription,
    ProcessList,
    ProcessRequest,
    Schema,
)

bbox_input = InputDescription(
    title="Bounding box",
    schema=Schema.model_validate(
        {
            "type": "array",
            "items": {"type": "number"},
            "format": "bbox",
        }
    ),
)

date_input = InputDescription(
    title="Date",
    schema=Schema.model_validate(
        {
            "type": "string",
            "format": "date",
            "default": "2025-01-01",
        }
    ),
)

int_input = InputDescription(
    title="Periodicity",
    schema=Schema.model_validate(
        {
            "type": "integer",
            "minimum": 1,
            "maximum": 10,
        },
    ),
)


class MainFormTest(TestCase):
    def test_with_int_input(self):
        main_form = _create_main_form({"periodicity": int_input})
        self.assertIsInstance(main_form.__panel__(), Panel)

    def test_with_bbox_input(self):
        main_form = _create_main_form({"bbox": bbox_input})
        self.assertIsInstance(main_form.__panel__(), Panel)

    def test_with_date_input(self):
        main_form = _create_main_form({"date": date_input})
        self.assertIsInstance(main_form.__panel__(), Panel)


def _create_main_form(process_inputs: dict[str, InputDescription]) -> MainForm:
    process = ProcessDescription(
        id="gen_scene",
        title="Generate a scene",
        version="1",
        inputs=process_inputs,
    )

    def on_get_process(_process_id: str):
        return process

    def on_execute_process(process_id: str, _request: ProcessRequest):
        return JobInfo(
            processID=process_id,
            jobID="job_8",
            type=JobType.process,
            status=JobStatus.successful,
        )

    process_list = ProcessList(processes=[process], links=[])

    return MainForm(
        process_list,
        None,
        on_get_process=on_get_process,
        on_execute_process=on_execute_process,
    )
