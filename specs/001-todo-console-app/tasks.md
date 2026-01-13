# Tasks: Todo Console Application

**Input**: Feature specification from `specs/001-todo-console-app/spec.md`
**Prerequisites**: spec.md (user stories and requirements)

**Tests**: No automated tests requested - manual CLI validation against acceptance criteria

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, at repository root (no tests/ directory for Phase I)
- Paths assume single project structure with domain logic separated from I/O

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure (src/ for application code)
- [X] T002 Create Python package structure with __init__.py files in src/
- [X] T003 [P] Create README.md with setup and usage instructions
- [X] T004 [P] Verify Python 3.13+ is available and document version requirement

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain model and data structures that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create Task domain model in src/models/task.py with attributes (id, title, description, completed)
- [X] T006 Create TaskRepository in src/repositories/task_repository.py for in-memory storage using dictionary
- [X] T007 Implement task ID generation strategy (auto-increment starting from 1) in TaskRepository
- [X] T008 Create base CLI framework in src/cli/menu.py with menu display and input handling
- [X] T009 Create main application entry point in src/main.py with application loop

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to add new tasks and view all existing tasks - foundation of todo application

**Independent Test**: Launch app, add several tasks with different titles and descriptions, view list to confirm all tasks appear with unique IDs and correct details

### Implementation for User Story 1

- [X] T010 [P] [US1] Implement add_task() method in src/repositories/task_repository.py with title validation
- [X] T011 [P] [US1] Implement get_all_tasks() method in src/repositories/task_repository.py
- [X] T012 [US1] Create CLI handler for "Add Task" in src/cli/task_handlers.py with input prompts for title and description
- [X] T013 [US1] Create CLI handler for "View Tasks" in src/cli/task_handlers.py with formatted output
- [X] T014 [US1] Integrate add_task handler into main menu in src/main.py (menu option 1)
- [X] T015 [US1] Integrate view_tasks handler into main menu in src/main.py (menu option 2)
- [X] T016 [US1] Add validation for empty/whitespace-only titles in add_task handler
- [X] T017 [US1] Add empty list message handling in view_tasks handler

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - this is the MVP!

**Manual Validation Checklist for US1**:
- [ ] Can add task with title only
- [ ] Can add task with title and description
- [ ] Cannot add task with empty title
- [ ] Can view all tasks with correct formatting
- [ ] View shows "No tasks" message when list is empty
- [ ] Each task displays: ID, title, description (if present), completion status

---

## Phase 4: User Story 2 - Mark Tasks Complete (Priority: P2)

**Goal**: Enable users to toggle task completion status between complete and incomplete

**Independent Test**: Add a task, mark it complete, view list to see status change, mark it incomplete again to verify toggle behavior

### Implementation for User Story 2

- [ ] T018 [P] [US2] Implement toggle_complete() method in src/repositories/task_repository.py
- [ ] T019 [P] [US2] Add task existence validation in toggle_complete() method
- [ ] T020 [US2] Create CLI handler for "Mark Complete/Incomplete" in src/cli/task_handlers.py
- [ ] T021 [US2] Add input prompt for task ID in mark_complete handler with non-numeric input handling
- [ ] T022 [US2] Integrate mark_complete handler into main menu in src/main.py (menu option 5)
- [ ] T023 [US2] Add confirmation message showing new status after toggle
- [ ] T024 [US2] Add "Task not found" error handling for invalid task IDs

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

**Manual Validation Checklist for US2**:
- [ ] Can mark incomplete task as complete
- [ ] Can mark complete task as incomplete (toggle)
- [ ] See "Task not found" error for invalid ID
- [ ] See confirmation message after successful toggle
- [ ] View tasks shows updated completion status

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Enable users to update task title and/or description for existing tasks

**Independent Test**: Add a task, update its title and/or description, view task to confirm changes were applied correctly

### Implementation for User Story 3

- [ ] T025 [P] [US3] Implement update_task() method in src/repositories/task_repository.py
- [ ] T026 [P] [US3] Add task existence validation in update_task() method
- [ ] T027 [US3] Create CLI handler for "Update Task" in src/cli/task_handlers.py
- [ ] T028 [US3] Add input prompts for task ID, new title, and new description in update handler
- [ ] T029 [US3] Implement partial update logic (update title only, description only, or both)
- [ ] T030 [US3] Add title validation (reject empty titles) in update handler
- [ ] T031 [US3] Integrate update_task handler into main menu in src/main.py (menu option 3)
- [ ] T032 [US3] Add confirmation message showing updated fields

**Checkpoint**: User Stories 1, 2, AND 3 should all work independently

**Manual Validation Checklist for US3**:
- [ ] Can update task title only
- [ ] Can update task description only
- [ ] Can update both title and description
- [ ] Cannot update with empty title
- [ ] See "Task not found" error for invalid ID
- [ ] See confirmation message after successful update

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P4)

**Goal**: Enable users to delete tasks they no longer need

**Independent Test**: Add several tasks, delete one or more by ID, view list to confirm deleted tasks no longer appear

### Implementation for User Story 4

- [ ] T033 [P] [US4] Implement delete_task() method in src/repositories/task_repository.py
- [ ] T034 [P] [US4] Add task existence validation in delete_task() method
- [ ] T035 [US4] Create CLI handler for "Delete Task" in src/cli/task_handlers.py
- [ ] T036 [US4] Add input prompt for task ID in delete handler with non-numeric input handling
- [ ] T037 [US4] Integrate delete_task handler into main menu in src/main.py (menu option 4)
- [ ] T038 [US4] Add confirmation message after successful deletion
- [ ] T039 [US4] Add "Task not found" error handling for invalid task IDs

**Checkpoint**: User Stories 1, 2, 3, AND 4 should all work independently

**Manual Validation Checklist for US4**:
- [ ] Can delete existing task by ID
- [ ] Deleted task no longer appears in view
- [ ] Other tasks remain after deletion
- [ ] See "Task not found" error for invalid ID
- [ ] See confirmation message after successful deletion

---

## Phase 7: User Story 5 - Exit Application (Priority: P5)

**Goal**: Enable graceful application exit with data loss warning

**Independent Test**: Select exit option from menu and confirm application terminates without errors

### Implementation for User Story 5

- [ ] T040 [US5] Implement exit handler in src/cli/menu.py with data loss warning
- [ ] T041 [US5] Integrate exit option into main menu in src/main.py (menu option 6)
- [ ] T042 [US5] Ensure clean application termination (no hanging processes)

**Checkpoint**: All user stories should now be independently functional - feature complete!

**Manual Validation Checklist for US5**:
- [ ] Can select "Exit" from menu
- [ ] See warning about data loss
- [ ] Application terminates cleanly
- [ ] No error messages on exit

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T043 [P] Add input validation for all menu selections (handle invalid choices gracefully)
- [ ] T044 [P] Standardize error messages across all handlers for consistency
- [ ] T045 [P] Improve task display formatting for better readability
- [ ] T046 [P] Add edge case handling for very long titles/descriptions (reasonable limits)
- [ ] T047 [P] Test unicode character support in titles and descriptions
- [ ] T048 Comprehensive manual testing against all acceptance criteria from spec.md
- [ ] T049 Update README.md with complete usage examples for all features
- [ ] T050 Final validation: Run through all user stories to ensure independent functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - No dependencies on other stories

**Key Insight**: All user stories are independent after the foundational phase completes!

### Within Each User Story

- Repository methods before CLI handlers
- CLI handlers before menu integration
- Validation and error handling after core functionality
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- T010 and T011 (repository methods for US1) can run in parallel
- Once Foundational phase completes, ALL user stories can start in parallel (if team capacity allows)
- All repository methods across different stories marked [P] can run in parallel
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch repository methods for User Story 1 together:
Task: "Implement add_task() method in src/repositories/task_repository.py"
Task: "Implement get_all_tasks() method in src/repositories/task_repository.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add and View Tasks)
4. **STOP and VALIDATE**: Manually test User Story 1 against acceptance criteria
5. This is a working MVP - demonstrates core value!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Working MVP!
3. Add User Story 2 → Test independently → Enhanced with completion tracking
4. Add User Story 3 → Test independently → Enhanced with editing
5. Add User Story 4 → Test independently → Enhanced with deletion
6. Add User Story 5 → Test independently → Complete with graceful exit
7. Polish → Final quality improvements
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
   - Developer E: User Story 5
3. Stories complete and integrate independently

---

## Manual Testing Strategy

After each user story phase, validate against acceptance criteria from spec.md:

### User Story 1 Acceptance Testing
1. Launch application
2. Add task with title only → verify ID assigned, status "Incomplete"
3. Add task with title and description → verify both fields stored
4. View all tasks → verify formatting, all fields visible
5. View tasks when empty → verify "No tasks" message
6. Attempt to add task with empty title → verify error message

### User Story 2 Acceptance Testing
1. Add a task
2. Mark it complete → verify status changes to "Complete"
3. Mark it complete again → verify status toggles to "Incomplete"
4. Attempt to mark non-existent task → verify "Task not found" error
5. View tasks → verify completion status displays correctly

### User Story 3 Acceptance Testing
1. Add a task
2. Update title only → verify title changes, description unchanged
3. Update description only → verify description changes, title unchanged
4. Update both → verify both change
5. Attempt to update non-existent task → verify "Task not found" error
6. Attempt to update with empty title → verify error message

### User Story 4 Acceptance Testing
1. Add multiple tasks
2. Delete one task by ID → verify task removed
3. View tasks → verify deleted task gone, others remain
4. Attempt to delete non-existent task → verify "Task not found" error

### User Story 5 Acceptance Testing
1. Add tasks
2. Select "Exit" option → verify data loss warning displays
3. Confirm exit → verify application terminates cleanly
4. Restart application → verify data is reset (no tasks from previous session)

### Edge Case Testing (Phase 8)
1. Test invalid menu selections (letters, numbers out of range)
2. Test non-numeric input for task IDs
3. Test very long titles and descriptions (10,000+ characters)
4. Test unicode characters in titles and descriptions
5. Test whitespace-only titles
6. Verify no crashes on any invalid input

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Manual testing against acceptance criteria is the primary validation method
- No automated test framework required for Phase I
- All code must be generated by Claude Code (no manual editing per constitution)
- Maintain separation of concerns: domain logic (models, repositories) separate from I/O (CLI handlers)
