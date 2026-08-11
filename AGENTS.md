# AGENTS.md

## Project

This repository is a small full-stack learning project.

The purpose is to build the application incrementally while learning professional full-stack development practices.

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

The AI agent is an implementation assistant, not the owner of the project.

The developer must understand and review the changes before they are committed.

Prefer:

- Small changes
- Clear code
- Existing project conventions
- Minimal abstractions
- Explicit implementation
- Tests for changed behavior

Avoid:

- Overengineering
- Unnecessary refactoring
- Adding libraries without a reason
- Implementing future features early
- Changing unrelated code

---

# 2. Issue-Driven Development

Every implementation must be based on a specific issue.

Before changing code:

1. Read the complete issue requirements.
2. Inspect the existing repository.
3. Identify the files and components relevant to the issue.
4. Understand the existing implementation.
5. Determine the smallest reasonable change set.
6. Identify how the change should be tested.

Do not implement requirements that are not part of the current issue.

If an issue is ambiguous, stop and ask for clarification rather than making assumptions that significantly change the architecture.

---

# 3. Standard Development Workflow

The expected workflow is:

```text
Linear Issue
    ↓
Clean main branch
    ↓
Feature branch
    ↓
Inspect repository
    ↓
Understand requirements
    ↓
AI implementation
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

The agent must not skip testing or review.

---

# 4. Agent Implementation Rules

When implementing an issue:

### Before coding

- Inspect relevant files first.
- Follow existing architecture.
- Reuse existing configuration and utilities when appropriate.
- Do not create duplicate implementations.
- Do not modify unrelated files.

### During coding

- Make the smallest clean change that satisfies the issue.
- Preserve existing behavior unless the issue explicitly requires changing it.
- Keep business logic separate from infrastructure.
- Prefer readable code over clever code.
- Add comments only when they explain something that is not obvious from the code.

### After coding

- Run relevant tests.
- Run available linting and formatting checks.
- Run type checks when configured.
- Inspect the final Git diff.
- Check for accidental changes.
- Report what was changed and why.

---

# 5. Scope Control

The agent must not:

- Rewrite unrelated code.
- Rename files/classes/functions without a requirement.
- Change the project's architecture unnecessarily.
- Add features from future issues.
- Add unnecessary dependencies.
- Change configuration unrelated to the issue.
- Modify generated files unless required.
- Modify frontend code for a backend-only issue unless necessary.

If a potentially useful improvement is discovered outside the issue scope:

1. Do not implement it automatically.
2. Mention it in the final report.
3. Recommend creating a separate issue if appropriate.

---

# 6. Testing Requirements

Every implementation must be tested.

At minimum:

1. Run the existing relevant test suite.
2. Add or update focused tests for changed behavior.
3. Verify that existing functionality still works.
4. Check for syntax/import errors.

Use the project's existing testing tools and conventions.

Do not weaken, remove, skip, or delete tests merely to make the test suite pass.

Do not hide test failures.

If a test cannot be run, clearly report why.

---

# 7. Automated Quality Checks

Before considering an issue implementation complete, run the quality checks available in the project.

Preferred checks as they are introduced:

```text
Tests
Lint
Formatting
Type checking
Git diff --check
```

For the Python backend, use the project's configured tools rather than introducing new tools solely for one issue.

The agent should report the exact commands executed and whether they passed.

---

# 8. Git Rules

The agent must NOT automatically:

- Commit changes
- Push changes
- Create pull requests
- Merge branches
- Rewrite Git history
- Force push

These actions require explicit developer instruction.

Before a commit, verify:

```text
git status
git diff
git diff --check
```

Only intentional files should be included in the commit.

Commit messages should clearly describe the change.

---

# 9. AI Self-Review

After implementation and testing, the agent should perform a final review before asking for human approval.

The review must check:

- Issue requirements
- Correctness
- Tests
- Architecture
- Scope
- Security
- Error handling where relevant
- Unnecessary changes
- Accidental changes in the diff

The agent should report:

```text
VERDICT: PASS
```

or

```text
VERDICT: FAIL
```

If the verdict is FAIL, list actionable problems.

The agent should not silently modify additional files during the review unless explicitly instructed to fix the identified problems.

---

# 10. Human Review

AI approval does not replace human approval.

Before committing an issue, the developer should understand:

- What changed
- Why it changed
- How it works
- How it was tested
- Any important trade-offs

The goal is not merely to make the tests pass.

The goal is to understand the implementation.

---

# 11. Dependencies

Do not add a dependency unless it is necessary for the current issue.

Before adding a dependency:

1. Check whether the project already provides an equivalent capability.
2. Confirm that the dependency is actually required.
3. Prefer established, maintained libraries.
4. Update the appropriate dependency file.
5. Verify that existing tests still pass.

Do not add libraries simply because they make implementation easier.

---

# 12. Configuration and Secrets

Never commit:

- API keys
- Passwords
- Tokens
- Private credentials
- `.env` files containing secrets

Use environment variables and the project's configuration system.

If a secret is accidentally exposed, stop and report it immediately.

---

# 13. Backend Architecture

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

---

# 14. Database Rules

Database infrastructure should remain separate from business/domain models.

Database foundation includes things such as:

- Engine
- Session factory
- Declarative Base
- Database dependencies
- Database configuration

Business/domain models should only be introduced when required by an issue.

Do not introduce migrations, repositories, services, or additional database abstractions unless the current issue requires them.

---

# 15. Documentation

Update documentation when the current issue changes:

- Project setup
- Architecture
- Required environment variables
- Development commands
- Important behavior

Do not rewrite documentation unnecessarily.

---

# 16. Final Implementation Report

After completing an issue, report:

### Files changed

List every created, modified, or deleted file.

### Implementation

Briefly explain what was implemented.

### Tests

List commands executed and their results.

### Quality checks

List linting, formatting, type checking, or other checks performed.

### Review

Report:

```text
VERDICT: PASS
```

or

```text
VERDICT: FAIL
```

### Concerns

Mention assumptions, limitations, or potential follow-up issues.

Do not commit or push unless explicitly instructed.

---

# 17. When Unsure

Prefer asking rather than guessing when a decision could:

- Change architecture
- Add a dependency
- Expand issue scope
- Change existing behavior
- Affect security
- Introduce significant technical debt

For small implementation details, follow existing project conventions and choose the simplest reasonable solution.

---

# Golden Rule

> **Implement only what the issue requires, keep the change small, test it, review it, and make sure the developer understands it before it is committed.**
