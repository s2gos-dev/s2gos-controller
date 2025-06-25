#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any, Callable, Optional, TypeAlias

import pandas as pd
import panel as pn
import param
from pydantic import BaseModel
from s2gos_client.exceptions import ClientException
from s2gos_common.models import JobInfo, JobList, JobResults, JobStatus

JobAction: TypeAlias = Callable[[str], Any]


class JobsForm(pn.viewable.Viewer):
    _jobs = param.List(default=[], doc="List of current jobs")

    def __init__(
        self,
        job_list: JobList,
        job_list_error: ClientException | None,
        on_delete_job: Optional[JobAction] = None,
        on_cancel_job: Optional[JobAction] = None,
        on_restart_job: Optional[JobAction] = None,
        on_get_job_results: Optional[JobAction] = None,
    ):
        super().__init__()
        # TODO: Report job_list_error if not None
        self._job_list_error = job_list_error
        self._on_delete_job = on_delete_job
        self._on_cancel_job = on_cancel_job
        self._on_restart_job = on_restart_job
        self._on_get_job_results = on_get_job_results
        self._tabulator = self._new_tabulator(job_list)
        self._tabulator.param.watch(self._update_buttons, "selection")
        # A placeholder for clicked action
        self._cancel_button = pn.widgets.Button(
            name="Cancel",
            # tooltip="Cancels the selected job(s)",
            button_type="primary",
            on_click=self._on_cancel_jobs_clicked,
            disabled=True,
        )
        self._delete_button = pn.widgets.Button(
            name="Delete",
            # tooltip="Deletes the selected job(s)",
            button_type="danger",
            on_click=self._on_delete_jobs_clicked,
            disabled=True,
        )
        self._restart_button = pn.widgets.Button(
            name="Restart",
            # tooltip="Restarts the selected job(s)",
            button_type="primary",
            on_click=self._on_restart_jobs_clicked,
            disabled=True,
        )
        self._get_results_button = pn.widgets.Button(
            name="Get Results",
            # tooltip="Gets the results from the selected job(s)",
            button_type="primary",
            on_click=self._on_get_job_result_clicked,
            disabled=True,
        )
        self._action_row = pn.Row(
            self._cancel_button,
            self._delete_button,
            self._restart_button,
            self._get_results_button,
        )
        self._message_md = pn.pane.Markdown("")
        self._view = pn.Column(
            self._action_row,
            self._tabulator,
            self._message_md,
        )

        # Reaction to changes in jobs list
        self.param.watch(self._on_jobs_changed, "_jobs")
        self.set_job_list(job_list, job_list_error)

    def __panel__(self) -> pn.viewable.Viewable:
        return self._view

    def set_job_list(self, job_list: JobList, job_list_error: ClientException | None):
        self._jobs = job_list.jobs
        self._job_list_error = job_list_error

    def _on_jobs_changed(self, _event: Any = None):
        """Will be called automatically, if self.jobs changes."""
        df = self._jobs_to_dataframe(self._jobs)
        self._tabulator.value = df

    def _update_buttons(self, _event: Any = None):
        """Will be called if selection changes."""

        selected_jobs = self.selected_jobs

        self._cancel_button.disabled = self._on_cancel_job is None or self.is_disabled(
            selected_jobs, {JobStatus.accepted, JobStatus.running}
        )
        self._delete_button.disabled = self._on_delete_job is None or self.is_disabled(
            selected_jobs,
            {JobStatus.successful, JobStatus.dismissed, JobStatus.failed},
        )
        self._restart_button.disabled = (
            self._on_restart_job is None
            or self.is_disabled(
                selected_jobs,
                {JobStatus.successful, JobStatus.dismissed, JobStatus.failed},
            )
        )
        self._get_results_button.disabled = (
            self._on_get_job_results is None
            or len(selected_jobs) != 1
            or self.is_disabled(selected_jobs, {JobStatus.successful, JobStatus.failed})
        )

    @classmethod
    def is_disabled(cls, jobs: list[JobInfo], requirements: set[JobStatus]):
        return not jobs or not all(j.status in requirements for j in jobs)

    @property
    def selected_jobs(self) -> list[JobInfo]:
        """Get selected jobs from jobs table."""
        selection = self._tabulator.selection
        if not selection:
            return []
        selected_ids = {self._jobs[row].jobID for row in selection}
        return [job for job in self._jobs if job.jobID in selected_ids]

    def _on_cancel_jobs_clicked(self, _event: Any):
        self._run_action_on_selected_jobs(
            self._on_cancel_job,
            "✅ Cancelled {job}",
            "⚠️ Failed cancelling {job}: {message}",
        )

    def _on_delete_jobs_clicked(self, _event: Any):
        self._run_action_on_selected_jobs(
            self._on_delete_job,
            "✅ Deleted {job}",
            "⚠️ Failed deleting {job}: {message}",
        )

    def _on_restart_jobs_clicked(self, _event: Any):
        self._run_action_on_selected_jobs(
            self._on_restart_job,
            "✅ Restarted {job}",
            "⚠️ Failed restarting {job}: {message}",
        )

    def _on_get_job_result_clicked(self, _event: Any):
        def handle_results(_job_id: str, results: JobResults | dict):
            # noinspection PyProtectedMember
            from IPython import get_ipython

            if isinstance(results, JobResults):
                results = results.root
            if isinstance(results, dict):
                results = JsonDict(
                    {
                        k: (v.model_dump() if isinstance(v, BaseModel) else v)
                        for k, v in results.items()
                    }
                )
            var_name = "_results"
            get_ipython().user_ns[var_name] = results
            return "✅ Stored results of {job} " + f"in variable **`{var_name}`**"

        self._run_action_on_selected_jobs(
            self._on_get_job_results,
            handle_results,
            "⚠️ Failed to get results for {job}: {message}",
        )

    def _run_action_on_selected_jobs(
        self,
        action: JobAction,
        success_format: str | Callable[[str, Any], str] | None,
        error_format: str,
    ):
        messages = []
        for job in self.selected_jobs:
            job_id = job.jobID
            job_text = f"job `{job_id}`"
            try:
                result = action(job_id)
                if isinstance(success_format, str):
                    messages.append(success_format.format(job=job_text))
                elif callable(success_format):
                    messages.append(success_format(job_id, result).format(job=job_text))
            except ClientException as e:
                messages.append(
                    error_format.format(
                        job=job_text,
                        message=f"{e.title} (status `{e.status_code}`): {e.detail}",
                    )
                )
        self._message_md.object = " \n".join(messages)

    @classmethod
    def _new_tabulator(cls, job_list: JobList) -> pn.widgets.Tabulator:
        dataframe = cls._jobs_to_dataframe(job_list.jobs)

        tabulator = pn.widgets.Tabulator(
            dataframe,
            theme="default",
            width=600,
            height=300,
            layout="fit_data",
            show_index=False,
            editors={},  # No editing
            # selectable=False,
            disabled=True,
            configuration={
                "columns": [
                    {"title": "Process ID", "field": "process_id"},
                    {"title": "Job ID", "field": "job_id"},
                    {"title": "Status", "field": "status"},
                    {
                        "title": "Progress",
                        "field": "progress",
                        "formatter": "progress",
                        "formatterParams": {
                            "min": 0,
                            "max": 100,
                            "color": [
                                "#f00",
                                "#ffa500",
                                "#ff0",
                                "#0f0",
                            ],  # red → orange → yellow → green
                        },
                    },
                    {"title": "Message", "field": "message"},
                    {
                        "title": "  ",
                        "field": "action",
                        "hozAlign": "center",
                        "formatter": "plaintext",
                        "cellClick": True,  # Needed to enable cell-level events
                        "cssClass": "action-cell",  # We'll style this column
                    },
                ]
            },
        )

        return tabulator

    @classmethod
    def _jobs_to_dataframe(cls, jobs: list[JobInfo]):
        return pd.DataFrame([cls._job_to_dataframe_row(job) for job in jobs])

    @classmethod
    def _job_to_dataframe_row(cls, job: JobInfo):
        return {
            "process_id": job.processID,
            "job_id": job.jobID,
            "status": job.status.value,
            "progress": job.progress or 0,
            "message": job.message or "-",
        }


class JsonDict(dict):
    def _repr_json_(self):
        return self, {"root": "Results:"}
