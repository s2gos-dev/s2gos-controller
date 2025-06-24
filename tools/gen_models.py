#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import datamodel_code_generator as dcg

from tools.common import (
    OPEN_API_PATH,
    S2GOS_PATH,
)

MODELS_PATH = S2GOS_PATH / "s2gos-common/src/s2gos_common/models.py"


def main():
    dcg.generate(
        input_=OPEN_API_PATH,
        input_file_type=dcg.InputFileType.OpenAPI,
        use_double_quotes=True,
        use_standard_collections=True,
        use_schema_description=True,
        set_default_enum_member=True,
        target_python_version=dcg.PythonVersion.PY_310,
        output_model_type=dcg.DataModelType.PydanticV2BaseModel,
        output=MODELS_PATH,
    )


if __name__ == "__main__":
    main()
