import asyncio
from collections.abc import Awaitable, Callable
from datetime import date, timedelta
from pathlib import Path

import pytest
from textual.pilot import Pilot
from textual.widgets import DataTable, Static

from habit_tracker.habits import Habit
from habit_tracker.storage import load_habits, save_habits
from habit_tracker.tui import ConfirmScreen, FormScreen, HabitDashboard

FRIDAY = date(2026, 11, 27)
THURSDAY = FRIDAY - timedelta(days=1)

Steps = Callable[[HabitDashboard, Pilot[None]], Awaitable[None]]


@pytest.fixture
def data_path(tmp_path: Path) -> Path:
    return tmp_path / "habits.json"


def use_dashboard(path: Path, steps: Steps) -> None:
    async def scenario() -> None:
        app = HabitDashboard(path, FRIDAY)
        async with app.run_test() as pilot:
            await pilot.pause()
            await steps(app, pilot)
            await pilot.pause()

    asyncio.run(scenario())


def detail_of(app: HabitDashboard) -> str:
    return str(app.query_one("#detail", Static).render())


def test_it_shows_one_row_per_habit_and_the_details_of_the_first(data_path: Path) -> None:
    save_habits(data_path, [Habit("reading", 3, [THURSDAY]), Habit("running", 2)])

    async def steps(app: HabitDashboard, pilot: Pilot[None]) -> None:
        assert app.query_one(DataTable).row_count == 2
        assert "1 day in a row" in detail_of(app)
        assert "November 2026" in detail_of(app)

    use_dashboard(data_path, steps)


def test_with_no_habits_it_says_how_to_add_one(data_path: Path) -> None:
    async def steps(app: HabitDashboard, pilot: Pilot[None]) -> None:
        assert "Press a to add" in detail_of(app)
        await pilot.press("space", "d", "r")
        assert not isinstance(app.screen, FormScreen | ConfirmScreen)

    use_dashboard(data_path, steps)
    assert load_habits(data_path) == []


def test_space_checks_in_today_and_space_again_undoes_it(data_path: Path) -> None:
    save_habits(data_path, [Habit("reading", 3)])

    async def check_in(app: HabitDashboard, pilot: Pilot[None]) -> None:
        await pilot.press("space")

    use_dashboard(data_path, check_in)
    assert load_habits(data_path) == [Habit("reading", 3, [FRIDAY])]
    use_dashboard(data_path, check_in)
    assert load_habits(data_path) == [Habit("reading", 3)]


def test_the_arrow_keys_choose_which_habit_a_key_acts_on(data_path: Path) -> None:
    save_habits(data_path, [Habit("reading", 3), Habit("running", 2)])

    async def steps(app: HabitDashboard, pilot: Pilot[None]) -> None:
        await pilot.press("down", "space")

    use_dashboard(data_path, steps)
    assert load_habits(data_path) == [Habit("reading", 3), Habit("running", 2, [FRIDAY])]


def test_a_adds_a_habit_with_its_weekly_goal(data_path: Path) -> None:
    async def steps(app: HabitDashboard, pilot: Pilot[None]) -> None:
        await pilot.press("a", *"reading", "enter", "backspace", "3", "enter")

    use_dashboard(data_path, steps)
    assert load_habits(data_path) == [Habit("reading", 3)]


def test_escape_closes_a_form_without_changing_anything(data_path: Path) -> None:
    async def steps(app: HabitDashboard, pilot: Pilot[None]) -> None:
        await pilot.press("a", *"reading", "escape")
        assert not isinstance(app.screen, FormScreen)

    use_dashboard(data_path, steps)
    assert not data_path.exists()


def test_c_and_u_check_in_and_undo_another_day(data_path: Path) -> None:
    save_habits(data_path, [Habit("reading", 3)])
    clear_the_field = ["backspace"] * len(FRIDAY.isoformat())

    async def check_in(app: HabitDashboard, pilot: Pilot[None]) -> None:
        await pilot.press("c", *clear_the_field, *THURSDAY.isoformat(), "enter")

    async def undo(app: HabitDashboard, pilot: Pilot[None]) -> None:
        await pilot.press("u", *clear_the_field, *THURSDAY.isoformat(), "enter")

    use_dashboard(data_path, check_in)
    assert load_habits(data_path) == [Habit("reading", 3, [THURSDAY])]
    use_dashboard(data_path, undo)
    assert load_habits(data_path) == [Habit("reading", 3)]


def test_r_renames_and_g_changes_the_goal_without_losing_check_ins(data_path: Path) -> None:
    save_habits(data_path, [Habit("reading", 3, [THURSDAY])])

    async def steps(app: HabitDashboard, pilot: Pilot[None]) -> None:
        await pilot.press("r", *["backspace"] * len("reading"), *"books", "enter")
        await pilot.press("g", "backspace", "5", "enter")

    use_dashboard(data_path, steps)
    assert load_habits(data_path) == [Habit("books", 5, [THURSDAY])]


def test_d_deletes_only_after_y(data_path: Path) -> None:
    save_habits(data_path, [Habit("reading", 3)])

    async def say_no(app: HabitDashboard, pilot: Pilot[None]) -> None:
        await pilot.press("d", "n")

    async def say_yes(app: HabitDashboard, pilot: Pilot[None]) -> None:
        await pilot.press("d", "y")

    use_dashboard(data_path, say_no)
    assert load_habits(data_path) == [Habit("reading", 3)]
    use_dashboard(data_path, say_yes)
    assert load_habits(data_path) == []


def test_bad_input_changes_nothing_and_the_dashboard_stays_open(data_path: Path) -> None:
    save_habits(data_path, [Habit("reading", 3)])

    async def steps(app: HabitDashboard, pilot: Pilot[None]) -> None:
        await pilot.press("g", "backspace", "9", "enter")
        await pilot.press("c", *"x", "enter")
        await pilot.press("a", *"reading", "enter", "enter")
        assert app.is_running
        assert app.query_one(DataTable).row_count == 1

    use_dashboard(data_path, steps)
    assert load_habits(data_path) == [Habit("reading", 3)]


def test_p_and_n_show_other_months(data_path: Path) -> None:
    save_habits(data_path, [Habit("reading", 3)])

    async def steps(app: HabitDashboard, pilot: Pilot[None]) -> None:
        await pilot.press("p")
        assert "October 2026" in detail_of(app)
        await pilot.press("n", "n")
        assert "December 2026" in detail_of(app)

    use_dashboard(data_path, steps)


def test_t_switches_between_the_light_and_the_dark_theme(data_path: Path) -> None:
    async def steps(app: HabitDashboard, pilot: Pilot[None]) -> None:
        await pilot.press("t")
        assert app.theme == "textual-light"
        await pilot.press("t")
        assert app.theme == "textual-dark"

    use_dashboard(data_path, steps)
