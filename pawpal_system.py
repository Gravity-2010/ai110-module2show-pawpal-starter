"""PawPal+ logic layer.

Backend classes for the pet care planning assistant. This module holds the
domain objects (Owner, Pet, Task, Plan) that the Streamlit UI in app.py will
call into. Structure mirrors diagrams/uml.mmd.

Method bodies are intentionally left as stubs to be implemented next.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Owner:
    """A pet owner."""

    name: str

    @classmethod
    def create_profile(cls, name: str) -> "Owner":
        """Create and return a new Owner profile."""
        raise NotImplementedError

    def update_name(self, new_name: str) -> None:
        """Change the owner's name."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet belonging to an Owner."""

    name: str
    species: str
    owner: Owner

    @classmethod
    def create_pet(cls, name: str, species: str, owner: Owner) -> "Pet":
        """Create and return a new Pet."""
        raise NotImplementedError

    def update_pet_info(self, name: str | None = None, species: str | None = None) -> None:
        """Update this pet's basic info."""
        raise NotImplementedError


@dataclass
class Task:
    """A single care task for a pet (e.g. a walk or feeding)."""

    title: str
    duration: int          # minutes
    priority: str          # "low" | "medium" | "high"
    pet: Pet
    completed: bool = False

    @classmethod
    def create_task(cls, title: str, duration: int, priority: str, pet: Pet) -> "Task":
        """Create and return a new Task."""
        raise NotImplementedError

    def edit_task(
        self,
        title: str | None = None,
        duration: int | None = None,
        priority: str | None = None,
    ) -> None:
        """Edit the task's fields."""
        raise NotImplementedError

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        raise NotImplementedError


@dataclass
class Plan:
    """A daily care plan: an ordered set of tasks for one pet."""

    pet: Pet
    date: date
    tasks: list[Task] = field(default_factory=list)
    summary: str = ""

    @classmethod
    def generate_plan(cls, pet: Pet, tasks: list[Task], day: date) -> "Plan":
        """Build a schedule for the day by choosing and ordering tasks
        based on constraints (time, priority, preferences)."""
        raise NotImplementedError

    def explain_plan(self) -> str:
        """Return a human-readable explanation of why each task was chosen
        and when it happens."""
        raise NotImplementedError
