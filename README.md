# habit-tracker

A command-line tool to track your daily habits. For anyone who wants to build routines from the terminal.

## Install

```bash
uv sync
```

## Run

```bash
uv run habit-tracker --help
uv run habit-tracker add reading --days 3
```
## I/O boundary (shell)

All I/O lives in `src/habit_tracker/cli.py`:
- line 17: `typer.echo(..., err=True)` — prints validation error to stderr
- line 18: `raise typer.Exit(code=1)` — exits with error code
- line 19: `typer.echo(...)` — prints confirmation to stdout

Everything else in `src/` is pure (no file access, no printing, no exit). The rules for
streaks, the monthly summary and the days-per-week check live in `src/habit_tracker/habits.py`.

## Develop

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

## AI use

The `habits.py` module and its tests (Checkpoint 2) were written by hand and then got reviewed by claude code to spot mistakes and then refixed by hand.
