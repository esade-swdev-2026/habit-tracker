import typer

from habit_tracker.habits import MAX_DAYS_PER_WEEK, MIN_DAYS_PER_WEEK, is_valid_days_per_week

app = typer.Typer(help="Track your daily habits.")


@app.callback()
def main() -> None:
    """Track your daily habits."""


@app.command()
def add(habit: str, days: int = 7) -> None:
    """Add a habit you want to do some days per week."""
    if not is_valid_days_per_week(days):
        typer.echo(f"days must be between {MIN_DAYS_PER_WEEK} and {MAX_DAYS_PER_WEEK}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Added {habit}: {days} days per week")
