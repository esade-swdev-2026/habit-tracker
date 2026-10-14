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

All I/O lives in two files:

- `src/habit_tracker/cli.py` — the terminal and the clock. Each command prints its result with
  `typer.echo`, and is the only code that calls `date.today()`. Errors go through one helper,
  `reporting_errors`, which catches `HabitError` and `OSError`; `fail` prints the message to
  stderr and exits with code 1. No other code exits with an error code.
- `src/habit_tracker/storage.py` — the data file. `data_file` reads the `HABIT_TRACKER_FILE`
  environment variable (default `habits.json`), and `load_habits` and `save_habits` read and
  write the JSON file.

`src/habit_tracker/habits.py` is pure (no file access, no printing, no exit, no clock): the rules
for streaks, the monthly summary, check-ins and the days-per-week check live there, and get
today's date passed in as an argument.

## Develop

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

## AI use

The `habits.py` module and its tests (Checkpoint 2) were written by hand and then got reviewed by claude code to spot mistakes and then refixed by hand.

The commands in `cli.py` and their tests in `test_cli.py` (issue #3): I used Claude Code (Anthropic) to implement this issue. I gave it the specification and constraints, and it wrote the code and tests and ran the checks; I reviewed the changes, ran the git steps and opened the pull request.
