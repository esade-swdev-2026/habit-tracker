import typer

app = typer.Typer(help="Track your daily habits.")


@app.callback()
def main() -> None:
    """Track your daily habits."""


@app.command()
def add(habit: str, days: int = 7) -> None:
    """Add a habit you want to do some days per week."""
    if days < 1 or days > 7:
        typer.echo("days must be between 1 and 7", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Added {habit}: {days} days per week")
