from __future__ import annotations


def test_import_src():
    import src

    assert src is not None


def test_import_api():
    import src.api

    assert src.api is not None


def test_import_models():
    import src.models

    assert src.models is not None


def test_import_screens():
    import src.screens

    assert src.screens is not None


def test_pytest_works():
    assert True is True
