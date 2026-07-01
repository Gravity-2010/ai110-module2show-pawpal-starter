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
