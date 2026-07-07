"""PawPal+ logic layer.

Backend classes for the pet care planning assistant. This module holds the
domain objects that the Streamlit UI in app.py calls into:

    Task      - a single care activity (description, time, frequency, status)
    Pet       - pet details plus its list of tasks
    Owner     - manages multiple pets and exposes all their tasks
    Scheduler - the "brain" that retrieves, organizes, and manages tasks
                across an owner's pets

Structure mirrors diagrams/uml.mmd (the earlier `Plan` class is now the
`Scheduler`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum, IntEnum


class Priority(IntEnum):
    """Task priority as an ordered value so the scheduler can sort/compare it.

    Higher number = more important. Using an IntEnum (instead of the strings
    "low"/"medium"/"high") means `sorted(tasks, key=lambda t: t.priority)`
    works directly and typos become errors instead of silent bugs.
    """

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(Enum):
    """How often a care task recurs."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    """A single care task for a pet (e.g. a walk or feeding).

    `start_time` is None while the task sits in the backlog and is set by the
    Scheduler once the task is placed in the day's schedule.
    """

    title: str
    duration: int                          # minutes
    priority: Priority = Priority.MEDIUM
    frequency: Frequency = Frequency.ONCE
    completed: bool = False
    start_time: time | None = None         # when it happens, once scheduled
    pet: "Pet | None" = None               # back-reference, set on attach

    @classmethod
    def create_task(
        cls,
        title: str,
        duration: int,
        priority: Priority = Priority.MEDIUM,
        frequency: Frequency = Frequency.ONCE,
    ) -> "Task":
        """Create and return a new Task (not yet attached to a pet)."""
        return cls(title=title, duration=duration, priority=priority, frequency=frequency)

    def edit_task(
        self,
        title: str | None = None,
        duration: int | None = None,
        priority: Priority | None = None,
        frequency: Frequency | None = None,
    ) -> None:
        """Edit the task's fields. Only the arguments you pass are changed."""
        if title is not None:
            self.title = title
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority
        if frequency is not None:
            self.frequency = frequency

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    """A pet belonging to an Owner. Holds the full backlog of care tasks."""

    name: str
    species: str
    owner: "Owner | None" = None
    tasks: list[Task] = field(default_factory=list)

    @classmethod
    def create_pet(cls, name: str, species: str, owner: "Owner | None" = None) -> "Pet":
        """Create and return a new Pet, attaching it to `owner` if given."""
        pet = cls(name=name, species=species)
        if owner is not None:
            owner.add_pet(pet)
        return pet

    def update_pet_info(self, name: str | None = None, species: str | None = None) -> None:
        """Update this pet's basic info."""
        if name is not None:
            self.name = name
        if species is not None:
            self.species = species

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's backlog and back-link it to the pet."""
        task.pet = self
        self.tasks.append(task)

    def pending_tasks(self) -> list[Task]:
        """Tasks that still need doing."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    """A pet owner. Owns many pets and provides access to all their tasks."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    @classmethod
    def create_profile(cls, name: str) -> "Owner":
        """Create and return a new Owner profile."""
        return cls(name=name)

    def update_name(self, new_name: str) -> None:
        """Change the owner's name."""
        self.name = new_name

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner and back-link it (keeps both sides in sync)."""
        pet.owner = self
        self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class Scheduler:
    """The "brain": retrieves, organizes, and manages tasks across an owner's pets.

    A single Scheduler works over one Owner. `build_schedule` chooses the most
    important pending tasks that fit within a time budget, orders them, and
    stamps each with a start time so the plan can say *when* things happen.
    """

    owner: Owner
    day_start: time = time(8, 0)   # tasks are laid out starting at this time

    # --- retrieve -------------------------------------------------------
    def all_tasks(self) -> list[Task]:
        """All tasks across the owner's pets (delegates to Owner)."""
        return self.owner.all_tasks()

    def pending_tasks(self, pet: Pet | None = None) -> list[Task]:
        """Uncompleted tasks, optionally narrowed to a single pet."""
        source = pet.tasks if pet is not None else self.all_tasks()
        return [t for t in source if not t.completed]

    # --- organize -------------------------------------------------------
    def build_schedule(self, available_minutes: int, pet: Pet | None = None) -> list[Task]:
        """Select pending tasks that fit the budget, ordered by priority and time-stamped."""
        candidates = sorted(
            self.pending_tasks(pet),
            key=lambda t: (-t.priority, t.duration),
        )

        scheduled: list[Task] = []
        remaining = available_minutes
        clock = self.day_start
        for task in candidates:
            if task.duration <= remaining:
                task.start_time = clock
                clock = self._advance(clock, task.duration)
                remaining -= task.duration
                scheduled.append(task)
        return scheduled

    # --- manage ---------------------------------------------------------
    def complete(self, task: Task) -> None:
        """Mark a task done."""
        task.mark_complete()

    def explain(self, available_minutes: int, pet: Pet | None = None) -> str:
        """Build a schedule and return a human-readable explanation of it."""
        scheduled = self.build_schedule(available_minutes, pet)
        if not scheduled:
            return "No tasks scheduled — nothing pending, or none fit the time budget."

        used = sum(t.duration for t in scheduled)
        lines = [
            f"Plan for {self.owner.name} "
            f"({used} of {available_minutes} min used, {len(scheduled)} tasks):"
        ]
        for t in scheduled:
            who = t.pet.name if t.pet else "unknown pet"
            stamp = t.start_time.strftime("%H:%M") if t.start_time else "--:--"
            lines.append(
                f"  {stamp}  {t.title} ({t.duration} min, {t.priority.name.lower()} "
                f"priority) for {who}"
            )
        skipped = [t for t in self.pending_tasks(pet) if t not in scheduled]
        if skipped:
            lines.append(
                f"Skipped {len(skipped)} task(s) that didn't fit: "
                + ", ".join(t.title for t in skipped)
            )
        return "\n".join(lines)

    @staticmethod
    def _advance(t: time, minutes: int) -> time:
        """Return the time `minutes` after `t` (same-day arithmetic helper)."""
        return (datetime.combine(date.min, t) + timedelta(minutes=minutes)).time()
