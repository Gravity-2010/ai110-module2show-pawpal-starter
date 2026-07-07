"""PawPal+ terminal testing ground.

A throwaway script to verify the logic layer works end-to-end before wiring it
into the Streamlit UI. Run with:  python main.py
"""

from datetime import date, time

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency


def main() -> None:
    # 1. Create an owner.
    owner = Owner.create_profile("Jordan")

    # 2. Create at least two pets (attached to the owner).
    mochi = Pet.create_pet("Mochi", "dog", owner)
    luna = Pet.create_pet("Luna", "cat", owner)

    # 3. Add tasks *out of order* (durations/priorities deliberately mixed) so
    #    the sorting methods below have something real to reorder.
    luna.add_task(Task.create_task("Playtime", 20, Priority.LOW, Frequency.ONCE))
    mochi.add_task(Task.create_task("Feed dinner", 10, Priority.HIGH, Frequency.DAILY))
    luna.add_task(Task.create_task("Clean litter", 15, Priority.MEDIUM, Frequency.DAILY))
    mochi.add_task(Task.create_task("Morning walk", 30, Priority.HIGH, Frequency.DAILY))

    # Quick sanity check of the object graph.
    print(f"Owner: {owner.name}")
    print(f"Pets:  {', '.join(p.name for p in owner.pets)}")
    print(f"Total tasks across all pets: {len(owner.all_tasks())}")
    print()

    scheduler = Scheduler(owner)

    # 4. Build and print "Today's Schedule".
    print("=== Today's Schedule ===")
    scheduled = scheduler.build_schedule(available_minutes=60)
    print(scheduler.explain(available_minutes=60))
    print()

    # 5. Sort the scheduled tasks by time (HH:MM) and list them chronologically.
    print("=== Scheduled tasks sorted by start time ===")
    for t in scheduler.sort_by_time(scheduled):
        stamp = t.start_time.strftime("%H:%M") if t.start_time else "--:--"
        print(f"  {stamp}  {t.title} ({t.pet.name})")
    print()

    # 6. Filtering: by pet name, and by completion status.
    print("=== Filtering ===")
    print("Mochi's tasks:", [t.title for t in scheduler.filter_tasks(pet_name="Mochi")])
    print("Pending tasks:", [t.title for t in scheduler.filter_tasks(completed=False)])
    print()

    # 7. Recurring tasks: completing a DAILY task spawns tomorrow's occurrence.
    print("=== Recurring regeneration ===")
    feed = mochi.tasks[0]  # "Feed dinner", a DAILY task
    today = date(2026, 7, 7)
    next_feed = scheduler.complete(feed, today=today)
    print(f"Completed '{feed.title}' (completed={feed.completed}).")
    if next_feed is not None:
        print(f"Auto-created next occurrence due {next_feed.due_date} "
              f"(completed={next_feed.completed}).")
    print()

    # 8. Conflict detection: two tasks deliberately placed at the same time.
    print("=== Conflict detection ===")
    vet = Task.create_task("Vet appointment", 45, Priority.HIGH)
    groom = Task.create_task("Grooming", 30, Priority.MEDIUM)
    mochi.add_task(vet)
    luna.add_task(groom)
    vet.start_time = time(9, 0)
    groom.start_time = time(9, 0)  # same slot -> should be flagged

    conflicts = scheduler.detect_conflicts([vet, groom])
    if conflicts:
        for warning in conflicts:
            print(warning)
    else:
        print("No conflicts detected.")


if __name__ == "__main__":
    main()
