import os
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
TEMPLATE = PROJECT / "packaging" / "binary-installer.sh"
ASSEMBLE = PROJECT / "packaging" / "assemble.sh"
BUILD_SCRIPT = PROJECT / "build-binary.sh"
MAN_PAGE = PROJECT / "man" / "cvss.1"
FAKE_PROGRAM = "#!/bin/sh\necho fake cvss $*\n"


def run_script(script: Path, tmp_path: Path, *args: str, **extra_env: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "HOME": str(tmp_path / "home"), **extra_env}
    env.pop("XDG_DATA_HOME", None)
    return subprocess.run(["sh", str(script), *args], capture_output=True, text=True, env=env, check=False)


@pytest.fixture
def installer(tmp_path: Path) -> Path:
    """A real installer built around a fake program: same header, same payload layout, no PyInstaller needed."""
    program = tmp_path / "fake-cvss"
    program.write_text(FAKE_PROGRAM, encoding="utf-8")
    built = tmp_path / "installer.sh"
    command = ["sh", str(ASSEMBLE), str(program), str(MAN_PAGE), str(built)]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return built


def test_scripts_are_executable() -> None:
    for script in (TEMPLATE, ASSEMBLE, BUILD_SCRIPT):
        assert os.access(script, os.X_OK)


def test_installer_prints_the_usage(installer: Path, tmp_path: Path) -> None:
    result = run_script(installer, tmp_path, "--help")

    assert result.returncode == 0
    assert "Usage: sh installer.sh" in result.stdout


def test_installer_rejects_an_unknown_option(installer: Path, tmp_path: Path) -> None:
    result = run_script(installer, tmp_path, "--nope")

    assert result.returncode == 2
    assert "Usage: sh installer.sh" in result.stderr


def test_uninstall_with_nothing_installed_is_harmless(installer: Path, tmp_path: Path) -> None:
    result = run_script(installer, tmp_path, "--uninstall")

    assert result.returncode == 0
    assert "Nothing to remove." in result.stdout


def test_the_unbuilt_template_refuses_to_install(tmp_path: Path) -> None:
    result = run_script(TEMPLATE, tmp_path)

    assert result.returncode == 1
    assert "installer template" in result.stderr
    assert not (tmp_path / "home" / ".local" / "share" / "cvss").exists()


def test_install_puts_the_command_and_the_man_page_in_place(installer: Path, tmp_path: Path) -> None:
    result = run_script(installer, tmp_path)
    home = tmp_path / "home"

    assert result.returncode == 0
    assert "Installed:" in result.stdout
    assert (home / ".local" / "share" / "man" / "man1" / "cvss.1").read_text(encoding="utf-8").startswith(".TH CVSS 1 ")
    command = subprocess.run([str(home / ".local" / "bin" / "cvss"), "-v", "X"], capture_output=True, text=True)
    assert command.stdout.strip() == "fake cvss -v X"


def test_installing_twice_upgrades_without_complaint(installer: Path, tmp_path: Path) -> None:
    run_script(installer, tmp_path)

    again = run_script(installer, tmp_path)

    assert again.returncode == 0


def test_uninstall_removes_everything_it_installed(installer: Path, tmp_path: Path) -> None:
    run_script(installer, tmp_path)
    home = tmp_path / "home"

    result = run_script(installer, tmp_path, "--uninstall")

    assert result.returncode == 0
    assert not (home / ".local" / "bin" / "cvss").exists()
    assert not (home / ".local" / "share" / "man" / "man1" / "cvss.1").exists()
    assert not (home / ".local" / "share" / "cvss").exists()


def test_install_never_overwrites_a_foreign_cvss(installer: Path, tmp_path: Path) -> None:
    foreign = tmp_path / "home" / ".local" / "bin" / "cvss"
    foreign.parent.mkdir(parents=True)
    foreign.write_text("#!/bin/sh\necho other\n", encoding="utf-8")

    result = run_script(installer, tmp_path)

    assert result.returncode == 1
    assert "not installed by this script" in result.stderr
    assert foreign.read_text(encoding="utf-8") == "#!/bin/sh\necho other\n"


def test_a_damaged_installer_is_rejected(installer: Path, tmp_path: Path) -> None:
    with installer.open("ab") as damaged:
        damaged.write(b"x")

    result = run_script(installer, tmp_path)

    assert result.returncode == 1
    assert "checksum mismatch" in result.stderr
    assert not (tmp_path / "home" / ".local" / "share" / "cvss").exists()


def test_an_installer_for_another_cpu_is_rejected(tmp_path: Path) -> None:
    program = tmp_path / "fake-cvss"
    program.write_text(FAKE_PROGRAM, encoding="utf-8")
    other_cpu = tmp_path / "other-cpu-installer.sh"
    subprocess.run(
        ["sh", str(ASSEMBLE), str(program), str(MAN_PAGE), str(other_cpu)],
        env={**os.environ, "PAYLOAD_ARCH": "riscv64"},
        check=True,
    )

    result = run_script(other_cpu, tmp_path)

    assert result.returncode == 1
    assert "built for riscv64" in result.stderr


def run_build(tmp_path: Path, python: str) -> subprocess.CompletedProcess[str]:
    """Run build-binary.sh in a throwaway copy of the project, so a test can never touch the real build/ or dist/."""
    project = tmp_path / "project"
    (project / "dist").mkdir(parents=True)
    (project / "dist" / "cvss-9.9.9-installer.sh").write_text("an earlier build", encoding="utf-8")
    shutil.copy(BUILD_SCRIPT, project / "build-binary.sh")
    shutil.copy(PROJECT / "pyproject.toml", project / "pyproject.toml")
    return subprocess.run(
        ["sh", str(project / "build-binary.sh")],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHON": python},
        check=False,
    )


def test_build_stops_when_python_is_missing(tmp_path: Path) -> None:
    result = run_build(tmp_path, str(tmp_path / "no-such-python"))

    assert result.returncode == 1
    assert "not found" in result.stderr


def test_build_explains_a_missing_venv_module(tmp_path: Path) -> None:
    broken_python = tmp_path / "broken-python"
    broken_python.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    broken_python.chmod(0o755)

    result = run_build(tmp_path, str(broken_python))

    assert result.returncode == 1
    assert "python3-venv" in result.stderr


def test_a_failed_build_leaves_the_earlier_installers_in_dist(tmp_path: Path) -> None:
    broken_python = tmp_path / "broken-python"
    broken_python.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    broken_python.chmod(0o755)

    run_build(tmp_path, str(broken_python))

    assert (tmp_path / "project" / "dist" / "cvss-9.9.9-installer.sh").read_text(encoding="utf-8") == "an earlier build"
