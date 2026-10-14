from pathlib import Path

import pytest
from typer.testing import CliRunner

from habit_tracker.cli import app
from habit_tracker.storage import DATA_FILE_ENV_VAR

runner = CliRunner()


@pytest.fixture(autouse=True)
def data_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "habits.json"
    monkeypatch.setenv(DATA_FILE_ENV_VAR, str(path))
    return path


def test_add_shows_the_habit() -> None:
    result = runner.invoke(app, ["add", "reading", "--days", "3"])
    assert result.exit_code == 0
    assert "reading" in result.stdout


def test_add_rejects_too_many_days() -> None:
    result = runner.invoke(app, ["add", "reading", "--days", "9"])
    assert result.exit_code == 1


def test_add_rejects_a_habit_that_already_exists() -> None:
    runner.invoke(app, ["add", "reading"])
    result = runner.invoke(app, ["add", "reading"])
    assert result.exit_code == 1
    assert "habit 'reading' already exists" in result.stderr


def test_list_shows_a_habit_added_in_an_earlier_run() -> None:
    runner.invoke(app, ["add", "reading", "--days", "3"])
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "reading: 3 days per week" in result.stdout


def test_streak_after_checking_in_today() -> None:
    runner.invoke(app, ["add", "reading"])
    runner.invoke(app, ["done", "reading"])
    result = runner.invoke(app, ["streak", "reading"])
    assert result.exit_code == 0
    assert "1 day in a row" in result.stdout


def test_done_rejects_an_unknown_habit() -> None:
    result = runner.invoke(app, ["done", "juggling"])
    assert result.exit_code == 1
    assert "no habit called 'juggling'" in result.stderr


def test_done_rejects_a_badly_written_date() -> None:
    runner.invoke(app, ["add", "reading"])
    result = runner.invoke(app, ["done", "reading", "--date", "yesterday"])
    assert result.exit_code == 1
    assert "not 'yesterday'" in result.stderr


def test_summary_counts_check_ins_in_the_chosen_month() -> None:
    runner.invoke(app, ["add", "reading"])
    runner.invoke(app, ["done", "reading", "--date", "2026-09-10"])
    runner.invoke(app, ["done", "reading", "--date", "2026-09-11"])
    result = runner.invoke(app, ["summary", "reading", "--month", "2026-09"])
    assert result.exit_code == 0
    assert "2 of 30 days done" in result.stdout


def test_broken_data_file_gives_a_message_not_a_traceback(data_path: Path) -> None:
    data_path.write_text("not json", encoding="utf-8")
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 1
    assert f"{data_path} is not a valid habit file" in result.stderr
    assert "Traceback" not in result.output
