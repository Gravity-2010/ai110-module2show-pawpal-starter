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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
