# Sync Format

Defines the contract for promoting draft health items in a GitHub Project to real GitHub Issues. Used by ghs-backlog-sync, ghs-backlog-fix, ghs-backlog-board, and ghs-backlog-next.

## Label Taxonomy

Labels created on the target repo during sync:

| Label | Color | Description |
|-------|-------|-------------|
| `ghs:health-check` | `#7057ff` (purple) | Health check finding from ghs-repo-scan |
| `tier:1` | `#d73a4a` (red) | Tier 1 --- Required |
| `tier:2` | `#fbca04` (yellow) | Tier 2 --- Recommended |
| `tier:3` | `#0e8a16` (green) | Tier 3 --- Nice to Have |
| `category:api-only` | `#c5def5` (light blue) | Fix requires API calls only (Category A) |
| `category:file-change` | `#bfd4f2` (blue) | Fix requires file changes (Category B) |
| `category:ci` | `#d4c5f9` (lavender) | Fix requires CI workflow changes (Category CI) |

All labels are created idempotently using `gh label create ... 2>&1 || true`.

## Issue Title Convention

```
[Health] {Check Name}
```

The title is the dedup key --- if an issue with this exact title already exists (in any state), it is matched rather than creating a duplicate.

Examples: `[Health] README`, `[Health] Branch Protection`, `[Health] .editorconfig`

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
| **Tier** | {tier_number} --- {tier_label} |
| **Points** | {points} |
| **Category** | {category} |
| **Detected** | {YYYY-MM-DD} |

## What's Missing
{description of the gap}

## Why It Matters
{explanation of impact}

## How to Fix
{remediation steps}

## Acceptance Criteria
- [ ] {criterion 1}
- [ ] {criterion 2}
```

### Hidden Metadata Comment

The `<!-- ghs-sync:metadata ... -->` block at the top is machine-readable and used to:

1. Match issues back to project items (via `slug`)
2. Preserve metadata even if the visible body is edited
3. Detect content changes for update decisions

Never strip or modify this comment when updating issue bodies.

## Promotion Workflow

When `ghs-backlog-sync` runs:

1. Find draft items in the `Todo` column where `Source = Health Check`
2. For each draft without a matching real issue (title-based dedup):
   - Create a GitHub Issue with labels (`ghs:health-check`, `tier:N`, `category:*`)
   - Delete the draft from the project
   - Add the new issue to the project
   - Copy custom field values (Tier, Points, Slug, Category, Detected)
3. For items with existing matching issues: update if metadata changed, skip otherwise

The `PR URL` custom field on the project item links findings to fix PRs created by ghs-backlog-fix.
