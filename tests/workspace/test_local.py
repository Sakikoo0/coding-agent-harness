import pytest

from coding_agent.workspace import LocalWorkspace


def test_local_workspace_runs_each_command_in_a_new_process(tmp_path) -> None:
    workspace = LocalWorkspace(tmp_path)

    assert workspace.execute("cd ..").return_code == 0
    result = workspace.execute("pwd")

    assert result.return_code == 0
    assert result.output.strip() == str(tmp_path.resolve())


def test_local_workspace_captures_nonzero_exit_and_stderr(tmp_path) -> None:
    result = LocalWorkspace(tmp_path).execute("printf 'failure\\n' >&2; exit 7")

    assert result.return_code == 7
    assert result.output == "failure\n"


def test_local_workspace_rejects_missing_root(tmp_path) -> None:
    with pytest.raises(ValueError, match="Workspace root is not a directory"):
        LocalWorkspace(tmp_path / "missing")
