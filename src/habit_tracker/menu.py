from datetime import date
from enum import Enum

from habit_tracker.habits import (
    Habit,
    current_streak,
    days_done_this_week,
    format_day_count,
    same_name,
)


class Action(Enum):
    CHECK_IN = "Check in a habit"
    UNDO = "Undo a check-in"
    STREAK = "Show a streak"
    WEEK = "Show this week against the goal"
    SUMMARY = "Show a monthly summary"
    HISTORY = "Show every day a habit was done"
    ADD = "Add a habit"
    RENAME = "Rename a habit"
    TARGET = "Change a weekly goal"
    DELETE = "Delete a habit"
    QUIT = "Quit"


QUIT_KEY = "q"
COLUMN_GAP = "  "
OVERVIEW_HEADINGS = ("#", "Habit", "Today", "This week", "Streak")
DONE_TODAY = "done"
NOT_DONE_TODAY = "not yet"


def menu_keys() -> dict[str, Action]:
    numbered = [action for action in Action if action is not Action.QUIT]
    keys = {str(number): action for number, action in enumerate(numbered, start=1)}
    return {**keys, QUIT_KEY: Action.QUIT}


def key_of(action: Action) -> str:
    return next(key for key, candidate in menu_keys().items() if candidate is action)


def format_menu() -> list[str]:
    keys = menu_keys()
    width = max(len(key) for key in keys)
    return [f"{key.rjust(width)}{COLUMN_GAP}{action.value}" for key, action in keys.items()]


def parse_choice(text: str) -> Action | None:
    return menu_keys().get(text.strip().casefold())


def pick_habit(names: list[str], answer: str) -> str:
    answer = answer.strip()
    if any(same_name(name, answer) for name in names if answer):
        return answer
    if answer.isdecimal() and 1 <= int(answer) <= len(names):
        return names[int(answer) - 1]
    return answer


def overview_row(number: int, habit: Habit, today: date) -> tuple[str, ...]:
    return (
        str(number),
        habit.name,
        DONE_TODAY if today in habit.check_ins else NOT_DONE_TODAY,
        f"{days_done_this_week(habit.check_ins, today)} of {habit.days_per_week}",
        format_day_count(current_streak(habit.check_ins, today)),
    )


def format_table(rows: list[tuple[str, ...]]) -> list[str]:
    widths = [max(len(row[column]) for row in rows) for column in range(len(rows[0]))]
    return [
        COLUMN_GAP.join(cell.ljust(width) for cell, width in zip(row, widths, strict=True)).rstrip()
        for row in rows
    ]


def format_overview(habits: list[Habit], today: date) -> list[str]:
    title = f"Habit Tracker: {today.strftime('%A')} {today.isoformat()}"
    if not habits:
        return [title, f"No habits yet. Choose {key_of(Action.ADD)} to add one."]
    rows = [overview_row(number, habit, today) for number, habit in enumerate(habits, start=1)]
    return [title, *format_table([OVERVIEW_HEADINGS, *rows])]
