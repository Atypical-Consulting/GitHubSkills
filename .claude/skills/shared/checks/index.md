# Health Checks Index

Registry of all health checks used by the ghs:repo-scan skill. Each check has its own file in this directory containing verification commands, pass conditions, and backlog content.

Consumed by: ghs:repo-scan (orchestrator and check agents), ghs:backlog-fix, ghs:backlog-board, ghs:backlog-score.

## Check Registry

### Tier 1 — Required (4 points each)

| Check | Slug | File | Scoring |
|-------|------|------|---------|
| README | `readme` | [readme.md](readme.md) | Normal |
| LICENSE | `license` | [license.md](license.md) | Normal |
| Description | `description` | [description.md](description.md) | Normal |
| Branch Protection | `branch-protection` | [branch-protection.md](branch-protection.md) | Normal |

### Tier 2 — Recommended (2 points each)

| Check | Slug | File | Scoring |
|-------|------|------|---------|
| .gitignore | `gitignore` | [gitignore.md](gitignore.md) | Normal |
| CI/CD Workflows | `ci-cd-workflows` | [ci-cd-workflows.md](ci-cd-workflows.md) | Normal |
| CI Workflow Health | `ci-workflow-health` | [ci-workflow-health.md](ci-workflow-health.md) | Normal |
| .editorconfig | `editorconfig` | [editorconfig.md](editorconfig.md) | Normal |
| CODEOWNERS | `codeowners` | [codeowners.md](codeowners.md) | Normal |
| Issue Templates | `issue-templates` | [issue-templates.md](issue-templates.md) | Normal |
| PR Template | `pr-template` | [pr-template.md](pr-template.md) | Normal |
| Topics | `topics` | [topics.md](topics.md) | Normal |

### Tier 3 — Nice to Have (1 point each)

| Check | Slug | File | Scoring |
|-------|------|------|---------|
| SECURITY.md | `security-md` | [security-md.md](security-md.md) | Normal |
| CONTRIBUTING.md | `contributing-md` | [contributing-md.md](contributing-md.md) | Normal |
| Security Alerts | `security-alerts` | [security-alerts.md](security-alerts.md) | Normal |
| .editorconfig Drift | `editorconfig-drift` | [editorconfig-drift.md](editorconfig-drift.md) | Normal |
| Funding | `funding` | [funding.md](funding.md) | **INFO only** |

## Scoring Summary

| Tier | Checks | Points each | Subtotal |
|------|--------|-------------|----------|
| Tier 1 | 4 | 4 | 16 |
| Tier 2 | 8 | 2 | 16 |
| Tier 3 | 4 (excluding Funding) | 1 | 4 |
| **Total** | **16** | | **36** |

- WARN items are excluded from both earned and possible totals.
- INFO items (Funding) carry no points and no penalty.
- Percentage: `earned / possible * 100`, rounded to nearest integer.

## How Agents Use This Index

Each check agent receives a tier assignment. It:
1. Reads this index to find the checks in its tier
2. For each check, reads the individual check file (`{slug}.md`)
3. Runs the verification command from the check file
4. Determines PASS/FAIL/WARN based on status rules
5. If FAIL/WARN, writes a backlog item using the Backlog Content section from the check file
6. Returns structured results to the orchestrator
