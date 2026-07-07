"""PawPal+ logic layer.

Backend classes for the pet care planning assistant. This module holds the
domain objects (Owner, Pet, Task, Plan) that the Streamlit UI in app.py will
call into. Structure mirrors diagrams/uml.mmd.

Method bodies are intentionally left as stubs to be implemented next.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from enum import IntEnum


class Priority(IntEnum):
    """Task priority as an ordered value so the scheduler can sort/compare it.

    Higher number = more important. Using an IntEnum (instead of the strings
    "low"/"medium"/"high") means `sorted(tasks, key=lambda t: t.priority)`
    works directly and typos become errors instead of silent bugs.
    """

    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Owner:
    """A pet owner. Owns many pets (see `pets`)."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    @classmethod
    def create_profile(cls, name: str) -> "Owner":
        """Create and return a new Owner profile."""
        raise NotImplementedError

    def update_name(self, new_name: str) -> None:
        """Change the owner's name."""
        raise NotImplementedError

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner (keeps `pets` in sync)."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet belonging to an Owner. Holds the full backlog of care tasks."""

    name: str
    species: str
    owner: Owner
    tasks: list[Task] = field(default_factory=list)

    @classmethod
    def create_pet(cls, name: str, species: str, owner: Owner) -> "Pet":
        """Create and return a new Pet."""
        raise NotImplementedError

    def update_pet_info(self, name: str | None = None, species: str | None = None) -> None:
        """Update this pet's basic info."""
        raise NotImplementedError

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's backlog."""
        raise NotImplementedError


@dataclass
class Task:
    """A single care task for a pet (e.g. a walk or feeding).

    `start_time` is None while the task sits in the backlog and is set by
    `Plan.generate_plan` once the task is placed in the day's schedule.
    """

    title: str
    duration: int                      # minutes
    priority: Priority
    pet: Pet
    completed: bool = False
    start_time: time | None = None     # when it happens, once scheduled

    @classmethod
    def create_task(cls, title: str, duration: int, priority: Priority, pet: Pet) -> "Task":
        """Create and return a new Task."""
        raise NotImplementedError

    def edit_task(
        self,
        title: str | None = None,
        duration: int | None = None,
        priority: Priority | None = None,
    ) -> None:
        """Edit the task's fields."""
        raise NotImplementedError

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        raise NotImplementedError


@dataclass
class Plan:
    """A daily care plan: the subset of a pet's tasks chosen for one day,
    ordered and time-stamped to fit within a time budget."""

    pet: Pet
    date: date
    tasks: list[Task] = field(default_factory=list)   # today's chosen subset
    summary: str = ""

    @classmethod
    def generate_plan(cls, pet: Pet, day: date, available_minutes: int) -> "Plan":
        """Build a schedule for the day.

        Reads candidate tasks from `pet.tasks`, then chooses and orders them
        by priority so their total duration fits within `available_minutes`,
        assigning each chosen task a `start_time`.
        """
        raise NotImplementedError

    def explain_plan(self) -> str:
        """Return a human-readable explanation of why each task was chosen
        and when it happens."""
        raise NotImplementedError
