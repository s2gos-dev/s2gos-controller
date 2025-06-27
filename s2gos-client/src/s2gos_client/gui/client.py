#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import threading
import time
from typing import Optional

from s2gos_client.api.client import Client as GeneratedClient
from s2gos_client.api.error import ClientError
from s2gos_client.api.transport import Transport
from s2gos_client.gui.jobs_form import JobsForm
from s2gos_client.gui.main_form import MainForm
from s2gos_common.models import JobList, ProcessList


class Client(GeneratedClient):
    def __init__(
        self,
        *,
        update_interval: float = 2.0,
        _transport: Optional[Transport] = None,
        **config,
    ):
        super().__init__(_transport=_transport, **config)
        self._update_interval = update_interval
        self._update_thread: Optional[threading.Thread] = None
        self._main_form: Optional[MainForm] = None
        self._jobs_form: Optional[JobsForm] = None

    def show(self):
        if self._main_form is None:
            self._main_form = MainForm(
                *self._get_processes(),
                on_get_process=self.get_process,
                on_execute_process=self.execute_process,
            )
        return self._main_form

    def show_jobs(self):
        if self._jobs_form is None:
            self._jobs_form = JobsForm(
                *self._get_jobs(),
                on_cancel_job=self._cancel_job,
                on_delete_job=self._delete_job,
                on_restart_job=self._restart_job,
                on_get_job_results=self.get_job_results,
            )

        if self._update_thread is None or not self._update_thread.is_alive():
            self._update_thread = threading.Thread(
                target=self._run_updater, daemon=True
            )
            self._update_thread.start()

        return self._jobs_form

    def stop_updating(self):
        self._update_thread = None

    def _cancel_job(self, job_id: str):
        return self.dismiss_job(job_id)

    def _delete_job(self, job_id: str):
        return self.dismiss_job(job_id)

    # noinspection PyMethodMayBeStatic
    def _restart_job(self, _job_id: str):
        # TODO: implement job restart
        print("Not implemented.")

    def __delete__(self, instance):
        self._update_thread = None
        self._jobs_form = None

    def _run_updater(self):
        while self._update_thread is not None:
            time.sleep(self._update_interval)
            if self._jobs_form is not None:
                self._jobs_form.set_job_list(*self._get_jobs())

    def _get_processes(self) -> tuple[ProcessList, ClientError | None]:
        try:
            return self.get_processes(), None
        except ClientError as e:
            return ProcessList(processes=[], links=[]), e

    def _get_jobs(self) -> tuple[JobList, ClientError | None]:
        try:
            return self.get_jobs(), None
        except ClientError as e:
            return JobList(jobs=[], links=[]), e
