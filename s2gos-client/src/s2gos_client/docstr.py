#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.


def inherit_docstrings(cls):
    """
    Decorator that copies the docstring from inherited methods,
    if methods of `cls` are lacking a docstring.
    """
    for name, attr in cls.__dict__.items():
        if callable(attr) and not attr.__doc__:
            for base in cls.__mro__[1:]:
                base_attr = getattr(base, name, None)
                if base_attr and getattr(base_attr, "__doc__", None):
                    attr.__doc__ = base_attr.__doc__
                    break
    return cls
