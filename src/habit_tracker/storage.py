import json
import os
from datetime import date
from pathlib import Path
from typing import TypedDict

from habit_tracker.habits import (
    MAX_DAYS_PER_WEEK,
    MIN_DAYS_PER_WEEK,
    Habit,
    HabitError,
    clean_name,
    has_duplicate_names,
    is_valid_days_per_week,
)

DEFAULT_DATA_FILE = Path("habits.json")
DATA_FILE_ENV_VAR = "HABIT_TRACKER_FILE"


class CorruptDataError(HabitError):
    pass


class HabitRecord(TypedDict):
    name: str
    days_per_week: int
    check_ins: list[str]


def habit_to_record(habit: Habit) -> HabitRecord:
    return {
        "name": habit.name,
        "days_per_week": habit.days_per_week,
        "check_ins": [day.isoformat() for day in habit.check_ins],
    }


def name_from_record(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("a habit needs a name")
    return clean_name(value)


def days_per_week_from_record(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not is_valid_days_per_week(value):
        raise ValueError(
            f"days per week must be between {MIN_DAYS_PER_WEEK} and {MAX_DAYS_PER_WEEK},"
            f" not {value!r}"
        )
    return value


def check_ins_from_record(value: object) -> list[date]:
    if not isinstance(value, list) or not all(isinstance(day, str) for day in value):
        raise ValueError("check-ins must be a list of dates")
    return sorted({date.fromisoformat(day) for day in value})


def habit_from_record(record: HabitRecord) -> Habit:
    return Habit(
        name=name_from_record(record["name"]),
        days_per_week=days_per_week_from_record(record["days_per_week"]),
        check_ins=check_ins_from_record(record["check_ins"]),
    )


def data_file() -> Path:
    return Path(os.environ.get(DATA_FILE_ENV_VAR, DEFAULT_DATA_FILE))


def load_habits(path: Path) -> list[Habit]:
    if not path.exists():
        return []
    try:
        records = json.loads(path.read_text(encoding="utf-8"))["habits"]
        habits = [habit_from_record(record) for record in records]
    except (KeyError, TypeError, ValueError) as error:
        raise CorruptDataError(f"{path} is not a valid habit file") from error
    if has_duplicate_names(habits):
        raise CorruptDataError(f"{path} is not a valid habit file: two habits have the same name")
    return habits


def save_habits(path: Path, habits: list[Habit]) -> None:
    document = {"habits": [habit_to_record(habit) for habit in habits]}
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
