<!-- Template: sync-issue-body | Used by: ghs-backlog-sync -->

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

{whats_missing}

## Why It Matters

{why_it_matters}

## How to Fix

{how_to_fix}

## Acceptance Criteria

- [ ] {criterion_1}
- [ ] {criterion_2}

## References

- Project item: [GHS] {owner}/{repo} project, slug: {slug}
- Check definition: `.claude/skills/shared/checks/{module}/{category}/{slug}.md`
