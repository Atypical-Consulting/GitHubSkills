# GSD Integration

How GHS skills invoke the [GSD framework](https://github.com/gsd-build/get-shit-done) for complex, multi-phase implementation tasks. GSD is a **hard dependency** --- skills that need it fail fast with a clear message if GSD is not installed.

## GSD Detection

Before invoking GSD commands, verify installation:

```bash
ls ~/.claude/commands/gsd:* 2>/dev/null || ls ~/.claude/plugins/*/skills/gsd-*/SKILL.md 2>/dev/null
```

If not found, emit an error with install instructions and stop. Do not fall back to a simpler approach --- the complexity warrants GSD.

## Complexity Routing

Not every task needs GSD. The routing decision determines whether a task takes the **fast path** (single-shot agent) or the **GSD path** (multi-phase planning and execution).

### Decision Matrix

| Signal | Fast Path | GSD Path |
|--------|-----------|----------|
| Complexity rating | Low, Medium | High, Very High |
| Estimated files changed | 1--3 | 4+ |
| Cross-cutting concerns | None | Multiple modules, tests, docs |
| Issue has sub-tasks | No | Yes |
| Requires architectural decisions | No | Yes |

### Routing Rules

1. **Explicit user override always wins** --- "just do it quick" or "use GSD for this"
2. **ghs-issue-analyze is the primary signal** --- use its complexity rating directly
3. **When no analysis exists**, estimate from issue body (acceptance criteria count, file mentions, keywords like "refactor" or "migration")
4. **Default to fast path** when signals are ambiguous

### Complexity Levels

| Level | Criteria | Example |
|-------|----------|---------|
| **Low** | Single file, clear fix | Typo in README |
| **Medium** | 2--3 files, straightforward | Add form validation |
| **High** | 4+ files, cross-module, tests required | New API endpoint with auth |
| **Very High** | Architectural change, multiple subsystems | Auth system rewrite |

## GSD Command Flow

### Implementation (ghs-issue-implement, GSD path)

```
Step 1: Prepare context     -> Write PROJECT.md with repo + issue details
Step 2: /gsd:discuss-phase  -> Capture implementation preferences
Step 3: /gsd:plan-phase     -> Create atomic task plans (PLAN.md files)
Step 4: /gsd:execute-phase  -> Wave-based execution, fresh context per task
Step 5: /gsd:verify-work    -> Automated acceptance testing
```

### Health Fix (ghs-backlog-fix, wave-based)

For multi-item batches with dependencies, GSD provides wave-based execution without full planning:

```
Step 1: Classify items + build dependency graph
Step 2: /gsd:execute-phase with wave definitions
Step 3: Verify per wave, report progress incrementally
```

### Quick Tasks

For simple tasks that benefit from GSD's quality guarantees:

```
/gsd:quick "Add LICENSE file to repository"
```

## Skill-to-GSD Contract

### What GHS provides to GSD

| Artifact | Location | Content |
|----------|----------|---------|
| `PROJECT.md` | `.planning/PROJECT.md` | Repo name, tech stack, issue details, acceptance criteria |
| `REQUIREMENTS.md` | `.planning/REQUIREMENTS.md` | Extracted from issue body + analysis comment |
| Issue context | Discuss phase | Full issue body, comments, labels |

### What GSD returns to GHS

| Artifact | Location | Content |
|----------|----------|---------|
| Git commits | In worktree/branch | Atomic commits per task |
| Verification | `.planning/{N}-VERIFICATION.md` | Pass/fail per acceptance criterion |

GSD handles implementation but does **not** create PRs --- the GHS orchestrator pushes the branch, creates the PR, and updates backlog status.

## Error Handling

| Failure | Action |
|---------|--------|
| GSD not installed | Fail fast with install instructions |
| Plan validation fails 3 times | Mark as NEEDS_HUMAN, preserve worktree |
| Execute task fails | GSD handles retries internally |
| Verify finds failures | GSD generates fix plans; orchestrator re-executes or escalates |
| 3 consecutive command failures | Preserve worktree, suggest fast path fallback, mark NEEDS_HUMAN |
