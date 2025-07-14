#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from dataclasses import dataclass
from pathlib import Path

from s2gos_server.services.base.function_process import FunctionProcess


@dataclass
class DagWriter:
    airflow_dags_folder: str
    airflow_user_package: str

    def write_dag(self, process: FunctionProcess):
        function_name = process.process.id

        file_path = Path(self.airflow_dags_folder, f"{function_name}.py")
        with open(file_path, "w") as f:
            json_schema = process.model_class.model_json_schema(by_alias=True)

            param_defs = []
            for param_name, param_schema in json_schema.get("properties", {}).items():
                param_args = ", ".join(
                    f"{sk}={sv!r}" for sk, sv in param_schema.items()
                )
                param_defs.append(f"{param_name!r}: Param({param_args})")

            tab = "    "
            num_outputs = len(process.process.outputs or [])
            lines = [
                "from airflow.sdk import Param, dag, task",
                "",
                f"from {self.airflow_user_package} import {function_name}",
                "",
                "",
                "@dag(",
                f"{tab}{function_name!r},",
                f"{tab}multiple_outputs={(num_outputs > 1)!r},",
                f"{tab}params=" + "{",
                *[f"{tab}{tab}{p}," for p in param_defs],
                f"{tab}" + "},",
                ")",
                f"def {function_name}_dag():",
                "",
                f"{tab}@task('invoke_processor')",
                f"{tab}def {function_name}_task(params):",
                f"{tab}{tab}return {function_name}(**params)",
                "",
                f"{tab}task = {function_name}_task()",
            ]
            f.write("\n".join(lines) + "\n")
