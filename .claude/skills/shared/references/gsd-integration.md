# GSD Integration Reference

How ghs-skills invoke the GSD framework for complex, multi-phase implementation tasks. GSD is a **hard dependency** — skills that need it fail fast with a clear message if GSD is not installed.

## Table of Contents

1. [GSD Detection](#gsd-detection)
2. [Complexity Routing](#complexity-routing)
3. [GSD Command Patterns](#gsd-command-patterns)
4. [Skill-to-GSD Contract](#skill-to-gsd-contract)
5. [Context Handoff](#context-handoff)
6. [Error Handling](#error-handling)

---

## GSD Detection

### Pre-flight Check

Before invoking any GSD command, verify installation:

```bash
# Check if GSD skills are available
ls ~/.claude/commands/gsd:* 2>/dev/null || ls ~/.claude/plugins/*/skills/gsd-*/SKILL.md 2>/dev/null
```

If GSD is not found, emit a clear error and stop:

```
[ERROR] GSD framework required but not installed.
        Install: https://github.com/gsd-build/get-shit-done
        This skill uses GSD for multi-phase implementation planning and execution.
```

Do not attempt to fall back to a simpler approach when the user's issue has been routed to the GSD path — the complexity warrants GSD, and a degraded experience would produce incomplete or broken results.

### Version Compatibility

GSD skills are invoked via slash commands (`/gsd:plan-phase`, `/gsd:execute-phase`, etc.). These commands are loaded as skills and executed through the Skill tool. No version pinning is required — GSD maintains backward compatibility for its public command interface.

---

## Complexity Routing

Not every task needs GSD. The routing decision determines whether a task takes the **fast path** (single-shot agent, current behavior) or the **GSD path** (multi-phase planning and execution).

### Decision Matrix

| Signal | Fast Path | GSD Path |
|--------|-----------|----------|
| `ghs-issue-analyze` complexity | Low, Medium | High, Very High |
| Estimated files changed | 1–3 | 4+ |
| Cross-cutting concerns | None | Multiple modules, tests, docs |
| Issue has sub-tasks | No | Yes |
| Requires architectural decisions | No | Yes |

### Routing Rules

1. **Explicit user override always wins.** If the user says "just do it quick" or "use GSD for this", respect that regardless of complexity signals.
2. **`ghs-issue-analyze` is the primary signal.** When an analysis comment exists on the issue, use its complexity rating directly.
3. **When no analysis exists**, estimate complexity from issue body: count of acceptance criteria, number of files mentioned, presence of words like "refactor", "migration", "redesign".
4. **Default to fast path** when signals are ambiguous. GSD overhead isn't justified for uncertain complexity — the user can always re-run with GSD if the fast path fails.

### Complexity Assessment (for ghs-issue-analyze)

When `ghs-issue-analyze` runs, it should include a `**Complexity**` field in its analysis comment:

| Level | Criteria | Example |
|-------|----------|---------|
| **Low** | Single file, clear fix, no tests needed | Typo in README, missing env var |
| **Medium** | 2-3 files, straightforward logic, may need tests | Add validation to a form, fix a bug with known root cause |
| **High** | 4+ files, cross-module changes, tests required, design decisions | New API endpoint with auth, database migration |
| **Very High** | Architectural change, multiple subsystems, breaking changes possible | Auth system rewrite, framework migration, new module |

---

## GSD Command Patterns

### Implementation Flow (ghs-issue-implement, GSD path)

```
Step 1: Prepare GSD context
  - Clone/pull repo to repos/{owner}_{repo}/
  - Create .planning/ directory in repo root (or worktree)
  - Write PROJECT.md with repo context and issue details

Step 2: Discuss phase (capture preferences)
  /gsd:discuss-phase 1
  - GSD asks clarifying questions about the implementation approach
  - Feeds answers into .planning/1-CONTEXT.md

Step 3: Plan phase (atomic task plans)
  /gsd:plan-phase 1
  - GSD researches the codebase, creates PLAN.md files
  - Plan checker validates against 8 dimensions
  - Output: .planning/1-{N}-PLAN.md files with XML task definitions

Step 4: Execute phase (wave-based, fresh context per task)
  /gsd:execute-phase 1
  - GSD analyzes task dependencies, creates execution waves
  - Each task gets fresh 200k context window
  - Atomic commit per completed task

Step 5: Verify work (automated UAT)
  /gsd:verify-work 1
  - GSD walks through acceptance criteria
  - Spawns debug agents for failures
  - Generates fix plans if needed
```

### Health Fix Flow (ghs-backlog-fix, wave-based)

For complex health fixes (multi-item batches with dependencies), GSD provides wave-based execution without the full planning ceremony:

```
Step 1: Classify items and build dependency graph
  - Use item-categories.md for classification
  - Detect dependencies (e.g., CI workflow depends on .editorconfig)

Step 2: Execute waves
  /gsd:execute-phase (with wave definitions in PLAN.md)
  - Wave 1: Independent items (parallel)
  - Wave 2: Items depending on Wave 1 (parallel)
  - Wave N: Remaining items

Step 3: Verify per wave
  - Recalculate health score after each wave
  - Report progress incrementally
```

### Quick Tasks

For simple, well-defined tasks that don't need full phasing but benefit from GSD's quality guarantees (atomic commits, state tracking):

```
/gsd:quick "Add LICENSE file to repository"
```

This skips research and planning but still provides:
- Atomic git commit
- State tracking
- Verification step

---

## Skill-to-GSD Contract

### What ghs-skills provide to GSD

| Artifact | Location | Content |
|----------|----------|---------|
| `PROJECT.md` | `.planning/PROJECT.md` | Repo name, description, tech stack, issue details, acceptance criteria |
| `REQUIREMENTS.md` | `.planning/REQUIREMENTS.md` | Extracted from issue body + analysis comment |
| Issue context | Passed in discuss phase | Full issue body, comments, labels, linked PRs |
| Repo context | Detected automatically | Tech stack, existing CI, branch protection status |

### What GSD returns to ghs-skills

| Artifact | Location | Content |
|----------|----------|---------|
| Git commits | In worktree/branch | Atomic commits per task, semantic messages |
| `.planning/` artifacts | In worktree | PLAN.md, VERIFICATION.md, STATE.md |
| Verification result | `.planning/{N}-VERIFICATION.md` | Pass/fail for each acceptance criterion |

### PR Creation (ghs-skill responsibility)

GSD handles implementation but does **not** create PRs. The ghs-skill orchestrator:
1. Reads GSD's verification results
2. Pushes the branch (if GSD hasn't already)
3. Creates the PR with proper body (issue refs, acceptance criteria checklist, `Fixes #N`)
4. Updates backlog item status
5. Cleans up `.planning/` artifacts (optional — they're in the worktree, which gets cleaned)

This separation keeps GSD repo-agnostic while ghs-skills handle the GitHub-specific integration.

---

## Context Handoff

### From ghs-issue-analyze to GSD

When an analyzed issue enters the GSD path, the analysis comment provides pre-computed context:

```markdown
## Issue #{number}: {title}

### Analysis (from ghs-issue-analyze)
- **Complexity**: {High|Very High}
- **Affected files**: {list}
- **Suggested approach**: {summary}
- **Risks**: {list}
- **Effort estimate**: {estimate}

### Acceptance Criteria (from issue body)
- [ ] {criterion 1}
- [ ] {criterion 2}

### Tech Stack
- {detected stack from repo scan}
```

This is written to `.planning/PROJECT.md` so GSD's research and planning phases have a head start.

### From GSD to ghs-backlog-fix

After GSD execution completes, the orchestrator extracts:
- Commit SHAs (from git log)
- Verification pass/fail (from VERIFICATION.md)
- Any unresolved items (from STATE.md blockers)

These map to the standard agent result contract:

```json
{
  "source": "issue",
  "slug": "42-login-crash",
  "status": "PASS|FAILED|NEEDS_HUMAN",
  "pr_url": null,
  "verification": ["extracted from VERIFICATION.md"],
  "error": "extracted from STATE.md blockers or null"
}
```

---

## Error Handling

### GSD Command Failures

| Failure | Action |
|---------|--------|
| GSD not installed | Fail fast with install instructions |
| `/gsd:plan-phase` fails validation 3 times | Mark as NEEDS_HUMAN, preserve worktree |
| `/gsd:execute-phase` task fails | GSD handles retries internally; check VERIFICATION.md |
| `/gsd:verify-work` finds failures | GSD generates fix plans; orchestrator can re-execute or escalate |
| Context exhaustion during GSD phase | GSD handles via `/gsd:pause-work`; orchestrator detects and resumes |

### Timeout Handling

GSD phases can be long-running (especially for Very High complexity issues). The orchestrator should:
- Not impose artificial timeouts on GSD commands
- Monitor progress via `.planning/STATE.md` updates
- Report incremental progress to the user when possible

### Fallback Strategy

If GSD fails completely (3 consecutive command failures), the orchestrator should:
1. Preserve the worktree with all `.planning/` artifacts
2. Report the failure with GSD's error context
3. Suggest the user run the issue through the fast path as a fallback
4. Mark the item as NEEDS_HUMAN
