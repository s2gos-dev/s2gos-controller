"""Run with python -m examples.guides.app; stop with Ctrl+C."""

import time

# isort: split
# --8<-- [start:open]
from typing import Literal

from cuiman.app import App

from s2gos_client import Client, create_client


def open_app(display: Literal["browser", "notebook"] = "browser") -> tuple[Client, App]:
    client = create_client(api_url="http://127.0.0.1:8008", auth={"auth_type": "none"})
    try:
        app = client.show_app(display=display, height=640)
    except Exception:
        client.close()
        raise
    return client, app


# --8<-- [end:open]


# --8<-- [start:update]
def set_duration(app: App, duration: float = 2) -> None:
    request = app.get_process_request("sleep_a_while")
    if request is None:
        raise ValueError("Open the sleep_a_while process in the App first.")
    if request.inputs is None:
        request.inputs = {}
    request.inputs["duration"] = duration
    app.set_process_request("sleep_a_while", request)


# --8<-- [end:update]


# --8<-- [start:close]
def close_app(client: Client, app: App) -> None:
    try:
        app.serve_result.stop()
    finally:
        client.close()


# --8<-- [end:close]


def main() -> None:
    client, app = open_app()
    try:
        print("App is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        close_app(client, app)


if __name__ == "__main__":
    main()
