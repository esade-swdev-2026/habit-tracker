from collections.abc import Callable
from datetime import date
from pathlib import Path

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Header, Input, Label, Static

from habit_tracker.dashboard import (
    WEEKDAY_HEADINGS,
    CalendarDay,
    DayState,
    HabitRow,
    first_of_month,
    goal_bar,
    goal_reached,
    habit_row,
    month_calendar,
    next_month,
    parse_days_per_week,
    previous_month,
)
from habit_tracker.habits import (
    MAX_DAYS_PER_WEEK,
    Habit,
    HabitError,
    add_habit,
    change_weekly_target,
    check_in,
    delete_habit,
    format_day_count,
    format_streaks,
    format_summary,
    format_week,
    monthly_summary,
    parse_day,
    rename_habit,
    undo_check_in,
)
from habit_tracker.storage import load_habits, save_habits

COLUMN_HEADINGS = ("Habit", "Today", "This week", "Streak")
NO_HABITS_TEXT = "No habits yet.\n\nPress a to add your first one."
SELECT_A_HABIT_MESSAGE = "Add a habit first: press a."
FORM_HINT = "Enter to confirm · Esc to cancel"
CONFIRM_HINT = "y to delete · n or Esc to keep it"
MONTH_KEYS_HINT = "p / n: other months"
LIGHT_THEME = "textual-light"
DARK_THEME = "textual-dark"

DONE_STYLE = "bold green"
DAY_STYLES = {
    DayState.DONE: "bold black on green",
    DayState.TODAY: "bold underline",
    DayState.NOT_DONE: "",
    DayState.FUTURE: "dim",
}

Change = Callable[[list[Habit]], list[Habit]]


def today_cell(row: HabitRow) -> Text:
    return Text("✓ done", style=DONE_STYLE) if row.done_today else Text("not yet", style="dim")


def week_cell(row: HabitRow) -> Text:
    bar = goal_bar(row.days_done_this_week, row.days_per_week)
    cell = f"{bar} {row.days_done_this_week}/{row.days_per_week}"
    return Text(cell, style=DONE_STYLE if goal_reached(row) else "")


def table_cells(row: HabitRow) -> tuple[Text | str, ...]:
    return (
        row.name,
        today_cell(row),
        week_cell(row),
        format_day_count(row.current_streak),
    )


def calendar_text(weeks: list[list[CalendarDay | None]]) -> Text:
    text = Text()
    text.append(" ".join(WEEKDAY_HEADINGS) + "\n", style="bold")
    for week in weeks:
        for cell in week:
            if cell is None:
                text.append("   ")
            else:
                text.append(f"{cell.day.day:>2}", style=DAY_STYLES[cell.state])
                text.append(" ")
        text.append("\n")
    return text


def detail_text(habit: Habit, shown_month: date, today: date) -> Text:
    row = habit_row(habit, today)
    month = monthly_summary(habit.check_ins, shown_month.year, shown_month.month)
    lines = [
        *format_week(habit, row.days_done_this_week),
        *format_streaks(habit.name, row.current_streak, row.longest_streak),
    ]
    text = Text()
    for line in lines:
        text.append(line.removeprefix(f"{habit.name}: ") + "\n")
    text.append("\n" + shown_month.strftime("%B %Y") + "\n", style="bold")
    text.append("\n".join(format_summary(habit.name, month)[1:]) + "\n\n")
    text.append_text(calendar_text(month_calendar(habit.check_ins, shown_month, today)))
    text.append("\n")
    text.append(" 1", style=DAY_STYLES[DayState.DONE])
    text.append(" done   ")
    text.append(" 1", style=DAY_STYLES[DayState.TODAY])
    text.append(" today\n")
    text.append(MONTH_KEYS_HINT, style="dim")
    return text


def error_message(error: HabitError | OSError) -> str:
    if isinstance(error, OSError):
        return f"could not open the data file {error.filename}: {error.strerror}"
    return str(error)


class FormScreen(ModalScreen[list[str] | None]):
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, title: str, fields: list[tuple[str, str]]) -> None:
        super().__init__()
        self.form_title = title
        self.fields = fields

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog"):
            yield Label(self.form_title, classes="dialog-title")
            for question, starting_value in self.fields:
                yield Label(question)
                yield Input(value=starting_value)
            yield Label(FORM_HINT, classes="hint")

    def on_input_submitted(self, submitted: Input.Submitted) -> None:
        inputs = list(self.query(Input))
        position = inputs.index(submitted.input)
        if position < len(inputs) - 1:
            inputs[position + 1].focus()
        else:
            self.dismiss([field.value for field in inputs])

    def action_cancel(self) -> None:
        self.dismiss(None)


class ConfirmScreen(ModalScreen[bool]):
    BINDINGS = [
        Binding("y", "answer(True)", "Yes"),
        Binding("n,escape", "answer(False)", "No"),
    ]

    def __init__(self, question: str) -> None:
        super().__init__()
        self.question = question

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog"):
            yield Label(self.question, classes="dialog-title")
            yield Label(CONFIRM_HINT, classes="hint")

    def action_answer(self, confirmed: bool) -> None:
        self.dismiss(confirmed)


class HabitDashboard(App[None]):
    TITLE = "Habit Tracker"
    ENABLE_COMMAND_PALETTE = False
    CSS = """
    #habits { width: 1fr; height: 100%; border: round $primary; }
    #detail { width: 30; height: 100%; border: round $primary; padding: 1 2; }
    ModalScreen { align: center middle; }
    .dialog { width: 60; height: auto; padding: 1 2; border: thick $primary; background: $surface; }
    .dialog-title { width: 100%; text-style: bold; margin-bottom: 1; }
    .hint { color: $text-muted; margin-top: 1; }
    """
    BINDINGS = [
        Binding("space", "toggle_today", "Today"),
        Binding("c", "check_in_day", "Check in"),
        Binding("u", "undo_day", "Undo"),
        Binding("a", "add", "Add"),
        Binding("r", "rename", "Rename"),
        Binding("g", "goal", "Goal"),
        Binding("d", "delete", "Delete"),
        Binding("p", "previous_month", "Prev month", show=False),
        Binding("n", "next_month", "Next month", show=False),
        Binding("t", "switch_theme", "Theme"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, path: Path, today: date) -> None:
        super().__init__()
        self.path = path
        self.today = today
        self.habits: list[Habit] = []
        self.shown_month = first_of_month(today)

    def compose(self) -> ComposeResult:
        yield Header(icon="")
        with Horizontal():
            yield DataTable(id="habits", cursor_type="row", zebra_stripes=True)
            yield Static(id="detail")
        yield Footer(compact=True)

    def on_mount(self) -> None:
        self.sub_title = f"{self.today.strftime('%A')} {self.today.isoformat()}"
        table = self.query_one(DataTable)
        table.border_title = "Habits"
        table.add_columns(*COLUMN_HEADINGS)
        self.apply(lambda habits: habits)

    def apply(self, change: Change, message: str = "") -> None:
        try:
            before = load_habits(self.path)
            after = change(before)
            if after != before:
                save_habits(self.path, after)
        except (HabitError, OSError) as error:
            self.notify(error_message(error), severity="error")
            return
        self.show_habits(after)
        if message:
            self.notify(message)

    def show_habits(self, habits: list[Habit]) -> None:
        self.habits = habits
        table = self.query_one(DataTable)
        selected = min(table.cursor_row, max(len(habits) - 1, 0))
        table.clear()
        for habit in habits:
            table.add_row(*table_cells(habit_row(habit, self.today)))
        table.move_cursor(row=selected)
        self.show_detail()

    def show_detail(self) -> None:
        detail = self.query_one("#detail", Static)
        habit = self.selected_habit()
        if habit is None:
            detail.border_title = "Details"
            detail.update(NO_HABITS_TEXT)
        else:
            detail.border_title = habit.name
            detail.update(detail_text(habit, self.shown_month, self.today))

    def selected_habit(self) -> Habit | None:
        row = self.query_one(DataTable).cursor_row
        return self.habits[row] if 0 <= row < len(self.habits) else None

    def on_data_table_row_highlighted(self) -> None:
        self.show_detail()

    def with_selected_habit(self, use: Callable[[Habit], None]) -> None:
        habit = self.selected_habit()
        if habit is None:
            self.notify(SELECT_A_HABIT_MESSAGE, severity="warning")
        else:
            use(habit)

    def ask(
        self, title: str, fields: list[tuple[str, str]], use: Callable[[list[str]], None]
    ) -> None:
        def use_answers(answers: list[str] | None) -> None:
            if answers is not None:
                use(answers)

        self.push_screen(FormScreen(title, fields), use_answers)

    def action_toggle_today(self) -> None:
        self.with_selected_habit(self.toggle_today)

    def toggle_today(self, habit: Habit) -> None:
        day = self.today.isoformat()
        if self.today in habit.check_ins:
            self.apply(
                lambda habits: undo_check_in(habits, habit.name, self.today),
                f"Removed the check-in of {habit.name} on {day}",
            )
        else:
            self.apply(
                lambda habits: check_in(habits, habit.name, self.today, self.today),
                f"Checked in {habit.name} on {day}",
            )

    def action_check_in_day(self) -> None:
        self.with_selected_habit(
            lambda habit: self.ask(
                f"Check in {habit.name}",
                [("Day as YYYY-MM-DD", self.today.isoformat())],
                lambda answers: self.apply(
                    lambda habits: check_in(habits, habit.name, parse_day(answers[0]), self.today),
                    f"Checked in {habit.name} on {answers[0]}",
                ),
            )
        )

    def action_undo_day(self) -> None:
        self.with_selected_habit(
            lambda habit: self.ask(
                f"Undo a check-in of {habit.name}",
                [("Day as YYYY-MM-DD", self.today.isoformat())],
                lambda answers: self.apply(
                    lambda habits: undo_check_in(habits, habit.name, parse_day(answers[0])),
                    f"Removed the check-in of {habit.name} on {answers[0]}",
                ),
            )
        )

    def action_add(self) -> None:
        self.ask(
            "Add a habit",
            [("Name", ""), ("Days per week (1 to 7)", str(MAX_DAYS_PER_WEEK))],
            lambda answers: self.apply(
                lambda habits: add_habit(habits, answers[0], parse_days_per_week(answers[1])),
                f"Added {answers[0].strip()}",
            ),
        )

    def action_rename(self) -> None:
        self.with_selected_habit(
            lambda habit: self.ask(
                f"Rename {habit.name}",
                [("New name", habit.name)],
                lambda answers: self.apply(
                    lambda habits: rename_habit(habits, habit.name, answers[0]),
                    f"Renamed {habit.name} to {answers[0].strip()}",
                ),
            )
        )

    def action_goal(self) -> None:
        self.with_selected_habit(
            lambda habit: self.ask(
                f"Weekly goal of {habit.name}",
                [("Days per week (1 to 7)", str(habit.days_per_week))],
                lambda answers: self.apply(
                    lambda habits: change_weekly_target(
                        habits, habit.name, parse_days_per_week(answers[0])
                    ),
                    f"Updated {habit.name}: {answers[0].strip()} days per week",
                ),
            )
        )

    def action_delete(self) -> None:
        self.with_selected_habit(self.confirm_delete)

    def confirm_delete(self, habit: Habit) -> None:
        def delete_if_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                self.apply(lambda habits: delete_habit(habits, habit.name), f"Deleted {habit.name}")

        question = f"Delete {habit.name} and all its check-ins? This cannot be undone."
        self.push_screen(ConfirmScreen(question), delete_if_confirmed)

    def action_previous_month(self) -> None:
        self.shown_month = previous_month(self.shown_month)
        self.show_detail()

    def action_next_month(self) -> None:
        self.shown_month = next_month(self.shown_month)
        self.show_detail()

    def action_switch_theme(self) -> None:
        self.theme = DARK_THEME if self.theme == LIGHT_THEME else LIGHT_THEME
