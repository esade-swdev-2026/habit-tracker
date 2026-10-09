import calendar
from dataclasses import dataclass
from datetime import date, timedelta

MIN_DAYS_PER_WEEK = 1
MAX_DAYS_PER_WEEK = 7

ONE_DAY = timedelta(days=1)


@dataclass(frozen=True)
class MonthlySummary:
    year: int
    month: int
    days_done: int
    days_in_month: int
    completion_rate: float


def is_valid_days_per_week(days: int) -> bool:
    return MIN_DAYS_PER_WEEK <= days <= MAX_DAYS_PER_WEEK


def current_streak(check_ins: list[date], today: date) -> int:
    done = set(check_ins)
    day = today if today in done else today - ONE_DAY
    streak = 0
    while day in done:
        streak += 1
        day -= ONE_DAY
    return streak


def longest_streak(check_ins: list[date]) -> int:
    longest = 0
    streak = 0
    previous = None
    for day in sorted(set(check_ins)):
        streak = streak + 1 if previous is not None and day - previous == ONE_DAY else 1
        longest = max(longest, streak)
        previous = day
    return longest


def completion_rate(days_done: int, days_possible: int) -> float:
    if days_possible <= 0:
        return 0.0
    return days_done / days_possible


def monthly_summary(check_ins: list[date], year: int, month: int) -> MonthlySummary:
    days_in_month = calendar.monthrange(year, month)[1]
    days_done = len({day for day in check_ins if day.year == year and day.month == month})
    return MonthlySummary(
        year=year,
        month=month,
        days_done=days_done,
        days_in_month=days_in_month,
        completion_rate=completion_rate(days_done, days_in_month),
    )


def format_summary(habit: str, summary: MonthlySummary) -> list[str]:
    return [
        f"{habit}: {summary.year}-{summary.month:02d}",
        f"{summary.days_done} of {summary.days_in_month} days done",
        f"{summary.completion_rate:.0%} complete",
    ]
