# ui-brand.md — GHS Visual Output Branding Reference

Standardizes **visual chrome** across all GHS skills: banners, boxes, indicators, routing blocks.
For data formats (tables, scores, status indicators), see `output-conventions.md`.

---

## 1. Stage Banners

Use at the start of every major skill phase. Width: 53 chars of `━`.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GHS ► {STAGE NAME}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

| Skill context       | Stage name      |
|---------------------|-----------------|
| ghs-repo-scan       | SCANNING        |
| ghs-backlog-fix     | FIXING          |
| ghs-issue-triage    | TRIAGING        |
| ghs-issue-analyze   | ANALYZING       |
| ghs-issue-implement | IMPLEMENTING    |
| ghs-review-pr       | REVIEWING       |
| ghs-merge-prs       | MERGING         |
| ghs-backlog-sync    | SYNCING         |
| ghs-release         | RELEASING       |
| ghs-orchestrate     | ORCHESTRATING   |
| ghs-dev-loop        | DEV LOOP        |
| ghs-backlog-board   | BOARD           |
| ghs-project-init    | INITIALIZING    |
| ghs-action-fix      | ACTION FIX      |
| ghs-repos-pull      | PULLING         |

---

## 2. Checkpoint Boxes

Use before pausing for human input or destructive actions. Box width: 62 chars inner.

```
╔══════════════════════════════════════════════════════════════╗
║  CHECKPOINT: {Type}                                          ║
╚══════════════════════════════════════════════════════════════╝
```

| Type                    | When to use                                      |
|-------------------------|--------------------------------------------------|
| Verification Required   | Agent output needs human review before next step |
| Decision Required       | Multiple valid paths; human must choose          |
| Action Required         | Human must run a command or complete a step      |
| Confirmation Required   | Destructive action (delete, force-push, drop)    |

---

## 3. Status Symbols

Use consistently — never mix Unicode variants or emoji substitutes.

| Symbol | Meaning                          |
|--------|----------------------------------|
| `✓`    | Complete / Passed / Verified     |
| `✗`    | Failed / Missing / Blocked       |
| `◆`    | In Progress / Active             |
| `○`    | Pending / Not started            |
| `⚠`    | Warning / Needs attention        |
| `⚡`   | Auto-approved / Skipped          |

Usage:

```
✓ README.md — present and non-empty
✗ CONTRIBUTING.md — missing
⚠ LICENSE — present but unrecognized SPDX identifier
○ SECURITY.md — not yet checked
◆ Running health checks...
⚡ CI check skipped (no workflows directory)
```

---

## 4. Spawning Indicators

Use when launching subagents. Single agent:

```
◆ Spawning agent: {description}...
✓ Agent complete: {result summary}
✗ Agent failed: {error summary}
```

Parallel batch:

```
◆ Spawning {N} agents in parallel...
  → {agent-1-desc}
  → {agent-2-desc}
  → {agent-3-desc}
✓ All agents complete (3/3)
```

Partial failure:

```
✓ Agent complete: README fix merged as PR #42
✗ Agent failed: LICENSE — content filter blocked response
⚠ 1/3 agents failed — see backlog for retry
```

---

## 5. Progress Display

Use for multi-step operations, waves, or item batches.

```
Progress: ████████░░ 80%
Items: 3/5 complete
Wave 2/3: ██████░░░░ 60%
```

Rules:
- Bar width: 10 blocks (`█` filled, `░` empty)
- Always show numeric alongside bar
- Label the unit (Items, Wave, Repos, Checks)

---

## 6. Error Box

Use when a skill cannot continue. Same 62-char box as checkpoints.

```
╔══════════════════════════════════════════════════════════════╗
║  ERROR                                                       ║
╚══════════════════════════════════════════════════════════════╝

{Error description — one or two sentences, plain language}

**To fix:** {Concrete resolution steps, numbered if >1}
```

Example:

```
╔══════════════════════════════════════════════════════════════╗
║  ERROR                                                       ║
╚══════════════════════════════════════════════════════════════╝

GitHub Projects write permission denied for owner/repo.

**To fix:**
1. Ensure your token has `project` scope: gh auth refresh -s project
2. Confirm you have Admin or Write access to the project
3. Re-run the skill
```

---

## 7. Next Up Block

Append at the end of every skill's output. Separators: 63 `─` chars.

```
───────────────────────────────────────────────────────────────

## ▶ Next Up

**{Skill name}** — {one-line description of what it does next}

  /ghs-{skill} {suggested-args}

───────────────────────────────────────────────────────────────

**Also available:**
- `/ghs-{alt-1}` — {short description}
- `/ghs-{alt-2}` — {short description}

───────────────────────────────────────────────────────────────
```

Standard routing table by skill:

| After running        | Primary Next Up      | Alternatives                          |
|----------------------|----------------------|---------------------------------------|
| ghs-repo-scan        | ghs-backlog-board    | ghs-backlog-fix, ghs-backlog-sync     |
| ghs-backlog-board    | ghs-backlog-fix      | ghs-backlog-next, ghs-backlog-sync    |
| ghs-backlog-fix      | ghs-review-pr        | ghs-backlog-board, ghs-merge-prs      |
| ghs-backlog-sync     | ghs-backlog-board    | ghs-backlog-fix                       |
| ghs-issue-triage     | ghs-issue-analyze    | ghs-issue-implement                   |
| ghs-issue-analyze    | ghs-issue-implement  | ghs-review-pr                         |
| ghs-issue-implement  | ghs-review-pr        | ghs-merge-prs                         |
| ghs-review-pr        | ghs-merge-prs        | ghs-issue-implement, ghs-release      |
| ghs-merge-prs        | ghs-release          | ghs-backlog-board                     |
| ghs-release          | ghs-backlog-board    | ghs-orchestrate                       |
| ghs-orchestrate      | ghs-backlog-board    | ghs-dev-loop                          |

---

## 8. Dry-Run Indicator

Show immediately after the stage banner when `--dry-run` is active.

```
╔══════════════════════════════════════════════════════════════╗
║  DRY RUN — No changes will be made                           ║
╚══════════════════════════════════════════════════════════════╝
```

All mutation descriptions in dry-run mode should be prefixed with `[DRY RUN]`:

```
[DRY RUN] Would create PR: "fix: add CONTRIBUTING.md"
[DRY RUN] Would apply label: priority/high
[DRY RUN] Would merge PR #38
```

---

## 9. Anti-Patterns

| Do NOT                                      | Do Instead                              | Why                                      |
|---------------------------------------------|-----------------------------------------|------------------------------------------|
| Use random emoji (🚀, 🎉, ✅, ❌)          | Use the defined symbol set (✓ ✗ ⚠ ◆)  | Consistent terminal rendering            |
| Vary box widths per skill                   | Always use 62-char inner width          | Visual alignment across skill outputs    |
| Use bold headers mid-output without context | Use stage banners for phase transitions | Banners signal scope changes clearly     |
| Skip Next Up block                          | Always append Next Up at end            | Users need guided continuation           |
| Mix `━` and `─` as section separators      | `━` for banners, `─` for Next Up only  | Visual hierarchy is load-bearing         |
| Omit `[DRY RUN]` prefix on mutations       | Prefix every would-be mutation          | Prevents confusion about what ran        |
| Print raw API errors verbatim               | Wrap in Error Box with fix steps        | Raw errors are unactionable              |
| Use multiple parallel progress styles       | One bar format: `████░░ N%`            | Cognitive load from mixed formats        |
