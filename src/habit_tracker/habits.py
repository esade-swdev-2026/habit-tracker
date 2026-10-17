import calendar
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta

MIN_DAYS_PER_WEEK = 1
MAX_DAYS_PER_WEEK = 7

ONE_DAY = timedelta(days=1)

DAY_FORMAT = "%Y-%m-%d"
MONTH_FORMAT = "%Y-%m"


class HabitError(Exception):
    pass


class DuplicateHabitError(HabitError):
    pass


class UnknownHabitError(HabitError):
    pass


class FutureCheckInError(HabitError):
    pass


class InvalidDateError(HabitError):
    pass


class BlankNameError(HabitError):
    pass


class AlreadyCheckedInError(HabitError):
    pass


class InvalidDaysPerWeekError(HabitError):
    pass


@dataclass(frozen=True)
class Habit:
    name: str
    days_per_week: int
    check_ins: list[date] = field(default_factory=list)


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


def clean_name(name: str) -> str:
    cleaned = " ".join(name.split())
    if not cleaned:
        raise BlankNameError("habit name cannot be blank")
    return cleaned


def same_name(first: str, second: str) -> bool:
    return clean_name(first).casefold() == clean_name(second).casefold()


def find_habit(habits: list[Habit], name: str) -> Habit:
    for habit in habits:
        if same_name(habit.name, name):
            return habit
    raise UnknownHabitError(f"no habit called '{clean_name(name)}'")


def has_duplicate_names(habits: list[Habit]) -> bool:
    names = [clean_name(habit.name).casefold() for habit in habits]
    return len(set(names)) != len(names)


def add_habit(habits: list[Habit], name: str, days_per_week: int) -> list[Habit]:
    name = clean_name(name)
    if not is_valid_days_per_week(days_per_week):
        raise InvalidDaysPerWeekError(
            f"days must be between {MIN_DAYS_PER_WEEK} and {MAX_DAYS_PER_WEEK}"
        )
    if any(same_name(habit.name, name) for habit in habits):
        raise DuplicateHabitError(f"habit '{name}' already exists")
    return [*habits, Habit(name=name, days_per_week=days_per_week)]


def check_in(habits: list[Habit], name: str, day: date, today: date) -> list[Habit]:
    habit = find_habit(habits, name)
    if day > today:
        raise FutureCheckInError(f"{day.strftime(DAY_FORMAT)} has not happened yet")
    if day in habit.check_ins:
        raise AlreadyCheckedInError(
            f"{habit.name} is already checked in on {day.strftime(DAY_FORMAT)}"
        )
    checked_in = replace(habit, check_ins=sorted([*habit.check_ins, day]))
    return [checked_in if other is habit else other for other in habits]


def start_of_week(day: date) -> date:
    return day - timedelta(days=day.weekday())


def days_done_this_week(check_ins: list[date], today: date) -> int:
    monday = start_of_week(today)
    return len({day for day in check_ins if monday <= day <= today})


def format_week(habit: Habit, days_done: int) -> list[str]:
    goal = habit.days_per_week
    left = max(goal - days_done, 0)
    status = "goal reached" if left == 0 else f"{format_day_count(left)} to go"
    return [f"{habit.name}: {days_done} of {format_day_count(goal)} this week", status]


def parse_day(text: str) -> date:
    try:
        return datetime.strptime(text, DAY_FORMAT).date()
    except ValueError as error:
        raise InvalidDateError(f"date must look like 2026-10-12, not '{text}'") from error


def parse_month(text: str) -> date:
    try:
        return datetime.strptime(text, MONTH_FORMAT).date()
    except ValueError as error:
        raise InvalidDateError(f"month must look like 2026-10, not '{text}'") from error


def format_day_count(days: int) -> str:
    unit = "day" if days == 1 else "days"
    return f"{days} {unit}"


def format_habit(habit: Habit) -> str:
    return f"{habit.name}: {format_day_count(habit.days_per_week)} per week"


def format_streaks(habit: str, current: int, longest: int) -> list[str]:
    return [
        f"{habit}: {format_day_count(current)} in a row",
        f"longest streak: {format_day_count(longest)}",
    ]
