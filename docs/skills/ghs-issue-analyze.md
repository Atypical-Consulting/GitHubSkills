# ghs-issue-analyze

Deep-analyzes a GitHub issue by inspecting the codebase and posts a structured analysis comment with feasibility, complexity, affected files, and suggested approach.

::: info Skill Info
**Version:** 4.0.0
**Arguments:** `<owner/repo#number> | <issue-url>`
**Trigger phrases:** "analyze issue #123", "deep dive on this issue", "what would it take to fix #42", "assess this issue", "how complex is issue #42", "break down issue #42"
:::

## What It Does

`ghs-issue-analyze` fetches a GitHub issue, clones the repository, searches the codebase for relevant files and patterns, and produces a structured analysis. The analysis is posted as a GitHub comment on the issue and displayed in the terminal.

### Analysis Output

Each analysis includes a classification table:

| Field | Possible Values |
|-------|----------------|
| **Feasibility** | Feasible, Partially Feasible, Needs Clarification |
| **Complexity** | Low, Medium, High, Very High |
| **Effort** | S (< 1h), M (1-4h), L (4-8h), XL (> 8h) |
| **Risk** | Low, Medium, High |

Plus sections for affected areas (files with line numbers), suggested approach (numbered steps), risks and dependencies, and open questions.

### Process

1. Fetch the full issue from GitHub (title, body, labels, comments)
2. Clone or pull the repository
3. Investigate the codebase: keyword extraction, file search, code reading, dependency tracing, test coverage check
4. Produce the structured analysis
5. Post the analysis as a GitHub comment
6. Update the issue label to `status:analyzing`

## Example

```
## Analysis: #42 — Login page crashes on mobile

| Field         | Value     |
|---------------|-----------|
| Feasibility   | Feasible  |
| Complexity    | Medium    |
| Effort        | M (1-4h)  |
| Risk          | Low       |

### Affected Areas

- `src/components/LoginForm.tsx` (L45-82) — form validation logic
- `src/hooks/useAuth.ts` (L12-30) — authentication state management
- `src/styles/login.css` (L15-22) — responsive breakpoints
- `tests/LoginForm.test.tsx` — needs new mobile viewport test cases

### Suggested Approach

1. Add viewport meta tag check in LoginForm component
2. Fix CSS media query breakpoint at 768px
3. Add touch event handlers alongside click handlers
4. Add mobile viewport test cases

### Risks & Dependencies

- CSS changes may affect other pages using shared styles
- Touch event handlers need testing on actual mobile devices

---
Comment posted: https://github.com/phmatray/my-project/issues/42#issuecomment-123456
```

## Routes To

After analyzing, GHS suggests:

- **[ghs-issue-implement](/skills/ghs-issue-implement)** — to implement the analyzed issue
- **[ghs-issue-triage](/skills/ghs-issue-triage)** — if the issue lacks type/priority labels

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(gh:*)`, `Bash(git:*)`, `Read`, `Glob`, `Grep` |
| Spawns sub-agents | No — analysis requires accumulated context that does not parallelize well |
| Phases | 7 (Fetch Issue, Prepare Repo, Investigate Codebase, Produce Analysis, Post Comment, Update Label, Terminal Output) |
| Requires | `gh` CLI (authenticated), `git`, network access |
| Re-run safe | Yes — checks for existing analysis comments before posting duplicates |
