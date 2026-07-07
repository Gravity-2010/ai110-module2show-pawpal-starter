"""PawPal+ terminal testing ground.

A throwaway script to verify the logic layer works end-to-end before wiring it
into the Streamlit UI. Run with:  python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency


def main() -> None:
    # 1. Create an owner.
    owner = Owner.create_profile("Jordan")

    # 2. Create at least two pets (attached to the owner).
    mochi = Pet.create_pet("Mochi", "dog", owner)
    luna = Pet.create_pet("Luna", "cat", owner)

    # 3. Add at least three tasks with different durations/priorities.
    mochi.add_task(Task.create_task("Morning walk", 30, Priority.HIGH, Frequency.DAILY))
    mochi.add_task(Task.create_task("Feed dinner", 10, Priority.HIGH, Frequency.DAILY))
    luna.add_task(Task.create_task("Clean litter", 15, Priority.MEDIUM, Frequency.DAILY))
    luna.add_task(Task.create_task("Playtime", 20, Priority.LOW, Frequency.ONCE))

    # Quick sanity check of the object graph.
    print(f"Owner: {owner.name}")
    print(f"Pets:  {', '.join(p.name for p in owner.pets)}")
    print(f"Total tasks across all pets: {len(owner.all_tasks())}")
    print()

    # 4. Build and print "Today's Schedule".
    scheduler = Scheduler(owner)
    print("=== Today's Schedule ===")
    print(scheduler.explain(available_minutes=60))


if __name__ == "__main__":
    main()
