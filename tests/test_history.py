from datetime import date

from habit_tracker.habits import Habit
from habit_tracker.history import format_history


def test_a_habit_without_check_ins_says_so() -> None:
    habit = Habit(name="reading", days_per_week=3)
    assert format_history(habit) == ["reading: no check-ins yet"]


def test_one_check_in_uses_the_singular() -> None:
    habit = Habit(name="reading", days_per_week=3, check_ins=[date(2026, 10, 15)])
    assert format_history(habit) == ["reading: done on 1 day", "2026-10-15"]


def test_days_are_listed_oldest_first() -> None:
    check_ins = [date(2026, 10, 16), date(2026, 9, 30), date(2026, 10, 1)]
    habit = Habit(name="reading", days_per_week=3, check_ins=check_ins)
    assert format_history(habit) == [
        "reading: done on 3 days",
        "2026-09-30",
        "2026-10-01",
        "2026-10-16",
    ]


def test_a_day_listed_twice_is_counted_once() -> None:
    check_ins = [date(2026, 10, 15), date(2026, 10, 15)]
    habit = Habit(name="reading", days_per_week=3, check_ins=check_ins)
    assert format_history(habit) == ["reading: done on 1 day", "2026-10-15"]
