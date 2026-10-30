import subprocess
import sys

import weathercli


def test_package_imports() -> None:
    assert weathercli.__version__


def test_module_entry_point_prints_help():
    result = subprocess.run(
        [sys.executable, "-m", "weathercli", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0
    assert "usage" in result.stdout.lower()
