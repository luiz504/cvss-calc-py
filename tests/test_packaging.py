import importlib
import tomllib
from pathlib import Path

PYPROJECT = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8"))


def test_project_declares_a_build_backend() -> None:
    assert PYPROJECT["build-system"]["build-backend"] == "setuptools.build_meta"


def test_console_script_points_to_a_callable() -> None:
    target = PYPROJECT["project"]["scripts"]["cvss"]
    module_name, function_name = target.split(":")

    assert callable(getattr(importlib.import_module(module_name), function_name))
