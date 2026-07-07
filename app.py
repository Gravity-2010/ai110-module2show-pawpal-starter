import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

# --- Persist the Owner in the session "vault" -----------------------------
# st.session_state survives Streamlit's top-to-bottom re-run on every click.
# Create the Owner only the FIRST time; afterwards reuse the stored instance
# so its pets and tasks persist as the user interacts with the app.
if "owner" not in st.session_state:
    st.session_state.owner = Owner.create_profile(owner_name)

# Always read the persisted owner back out of the vault, then sync its name.
owner = st.session_state.owner
owner.update_name(owner_name)

# --- Add a Pet ------------------------------------------------------------
st.markdown("### Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name", value="Mochi")
    new_species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet") and new_pet_name:
        # Pet.create_pet builds the object; owner.add_pet stores + back-links it.
        owner.add_pet(Pet.create_pet(new_pet_name, new_species))
        st.success(f"Added {new_pet_name} the {new_species}.")

if not owner.pets:
    st.info("No pets yet. Add one above to start scheduling tasks.")
    st.stop()

# Pick which pet to work with (by index, so duplicate names don't collide).
pet_index = st.selectbox(
    "Select a pet",
    range(len(owner.pets)),
    format_func=lambda i: f"{owner.pets[i].name} ({owner.pets[i].species})",
)
pet = owner.pets[pet_index]

st.markdown(f"### Tasks for {pet.name}")
st.caption("Add care tasks. They attach to the selected pet and feed into the scheduler.")

# Map the UI's string priority to the Priority enum the logic layer expects.
PRIORITY_MAP = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    pet.add_task(
        Task.create_task(task_title, int(duration), PRIORITY_MAP[priority])
    )

if pet.tasks:
    st.write("Current tasks:")
    # Filter via the Scheduler so the UI reflects the same logic the planner uses.
    scheduler = Scheduler(owner)
    task_filter = st.radio(
        "Show", ["All", "Pending", "Done"], horizontal=True, label_visibility="collapsed"
    )
    completed_flag = {"All": None, "Pending": False, "Done": True}[task_filter]
    shown = scheduler.filter_tasks(completed=completed_flag, pet_name=pet.name)

    if shown:
        st.table(
            [
                {
                    "title": t.title,
                    "duration_minutes": t.duration,
                    "priority": t.priority.name.lower(),
                    "frequency": t.frequency.value,
                    "done": "✅" if t.completed else "⬜",
                }
                for t in shown
            ]
        )
    else:
        st.info(f"No {task_filter.lower()} tasks for {pet.name}.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Chooses the highest-priority tasks that fit your time budget and orders them.")

available_minutes = st.number_input(
    "Time available today (minutes)", min_value=5, max_value=1440, value=60
)

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    scheduled = scheduler.build_schedule(available_minutes=int(available_minutes))

    if not scheduled:
        st.warning(
            "Nothing scheduled — either there are no pending tasks, or none fit "
            "your time budget. Try adding more minutes above."
        )
    else:
        used = sum(t.duration for t in scheduled)
        st.success(
            f"Planned {len(scheduled)} task(s) using {used} of "
            f"{int(available_minutes)} minutes for {owner.name}."
        )

        # --- Today's schedule, sorted chronologically by start time --------
        st.markdown("#### 🕒 Today's schedule")
        st.table(
            [
                {
                    "time": t.start_time.strftime("%H:%M") if t.start_time else "--:--",
                    "task": t.title,
                    "pet": t.pet.name if t.pet else "—",
                    "minutes": t.duration,
                    "priority": t.priority.name.lower(),
                }
                for t in scheduler.sort_by_time(scheduled)
            ]
        )

        # --- Tasks that didn't fit the budget ------------------------------
        skipped = [t for t in scheduler.pending_tasks() if t not in scheduled]
        if skipped:
            st.info(
                "Didn't fit today: " + ", ".join(t.title for t in skipped)
            )

        # --- Conflict warnings ---------------------------------------------
        st.markdown("#### ⚠️ Conflict check")
        conflicts = scheduler.detect_conflicts(scheduled)
        if conflicts:
            st.warning(
                f"{len(conflicts)} scheduling conflict(s) found. These tasks "
                "overlap — you'll want to move one or shorten it:"
            )
            for warning in conflicts:
                # Strip the leading emoji; Streamlit's st.warning adds its own icon.
                st.warning(warning.replace("⚠️  ", ""))
        else:
            st.success("No scheduling conflicts — your pets' day is clear! 🐾")
