from typer.testing import CliRunner

from coding_agent import __version__
from coding_agent.cli import app

runner = CliRunner()

def test_version_option_reports_package_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout == f"coding-agent {__version__}\n"

def test_unknown_option_fails() -> None:
    result = runner.invoke(app, ["--not-a-real-option"])

    assert result.exit_code == 2
    assert "No such option: --not-a-real-option" in result.output