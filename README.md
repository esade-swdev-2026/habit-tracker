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

```bash
uv run habit-tracker --help
```
Add a habit that you want to complete three days per week:
```bash
uv run habit-tracker add reading --days 3
```
Output:

```text
Added reading: 3 days per week
```
To see how the `add` command works:

```bash
uv run habit-tracker add --help
```

`habit` is a required string argument.

`--days` is an integer option. Its default value is `7`.

<!--
Complete this section after the commands branch has been merged into main.

Every command and every output shown here must be run and verified.

The final README must include a copy-pasteable example using:
- done
- done --date
- streak
- summary --month
- list
-->

## What a streak is

A streak is the number of consecutive days on which a habit has been completed according to its schedule. Today does not break the streak until the day is over.

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

Habit data is stored in `habits.json` in the directory from which the program is run.

The file is ignored by Git. The storage location can be changed with the `HABIT_TRACKER_FILE` environment variable.


## How the code is organised

- `habits.py` contains the habit rules and core logic.
- `storage.py` handles reading and writing habit data.
- `cli.py` defines the command-line interface and its commands.


## Develop

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

## AI use

The `habits.py` module and its tests (Checkpoint 2) were written by hand and then got reviewed by claude code to spot mistakes and then refixed by hand.


The breakdown of this submission into four tasks and the task descriptions in the GitHub issues were drafted with Claude Code.

All documented commands and outputs will be verified manually before submission.

ChatGPT was used to understand issue #4, structure the README, and review the documentation requirements.

<!--
Add each other teammate's actual AI use here after asking them.
Do not guess.
-->