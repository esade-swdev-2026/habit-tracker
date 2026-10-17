from datetime import date
from pathlib import Path

import pytest

from habit_tracker.habits import Habit
from habit_tracker.storage import (
    DATA_FILE_ENV_VAR,
    DEFAULT_DATA_FILE,
    CorruptDataError,
    HabitRecord,
    data_file,
    habit_from_record,
    habit_to_record,
    load_habits,
    save_habits,
)

READING = Habit(name="reading", days_per_week=3, check_ins=[date(2026, 10, 8), date(2026, 10, 9)])


def test_a_habit_becomes_a_record_with_iso_dates() -> None:
    assert habit_to_record(READING) == {
        "name": "reading",
        "days_per_week": 3,
        "check_ins": ["2026-10-08", "2026-10-09"],
    }


def test_a_record_turns_back_into_the_same_habit() -> None:
    assert habit_from_record(habit_to_record(READING)) == READING


def test_a_record_with_a_broken_date_is_rejected() -> None:
    with pytest.raises(ValueError):
        habit_from_record({"name": "reading", "days_per_week": 3, "check_ins": ["yesterday"]})


def test_a_record_name_loads_without_extra_spaces() -> None:
    record: HabitRecord = {"name": "  morning   run ", "days_per_week": 2, "check_ins": []}

    assert habit_from_record(record).name == "morning run"


def test_the_data_file_is_habits_json_unless_told_otherwise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(DATA_FILE_ENV_VAR, raising=False)

    assert data_file() == DEFAULT_DATA_FILE


def test_the_data_file_can_be_moved_with_an_environment_variable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    elsewhere = tmp_path / "my-habits.json"
    monkeypatch.setenv(DATA_FILE_ENV_VAR, str(elsewhere))

    assert data_file() == elsewhere


def test_a_missing_file_means_no_habits_yet(tmp_path: Path) -> None:
    assert load_habits(tmp_path / "habits.json") == []


def test_saved_habits_load_back_unchanged(tmp_path: Path) -> None:
    path = tmp_path / "habits.json"
    habits = [READING, Habit(name="running", days_per_week=2)]

    save_habits(path, habits)

    assert load_habits(path) == habits


def test_saving_replaces_what_was_in_the_file(tmp_path: Path) -> None:
    path = tmp_path / "habits.json"
    save_habits(path, [READING])

    save_habits(path, [Habit(name="running", days_per_week=2)])

    assert load_habits(path) == [Habit(name="running", days_per_week=2)]


@pytest.mark.parametrize(
    "content",
    [
        "not json at all",
        "[]",
        '{"habits": [{"name": "reading"}]}',
        '{"habits": [{"name": "reading", "days_per_week": 3, "check_ins": ["yesterday"]}]}',
        '{"habits": [{"name": 5, "days_per_week": 3, "check_ins": []}]}',
        '{"habits": [{"name": "  ", "days_per_week": 3, "check_ins": []}]}',
        '{"habits": [{"name": "reading", "days_per_week": 99, "check_ins": []}]}',
        '{"habits": [{"name": "reading", "days_per_week": "3", "check_ins": []}]}',
        '{"habits": [{"name": "reading", "days_per_week": true, "check_ins": []}]}',
        '{"habits": [{"name": "reading", "days_per_week": 3, "check_ins": "2026-10-08"}]}',
        '{"habits": [{"name": "Reading", "days_per_week": 3, "check_ins": []},'
        ' {"name": "reading", "days_per_week": 5, "check_ins": []}]}',
    ],
)
def test_a_file_that_is_not_a_habit_file_is_reported(tmp_path: Path, content: str) -> None:
    path = tmp_path / "habits.json"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(CorruptDataError, match="is not a valid habit file"):
        load_habits(path)
