from datetime import date

import pytest

from habit_tracker.dashboard import (
    CalendarDay,
    DayState,
    day_state,
    first_of_month,
    goal_bar,
    goal_reached,
    habit_row,
    month_calendar,
    next_month,
    parse_days_per_week,
    previous_month,
)
from habit_tracker.habits import Habit, InvalidDaysPerWeekError

FRIDAY = date(2026, 11, 27)
THURSDAY = date(2026, 11, 26)
WEDNESDAY = date(2026, 11, 25)
LAST_SUNDAY = date(2026, 11, 22)
SATURDAY = date(2026, 11, 28)


def test_a_row_says_what_the_habit_looks_like_today() -> None:
    habit = Habit("reading", 3, [LAST_SUNDAY, WEDNESDAY, THURSDAY, FRIDAY])
    row = habit_row(habit, FRIDAY)
    assert row.name == "reading"
    assert row.done_today
    assert row.days_done_this_week == 3
    assert row.days_per_week == 3
    assert row.current_streak == 3
    assert row.longest_streak == 3


def test_a_row_of_a_habit_with_no_check_ins_is_all_zero() -> None:
    row = habit_row(Habit("reading", 3), FRIDAY)
    assert not row.done_today
    assert (row.days_done_this_week, row.current_streak, row.longest_streak) == (0, 0, 0)


def test_the_goal_is_reached_at_the_goal_and_above_it() -> None:
    assert not goal_reached(habit_row(Habit("reading", 2, [FRIDAY]), FRIDAY))
    assert goal_reached(habit_row(Habit("reading", 2, [THURSDAY, FRIDAY]), FRIDAY))
    assert goal_reached(habit_row(Habit("reading", 2, [WEDNESDAY, THURSDAY, FRIDAY]), FRIDAY))


@pytest.mark.parametrize(
    ("days_done", "days_per_week", "bar"),
    [(0, 3, "□□□"), (2, 3, "■■□"), (3, 3, "■■■"), (5, 3, "■■■"), (1, 7, "■□□□□□□")],
)
def test_the_goal_bar_has_one_cell_per_goal_day(
    days_done: int, days_per_week: int, bar: str
) -> None:
    assert goal_bar(days_done, days_per_week) == bar


def test_a_day_is_done_not_done_today_or_still_to_come() -> None:
    check_ins = [WEDNESDAY]
    assert day_state(WEDNESDAY, check_ins, FRIDAY) is DayState.DONE
    assert day_state(THURSDAY, check_ins, FRIDAY) is DayState.NOT_DONE
    assert day_state(FRIDAY, check_ins, FRIDAY) is DayState.TODAY
    assert day_state(SATURDAY, check_ins, FRIDAY) is DayState.FUTURE


def test_today_counts_as_done_once_it_is_checked_in() -> None:
    assert day_state(FRIDAY, [FRIDAY], FRIDAY) is DayState.DONE


def test_the_month_calendar_has_one_row_per_week_from_monday_to_sunday() -> None:
    weeks = month_calendar([WEDNESDAY], date(2026, 11, 1), FRIDAY)
    assert all(len(week) == 7 for week in weeks)
    assert weeks[0] == [None] * 6 + [CalendarDay(date(2026, 11, 1), DayState.NOT_DONE)]
    assert weeks[-1][0] == CalendarDay(date(2026, 11, 30), DayState.FUTURE)
    assert weeks[-1][1:] == [None] * 6


def test_the_month_calendar_marks_the_days_that_were_done() -> None:
    weeks = month_calendar([WEDNESDAY], date(2026, 11, 1), FRIDAY)
    days = [cell for week in weeks for cell in week if cell is not None]
    assert len(days) == 30
    assert [cell.day for cell in days if cell.state is DayState.DONE] == [WEDNESDAY]


def test_february_in_a_leap_year_has_29_days() -> None:
    weeks = month_calendar([], date(2028, 2, 1), FRIDAY)
    assert sum(cell is not None for week in weeks for cell in week) == 29


def test_moving_a_month_back_and_forward_crosses_the_year() -> None:
    assert previous_month(date(2026, 11, 1)) == date(2026, 10, 1)
    assert previous_month(date(2026, 1, 1)) == date(2025, 12, 1)
    assert next_month(date(2026, 11, 1)) == date(2026, 12, 1)
    assert next_month(date(2026, 12, 1)) == date(2027, 1, 1)
    assert next_month(date(2026, 1, 1)) == date(2026, 2, 1)
    assert first_of_month(FRIDAY) == date(2026, 11, 1)


@pytest.mark.parametrize(("text", "days"), [("3", 3), (" 7 ", 7), ("9", 9)])
def test_days_per_week_are_read_from_what_was_typed(text: str, days: int) -> None:
    assert parse_days_per_week(text) == days


@pytest.mark.parametrize("text", ["", "three", "-1", "2.5"])
def test_days_per_week_that_are_not_a_whole_number_are_refused(text: str) -> None:
    with pytest.raises(InvalidDaysPerWeekError, match="days must be between 1 and 7"):
        parse_days_per_week(text)
