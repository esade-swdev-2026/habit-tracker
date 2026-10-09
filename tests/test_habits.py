from datetime import date

import pytest

from habit_tracker.habits import (
    MonthlySummary,
    completion_rate,
    current_streak,
    format_summary,
    is_valid_days_per_week,
    longest_streak,
    monthly_summary,
)

TODAY = date(2026, 10, 9)


@pytest.fixture
def check_ins() -> list[date]:
    return [
        date(2026, 9, 29),
        date(2026, 9, 30),
        date(2026, 10, 1),
        date(2026, 10, 2),
        date(2026, 10, 7),
        date(2026, 10, 8),
        date(2026, 10, 9),
    ]


@pytest.mark.parametrize(
    ("days", "expected"),
    [
        (-1, False),
        (0, False),
        (1, True),
        (7, True),
        (8, False),
    ],
)
def test_days_per_week_must_be_between_one_and_seven(days: int, expected: bool) -> None:
    assert is_valid_days_per_week(days) == expected


def test_current_streak_counts_back_from_today(check_ins: list[date]) -> None:
    assert current_streak(check_ins, TODAY) == 3


def test_no_check_ins_means_no_current_streak() -> None:
    assert current_streak([], TODAY) == 0


def test_current_streak_survives_until_today_is_over(check_ins: list[date]) -> None:
    not_done_today_yet = [day for day in check_ins if day != TODAY]

    assert current_streak(not_done_today_yet, TODAY) == 2


def test_a_missed_day_resets_the_current_streak(check_ins: list[date]) -> None:
    assert current_streak(check_ins, date(2026, 10, 4)) == 0


def test_checking_in_twice_on_one_day_counts_once() -> None:
    twice_today = [date(2026, 10, 8), TODAY, TODAY]

    assert current_streak(twice_today, TODAY) == 2
    assert longest_streak(twice_today) == 2


def test_longest_streak_is_the_longest_run_of_days_in_a_row(check_ins: list[date]) -> None:
    assert longest_streak(check_ins) == 4


def test_longest_streak_of_nothing_is_zero() -> None:
    assert longest_streak([]) == 0


def test_longest_streak_does_not_need_the_check_ins_in_order() -> None:
    shuffled = [date(2026, 10, 3), date(2026, 10, 1), date(2026, 10, 2)]

    assert longest_streak(shuffled) == 3


@pytest.mark.parametrize(
    ("days_done", "days_possible", "expected"),
    [
        (0, 31, 0.0),
        (31, 31, 1.0),
        (3, 30, 0.1),
        (5, 0, 0.0),
    ],
)
def test_completion_rate(days_done: int, days_possible: int, expected: float) -> None:
    assert completion_rate(days_done, days_possible) == pytest.approx(expected)


def test_monthly_summary_only_counts_days_in_that_month(check_ins: list[date]) -> None:
    summary = monthly_summary(check_ins, 2026, 10)

    assert summary.days_done == 5
    assert summary.days_in_month == 31
    assert summary.completion_rate == pytest.approx(5 / 31)


def test_monthly_summary_of_a_month_nobody_checked_in(check_ins: list[date]) -> None:
    assert monthly_summary(check_ins, 2026, 8) == MonthlySummary(2026, 8, 0, 31, 0.0)


def test_monthly_summary_knows_february_in_a_leap_year() -> None:
    assert monthly_summary([], 2028, 2).days_in_month == 29


def test_summary_lines_show_the_month_the_count_and_the_rate() -> None:
    summary = MonthlySummary(year=2026, month=9, days_done=3, days_in_month=30, completion_rate=0.1)

    assert format_summary("reading", summary) == [
        "reading: 2026-09",
        "3 of 30 days done",
        "10% complete",
    ]
