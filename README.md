# habit-tracker

Habit Tracker is a command-line tool for tracking daily habits.
It is designed for people who want to build routines and follow their progress from the terminal.

## Install

You need Git and uv installed on your computer.

Clone the repository and enter the project folder:

```bash
git clone https://github.com/esade-swdev-2026/habit-tracker.git
cd habit-tracker
```
Install the project and its dependencies:

```bash
uv sync
```


## Run

To see all available commands:

```bash
uv run habit-tracker --help
```

### First example: track a reading habit

The following example shows how to add a habit, record completed days, and check your progress.

To avoid mixing the example with your personal habit data, create a temporary data file:

```bash
export HABIT_TRACKER_FILE="$(mktemp -d)/habits.json"
```

Run all the following commands in the same terminal.

### 1. Add a habit

Add a habit called `reading` with a goal of three days per week:

```bash
uv run habit-tracker add reading --days 3
```

Output:

```text
Added reading: 3 days per week
```

### 2. List your habits

```bash
uv run habit-tracker list
```

Output:

```text
reading: 3 days per week
```

### 3. Mark a habit as completed today

```bash
uv run habit-tracker done reading
```

When tested on October 16, 2026, the output was:

```text
Checked in reading on 2026-10-16
```

Without `--date`, the program automatically uses today's date.

### 4. Mark a habit as completed on an earlier date

```bash
uv run habit-tracker done reading --date 2026-10-15
```

The `--date` option lets you record a completed habit for a specific day using the `YYYY-MM-DD` format.

### 5. Check your streak

```bash
uv run habit-tracker streak reading
```

After recording October 15 and 16, the output on October 16, 2026 was:

```text
reading: 2 days in a row
longest streak: 2 days
```

### 6. Check your monthly summary

```bash
uv run habit-tracker summary reading --month 2026-10
```

Output from the same test:

```text
reading: 2026-10
2 of 31 days done
6% complete
```

These results reflect the two completed days recorded in October 2026. Results may differ if the commands are executed on another date.

After testing, you can return to the default storage location:

```bash
unset HABIT_TRACKER_FILE
```

### Command reference

| Command | What it does | Arguments and options |
|---|---|---|
| `add` | Adds a new habit with a weekly goal. | Required: `habit`. Optional: `--days` (integer from 1 to 7, default 7). |
| `done` | Records a completed day for a habit. | Required: `habit`. Optional: `--date YYYY-MM-DD` (default: today). |
| `streak` | Shows the current and longest streak. | Required: `habit`. |
| `summary` | Shows completed days and completion percentage for a month. | Required: `habit`. Optional: `--month YYYY-MM` (default: current month). |
| `list` | Lists every habit and its weekly goal. | No arguments required. |

To see the arguments and options of a specific command, use `--help`:

```bash
uv run habit-tracker add --help
uv run habit-tracker done --help
uv run habit-tracker streak --help
uv run habit-tracker summary --help
uv run habit-tracker list --help
```


## What a streak is

A streak is the number of consecutive calendar days on which a habit has been completed.

For example, completing `reading` on October 15 and October 16 creates a two-day streak.

Habit Tracker shows two values:

- **Current streak:** the number of consecutive completed days up to today or yesterday.
- **Longest streak:** the longest sequence of consecutive completed days recorded for a habit.

Today does not break the current streak just because the habit has not been completed yet. If yesterday was completed, the streak remains active while today is still in progress.

The weekly goal set using `--days` and the streak are different concepts. The weekly goal specifies how many days per week you aim to complete a habit, while a streak measures consecutive completed days.

## Bad input

The number of days per week must be between 1 and 7.

For example, entering `0` produces an error:

```bash
uv run habit-tracker add reading --days 0
```

Output:

```text
days must be between 1 and 7
```

The command exits with status code `1`.

## Where habits are stored

Habit Tracker stores habits and their completed dates in a JSON file called `habits.json`.

By default, the file is created in the directory from which the program is run.

The file is ignored by Git, so personal habit data is not included in commits.

The storage location can be changed using the `HABIT_TRACKER_FILE` environment variable.

For example:

```bash
export HABIT_TRACKER_FILE="$(mktemp -d)/habits.json"
```

This creates a separate temporary location for testing.

- `add` and `done` save data to the JSON file.
- `list`, `streak`, and `summary` read the saved data.

To return to the default location in the current terminal:

```bash
unset HABIT_TRACKER_FILE
```


## How the code is organised

The project separates its logic, storage, and command-line interface into different modules:

- `src/habit_tracker/habits.py` contains the core habit rules and logic, including check-ins, streak calculations, input validation, and monthly summaries.
- `src/habit_tracker/storage.py` handles reading and writing habit data in the JSON file.
- `src/habit_tracker/cli.py` defines the terminal commands, displays results and errors, and connects the commands to the habit logic and storage.
- `src/habit_tracker/__main__.py` provides another entry point for running the Python package.
- `tests/` contains automated tests that check the project's behaviour.

This separation makes it possible to test the habit rules independently from the terminal interface and file storage.


## Develop

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

These commands check:

- **Ruff check:** code quality and linting issues.
- **Ruff format:** whether the code follows the required formatting.
- **Mypy:** Python type correctness.
- **Pytest:** whether the automated tests pass.

All four checks should pass before submitting changes.


## AI use

The `habits.py` module and its tests (Checkpoint 2) were written by hand and then got reviewed by claude code to spot mistakes and then refixed by hand.


The breakdown of this submission into four tasks and the task descriptions in the GitHub issues were drafted with Claude Code.

All documented commands and outputs will be verified manually before submission.

For issue #3: The commands in `cli.py` and their tests in `test_cli.py`: I used Claude Code (Anthropic) to implement this issue. I gave it the specification and constraints, and it wrote the code and tests and ran the checks; I reviewed the changes, ran the git steps and opened the pull request.

For issue #4, ChatGPT (OpenAI) was used to understand the documentation requirements, structure and draft the README, explain the Git workflow, and help review the documentation. The CLI commands and their outputs were tested manually.

