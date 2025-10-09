#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any


def flatten_obj(
    obj: Any, *, parent_key: str = "", sep: str = ".", flatten_lists: bool = False
) -> dict[str, Any]:
    """
    Flatten nested dicts/lists into a flat dict with sep-delimited keys.

    Args:
        obj: The nested structure (dict, list, or scalar).
        parent_key: Internal recursion prefix for keys.
        sep: Separator string for flattened keys.
        flatten_lists: If True, expand lists into indexed keys (default).
                       If False, keep lists as values (without flattening inside).

    Returns:
        A flat dictionary mapping sep-delimited keys to values.
    """
    items: dict[str, Any] = {}

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            items.update(
                flatten_obj(v, parent_key=new_key, flatten_lists=flatten_lists, sep=sep)
            )
    elif isinstance(obj, list) and flatten_lists:
        for i, v in enumerate(obj):
            if v is None:  # skip None placeholders
                continue
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.update(
                flatten_obj(v, parent_key=new_key, flatten_lists=flatten_lists, sep=sep)
            )
    else:
        items[parent_key] = obj

    return items


# I avoided recursion for nest_obj because building a structure
# from paths is a more natural fit for an iterative approach,
# while flattening is inherently recursive.
#
def nest_obj(flattened_dict: dict[str, Any], *, sep: str = ".") -> dict | list:
    """Nest a flat dict with sep-delimited keys back into dicts/lists."""
    root: dict[str, Any] = {}

    for flat_key, value in flattened_dict.items():
        path = flat_key.split(sep)
        current: dict | list = root
        parent: dict | list | None = None
        parent_key: str | int | None = None

        for i, part in enumerate(path):
            is_last = i == len(path) - 1

            # Try to interpret part as a list index
            try:
                index: int | None = int(part)
            except ValueError:
                index = None

            if is_last:
                if index is not None:
                    if not isinstance(current, list):
                        if parent is not None:
                            parent[parent_key] = []
                            current = parent[parent_key]
                        else:
                            current = []
                            root = current
                    while len(current) <= index:
                        current.append(None)
                    current[index] = value
                else:
                    current[part] = value
            else:
                if index is not None:
                    if not isinstance(current, list):
                        if parent is not None:
                            parent[parent_key] = []
                            current = parent[parent_key]
                        else:
                            current = []
                            root = current
                    while len(current) <= index:
                        current.append({})
                    if not isinstance(current[index], (dict, list)):
                        current[index] = {}
                    parent, parent_key, current = current, index, current[index]
                else:
                    if part not in current or not isinstance(
                        current[part], (dict, list)
                    ):
                        current[part] = {}
                    parent, parent_key, current = current, part, current[part]

    return root
