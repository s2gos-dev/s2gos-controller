#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any

import panel
import panel as pn

from s2gos_client import ClientError
from s2gos_common.models import JobInfo, JobList

from .jobs_observer import JobsObserver


class JobInfoPanel(pn.viewable.Viewer):
    def __init__(self):
        super().__init__()

        self._job_info: JobInfo | None = None
        self._client_error: ClientError | None = None

        self._message_pane = panel.pane.Markdown()
        self._view = pn.Column([self._message_pane])

        self._render_view()

    def __panel__(self) -> pn.viewable.Viewable:
        return self._view

    def set_job_info(self, job_info: JobInfo | None):
        self._job_info = job_info
        self._render_view()

    def set_client_error(self, client_error: ClientError | None):
        self._client_error = client_error
        self._render_view()

    def on_job_added(self, job_info: JobInfo):
        self.on_job_changed(job_info)

    def on_job_changed(self, job_info: JobInfo):
        if self._is_observed_job(job_info):
            self.set_job_info(job_info)

    def on_job_removed(self, job_info: JobInfo):
        if self._is_observed_job(job_info):
            self._message_pane.object = (
                f"Job with ID=`{job_info.jobID}` has been deleted."
            )
            self.set_job_info(None)

    def on_job_list_changed(self, job_list: JobList):
        # Nothing to do
        pass

    def on_job_list_error(self, client_error: ClientError | None):
        self.set_client_error(client_error)

    def _is_observed_job(self, job_info):
        return self._job_info is not None and self._job_info.jobID == job_info.jobID

    def _render_view(self):
        # TODO: render self._client_error

        job_info: JobInfo = self._job_info
        if job_info is None:
            self._message_pane.object = "No job selected."
            self._view.objects[:] = [self._message_pane]
            return

        def _to_value(value: Any, units: str = ""):
            return f"{value}{units}" if value is not None else "-"

        column1 = pn.Column(
            pn.widgets.StaticText(name="Process ID", value=job_info.processID),
            pn.widgets.StaticText(name="Job ID", value=job_info.jobID),
            pn.widgets.StaticText(name="Status", value=job_info.status),
            pn.widgets.StaticText(
                name="Progress", value=_to_value(job_info.progress, "%")
            ),
        )
        column2 = pn.Column(
            pn.widgets.StaticText(name="Created", value=_to_value(job_info.created)),
            pn.widgets.StaticText(name="Started", value=_to_value(job_info.started)),
            pn.widgets.StaticText(name="Updated", value=_to_value(job_info.updated)),
            pn.widgets.StaticText(name="Finished", value=_to_value(job_info.finished)),
        )
        self._message_pane.object = job_info.message or ""
        self._view.objects[:] = [self._message_pane, pn.Row(column1, column2)]


JobsObserver.register(JobInfoPanel)
