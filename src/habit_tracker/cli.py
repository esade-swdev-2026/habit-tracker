from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from typing import Annotated, NoReturn

import typer

from habit_tracker.habits import (
    MAX_DAYS_PER_WEEK,
    MIN_DAYS_PER_WEEK,
    HabitError,
    add_habit,
    check_in,
    current_streak,
    days_done_this_week,
    find_habit,
    format_habit,
    format_streaks,
    format_summary,
    format_week,
    is_valid_days_per_week,
    longest_streak,
    monthly_summary,
    parse_day,
    parse_month,
)
from habit_tracker.storage import data_file, load_habits, save_habits

app = typer.Typer(help="Track your daily habits.")

NO_HABITS_MESSAGE = "No habits yet. Add one with: habit-tracker add reading --days 3"


def fail(message: str) -> NoReturn:
    typer.echo(message, err=True)
    raise typer.Exit(code=1)


@contextmanager
def reporting_errors() -> Iterator[None]:
    try:
        yield
    except (HabitError, OSError) as error:
        fail(str(error))


@app.callback()
def main() -> None:
    """Track your daily habits."""


@app.command()
def add(habit: str, days: int = 7) -> None:
    """Add a habit you want to do some days per week."""
    if not is_valid_days_per_week(days):
        fail(f"days must be between {MIN_DAYS_PER_WEEK} and {MAX_DAYS_PER_WEEK}")
    with reporting_errors():
        path = data_file()
        habits = add_habit(load_habits(path), habit, days)
        save_habits(path, habits)
        typer.echo(f"Added {format_habit(find_habit(habits, habit))}")


@app.command()
def done(
    habit: str,
    day_text: Annotated[str | None, typer.Option("--date", help="Day as YYYY-MM-DD.")] = None,
) -> None:
    """Check in a habit for today or an earlier day."""
    with reporting_errors():
        today = date.today()
        day = parse_day(day_text) if day_text is not None else today
        path = data_file()
        habits = check_in(load_habits(path), habit, day, today)
        save_habits(path, habits)
        typer.echo(f"Checked in {find_habit(habits, habit).name} on {day.isoformat()}")


@app.command()
def streak(habit: str) -> None:
    """Show the current and longest streak of a habit."""
    with reporting_errors():
        found = find_habit(load_habits(data_file()), habit)
        current = current_streak(found.check_ins, date.today())
        typer.echo("\n".join(format_streaks(found.name, current, longest_streak(found.check_ins))))


@app.command()
def summary(
    habit: str,
    month: Annotated[str | None, typer.Option(help="Month as YYYY-MM.")] = None,
) -> None:
    """Show how many days of a month a habit was done."""
    with reporting_errors():
        first_day = parse_month(month) if month is not None else date.today()
        found = find_habit(load_habits(data_file()), habit)
        result = monthly_summary(found.check_ins, first_day.year, first_day.month)
        typer.echo("\n".join(format_summary(found.name, result)))


@app.command()
def week(habit: str) -> None:
    """Show this week's check-ins against the weekly goal."""
    with reporting_errors():
        found = find_habit(load_habits(data_file()), habit)
        days_done = days_done_this_week(found.check_ins, date.today())
        typer.echo("\n".join(format_week(found, days_done)))


@app.command("list")
def list_habits() -> None:
    """List every habit with its weekly goal."""
    with reporting_errors():
        habits = load_habits(data_file())
        lines = [format_habit(habit) for habit in habits] or [NO_HABITS_MESSAGE]
        typer.echo("\n".join(lines))
