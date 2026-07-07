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
    due_date: date | None = None           # which day this occurrence is for
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

    def mark_complete(self, today: date | None = None) -> "Task | None":
        """Mark this task completed and, if it recurs, spawn the next occurrence.

        For a DAILY or WEEKLY task, completing it automatically creates a fresh
        (uncompleted) copy whose `due_date` is advanced by the right interval —
        today + 1 day for daily, today + 7 days for weekly — attaches it to the
        same pet, and returns it. A ONCE task recurs nothing and returns None.

        `today` defaults to the real current date; pass it explicitly in tests
        so the computed due date is deterministic.
        """
        self.completed = True

        interval = {
            Frequency.DAILY: timedelta(days=1),
            Frequency.WEEKLY: timedelta(weeks=1),
        }.get(self.frequency)
        if interval is None:
            return None  # ONCE — nothing to reschedule

        base = today or self.due_date or date.today()
        next_task = Task(
            title=self.title,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            due_date=base + interval,
        )
        if self.pet is not None:
            self.pet.add_task(next_task)
        return next_task


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

    # --- sort & filter --------------------------------------------------
    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks sorted chronologically by their `start_time`.

        The sort key is each task's time rendered as an "HH:MM" string. Because
        the hours and minutes are zero-padded, plain string order matches clock
        order (e.g. "08:30" < "10:00"). Unscheduled tasks (start_time is None)
        sort to the end via the sentinel "99:99".
        """
        if tasks is None:
            tasks = self.all_tasks()
        return sorted(
            tasks,
            key=lambda t: t.start_time.strftime("%H:%M") if t.start_time else "99:99",
        )

    def filter_tasks(
        self, completed: bool | None = None, pet_name: str | None = None
    ) -> list[Task]:
        """Filter all of the owner's tasks by completion status and/or pet name.

        Pass `completed=True/False` to keep only done / not-done tasks, and/or
        `pet_name` to keep only one pet's tasks (case-insensitive). Omit both to
        get everything.
        """
        tasks = self.all_tasks()
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet and t.pet.name.lower() == pet_name.lower()]
        return tasks

    # --- manage ---------------------------------------------------------
    def complete(self, task: Task, today: date | None = None) -> "Task | None":
        """Mark a task done; return the next occurrence if it recurs (else None)."""
        return task.mark_complete(today)

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Lightweight overlap check across scheduled tasks.

        Sorts the timed tasks chronologically and compares each with the next,
        flagging any pair whose time slots overlap (including two tasks that
        start at the exact same time). Returns a list of human-readable warning
        strings — empty when there are no conflicts. Never raises, so callers
        can print the warnings without wrapping the call in error handling.
        """
        if tasks is None:
            tasks = self.all_tasks()

        timed = self.sort_by_time([t for t in tasks if t.start_time is not None])
        warnings: list[str] = []
        for current, nxt in zip(timed, timed[1:]):
            current_end = self._advance(current.start_time, current.duration)
            if nxt.start_time < current_end:
                who_a = current.pet.name if current.pet else "unknown pet"
                who_b = nxt.pet.name if nxt.pet else "unknown pet"
                warnings.append(
                    f"⚠️  Conflict: '{current.title}' ({who_a}) at "
                    f"{current.start_time.strftime('%H:%M')} overlaps "
                    f"'{nxt.title}' ({who_b}) at {nxt.start_time.strftime('%H:%M')}."
                )
        return warnings

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
