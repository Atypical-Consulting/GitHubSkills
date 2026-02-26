# Sync Format Reference

Defines the contract for syncing local health backlog items to GitHub Issues. Consumed by: ghs-backlog-sync, ghs-backlog-fix, ghs-backlog-board, ghs-backlog-next.

## Label Taxonomy

Labels created on the target repo during sync:

| Label | Color | Description |
|-------|-------|-------------|
| `ghs:health-check` | `#7057ff` (purple) | Health check finding from ghs-repo-scan |
| `tier:1` | `#d73a4a` (red) | Tier 1 — Required |
| `tier:2` | `#fbca04` (yellow) | Tier 2 — Recommended |
| `tier:3` | `#0e8a16` (green) | Tier 3 — Nice to Have |
| `category:api-only` | `#c5def5` (light blue) | Fix requires API calls only (Category A) |
| `category:file-change` | `#bfd4f2` (blue) | Fix requires file changes (Category B) |
| `category:ci` | `#d4c5f9` (lavender) | Fix requires CI workflow changes (Category CI) |

All labels are created idempotently using `gh label create ... 2>&1 || true`.

## Issue Title Convention

```
[Health] {Check Name}
```

The title serves as the dedup key — if an issue with this exact title already exists (in any state), it is matched to the local item rather than creating a duplicate.

Examples:
- `[Health] README`
- `[Health] Branch Protection`
- `[Health] .editorconfig`
- `[Health] CI Workflow Health`

## Issue Body Template

```markdown
<!-- ghs-sync:metadata
slug: {slug}
tier: {tier_number}
points: {points}
category: {A|B|CI}
detected: {YYYY-MM-DD}
-->

| Field | Value |
|-------|-------|
| **Tier** | {tier_number} — {tier_label} |
| **Points** | {points} |
| **Category** | {A (API-only) \| B (file changes) \| CI} |
| **Detected** | {YYYY-MM-DD} |

## What's Missing

{Content from the local backlog item's "What's Missing" section}

## Why It Matters

{Content from the local backlog item's "Why It Matters" section, or a brief explanation}

## How to Fix

{Content from the local backlog item's "How to Fix" or "Quick Fix" section}

## Acceptance Criteria

- [ ] {criterion 1}
- [ ] {criterion 2}
- [ ] ...

## References

- Local backlog item: `backlog/{owner}_{repo}/health/tier-{N}--{slug}.md`
- Check definition: `.claude/skills/shared/checks/{category}/{slug}.md`
```

### Hidden Metadata Comment

The `<!-- ghs-sync:metadata ... -->` block at the top of the issue body is machine-readable and used to:
1. Match issues back to local backlog items (via `slug`)
2. Preserve metadata even if the visible body is edited by users
3. Detect content changes for update decisions

**Never strip or modify this comment** when updating issue bodies — it is the source of truth for the sync relationship.

## Local Backlog Metadata Additions

After syncing, two optional rows are added to the local backlog item's metadata table:

```markdown
| **Synced Issue** | #{number} |
| **Issue URL** | {url} |
```

These rows are appended after the existing `| **Detected** | ... |` row. They are backward-compatible — items that have not been synced simply lack these rows.

Example of a synced health item metadata table:

```markdown
| Field | Value |
|-------|-------|
| **Repository** | `phmatray/NewSLN` |
| **Source** | Health Check |
| **Tier** | 1 — Required |
| **Points** | 4 |
| **Status** | FAIL |
| **Detected** | 2026-01-15 |
| **Synced Issue** | #42 |
| **Issue URL** | https://github.com/phmatray/NewSLN/issues/42 |
```
