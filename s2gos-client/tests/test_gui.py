#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import s2gos_client.gui
from cuiman.gui.component import ComponentContainer, ComponentFactory


def test_gui_ok():
    assert {"Client"}.issubset(dir(s2gos_client.gui))


def test_extra_gui_components_registered():
    factory = ComponentContainer.registry.find_factory({"type": "object"})
    assert factory is None

    factory = ComponentContainer.registry.find_factory(
        {"type": "object", "format": "PathRef"}
    )
    assert isinstance(factory, ComponentFactory)
