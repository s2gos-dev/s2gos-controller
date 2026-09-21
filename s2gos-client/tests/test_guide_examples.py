"""Check the maintained walkthroughs without requiring a deployed S2GOS service."""

import html
import re
from pathlib import Path
from unittest.mock import Mock

import pytest
import xarray as xr
from cuiman.app import App
from gavicore.models import JobInfo, JobStatus, ProcessRequest
from markdown import markdown
from procodile import Job
from remotestate import ServeResult
from typer.testing import CliRunner
from wraptile.services.local.testing import service

from examples.guides import api, app, results
from s2gos_client import Client
from s2gos_client.api import S2GOSConfig
from s2gos_client.cli import cli

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def client():
    client = Mock(spec=Client)
    client.execute_process.return_value = JobInfo(
        jobID="submitted-42", status="accepted"
    )
    return client


@pytest.mark.parametrize("status", list(JobStatus))
def test_session_follows_submitted_job_and_closes(monkeypatch, client, status):
    monkeypatch.setattr(api, "connect", lambda: client)
    client.get_job.return_value = JobInfo(jobID="submitted-42", status=status)
    assert api.main() == "submitted-42"
    client.execute_process.assert_called_once_with(
        "primes_between", request=ProcessRequest(inputs={"min_val": 10, "max_val": 80})
    )
    client.get_job.assert_called_once_with("submitted-42")
    if status == JobStatus.successful:
        client.get_job_results.assert_called_once_with("submitted-42")
    else:
        client.get_job_results.assert_not_called()
    client.close.assert_called_once()


def test_session_closes_when_discovery_fails(monkeypatch, client):
    monkeypatch.setattr(api, "connect", lambda: client)
    client.get_processes.side_effect = RuntimeError("unavailable")
    with pytest.raises(RuntimeError, match="unavailable"):
        api.main()
    client.execute_process.assert_not_called()
    client.close.assert_called_once()


def test_local_connection_overrides_hosted_configuration(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(S2GOSConfig, "default_path", tmp_path / "missing.yaml")
    monkeypatch.setenv("S2GOS_API_URL", "https://example.test/")
    client = api.connect()
    try:
        assert isinstance(client.config, S2GOSConfig)
        assert client.config.api_url == "http://127.0.0.1:8008/"
        assert client.config.auth.auth_type == "none"
    finally:
        client.close()


@pytest.mark.parametrize("display", ["browser", "notebook"])
def test_app_lifetime(monkeypatch, client, display):
    monkeypatch.setattr(app, "create_client", Mock(return_value=client))
    assert app.open_app(display) == (client, client.show_app.return_value)
    client.show_app.assert_called_once_with(display=display, height=640)
    client.close.assert_not_called()
    app.close_app(client, client.show_app.return_value)
    client.show_app.return_value.serve_result.stop.assert_called_once()
    client.close.assert_called_once()


def test_app_launch_failure_closes_client(monkeypatch, client):
    monkeypatch.setattr(app, "create_client", Mock(return_value=client))
    client.show_app.side_effect = RuntimeError("launch failed")
    with pytest.raises(RuntimeError, match="launch failed"):
        app.open_app()
    client.close.assert_called_once()


def test_app_stop_failure_still_closes_client(client):
    instance = Mock(spec=App)
    instance.serve_result.stop.side_effect = RuntimeError("stop failed")
    with pytest.raises(RuntimeError, match="stop failed"):
        app.close_app(client, instance)
    client.close.assert_called_once()


def test_app_updates_only_requested_input():
    instance = App(App.create_remote_store(), Mock(spec=ServeResult))
    with pytest.raises(ValueError, match="Open the sleep_a_while"):
        app.set_duration(instance)
    request = ProcessRequest(
        inputs={"duration": 10, "fail": True},
        outputs={"return_value": {"transmissionMode": "value"}},
    )
    instance.set_process_request("sleep_a_while", request)
    app.set_duration(instance, 2)
    updated = instance.get_process_request("sleep_a_while")
    assert updated.inputs == {"duration": 2, "fail": True}
    assert updated.outputs == request.outputs


def test_app_can_fill_an_empty_request():
    instance = App(App.create_remote_store(), Mock(spec=ServeResult))
    instance.set_process_request("sleep_a_while", ProcessRequest())
    app.set_duration(instance, 3)
    assert instance.get_process_request("sleep_a_while").inputs == {"duration": 3}


def test_app_script_stops_on_interrupt(monkeypatch, client):
    import runpy

    import s2gos_client

    monkeypatch.setattr(s2gos_client, "create_client", Mock(return_value=client))
    monkeypatch.setattr("time.sleep", Mock(side_effect=KeyboardInterrupt))
    runpy.run_path(app.__file__, run_name="__main__")
    client.show_app.return_value.serve_result.stop.assert_called_once()
    client.close.assert_called_once()


def test_api_script_submits_only_once(monkeypatch, client):
    import runpy

    import s2gos_client

    monkeypatch.setattr(s2gos_client, "create_client", Mock(return_value=client))
    client.get_job.return_value = JobInfo(jobID="submitted-42", status="running")
    runpy.run_path(api.__file__, run_name="__main__")
    client.execute_process.assert_called_once()
    client.close.assert_called_once()


@pytest.mark.parametrize(
    "filename,process_id",
    [
        ("primes-request.json", "primes_between"),
        ("simulate-scene-request.json", "simulate_scene"),
    ],
)
def test_cli_requests_validate_offline(filename, process_id):
    result = CliRunner().invoke(
        cli,
        [
            "validate-request",
            process_id,
            "--request",
            str(ROOT / "examples/guides" / filename),
        ],
    )
    assert result.exit_code == 0, result.output


def test_cli_request_matches_actual_prime_process():
    from gavicore.util.request import ExecutionRequest

    request = ExecutionRequest.create(
        request_path=str(ROOT / "examples/guides/primes-request.json")
    )
    job = Job.create(
        service.process_registry.get(request.process_id), request.to_process_request()
    )
    assert job.run().root["return_value"] == [
        11,
        13,
        17,
        19,
        23,
        29,
        31,
        37,
        41,
        43,
        47,
        53,
        59,
        61,
        67,
        71,
        73,
        79,
    ]


def test_dataset_example_reads_real_local_result(monkeypatch, tmp_path, capsys):
    data_dir = tmp_path / "directory with spaces"
    data_dir.mkdir()
    monkeypatch.chdir(data_dir)
    monkeypatch.setattr(S2GOSConfig, "default_path", tmp_path / "missing.yaml")
    client = api.connect()
    jobs = {}

    def execute(process_id, request):
        job = Job.create(service.process_registry.get(process_id), request)
        job_results = job.run()
        jobs[job.job_info.jobID] = (job.job_info, job_results)
        return job.job_info

    monkeypatch.setattr(client, "execute_process", execute)
    monkeypatch.setattr(client, "get_job", lambda job_id: jobs[job_id][0])
    monkeypatch.setattr(client, "get_job_results", lambda job_id: jobs[job_id][1])
    monkeypatch.setattr(
        client,
        "get_process",
        lambda process_id: service.process_registry.get(process_id).description,
    )
    try:
        registry = client.config.get_job_result_opener_registry()
        original_openers = registry.opener_types
        job_id = results.submit_scene(
            client, ROOT / "examples/guides/simulate-scene-request.json"
        )
        results.inspect_dataset(client, job_id)
        output = capsys.readouterr().out
        assert "'time': 2" in output and "'lat': 4" in output and "'lon': 4" in output
        assert "['a', 'b']" in output
        assert output.strip().endswith("0.0")
        assert registry.opener_types == original_openers
    finally:
        client.close()


def test_reopen_does_not_resubmit_and_closes_on_timeout(monkeypatch, client):
    monkeypatch.setattr(results, "connect", lambda: client)
    client.open_job_result.side_effect = TimeoutError("still running")
    with pytest.raises(TimeoutError, match="still running"):
        results.main("saved-job")
    client.execute_process.assert_not_called()
    assert client.open_job_result.call_args.args == ("saved-job",)
    client.close.assert_called_once()
    client.config.register_job_result_opener.return_value.assert_called_once()


def test_scene_session_submits_and_closes_dataset(monkeypatch, client):
    monkeypatch.setattr(results, "connect", lambda: client)
    dataset = xr.Dataset({"a": ("time", [0.0, 0.0])})
    closed = Mock()
    dataset.set_close(closed)
    client.open_job_result.return_value = dataset
    assert results.main() == "submitted-42"
    client.execute_process.assert_called_once()
    assert client.execute_process.call_args.args == ("simulate_scene",)
    assert client.open_job_result.call_args.args == ("submitted-42",)
    closed.assert_called_once()
    client.close.assert_called_once()


def test_invalid_scene_request_never_submits(tmp_path, client):
    path = tmp_path / "invalid.json"
    path.write_text('{"inputs": []}', encoding="utf-8")
    with pytest.raises(ValueError):
        results.submit_scene(client, path)
    client.execute_process.assert_not_called()


def test_dataset_closes_if_inspection_fails(client):
    dataset = xr.Dataset()
    closed = Mock()
    dataset.set_close(closed)
    client.open_job_result.return_value = dataset
    with pytest.raises(KeyError, match="a"):
        results.inspect_dataset(client, "saved-job")
    closed.assert_called_once()


@pytest.mark.parametrize(
    "href,media_type,data_type,accepted",
    [
        ("file:///tmp/scene.zarr", "application/zarr", None, True),
        ("file:///tmp/scene.zarr", "application/json", None, False),
        ("https://example.test/scene.zarr", "application/zarr", None, False),
        ("file://remote/scene.zarr", "application/zarr", None, False),
        ("file:///tmp/scene.zarr", "application/zarr", str, False),
    ],
)
def test_local_opener_selects_only_supported_outputs(
    href, media_type, data_type, accepted
):
    import asyncio

    from cuiman.api.opener import JobResultOpenContext
    from gavicore.models import JobResults, Link

    ctx = JobResultOpenContext(
        config=S2GOSConfig(auth={"auth_type": "none"}),
        job_id="example",
        job_results=JobResults(root={"return_value": Link(href=href, type=media_type)}),
        output_name="return_value",
        data_type=data_type,
    )
    assert asyncio.run(results.LocalZarrOpener().accept_job_result(ctx)) is accepted


def test_rendered_api_walkthrough_runs_in_order(monkeypatch, client):
    import s2gos_client

    monkeypatch.setattr(s2gos_client, "create_client", Mock(return_value=client))
    client.get_job.return_value = JobInfo(jobID="submitted-42", status="successful")
    rendered = markdown(
        (ROOT / "docs/guide/client-api.md").read_text(encoding="utf-8"),
        extensions=["pymdownx.snippets", "fenced_code"],
        extension_configs={
            "pymdownx.snippets": {
                "base_path": [str(ROOT)],
                "check_paths": True,
                "dedent_subsections": True,
            }
        },
    )
    namespace = {}
    blocks = re.findall(r'<code class="language-python">(.*?)</code>', rendered, re.S)
    assert len(blocks) == 5
    for block in blocks:
        exec(compile(html.unescape(block), "<rendered guide>", "exec"), namespace)
    assert namespace["job_id"] == "submitted-42"
    client.execute_process.assert_called_once()
    client.close.assert_called_once()
