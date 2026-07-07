# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The 5 core actions that I think the user should be able to perform are:

- Add a pet
- Add a care task (such as a walk or feeding)
- Schedule a task for today
- View today’s tasks
- Mark a task as complete


Objects I want to use along with their methods and attributes:

1. Owner
- Attributes:
    name
- Methods:
    create_profile()
    update_name()

2. Pet
- Attributes:
    name
    species
    owner
- Methods:
    create_pet()
    update_pet_info()

3. Task
- Attributes:
    title
    duration
    priority
    pet
    completed (optional for now)
- Methods:
    create_task()
    edit_task()
    mark_complete()

4. Plan
- Attributes:
    pet
    tasks
    date
    summary/explanation
- Methods:
    generate_plan()
    explain_plan()

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Following are the gaps which I fixed:

1. Made the class relationships two-directional and settled where tasks live. 
My UML said an Owner owns many Pets and a Pet has many Tasks, but in code only the child pointed up (`Pet.owner`, `Task.pet`) — a parent had no way to list its children. I added `Owner.pets` and `Pet.tasks` (plus
`add_pet()` / `add_task()` helpers). This also resolved an ambiguity: the Pet now holds the full backlog** of care tasks, while a Plan holds only
the subset chosen for one day. Without this, "Add a pet" and "View today's tasks" had nowhere to store or read their data.

2. Changed `priority` from a string to a `Priority` IntEnum (LOW/MEDIUM/HIGH). The scheduler's core step is ordering tasks by priority, and the strings `"low"/"medium"/"high"` sort alphabetically (`"high" < "low"`), which is wrong. An ordered IntEnum lets me sort tasks directly and turns a mistyped priority into an error instead of a silent bug.

3. Added scheduling time and a time budget, which the original design was missing. `explain_plan()` promised to say "when" each task happens, but nothing recorded a time, and `generate_plan()` had no limit to schedule
against. I added `Task.start_time` (set when a task is placed in a plan) and changed `generate_plan(pet, day, available_minutes)` to take the day's available minutes. Now the scheduler has a real constraint to enforce and can report when each task occurs (what to drop when tasks don't all fit).

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
