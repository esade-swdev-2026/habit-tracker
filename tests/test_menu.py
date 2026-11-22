from datetime import date

import pytest

from habit_tracker.habits import Habit
from habit_tracker.menu import (
    Action,
    format_menu,
    format_overview,
    key_of,
    menu_keys,
    parse_choice,
    pick_habit,
)

SUNDAY = date(2026, 11, 22)
SATURDAY = date(2026, 11, 21)
LAST_SUNDAY = date(2026, 11, 15)


def test_every_action_has_one_key_and_quit_is_q() -> None:
    keys = menu_keys()
    assert sorted(keys.values(), key=lambda action: action.name) == sorted(
        Action, key=lambda action: action.name
    )
    assert keys["q"] is Action.QUIT
    assert keys["1"] is Action.CHECK_IN


def test_the_menu_shows_one_line_per_action_with_its_key() -> None:
    lines = format_menu()
    assert len(lines) == len(Action)
    assert lines[0] == " 1  Check in a habit"
    assert lines[-1] == " q  Quit"


@pytest.mark.parametrize(
    ("text", "action"),
    [
        ("1", Action.CHECK_IN),
        (" 7 ", Action.ADD),
        ("10", Action.DELETE),
        ("q", Action.QUIT),
        ("Q", Action.QUIT),
    ],
)
def test_a_key_chooses_its_action(text: str, action: Action) -> None:
    assert parse_choice(text) is action


@pytest.mark.parametrize("text", ["", "0", "11", "quit", "one", "1.0"])
def test_anything_else_is_not_a_choice(text: str) -> None:
    assert parse_choice(text) is None


def test_a_habit_can_be_picked_by_its_number() -> None:
    assert pick_habit(["reading", "running"], "2") == "running"
    assert pick_habit(["reading", "running"], " 1 ") == "reading"


def test_a_habit_can_be_picked_by_its_name() -> None:
    assert pick_habit(["reading", "running"], "Running") == "Running"


def test_a_number_outside_the_list_is_passed_on_as_a_name() -> None:
    assert pick_habit(["reading", "running"], "3") == "3"
    assert pick_habit(["reading", "running"], "0") == "0"
    assert pick_habit([], "1") == "1"


def test_a_habit_whose_name_is_a_number_wins_over_the_position() -> None:
    assert pick_habit(["2", "reading"], "2") == "2"


def test_a_blank_answer_stays_blank() -> None:
    assert pick_habit(["reading"], "   ") == ""


def test_the_overview_without_habits_points_at_the_add_choice() -> None:
    assert format_overview([], SUNDAY) == [
        "Habit Tracker: Sunday 2026-11-22",
        f"No habits yet. Choose {key_of(Action.ADD)} to add one.",
    ]


def test_the_overview_shows_today_the_week_and_the_streak_of_each_habit() -> None:
    habits = [
        Habit(name="reading", days_per_week=3, check_ins=[LAST_SUNDAY, SATURDAY, SUNDAY]),
        Habit(name="morning run", days_per_week=1),
    ]
    assert format_overview(habits, SUNDAY) == [
        "Habit Tracker: Sunday 2026-11-22",
        "#  Habit        Today    This week  Streak",
        "1  reading      done     2 of 3     2 days",
        "2  morning run  not yet  0 of 1     0 days",
    ]


def test_the_overview_counts_yesterday_in_the_streak_when_today_is_not_done() -> None:
    habits = [Habit(name="reading", days_per_week=7, check_ins=[SATURDAY])]
    assert format_overview(habits, SUNDAY)[2] == "1  reading  not yet  1 of 7     1 day"
