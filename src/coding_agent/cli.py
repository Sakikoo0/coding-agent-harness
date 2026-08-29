"""Command-line interface for Coding Agent Harness."""

from typing import Annotated

import typer

from coding_agent import __version__

app = typer.Typer(help="A small, extensible harness for coding agents.")

def _show_version(value: bool) -> None:
    if value:
        typer.echo(f"coding-agent {__version__}")
        raise typer.Exit

@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", callback=_show_version, is_eager=True, help="show the version and exit")
    ] = False
) -> None:
    """Run Coding Agent Harness."""