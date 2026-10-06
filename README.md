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
- line 15: `typer.echo(..., err=True)` — prints validation error to stderr
- line 16: `raise typer.Exit(code=1)` — exits with error code
- line 17: `typer.echo(...)` — prints confirmation to stdout

Everything else in `src/` is pure (no file access, no printing, no exit).