from habit_tracker.habits import Habit, format_day_count


def format_history(habit: Habit) -> list[str]:
    if not habit.check_ins:
        return [f"{habit.name}: no check-ins yet"]
    days = sorted(set(habit.check_ins))
    header = f"{habit.name}: done on {format_day_count(len(days))}"
    return [header, *(day.isoformat() for day in days)]
