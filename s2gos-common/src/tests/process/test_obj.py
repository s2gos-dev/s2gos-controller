#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from s2gos_common.util.obj import flatten_obj, nest_obj


def test_flatten_and_nest_dict_only():
    nested = {"a": {"b": {"c": 1}}}
    flat = flatten_obj(nested)
    assert flat == {"a.b.c": 1}
    assert nest_obj(flat) == nested


def test_flatten_and_nest_list_only():
    nested = [1, 2, [3, 4]]
    flat = flatten_obj(nested, flatten_lists=True)
    assert flat == {"0": 1, "1": 2, "2.0": 3, "2.1": 4}
    assert nest_obj(flat) == nested


def test_flatten_and_nest_mixed():
    nested = {"a": [{"x": 1}, {"y": 2}], "b": 3}
    flat = flatten_obj(nested, flatten_lists=True)
    assert flat == {"a.0.x": 1, "a.1.y": 2, "b": 3}
    assert nest_obj(flat) == nested


def test_overwrite_and_sparse_lists():
    flat = {"a.0": "first", "a.2": "third"}
    nested = nest_obj(flat)
    assert nested == {"a": ["first", None, "third"]}
    assert flatten_obj(nested, flatten_lists=True) == flat
