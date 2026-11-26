import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum

from habit_tracker.habits import (
    MAX_DAYS_PER_WEEK,
    MIN_DAYS_PER_WEEK,
    Habit,
    InvalidDaysPerWeekError,
    current_streak,
    days_done_this_week,
    longest_streak,
)

FILLED_CELL = "■"
EMPTY_CELL = "□"
WEEKDAY_HEADINGS = ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")
LONGEST_MONTH = timedelta(days=31)


class DayState(Enum):
    DONE = "done"
    NOT_DONE = "not done"
    TODAY = "today, not done yet"
    FUTURE = "has not happened yet"


@dataclass(frozen=True)
class HabitRow:
    name: str
    done_today: bool
    days_done_this_week: int
    days_per_week: int
    current_streak: int
    longest_streak: int


@dataclass(frozen=True)
class CalendarDay:
    day: date
    state: DayState


def habit_row(habit: Habit, today: date) -> HabitRow:
    return HabitRow(
        name=habit.name,
        done_today=today in habit.check_ins,
        days_done_this_week=days_done_this_week(habit.check_ins, today),
        days_per_week=habit.days_per_week,
        current_streak=current_streak(habit.check_ins, today),
        longest_streak=longest_streak(habit.check_ins),
    )


def goal_reached(row: HabitRow) -> bool:
    return row.days_done_this_week >= row.days_per_week


def goal_bar(days_done: int, days_per_week: int) -> str:
    filled = min(days_done, days_per_week)
    return FILLED_CELL * filled + EMPTY_CELL * (days_per_week - filled)


def day_state(day: date, check_ins: list[date], today: date) -> DayState:
    if day in check_ins:
        return DayState.DONE
    if day > today:
        return DayState.FUTURE
    if day == today:
        return DayState.TODAY
    return DayState.NOT_DONE


def month_calendar(
    check_ins: list[date], first_day: date, today: date
) -> list[list[CalendarDay | None]]:
    weeks = calendar.Calendar().monthdatescalendar(first_day.year, first_day.month)
    return [
        [
            CalendarDay(day, day_state(day, check_ins, today))
            if day.month == first_day.month
            else None
            for day in week
        ]
        for week in weeks
    ]


def first_of_month(day: date) -> date:
    return day.replace(day=1)


def previous_month(first_day: date) -> date:
    return first_of_month(first_day - timedelta(days=1))


def next_month(first_day: date) -> date:
    return first_of_month(first_day + LONGEST_MONTH)


def parse_days_per_week(text: str) -> int:
    if not text.strip().isdecimal():
        raise InvalidDaysPerWeekError(
            f"days must be between {MIN_DAYS_PER_WEEK} and {MAX_DAYS_PER_WEEK}"
        )
    return int(text)
