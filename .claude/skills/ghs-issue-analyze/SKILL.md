---
name: ghs-issue-analyze
description: >
  Deep-analyze a GitHub issue by inspecting the codebase and post a structured analysis comment
  with feasibility, complexity, affected files, suggested approach, and effort estimate. Use this
  skill whenever the user wants to analyze an issue, understand an issue before implementing it,
  get a complexity estimate, or says things like "analyze issue #42", "what would it take to fix
  #42", "assess this issue", "investigate issue #42", "how complex is issue #42", "issue analysis",
  "deep dive on issue #42", or "break down issue #42".
  Do NOT use for triaging/labeling issues (use ghs-issue-triage), implementing issues
  (use ghs-issue-implement), or scanning repo health (use ghs-repo-scan).
allowed-tools: "Bash(gh:*) Bash(git:*) Read Glob Grep"
compatibility: "Requires gh CLI (authenticated), git, network access"
license: MIT
metadata:
  author: phmatray
  version: 2.0.0
routes-to:
  - ghs-issue-implement
  - ghs-issue-triage
routes-from:
  - ghs-issue-triage
---

# Issue Analysis

Fetch a GitHub issue, clone the repo, search the codebase for relevant files and patterns, then produce a structured analysis posted as a GitHub comment.

<context>
Purpose: Deep-analyze GitHub issues by inspecting the actual codebase, producing actionable analysis that speeds up implementation.

Roles:
1. **Analyst** (you) — fetches the issue, clones the repo, investigates the codebase, produces the analysis, posts the comment

This skill does not spawn sub-agents — the analysis requires accumulated context from file reads that doesn't parallelize well.

Shared docs:
- `../shared/gh-prerequisites.md` — authentication, repo detection, error handling
- `../shared/implementation-workflow.md` §1 — repository clone/pull logic
</context>

<objective>
Produce a structured analysis comment on the GitHub issue with feasibility, complexity, affected files, and suggested approach.

Outputs:
- GitHub comment posted on the issue with structured analysis
- Issue label updated to `status:analyzing`
- Terminal display of the same analysis

Next routing:
- Suggest `ghs-issue-implement #{number}` to implement — "To implement: `/ghs-issue-implement #{number}`"
- If the issue lacks labels, suggest `ghs-issue-triage` first
- For batch analysis, show a summary table and suggest implementing the simplest issues first
</objective>

<process>

## Input

- **Single issue**: `analyze issue #42` or `analyze #42`
- **Multiple issues**: `analyze issues #42, #43, #45` — processes each sequentially
- **By label**: `analyze all triaged issues` — fetches issues with `status:triaged` label

## Phase 1 — Fetch Issue

Retrieve the full issue from GitHub:

```bash
gh issue view {number} --repo {owner}/{repo} \
  --json number,title,body,labels,comments,assignees,state,createdAt
```

Extract:
- Title and body (the problem description)
- Existing labels (especially `type:*` and `priority:*` from triage)
- Comments (may contain additional context, reproduction steps, or workarounds)

If the issue is closed, warn the user and ask whether to proceed.

## Phase 2 — Prepare Repository

Follow `../shared/implementation-workflow.md` §1 — clone or pull the repo to `repos/{owner}_{repo}/`.

Detect the default branch and tech stack.

## Phase 3 — Codebase Investigation

Search the codebase for files, functions, and patterns related to the issue:

1. **Keyword extraction**: Pull key terms from the issue title and body (function names, file paths, error messages, component names, API endpoints)
2. **File search**: Use Grep and Glob tools within `repos/{owner}_{repo}/` to locate relevant files
3. **Code reading**: Use the Read tool on the most relevant files to understand the current implementation
4. **Dependency tracing**: If the issue mentions a component, trace its imports/exports to identify the full dependency graph — partial fixes that miss a dependency create new bugs
5. **Test coverage**: Check if existing tests cover the affected area — this informs the risk assessment

Build a map of affected files with line numbers and brief descriptions of what each does.

## Phase 4 — Produce Analysis

Generate a structured analysis with these sections:

### Classification Table

| Field | Value |
|-------|-------|
| **Feasibility** | Feasible / Partially Feasible / Needs Clarification |
| **Complexity** | Low / Medium / High / Very High |
| **Effort** | S (< 1h) / M (1–4h) / L (4–8h) / XL (> 8h) |
| **Risk** | Low / Medium / High |

### Affected Areas

List files/modules that would need changes:

```
- `src/components/LoginForm.tsx` (L45-82) — form validation logic
- `src/api/auth.ts` (L12-30) — authentication endpoint
- `tests/auth.test.ts` — needs new test cases
```

### Suggested Approach

Numbered steps describing how to implement the fix/feature.

### Risks & Dependencies

Specific risks and external dependencies that could affect implementation.

### Open Questions

Questions that need answers before implementation (if any).

## Phase 5 — Post GitHub Comment

Post the analysis as a comment on the issue:

```bash
gh issue comment {number} --repo {owner}/{repo} --body "$(cat <<'EOF'
## Issue Analysis

| Field | Value |
|-------|-------|
| **Feasibility** | {feasibility} |
| **Complexity** | {complexity} |
| **Effort** | {effort} |
| **Risk** | {risk} |

### Affected Areas

{affected_areas_list}

### Suggested Approach

{numbered_steps}

### Risks & Dependencies

{risks_list}

{### Open Questions (if any)}

---

*Automated analysis by ghs-issue-analyze — review before implementation.*
EOF
)"
```

## Phase 6 — Update Status Label

If the issue has a `status:triaged` label, update it to `status:analyzing` — this signals to other skills and users that the issue is being worked on:

```bash
gh issue edit {number} --repo {owner}/{repo} \
  --remove-label "status:triaged" --add-label "status:analyzing"
```

## Phase 7 — Terminal Output

Show the same analysis in the terminal:

```
## Analysis: #{number} — {title}

| Field | Value |
|-------|-------|
| Feasibility | {feasibility} |
| Complexity | {complexity} |
| Effort | {effort} |
| Risk | {risk} |

### Affected Areas
{list}

### Suggested Approach
{steps}

### Risks & Dependencies
{risks}

---
Comment posted: https://github.com/{owner}/{repo}/issues/{number}#issuecomment-{id}
```

</process>

## Batch Mode

When analyzing multiple issues:

1. Process each issue sequentially — codebase context accumulates, making later analyses faster
2. After all analyses, show a summary table:

```
## Analysis Summary: {owner}/{repo}

| # | Issue | Complexity | Effort | Risk | Comment |
|---|-------|-----------|--------|------|---------|
| #42 | Login crashes | High | L | Medium | Posted |
| #43 | Add dark mode | Medium | M | Low | Posted |
| #45 | Fix typo | Low | S | Low | Posted |
```

## Edge Cases

- **Issue has no body**: Analyze based on title only. Note in the analysis that the issue lacks a description and suggest the author add more context.
- **Issue references external URLs**: Note them but don't fetch external content.
- **Very large codebase**: Focus on files directly referenced in the issue. Limit search depth.
- **Issue already has an analysis comment**: Check for existing comments starting with `## Issue Analysis`. If found, ask the user whether to update (edit comment) or add a new one.
- **Closed issue**: Warn the user and ask whether to proceed.
- **Issue is a pull request**: Warn — PRs have different workflows. Suggest reviewing the PR diff instead.
- **Multiple issues share affected files**: Note overlapping areas in the batch summary — these may conflict if implemented in parallel.

## Examples

**Example 1: Analyze a single issue**
User says: "analyze issue #42"
Result: Fetches issue, clones/pulls repo, investigates codebase, posts structured comment, updates label, shows analysis in terminal.

**Example 2: Analyze all triaged issues**
User says: "analyze all triaged issues"
Result: Fetches issues with `status:triaged`, analyzes each sequentially, posts comments, shows batch summary.

**Example 3: Quick assessment**
User says: "how complex is #42?"
Result: Same as analyze — produces full analysis with complexity rating.
