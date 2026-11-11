import pytest


def indicator_case(function, _variant, /, *args, id_suffix=None, marks=(), **kwargs):
    """
    Build a parametrized indicator test case as
    `pytest.param(function, _variant, args, kwargs)`.

    `_variant` is passed through to the test untouched as 2nd positional argument.

    The test id is built from the function name, `_variant` and the optional `id_suffix`
    (e.g. ``atr-df-exp``).
    This keeps snapshot file names stable when cases are added, removed or reordered.
    """
    case_id = f"{function.__name__}-{_variant}"
    if id_suffix:
        case_id += f"-{id_suffix}"
    return pytest.param(function, _variant, args, kwargs, id=case_id, marks=marks)
