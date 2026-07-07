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

*Briefly describe your initial UML design. What classes did you include, and what
responsibilities did you assign to each?*

My initial UML (see `diagrams/uml.mmd`) had four classes:

- **Owner** — the person using the app; responsible for identity (`name`) and profile
  management (`create_profile`, `update_name`).
- **Pet** — a single animal belonging to an owner; responsible for its own details
  (`name`, `species`) and edits (`create_pet`, `update_pet_info`).
- **Task** — one care activity; responsible for its own data (`title`, `duration`,
  `priority`, `completed`) and lifecycle (`create_task`, `edit_task`, `mark_complete`).
- **Plan** — the scheduling object; responsible for choosing tasks for a day and
  explaining the result (`generate_plan`, `explain_plan`).

The idea was a clear ownership chain (Owner → Pet → Task) with `Plan` as a separate
object that assembled a day's tasks. The final version keeps this shape but renames
`Plan` to **Scheduler** and moves the task backlog onto `Pet` (see the changes below).
The as-built diagram is `diagrams/uml_final.mmd`.

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

*What constraints does your scheduler consider? How did you decide which mattered most?*

The scheduler balances two hard constraints:

1. **Time budget** — the owner says how many minutes they have today, and
   `build_schedule()` never schedules past that limit. Any task that doesn't fit is
   reported as "skipped" instead of being dropped silently.
2. **Priority** — tasks are ordered highest-priority-first (a `Priority` IntEnum:
   HIGH > MEDIUM > LOW), with ties broken by shortest duration so more tasks fit.

I decided priority mattered most because the whole point of the app is helping a busy
owner do the *important* things first when they can't do everything. Time is the
constraint that forces the trade-off — without a budget, "prioritization" is
meaningless because everything just gets scheduled. Together they answer the real
question: "If I only have an hour, what should I actually do?" I treated per-owner
preferences (preferred times, per-pet ordering) as out of scope for this iteration to
keep the core algorithm simple and testable.

**b. Tradeoffs**

Conflict detection warns instead of resolving, and only checks neighbouring tasks.

`Scheduler.detect_conflicts()` compares each task's full time slot against the next one (start time plus duration, via `_advance`), so it does catch real overlaps — not just tasks that start at the exact same minute. But it makes two
deliberate simplifications:

1. It reports conflicts rather than fixing them. When two tasks overlap, the method returns a plain warning string and leaves both tasks where they are. It never shuffles start times, shortens a task, or drops one. The owner is told "these two clash — you decide," instead of the program silently rearranging their day.
2. It only compares each task with its immediate neighbour after sorting by time, not every task against every other. This is O(n) instead of O(n²): fast and simple, and enough to flag back-to-back clashes. The blind spot is one long task that overlaps a later, non-adjacent task — e.g. a 90-minute task at 9:00 that runs into a task at 10:15 with a shorter task sitting between them could be missed.

---

## 3. AI Collaboration

**a. How you used AI**

*How did you use AI tools during this project? What kinds of prompts were most helpful?*

I used my AI coding assistant across every phase:

- **Design brainstorming** — turning my rough class list into a UML diagram and
  pressure-testing whether the relationships made sense.
- **Implementation** — generating the dataclass scaffolding for `Owner`, `Pet`, `Task`,
  and `Scheduler`, then filling in the scheduling logic incrementally.
- **Refactoring** — catching the `Plan` → `Scheduler` rename and the string-vs-enum
  priority bug.
- **Testing** — drafting the pytest suite covering sorting, recurrence, and conflicts.

The most helpful prompts were **specific and behavior-focused** — e.g. "what edge cases
should I test for a scheduler with recurring tasks?" or "how should a conflict warning be
presented to a pet owner?" — rather than "write my app." Asking *why* a suggestion was
made was more useful than asking *what* to write.

**b. Judgment and verification**

*Describe one moment where you did not accept an AI suggestion as-is. How did you verify?*

When I asked for a priority field, the first suggestion used plain strings
(`"low"/"medium"/"high"`). I rejected it because sorting those strings alphabetically
puts `"high"` before `"low"` — the exact opposite of what the scheduler needs. I replaced
it with a `Priority` IntEnum so `sorted()` works directly and a typo becomes an error.

I verified AI suggestions by (1) reading the code line by line rather than pasting it
blindly, (2) running `python main.py` to watch real output end-to-end, and (3) writing
tests that assert the behavior — the 12-test suite passing is my objective check that the
logic does what the AI and I agreed it should.

**c. AI Strategy**

*Which AI coding assistant features were most effective for building your scheduler?*

The most effective features were **multi-file, context-aware editing** (the assistant
could see `pawpal_system.py`, `app.py`, and the tests together and keep them consistent),
**inline explanation of trade-offs** (e.g. why O(n) neighbor-only conflict detection is a
reasonable simplification), and the ability to **run tests/scripts and read the output**
so suggestions were grounded in real behavior instead of guesses. Asking it to generate
edge-case *test ideas* was more valuable than asking it to generate features.

*Give one example of an AI suggestion you rejected or modified to keep the design clean.*

Beyond the string-vs-enum priority fix, the assistant initially proposed having the
`Scheduler` (originally `Plan`) own the master list of tasks. I modified this so the
**backlog lives on `Pet`** and the `Scheduler` only *selects* from it for a given day.
This kept a single source of truth for tasks and stopped the scheduler from turning into
a god-object that owned all the state — the pet owns its tasks; the scheduler just plans.

*How did using separate chat sessions for different phases help you stay organized?*

I kept separate sessions for **design**, **implementation**, and **testing/docs**. This
stopped context from bleeding together: the design session stayed focused on class
responsibilities without drowning in syntax, and the testing session started from the
finished code instead of half-formed ideas. Each session had a clear goal, so when I came
back I knew exactly what "done" looked like, and I could revisit the design conversation
without scrolling past hundreds of lines of implementation chatter.

*What did you learn about being the "lead architect" when collaborating with powerful AI
tools?*

The AI is a fast, tireless implementer, but it optimizes for "make this work now," not
"keep the system coherent over time" — that judgment is mine. My job as lead architect
was to **own the decisions that are expensive to reverse**: the class boundaries, where
state lives, and which constraints matter. The AI could propose ten ways to detect
conflicts, but deciding to *warn instead of auto-resolve* (so the owner stays in control)
was a design call, not a coding one. I learned to treat AI output as a strong draft to
review against my design intent, not as an answer to accept — the best results came when
I set the direction clearly and used the AI to move fast *within* those guardrails.

---

## 4. Testing and Verification

**a. What you tested**

*What behaviors did you test, and why were these tests important?*

The suite in `tests/test_pawpal.py` (12 tests, all passing) covers:

- **Task basics** — completing a task flips its status; adding a task grows the list.
- **Sorting correctness** — `sort_by_time()` returns chronological order, and
  unscheduled tasks sort last instead of crashing.
- **Recurrence** — completing a daily task spawns a new task due the next day (weekly →
  +7 days), attached to the same pet; a `ONCE` task does not recur.
- **Conflict detection** — identical times flagged, overlaps flagged, adjacent
  back-to-back tasks *not* flagged, and empty input produces no warnings.
- **Budget planning** — `build_schedule()` skips tasks that don't fit.

These matter because sorting, recurrence, and conflict detection are the three
behaviors most likely to be *subtly* wrong (off-by-one on time boundaries, wrong date
math, alphabetical vs. numeric ordering) — the kind of bug that looks fine in a demo but
fails on a real edge case.

**b. Confidence**

*How confident are you that your scheduler works correctly? What would you test next?*

Fairly confident — **4 / 5**. Every core algorithm is exercised by a passing test,
including the tricky boundary cases (same-time vs. adjacent tasks). I'd hold back the
last point because the tests are unit-level only. With more time I'd test: the Streamlit
UI flows in `app.py`, the non-adjacent overlap blind spot in `detect_conflicts()` (a long
task overlapping a later, non-neighboring one), scheduling across many pets at scale, and
day-boundary/timezone behavior when a recurring task rolls into the next day.

---

## 5. Reflection

**a. What went well**

*What part of this project are you most satisfied with?*

I'm most satisfied with how the `Scheduler` turned out as a clean "brain" layer: it reads
and organizes tasks that live on the pets without owning that state itself. The priority-
first budgeting plus the plain-language `explain()` output makes the app feel like it's
actually *reasoning* about the day rather than just listing tasks — and the whole thing
is backed by a passing test suite.

**b. What you would improve**

*If you had another iteration, what would you improve or redesign?*

I'd upgrade `detect_conflicts()` from neighbor-only (O(n)) to a full pairwise/interval
check so it catches a long task overlapping a later non-adjacent one. I'd also add owner
**preferences** (preferred time windows, per-pet ordering) as a real constraint, and let
the scheduler *suggest* a resolution for conflicts (e.g. "move grooming to 09:45") instead
of only warning. Persisting data beyond the Streamlit session would make it genuinely
usable day to day.

**c. Key takeaway**

*What is one important thing you learned about designing systems or working with AI?*

The biggest lesson was that **where state lives is the decision that shapes everything
else.** Moving the task backlog onto `Pet` (and keeping the `Scheduler` stateless over the
owner) resolved a cascade of smaller ambiguities. Working with AI reinforced this: the AI
is excellent at producing code fast, but the architectural calls — class boundaries,
constraints, warn-vs-resolve — are mine to own. I got the best results by setting a clear
design and using AI to move quickly *within* it, then verifying everything with tests.
