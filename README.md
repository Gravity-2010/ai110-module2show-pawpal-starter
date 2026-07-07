# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## ✨ Features

PawPal+ implements the following scheduling algorithms (all in `pawpal_system.py`):

- **Priority-first budgeting** — `build_schedule()` sorts pending tasks by priority
  (highest first, ties broken by shortest duration), then greedily packs them into the
  day's available-minutes budget, stamping each with a `start_time`. Tasks that don't
  fit are reported as "skipped" rather than silently dropped.
- **Sorting by time** — `sort_by_time()` returns tasks in chronological order using each
  task's zero-padded `"HH:MM"` string as the key; unscheduled tasks sort to the end.
- **Filtering** — `filter_tasks()` narrows the task list by completion status and/or pet
  name (case-insensitive).
- **Conflict warnings** — `detect_conflicts()` sorts timed tasks and compares each with
  its neighbor, flagging any overlap (including two tasks at the exact same minute) as a
  friendly warning. It warns rather than auto-resolving, leaving the owner in control.
- **Daily / weekly recurrence** — completing a recurring task (`mark_complete()`)
  auto-spawns the next occurrence, due +1 day (daily) or +7 days (weekly), attached to
  the same pet. `ONCE` tasks don't recur.
- **Plain-language explanations** — `explain()` renders a human-readable summary of the
  generated plan, including how much of the time budget was used.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```
'''
![alt text](file:///home/gravity/Pictures/Screenshots/Screenshot%20from%202026-07-07%2011-58-16.png)
'''

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The suite lives in `tests/test_pawpal.py` and covers both the happy paths and the
trickier edge cases of the scheduling logic in `pawpal_system.py`:

- **Task basics** — completing a task flips its status; adding a task grows the pet's list.
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological order, and
  unscheduled tasks (`start_time is None`) sort to the end instead of crashing.
- **Recurrence logic** — completing a `DAILY` task spawns a new task due the following
  day (and a `WEEKLY` task one 7 days out), attached to the same pet; a `ONCE` task
  does not recur.
- **Conflict detection** — two tasks at the exact same time are flagged, overlapping
  slots are flagged, back-to-back (adjacent) tasks are *not* flagged, and an empty
  schedule produces no warnings.
- **Budget planning** — `build_schedule()` skips tasks that don't fit the time budget.

Successful test run:

```
============================= test session starts ==============================
platform linux -- Python 3.13.5, pytest-9.1.1, pluggy-1.5.0
rootdir: /mnt/Documents/Summer2026/AI110/ai110-module2show-pawpal-starter
collected 12 items

tests/test_pawpal.py ............                                        [100%]

============================== 12 passed in 0.02s ==============================
```

### Confidence Level: ★★★★☆ (4 / 5)

All 12 tests pass and they exercise every core scheduling behavior — sorting,
recurrence, conflict detection, and budget-limited planning — plus the main edge
cases (no tasks, identical/adjacent times, non-recurring tasks). The core logic is
well covered and behaves as designed. Holding back the fifth star because the tests
are unit-level only: the Streamlit UI in `app.py`, cross-pet scheduling at scale, and
day-boundary/timezone behavior are not yet under test.

## 📐 Smarter Scheduling

All scheduling logic lives in `pawpal_system.py`. Each feature and the method that implements it:

| Feature | Method | What it does |
|---------|--------|--------------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks chronologically by `start_time`, using each task's "HH:MM" string as the sort key. Unscheduled tasks go last. |
| Filtering | `Scheduler.filter_tasks()` | Returns tasks filtered by completion status (`completed=True/False`) and/or `pet_name` (case-insensitive). |
| Conflict detection | `Scheduler.detect_conflicts()` | Compares each scheduled task's time slot with the next one and returns a warning message for any overlap. Warns instead of crashing. |
| Recurring tasks | `Task.mark_complete()` | Completing a `DAILY` or `WEEKLY` task auto-creates the next occurrence (due today + 1 day / + 7 days, via `timedelta`). `ONCE` tasks don't recur. |
| Priority planning | `Scheduler.build_schedule()` | Picks pending tasks that fit the time budget, highest priority first, and stamps each with a start time. |

## 📸 Demo Walkthrough

### Main UI features and actions

Launch the Streamlit app with `streamlit run app.py`. From there a pet owner can:

- **Set up an owner profile** — enter/update the owner's name (persisted across reruns
  via `st.session_state`).
- **Add pets** — name + species; each pet is stored under the owner.
- **Add care tasks** to the selected pet — title, duration (minutes), and priority
  (low / medium / high).
- **Browse tasks** with a filter toggle (**All / Pending / Done**) that runs through
  `Scheduler.filter_tasks()`, shown in a clean table with priority and frequency.
- **Generate a daily schedule** by entering the minutes available today. The app builds
  the plan, shows a chronological table, lists anything that didn't fit, and runs a
  conflict check.

### Example workflow

1. Owner **Jordan** opens the app.
2. Adds a pet: **Mochi (dog)**, then a second pet **Luna (cat)**.
3. Adds tasks — *Morning walk* (30 min, high), *Feed dinner* (10 min, high) for Mochi;
   *Clean litter* (15 min, medium), *Playtime* (20 min, low) for Luna.
4. Enters **60 minutes** available today and clicks **Generate schedule**.
5. Views **Today's schedule** sorted by start time, sees *Playtime* flagged as skipped
   (didn't fit the budget), and reads the conflict check result.

### Key Scheduler behaviors shown

- **Priority-first budgeting** — high-priority tasks are placed first; the low-priority
  *Playtime* is dropped when 60 minutes runs out (`build_schedule()`).
- **Sorting by time** — the schedule table is ordered chronologically (`sort_by_time()`).
- **Recurrence** — completing the daily *Feed dinner* auto-creates tomorrow's occurrence
  (`mark_complete()`).
- **Conflict warnings** — two tasks placed at the same time (e.g. a 9:00 vet visit and a
  9:00 grooming) are flagged with a friendly warning (`detect_conflicts()`), presented in
  the UI via `st.warning` so the owner can decide which to move.

### Sample CLI output (`python main.py`)

The `main.py` script exercises the full logic layer end-to-end in the terminal:

```
Owner: Jordan
Pets:  Mochi, Luna
Total tasks across all pets: 4

=== Today's Schedule ===
Plan for Jordan (55 of 60 min used, 3 tasks):
  08:00  Feed dinner (10 min, high priority) for Mochi
  08:10  Morning walk (30 min, high priority) for Mochi
  08:40  Clean litter (15 min, medium priority) for Luna
Skipped 1 task(s) that didn't fit: Playtime

=== Scheduled tasks sorted by start time ===
  08:00  Feed dinner (Mochi)
  08:10  Morning walk (Mochi)
  08:40  Clean litter (Luna)

=== Filtering ===
Mochi's tasks: ['Feed dinner', 'Morning walk']
Pending tasks: ['Feed dinner', 'Morning walk', 'Playtime', 'Clean litter']

=== Recurring regeneration ===
Completed 'Feed dinner' (completed=True).
Auto-created next occurrence due 2026-07-08 (completed=False).

=== Conflict detection ===
⚠️  Conflict: 'Vet appointment' (Mochi) at 09:00 overlaps 'Grooming' (Luna) at 09:00.
```
