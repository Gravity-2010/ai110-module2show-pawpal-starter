"""Simple tests for the PawPal+ logic layer.

Run with pytest:      pytest
Or standalone:        python tests/test_pawpal.py
"""

import os
import sys

# Allow importing pawpal_system from the project root when run from anywhere.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Owner, Pet, Task, Priority


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
