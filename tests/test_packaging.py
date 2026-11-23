import importlib
import re
import tomllib
from pathlib import Path

from cvss.app import build_parser

MAN_PAGE = Path(__file__).resolve().parents[1] / "man" / "cvss.1"
PYPROJECT = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8"))


def test_project_declares_a_build_backend() -> None:
    assert PYPROJECT["build-system"]["build-backend"] == "setuptools.build_meta"


def test_console_script_points_to_a_callable() -> None:
    target = PYPROJECT["project"]["scripts"]["cvss"]
    module_name, function_name = target.split(":")

    assert callable(getattr(importlib.import_module(module_name), function_name))


def test_man_page_has_the_man_header() -> None:
    assert MAN_PAGE.read_text(encoding="utf-8").startswith(".TH CVSS 1 ")


def test_man_page_documents_every_long_option() -> None:
    help_text = build_parser().format_help()
    man_text = MAN_PAGE.read_text(encoding="utf-8").replace("\\-", "-")

    for option in sorted(set(re.findall(r"--[a-z]+", help_text))):
        assert option in man_text


def test_man_page_is_installed_with_the_package() -> None:
    data_files = PYPROJECT["tool"]["setuptools"]["data-files"]

    assert data_files["share/man/man1"] == ["man/cvss.1"]


def test_the_changelog_has_an_entry_for_the_project_version() -> None:
    version = PYPROJECT["project"]["version"]
    changelog = (Path(__file__).resolve().parents[1] / "CHANGELOG.md").read_text(encoding="utf-8")

    assert f"## [{version}]" in changelog
