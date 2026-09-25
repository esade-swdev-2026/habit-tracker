from typer.testing import CliRunner

from habit_tracker.cli import app

runner = CliRunner()


def test_add_shows_the_habit() -> None:
    result = runner.invoke(app, ["add", "reading", "--days", "3"])
    assert result.exit_code == 0
    assert "reading" in result.stdout


def test_add_rejects_too_many_days() -> None:
    result = runner.invoke(app, ["add", "reading", "--days", "9"])
    assert result.exit_code == 1
