import pytest


def indicator_case(function, kind, /, *args, id_suffix=None, marks=(), **kwargs):
    """
    Build a parametrized indicator test case as
    `pytest.param(function, kind, args, kwargs)`.

    The test id is built from the function name, `kind` and the optional `id_suffix`
    (e.g. ``atr-df-exp``).
    This keeps snapshot file names stable when cases are added, removed or reordered.
    """
    case_id = f"{function.__name__}-{kind}"
    if id_suffix:
        case_id += f"-{id_suffix}"
    return pytest.param(function, kind, args, kwargs, id=case_id, marks=marks)
