# Sync Format Reference

Defines the contract for promoting draft health items in a GitHub Project to real GitHub Issues. Consumed by: ghs-backlog-sync, ghs-backlog-fix, ghs-backlog-board, ghs-backlog-next.

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

- Project item: [GHS] {owner}/{repo} project, slug: {slug}
- Check definition: `.claude/skills/shared/checks/{category}/{slug}.md`
```

### Hidden Metadata Comment

The `<!-- ghs-sync:metadata ... -->` block at the top of the issue body is machine-readable and used to:
1. Match issues back to local backlog items (via `slug`)
2. Preserve metadata even if the visible body is edited by users
3. Detect content changes for update decisions

**Never strip or modify this comment** when updating issue bodies — it is the source of truth for the sync relationship.

## Promotion Workflow

When `ghs-backlog-sync` runs, it promotes draft items in the GitHub Project to real GitHub Issues:

1. Find draft items in `Todo` column where `Source = Health Check`
2. For each draft item without a matching real issue (title-based dedup):
   a. Create a real GitHub Issue with labels (`ghs:health-check`, `tier:N`, `category:*`)
   b. Delete the draft from the project (`gh project item-delete`)
   c. Add the new issue to the project (`gh project item-add --url`)
   d. Copy custom field values (Tier, Points, Slug, Category, Detected) to the linked item
3. For items that already have matching real issues: update if metadata changed, skip otherwise

The `PR URL` custom field on the project item links the finding to any fix PR created by `ghs-backlog-fix`.
