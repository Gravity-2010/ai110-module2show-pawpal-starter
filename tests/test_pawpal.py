"""Simple tests for the PawPal+ logic layer.

Run with pytest:      pytest
Or standalone:        python tests/test_pawpal.py
"""

import os
import sys
from datetime import date, time

# Allow importing pawpal_system from the project root when run from anywhere.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def test_mark_complete_changes_status():
    """Task Completion: mark_complete() flips completed False -> True."""
    task = Task.create_task("Morning walk", 30, Priority.HIGH)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Task Addition: adding a task grows the pet's task list by one."""
    owner = Owner.create_profile("Jordan")
    pet = Pet.create_pet("Mochi", "dog", owner)
    assert len(pet.tasks) == 0

    pet.add_task(Task.create_task("Feed dinner", 10, Priority.HIGH))

    assert len(pet.tasks) == 1


# --- helpers ------------------------------------------------------------

def _timed_task(title, hour, minute, duration=30):
    """A task with a fixed start_time, for sort/conflict tests."""
    t = Task.create_task(title, duration)
    t.start_time = time(hour, minute)
    return t


def _owner_with_pet():
    """Return (owner, pet, scheduler) wired together, no tasks yet."""
    owner = Owner.create_profile("Jordan")
    pet = Pet.create_pet("Mochi", "dog", owner)
    return owner, pet, Scheduler(owner)


# --- sorting correctness -----------------------------------------------

def test_sort_by_time_is_chronological():
    """Sorting: sort_by_time returns tasks in clock order regardless of input order."""
    owner, pet, sched = _owner_with_pet()
    # Added out of order on purpose.
    pet.add_task(_timed_task("Noon feed", 12, 0))
    pet.add_task(_timed_task("Early walk", 8, 30))
    pet.add_task(_timed_task("Mid meds", 10, 15))

    ordered = sched.sort_by_time()
    stamps = [t.start_time.strftime("%H:%M") for t in ordered]

    assert stamps == ["08:30", "10:15", "12:00"]


def test_sort_by_time_pushes_unscheduled_to_end():
    """Edge case: tasks with no start_time sort last, not first, and don't crash."""
    owner, pet, sched = _owner_with_pet()
    pet.add_task(_timed_task("Scheduled", 9, 0))
    pet.add_task(Task.create_task("Backlog item", 20))  # start_time stays None

    ordered = sched.sort_by_time()

    assert ordered[0].title == "Scheduled"
    assert ordered[-1].title == "Backlog item"


# --- recurrence logic ---------------------------------------------------

def test_daily_complete_creates_next_day_task():
    """Recurrence: completing a DAILY task spawns a new task due the following day."""
    owner, pet, sched = _owner_with_pet()
    walk = Task.create_task("Morning walk", 30, Priority.HIGH, Frequency.DAILY)
    pet.add_task(walk)
    assert len(pet.tasks) == 1

    today = date(2026, 7, 7)
    next_task = walk.mark_complete(today)

    assert walk.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == date(2026, 7, 8)      # exactly one day later
    assert next_task.frequency is Frequency.DAILY
    assert next_task in pet.tasks                       # attached to same pet
    assert len(pet.tasks) == 2


def test_weekly_complete_advances_seven_days():
    """Recurrence: a WEEKLY task's next occurrence is due 7 days out."""
    owner, pet, sched = _owner_with_pet()
    bath = Task.create_task("Bath", 45, Priority.MEDIUM, Frequency.WEEKLY)
    pet.add_task(bath)

    next_task = bath.mark_complete(date(2026, 7, 7))

    assert next_task is not None
    assert next_task.due_date == date(2026, 7, 14)


def test_once_task_does_not_recur():
    """Edge case: completing a ONCE task returns None and adds no new task."""
    owner, pet, sched = _owner_with_pet()
    vet = Task.create_task("Vet visit", 60, Priority.HIGH, Frequency.ONCE)
    pet.add_task(vet)

    result = vet.mark_complete(date(2026, 7, 7))

    assert result is None
    assert len(pet.tasks) == 1


# --- conflict detection -------------------------------------------------

def test_detect_conflicts_flags_identical_times():
    """Conflict: two tasks at the exact same start time are flagged."""
    owner, pet, sched = _owner_with_pet()
    pet.add_task(_timed_task("Feed", 8, 0, duration=15))
    pet.add_task(_timed_task("Meds", 8, 0, duration=15))

    warnings = sched.detect_conflicts()

    assert len(warnings) == 1
    assert "Conflict" in warnings[0]


def test_detect_conflicts_flags_overlap():
    """Conflict: an earlier task running into a later task's start is flagged."""
    owner, pet, sched = _owner_with_pet()
    pet.add_task(_timed_task("Long walk", 8, 0, duration=60))   # 08:00–09:00
    pet.add_task(_timed_task("Grooming", 8, 30, duration=30))   # starts 08:30

    warnings = sched.detect_conflicts()

    assert len(warnings) == 1


def test_detect_conflicts_ignores_adjacent_tasks():
    """Edge case: back-to-back tasks (one ends as the next starts) are NOT conflicts."""
    owner, pet, sched = _owner_with_pet()
    pet.add_task(_timed_task("Walk", 8, 0, duration=30))    # 08:00–08:30
    pet.add_task(_timed_task("Feed", 8, 30, duration=15))   # starts 08:30

    warnings = sched.detect_conflicts()

    assert warnings == []


def test_detect_conflicts_empty_when_no_tasks():
    """Edge case: a pet/owner with no tasks yields no conflicts and no error."""
    owner, pet, sched = _owner_with_pet()

    assert sched.detect_conflicts() == []


# --- scheduling edge cases ---------------------------------------------

def test_build_schedule_respects_time_budget():
    """Edge case: tasks that don't fit the minute budget are skipped."""
    owner, pet, sched = _owner_with_pet()
    pet.add_task(Task.create_task("Short feed", 10, Priority.HIGH))
    pet.add_task(Task.create_task("Long hike", 120, Priority.HIGH))

    scheduled = sched.build_schedule(available_minutes=30)

    titles = [t.title for t in scheduled]
    assert "Short feed" in titles
    assert "Long hike" not in titles


if __name__ == "__main__":
    # Minimal runner so the file works even without pytest installed.
    failures = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL  {name}: {exc}")
    sys.exit(1 if failures else 0)
