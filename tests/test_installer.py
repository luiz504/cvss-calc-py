import os
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
INSTALLER = PROJECT / "packaging" / "installer.sh"
BUILD_SCRIPT = PROJECT / "build.sh"


def run_installer(tmp_path: Path, *args: str, python: str = sys.executable) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "HOME": str(tmp_path), "PYTHON": python}
    env.pop("XDG_DATA_HOME", None)
    return subprocess.run(["sh", str(INSTALLER), *args], capture_output=True, text=True, env=env, check=False)


def test_scripts_are_executable() -> None:
    assert os.access(INSTALLER, os.X_OK)
    assert os.access(BUILD_SCRIPT, os.X_OK)


def test_installer_prints_the_usage(tmp_path: Path) -> None:
    result = run_installer(tmp_path, "--help")

    assert result.returncode == 0
    assert "Usage: sh installer.sh" in result.stdout


def test_installer_rejects_an_unknown_option(tmp_path: Path) -> None:
    result = run_installer(tmp_path, "--nope")

    assert result.returncode == 2
    assert "Usage: sh installer.sh" in result.stderr


def test_uninstall_with_nothing_installed_is_harmless(tmp_path: Path) -> None:
    result = run_installer(tmp_path, "--uninstall")

    assert result.returncode == 0
    assert "Nothing to remove." in result.stdout


def test_installer_stops_when_python_is_missing(tmp_path: Path) -> None:
    result = run_installer(tmp_path, python=str(tmp_path / "no-such-python"))

    assert result.returncode == 1
    assert "not found" in result.stderr


def test_installer_stops_when_python_is_too_old(tmp_path: Path) -> None:
    old_python = tmp_path / "old-python"
    old_python.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    old_python.chmod(0o755)

    result = run_installer(tmp_path, python=str(old_python))

    assert result.returncode == 1
    assert "needs Python 3.12 or newer" in result.stderr


def test_installer_never_overwrites_a_foreign_cvss(tmp_path: Path) -> None:
    foreign = tmp_path / ".local" / "bin" / "cvss"
    foreign.parent.mkdir(parents=True)
    foreign.write_text("#!/bin/sh\necho other\n", encoding="utf-8")

    result = run_installer(tmp_path)

    assert result.returncode == 1
    assert "not installed by this script" in result.stderr
    assert foreign.read_text(encoding="utf-8") == "#!/bin/sh\necho other\n"


def test_the_unbuilt_template_refuses_to_install(tmp_path: Path) -> None:
    result = run_installer(tmp_path)

    assert result.returncode == 1
    assert "installer template" in result.stderr
    assert not (tmp_path / ".local" / "share" / "cvss").exists()
