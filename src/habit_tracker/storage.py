import json
import os
from datetime import date
from pathlib import Path
from typing import TypedDict

from habit_tracker.habits import Habit, HabitError

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


def habit_from_record(record: HabitRecord) -> Habit:
    return Habit(
        name=record["name"],
        days_per_week=record["days_per_week"],
        check_ins=[date.fromisoformat(day) for day in record["check_ins"]],
    )


def data_file() -> Path:
    return Path(os.environ.get(DATA_FILE_ENV_VAR, DEFAULT_DATA_FILE))


def load_habits(path: Path) -> list[Habit]:
    if not path.exists():
        return []
    try:
        records = json.loads(path.read_text(encoding="utf-8"))["habits"]
        return [habit_from_record(record) for record in records]
    except (KeyError, TypeError, ValueError) as error:
        raise CorruptDataError(f"{path} is not a valid habit file") from error


def save_habits(path: Path, habits: list[Habit]) -> None:
    document = {"habits": [habit_to_record(habit) for habit in habits]}
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
