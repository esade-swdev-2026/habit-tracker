from datetime import date

import pytest

from habit_tracker.habits import (
    DuplicateHabitError,
    FutureCheckInError,
    Habit,
    InvalidDateError,
    MonthlySummary,
    UnknownHabitError,
    add_habit,
    check_in,
    completion_rate,
    current_streak,
    find_habit,
    format_habit,
    format_streaks,
    format_summary,
    is_valid_days_per_week,
    longest_streak,
    monthly_summary,
    parse_day,
    parse_month,
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


@pytest.fixture
def habits() -> list[Habit]:
    return [Habit("reading", 3), Habit("running", 1)]


def test_adding_a_habit_keeps_the_ones_already_there(habits: list[Habit]) -> None:
    assert add_habit(habits, "juggling", 2) == [
        Habit("reading", 3),
        Habit("running", 1),
        Habit("juggling", 2),
    ]


def test_adding_a_habit_does_not_change_the_list_it_was_given(habits: list[Habit]) -> None:
    add_habit(habits, "juggling", 2)

    assert habits == [Habit("reading", 3), Habit("running", 1)]


def test_adding_the_same_name_twice_raises_duplicate_habit_error(habits: list[Habit]) -> None:
    with pytest.raises(DuplicateHabitError, match="habit 'reading' already exists"):
        add_habit(habits, "reading", 5)


def test_find_habit_returns_the_habit_with_that_name(habits: list[Habit]) -> None:
    assert find_habit(habits, "running") == Habit("running", 1)


def test_finding_a_habit_nobody_added_raises_unknown_habit_error(habits: list[Habit]) -> None:
    with pytest.raises(UnknownHabitError, match="no habit called 'juggling'"):
        find_habit(habits, "juggling")


def test_checking_in_records_the_day_on_that_habit_only(habits: list[Habit]) -> None:
    checked_in = check_in(habits, "reading", TODAY, TODAY)

    assert find_habit(checked_in, "reading").check_ins == [TODAY]
    assert find_habit(checked_in, "running").check_ins == []


def test_checking_in_does_not_change_the_list_it_was_given(habits: list[Habit]) -> None:
    check_in(habits, "reading", TODAY, TODAY)

    assert find_habit(habits, "reading").check_ins == []


def test_checking_in_the_same_day_twice_records_it_once(habits: list[Habit]) -> None:
    once = check_in(habits, "reading", TODAY, TODAY)
    twice = check_in(once, "reading", TODAY, TODAY)

    assert find_habit(twice, "reading").check_ins == [TODAY]


def test_an_earlier_day_checked_in_later_ends_up_in_date_order(habits: list[Habit]) -> None:
    earlier = date(2026, 10, 7)
    today_first = check_in(habits, "reading", TODAY, TODAY)
    then_earlier = check_in(today_first, "reading", earlier, TODAY)

    assert find_habit(then_earlier, "reading").check_ins == [earlier, TODAY]


def test_checking_in_a_future_day_raises_future_check_in_error(habits: list[Habit]) -> None:
    tomorrow = date(2026, 10, 10)

    with pytest.raises(FutureCheckInError, match="2026-10-10 has not happened yet"):
        check_in(habits, "reading", tomorrow, TODAY)


def test_checking_in_a_habit_nobody_added_raises_unknown_habit_error(habits: list[Habit]) -> None:
    with pytest.raises(UnknownHabitError, match="no habit called 'juggling'"):
        check_in(habits, "juggling", TODAY, TODAY)


def test_parse_day_reads_a_good_date() -> None:
    assert parse_day("2026-10-12") == date(2026, 10, 12)


@pytest.mark.parametrize("text", ["yesterday", "09/10/2026", "2026-02-30", "2026-10", ""])
def test_parse_day_rejects_text_that_is_not_a_day(text: str) -> None:
    with pytest.raises(InvalidDateError):
        parse_day(text)


def test_parse_day_error_shows_what_a_date_should_look_like() -> None:
    with pytest.raises(InvalidDateError) as error:
        parse_day("yesterday")

    assert str(error.value) == "date must look like 2026-10-12, not 'yesterday'"


def test_parse_month_reads_a_good_month_as_its_first_day() -> None:
    assert parse_month("2026-10") == date(2026, 10, 1)


@pytest.mark.parametrize("text", ["october", "2026-13", "2026-10-09", "2026", ""])
def test_parse_month_rejects_text_that_is_not_a_month(text: str) -> None:
    with pytest.raises(InvalidDateError):
        parse_month(text)


def test_format_habit_shows_the_days_per_week() -> None:
    assert format_habit(Habit("reading", 3)) == "reading: 3 days per week"


def test_format_habit_says_day_not_days_for_one() -> None:
    assert format_habit(Habit("running", 1)) == "running: 1 day per week"


def test_streak_lines_for_a_one_day_streak() -> None:
    assert format_streaks("reading", 1, 4) == [
        "reading: 1 day in a row",
        "longest streak: 4 days",
    ]


def test_streak_lines_for_a_four_day_streak() -> None:
    assert format_streaks("reading", 4, 4) == [
        "reading: 4 days in a row",
        "longest streak: 4 days",
    ]


def test_streak_lines_for_no_streak_yet() -> None:
    assert format_streaks("reading", 0, 0) == [
        "reading: 0 days in a row",
        "longest streak: 0 days",
    ]
