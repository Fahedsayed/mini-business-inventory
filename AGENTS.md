# AGENTS.md

## Project

This repository is a small full-stack learning project.

The purpose is to build the application incrementally while learning professional full-stack development practices.

The AI agent is an implementation assistant. It is **not the owner of the project**.

The developer must understand and review changes before they are committed.

### Current stack

- Backend: FastAPI + Python
- Database: SQLAlchemy
- Frontend: React + TypeScript
- Testing: Python unittest / pytest as the project evolves
- Version control: Git + GitHub
- Project management: Linear

---

# 1. Core Development Philosophy

This is a **learning-by-practice project**.

Prefer:

- Small changes
- Clear code
- Existing project conventions
- Minimal abstractions
- Explicit implementation
- Tests for changed behavior
- Understanding over automation

Avoid:

- Overengineering
- Unnecessary refactoring
- Adding libraries without a reason
- Implementing future features early
- Changing unrelated code
- Guessing project structure

The agent should optimize for:

```text
Correctness
    +
Understanding
    +
Small change set
    +
Verifiable results
```

---

# 2. Repository Grounding — MANDATORY

Before implementing, testing, running, or verifying anything, the agent MUST first establish the actual repository structure.

## Never Assume Paths

Do NOT assume that these paths exist:

```text
backend/
frontend/
tests/
alembic/
database.db
main.py
requirements.txt
package.json
```

These are examples only.

The repository itself is the source of truth.

First determine the actual paths.

At the beginning of an implementation task, inspect:

```bash
pwd
git rev-parse --show-toplevel
git status
```

Then inspect the relevant repository structure.

Use the discovered paths for all subsequent commands.

---

# 3. Repository Discovery

Before coding, determine the following when relevant:

```text
Repository root:
Backend root:
Frontend root:
Python environment:
Python entry point:
FastAPI application object:
Database configuration:
Database path / URL:
SQLAlchemy Base:
Models location:
Test location:
Test framework:
Test command:
Frontend package manager:
Frontend start command:
Frontend build command:
Frontend test command:
```

Only report values that were actually discovered.

Never guess.

If something cannot be determined, report:

```text
Not determined
```

---

# 4. Environment Discovery

Before running application or test commands:

### Python

Determine:

- Whether a virtual environment exists
- Which Python executable is being used
- Which dependency management system is used
- Which dependency file controls the environment

Examples may include:

```text
.venv/
venv/
pyproject.toml
requirements.txt
```

But do not assume any of them.

Verify the actual environment.

### Frontend

Determine:

- package manager
- `package.json` location
- available scripts
- expected Node environment if relevant

Do not invent commands such as:

```bash
npm test
npm run build
npm run dev
```

unless the repository confirms them.

---

# 5. Application Startup Discovery

Never assume the application starts with:

```bash
uvicorn main:app --reload
```

First identify:

- FastAPI entry point
- application object
- startup command
- host
- port
- required environment variables

Use the repository's existing conventions.

If the application is already running, determine how it was started before starting another instance.

---

# 6. Database Discovery

Never assume the database location.

Determine the actual SQLAlchemy database configuration.

For example, if the application uses:

```text
sqlite:///...
```

resolve the actual database path based on the application's configuration.

The database used for verification MUST be the same database used by the application unless the issue explicitly requires otherwise.

For database-related issues, verify:

```text
Database configuration
        ↓
Actual database
        ↓
Expected schema
```

Do not create or inspect a different database accidentally.

---

# 7. Testing Discovery

Before testing, identify the project's actual testing framework and commands.

Possible frameworks include:

```text
unittest
pytest
Vitest
Jest
```

Do not assume which one is being used.

Inspect existing tests and project configuration first.

Use existing commands/conventions whenever possible.

If no test framework exists, do not spend excessive time inventing one.

Report:

```text
No existing test framework detected.
```

when appropriate.

---

# 8. Command Failure Recovery

If a command fails because of:

- File not found
- Directory not found
- Module not found
- Wrong working directory
- Wrong executable
- Wrong port
- Wrong database path
- Wrong configuration path
- Wrong test command

DO NOT repeatedly guess alternatives.

Follow this process:

```text
Command fails
     ↓
Stop
     ↓
Inspect repository/configuration
     ↓
Determine correct path/command
     ↓
Retry once
     ↓
If still failing → report blocker
```

Do not waste significant time repeatedly trying guessed paths.

---

# 9. Issue-Driven Development

Every implementation must be based on a specific issue.

Before changing code:

1. Read the complete issue requirements.
2. Inspect the existing repository.
3. Establish the actual project structure.
4. Identify relevant files/components.
5. Understand the existing implementation.
6. Determine the smallest reasonable change set.
7. Determine how the change will be tested.
8. Identify the acceptance criteria.

Do not implement requirements that are not part of the current issue.

If an issue is ambiguous, stop and ask for clarification when the ambiguity could significantly affect architecture, behavior, dependencies, or scope.

For small implementation details, follow existing conventions and choose the simplest reasonable solution.

---

# 10. Git Preparation

Before implementation:

```bash
git status
```

Determine:

- Current branch
- Working tree state
- Existing modifications
- Whether the current branch is appropriate for the issue

Do not overwrite, discard, or silently modify existing developer work.

If unrelated uncommitted changes exist:

1. Identify them.
2. Determine whether they belong to the current issue.
3. If they do not clearly belong to the issue, stop and report them.

Never automatically run:

```bash
git reset --hard
git clean -fd
git restore .
```

unless explicitly instructed.

---

# 11. Standard Development Workflow

The expected workflow is:

```text
Linear Issue
    ↓
Verify Git state
    ↓
Correct feature branch
    ↓
Repository discovery
    ↓
Understand requirements
    ↓
Inspect existing implementation
    ↓
Plan smallest change
    ↓
AI implementation
    ↓
Targeted verification
    ↓
Automated tests/checks
    ↓
AI self-review
    ↓
Human review
    ↓
Fix issues if necessary
    ↓
Final tests
    ↓
Commit
    ↓
Push
    ↓
Pull Request
    ↓
PR review
    ↓
Merge
```

The agent must not skip repository discovery, testing, or review.

The agent must not commit, push, or create a PR unless explicitly instructed.

---

# 12. Agent Implementation Rules

## Before coding

- Inspect relevant files first.
- Follow existing architecture.
- Reuse existing configuration and utilities when appropriate.
- Do not create duplicate implementations.
- Do not modify unrelated files.
- Identify the exact files likely to change.
- Confirm assumptions against the repository.

## During coding

- Make the smallest clean change that satisfies the issue.
- Preserve existing behavior unless explicitly required otherwise.
- Keep business logic separate from infrastructure.
- Prefer readable code over clever code.
- Add comments only when they explain something non-obvious.

## After coding

- Run targeted verification first.
- Run relevant tests.
- Run available linting and formatting checks.
- Run type checks when configured.
- Inspect the final Git diff.
- Check for accidental changes.
- Verify every acceptance criterion.
- Report what changed and why.

---

# 13. Scope Control

The agent must not:

- Rewrite unrelated code.
- Rename files/classes/functions without a requirement.
- Change architecture unnecessarily.
- Add features from future issues.
- Add unnecessary dependencies.
- Change unrelated configuration.
- Modify generated files unless required.
- Modify frontend code for a backend-only issue unless necessary.
- Modify backend code for a frontend-only issue unless necessary.

If a useful improvement is discovered outside the issue:

1. Do not implement it automatically.
2. Mention it in the final report.
3. Recommend a separate issue if appropriate.

---

# 14. Testing Requirements

Every implementation must be tested.

At minimum:

1. Run relevant existing tests.
2. Add or update focused tests when changed behavior requires them.
3. Verify existing functionality still works.
4. Check for syntax/import errors.
5. Verify the issue's acceptance criteria directly.

Use the project's existing testing tools and conventions.

Do not:

- weaken tests
- delete tests
- skip tests just to obtain a passing result
- hide test failures
- change production behavior merely to make tests pass

If a test cannot be run, clearly report why.

---

# 15. Targeted Verification Before Full Testing

Do not immediately run a large test suite.

First verify the specific functionality changed by the issue.

Use:

```text
Implementation
    ↓
Targeted verification
    ↓
Relevant test suite
    ↓
Application smoke test
    ↓
Final quality checks
```

This prevents wasting time diagnosing unrelated failures.

---

# 16. Quality Checks

Before considering an issue complete, run the quality checks actually supported by the repository.

Preferred checks as they are introduced:

```text
Tests
Lint
Formatting
Type checking
Git diff --check
```

Do not install new quality tools solely to complete one issue unless the issue explicitly requires them.

The agent must report the exact commands executed and their results.

---

# 17. Acceptance Criteria Verification

Every issue must end with an explicit acceptance-criteria check.

For each criterion:

```text
PASS — [criterion]
FAIL — [criterion]
NOT VERIFIED — [criterion]
```

A criterion may only be marked `PASS` when there is actual evidence.

For example, do not say:

```text
Product table exists.
```

unless the database was actually inspected.

Do not say:

```text
/health works.
```

unless the endpoint was actually called successfully.

Do not say:

```text
Tests pass.
```

unless the tests were actually executed.

---

# 18. Database Rules

Database infrastructure should remain separate from business/domain models.

Database foundation includes:

- Engine
- Session factory
- Declarative Base
- Database dependencies
- Database configuration
- Migration tooling when required

Business/domain models should only be introduced when required by an issue.

Do not introduce:

- CRUD
- repositories
- services
- migrations
- additional abstractions

unless the current issue requires them.

## Database Verification

For database issues, explicitly verify that the database being inspected is the same database used by the application.

When migrations are involved:

```text
SQLAlchemy Model
       ↓
Migration
       ↓
Database Schema
```

Changing a Python model does not automatically change an existing database schema.

---

# 19. Dependencies

Do not add a dependency unless necessary for the current issue.

Before adding one:

1. Check whether the project already provides equivalent functionality.
2. Confirm the dependency is required.
3. Prefer established, maintained libraries.
4. Update the appropriate dependency file.
5. Verify existing tests still pass.

Do not add libraries simply because they make implementation easier.

---

# 20. Configuration and Secrets

Never commit:

- API keys
- Passwords
- Tokens
- Private credentials
- `.env` files containing secrets

Use environment variables and the project's configuration system.

If a secret is accidentally exposed:

1. Stop.
2. Do not commit it.
3. Report it immediately.

---

# 21. Backend Architecture

Keep backend responsibilities separated.

Prefer:

```text
Configuration
    ↓
Database / Infrastructure
    ↓
API / Dependencies
    ↓
Business Logic
    ↓
Models / Schemas
```

Do not put database configuration, business logic, or unrelated infrastructure directly into `main.py` when a dedicated module is appropriate.

`main.py` should primarily contain application setup and API wiring.

Follow the actual existing project architecture rather than forcing this structure where the project has intentionally evolved differently.

---

# 22. Documentation

Update documentation when the current issue changes:

- Project setup
- Architecture
- Required environment variables
- Development commands
- Important behavior

Do not rewrite documentation unnecessarily.

---

# 23. Learning Requirements

This project is intended for learning, not just implementation.

When an issue contains explicit learning goals, the final report must briefly explain the important concepts introduced by the issue.

For example, for a database migration issue, explain:

```text
Python Model
      ↓
Migration
      ↓
Database Schema
```

The explanation should be concise but technically accurate.

The agent should distinguish between:

```text
"What I changed"
```

and:

```text
"What this teaches"
```

Do not hide important architectural decisions behind automation.

---

# 24. AI Self-Review

After implementation and testing, perform a final review.

Check:

- Issue requirements
- Acceptance criteria
- Correctness
- Tests
- Architecture
- Scope
- Security
- Error handling where relevant
- Unnecessary changes
- Accidental changes in the diff

The review must include:

```text
VERDICT: PASS
```

or:

```text
VERDICT: FAIL
```

If FAIL, list actionable problems.

Do not silently expand the implementation during self-review.

If a problem is discovered:

1. Report it.
2. Fix it only if it is within the current issue scope and fixing it is safe.
3. Re-run the affected verification.

---

# 25. Final Git Diff Review

Before declaring completion:

```bash
git status
git diff
git diff --check
```

Verify:

- Only intended files changed.
- No secrets were added.
- No generated/unrelated files were accidentally modified.
- No debugging code remains.
- No temporary files were introduced.
- No unrelated formatting changes were introduced.

---

# 26. Human Review

AI approval does not replace human approval.

Before committing an issue, the developer should understand:

- What changed
- Why it changed
- How it works
- How it was tested
- Important trade-offs
- Any limitations

The goal is not merely to make tests pass.

The goal is to understand the implementation.

---

# 27. Commit / Push / PR Rules

The agent must NOT automatically:

- Commit changes
- Push changes
- Create pull requests
- Merge branches
- Rewrite Git history
- Force push

These actions require explicit developer instruction.

Before a commit:

```text
git status
git diff
git diff --check
```

Only intentional files should be included.

---

# 28. Efficiency Rules

The agent should be thorough but efficient.

Do not:

- Repeatedly run commands that already failed for a known reason.
- Repeatedly guess paths.
- Run the entire test suite after every tiny change.
- Restart the application unnecessarily.
- Inspect unrelated parts of the repository.
- Install unnecessary dependencies.
- Spend excessive time on speculative improvements.

Use:

```text
Discover → Implement → Targeted Verify → Test → Review → Report
```

When blocked, investigate the actual cause rather than guessing.

---

# 29. Final Implementation Report

After completing an issue, report:

## Repository Context

```text
Repository root:
Backend path:
Frontend path:
Python environment:
Application entry point:
Database path:
Test framework:
Test command:
Application start command:
```

Only include values actually discovered.

## Files Changed

List every created, modified, or deleted file.

## Implementation

Briefly explain what was implemented.

## Tests

List the exact commands executed and their results.

## Quality Checks

List:

- Lint
- Formatting
- Type checking
- `git diff --check`
- Other relevant checks

Only list checks that were actually executed.

## Acceptance Criteria

For every criterion:

```text
PASS
FAIL
NOT VERIFIED
```

with a short explanation.

## Learning

Explain the key technical concept introduced by the issue.

## Review

```text
VERDICT: PASS
```

or:

```text
VERDICT: FAIL
```

## Concerns

Mention:

- Assumptions
- Limitations
- Blockers
- Potential follow-up issues

Do not commit or push unless explicitly instructed.

---

# 30. When Unsure

Prefer asking rather than guessing when a decision could:

- Change architecture
- Add a dependency
- Expand issue scope
- Change existing behavior
- Affect security
- Introduce significant technical debt
- Destroy or overwrite developer work

For small implementation details:

- Follow existing conventions.
- Choose the simplest reasonable solution.
- Verify assumptions against the repository.

---

# Golden Rules

> **DISCOVER FIRST. NEVER GUESS PROJECT STRUCTURE.**

> **IMPLEMENT ONLY WHAT THE ISSUE REQUIRES.**

> **TEST USING COMMANDS AND PATHS DISCOVERED FROM THE REPOSITORY.**

> **VERIFY WITH EVIDENCE, NOT ASSUMPTIONS.**

> **KEEP THE CHANGE SMALL.**

> **DO NOT HIDE FAILURES.**

> **DO NOT COMMIT OR PUSH WITHOUT EXPLICIT INSTRUCTION.**

> **THE GOAL IS NOT ONLY TO MAKE THE CODE WORK — THE DEVELOPER MUST UNDERSTAND WHY IT WORKS.**
