# GitHub Projects Format Reference

Canonical reference for GitHub Projects (ProjectsV2) schema used as the sole storage backend for health findings, issues, and scoring. Replaces the previous local `backlog/` file-based system. Consumed by: ghs-repo-scan, ghs-backlog-fix, ghs-backlog-board, ghs-backlog-score, ghs-backlog-next, ghs-backlog-sync.

For the full list of health checks (verification commands, pass conditions, fix suggestions), see `checks/index.md` (module registry) and the individual module indexes (`checks/core/index.md`, `checks/dotnet/index.md`).

## Table of Contents

1. [Project Naming](#project-naming)
2. [Board Layout](#board-layout)
3. [Custom Fields](#custom-fields)
4. [Item Types](#item-types)
5. [Scoring via jq](#scoring-via-jq)
6. [State Persistence](#state-persistence)
7. [Tier System](#tier-system)
8. [Status Values](#status-values)

---

## Project Naming

Each scanned repository gets one GitHub Project, owned by the repo owner (user or org):

```
[GHS] {owner}/{repo}
```

Examples:
- `[GHS] phmatray/Formidable`
- `[GHS] Atypical-Consulting/NewSLN`

The `[GHS]` prefix enables reliable discovery across all projects for an owner.

### Project Discovery

```bash
# Find all GHS projects for an owner
gh project list --owner {owner} --format json \
  --jq '.projects[] | select(.title | startswith("[GHS]"))'

# Find project for a specific repo
gh project list --owner {owner} --format json \
  --jq '.projects[] | select(.title == "[GHS] {owner}/{repo}") | .number'
```

---

## Board Layout

The project uses the **Board layout** (Kanban) as the default view, grouped by the built-in **Status** field.

### Built-in Status Field (Kanban Columns)

| Column | Meaning | Contains |
|--------|---------|----------|
| `Todo` | Awaiting action | FAIL items awaiting fix, OPEN issues awaiting triage |
| `In Progress` | Currently being fixed | Items with active worktree agents |
| `Done` | Resolved | PASS items, closed issues, merged PRs |

The built-in `Status` field drives the Kanban board. No separate custom status field is needed:
- `Todo` = FAIL / OPEN
- `Done` = PASS / CLOSED

WARN items are not added to the project (they are excluded from scoring and not actionable).

---

## Custom Fields

Each project is provisioned with 9 custom fields. Field creation is idempotent — look up existing fields before creating.

| Field | Type | Options / Format | Purpose |
|-------|------|------------------|---------|
| `Source` | SINGLE_SELECT | `Health Check`, `GitHub Issue` | Distinguish health findings from issues |
| `Module` | SINGLE_SELECT | `core`, `dotnet` | Which module detected the finding |
| `Tier` | SINGLE_SELECT | `1 — Required`, `2 — Recommended`, `3 — Nice to Have` | Importance tier |
| `Points` | NUMBER | 4, 2, or 1 | Point value for scoring |
| `Slug` | TEXT | Check slug (e.g., `readme`, `license`) | Machine-readable identifier |
| `Category` | SINGLE_SELECT | `A — API-only`, `B — File changes`, `CI` | Fix classification |
| `Detected` | DATE | `YYYY-MM-DD` | Date of first scan |
| `PR URL` | TEXT | URL string | Link to fix PR |
| `Score` | NUMBER | 0-100 | Health score percentage (on score record item only) |

### Field Provisioning

After creating or finding the project, ensure all fields exist:

```bash
EXISTING=$(gh project field-list $PROJECT_NUM --owner {owner} --format json --jq '.fields[].name')

for field in "Source" "Module" "Tier" "Points" "Slug" "Category" "Detected" "PR URL" "Score"; do
  if ! echo "$EXISTING" | grep -q "^${field}$"; then
    # Create the field (type depends on field name — see table above)
  fi
done
```

Cache the field IDs after provisioning — they are needed for `item-edit` operations.

---

## Item Types

### Health Findings (Draft Issues)

Created by `ghs-repo-scan` for each FAIL check result.

| Property | Value |
|----------|-------|
| Title | `[Health] {Check Name}` (e.g., `[Health] README`, `[Health] Branch Protection`) |
| Type | Draft issue |
| Status | `Todo` (FAIL) or `Done` (PASS) |
| Body | Description of what's missing and how to fix it |
| Source | `Health Check` |
| Module | `core` or `dotnet` |
| Tier | `1 — Required`, `2 — Recommended`, or `3 — Nice to Have` |
| Points | 4, 2, or 1 |
| Slug | Check slug (e.g., `readme`, `license`) |
| Category | `A — API-only`, `B — File changes`, or `CI` |
| Detected | Date of scan |

Title convention matches `sync-format.md` — `[Health] {Check Name}` enables title-based dedup.

### GitHub Issues (Linked Items)

Added by `ghs-repo-scan` for open GitHub issues on the repository.

```bash
gh project item-add {project_number} --owner {owner} --url {issue_url}
```

| Property | Value |
|----------|-------|
| Status | `Todo` (OPEN) or `Done` (CLOSED) |
| Source | `GitHub Issue` |

Linked issues carry their own title and body from GitHub. Custom fields (`Source`) are set after adding.

### Score Record (Draft Issue)

A single draft item per project that stores the computed health score.

| Property | Value |
|----------|-------|
| Title | `[GHS Score]` |
| Type | Draft issue |
| Body | JSON with score breakdown |
| Score | Health score percentage (0-100) |

Body format:
```json
{
  "score": 46,
  "core": {"earned": 30, "possible": 74, "pct": 41},
  "dotnet": {"earned": 18, "possible": 34, "pct": 53},
  "combined": true,
  "formula": "round(41 * 0.6 + 53 * 0.4)",
  "updated": "2026-02-28"
}
```

### State Record (Real GitHub Issue)

Session state is stored as a real GitHub Issue on the target repository (not a project draft).

| Property | Value |
|----------|-------|
| Title | `[GHS State] {owner}/{repo}` |
| Label | `ghs:state` |
| State | Open (always — closed only when repo is removed from GHS) |

See `state-persistence.md` for the full format and lifecycle.

---

## Scoring via jq

Health score is calculated by querying project items:

```bash
# Get all health check items
ITEMS=$(gh project item-list $PROJECT_NUM --owner {owner} --format json --limit 500)

# Count earned points (items in Done with Source = Health Check)
EARNED=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .status == "Done") | .points] | add // 0')

# Count possible points (items in Todo + Done with Source = Health Check)
POSSIBLE=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and (.status == "Todo" or .status == "Done")) | .points] | add // 0')

# Calculate percentage
SCORE=$(echo "scale=0; $EARNED * 100 / $POSSIBLE" | bc)
```

Items with status other than `Todo` or `Done` (e.g., `In Progress`) are counted as `Todo` for scoring purposes — they haven't passed yet.

WARN items are never added to the project, so they are automatically excluded from scoring.

### Per-Module Scoring

For repos with language modules, filter by the `Module` field:

```bash
# Core module score
CORE_EARNED=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .module == "core" and .status == "Done") | .points] | add // 0')
CORE_POSSIBLE=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .module == "core" and (.status == "Todo" or .status == "Done")) | .points] | add // 0')

# .NET module score
DOTNET_EARNED=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .module == "dotnet" and .status == "Done") | .points] | add // 0')
DOTNET_POSSIBLE=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .module == "dotnet" and (.status == "Todo" or .status == "Done")) | .points] | add // 0')

# Combined score
COMBINED=$(echo "scale=0; ($CORE_EARNED * 100 / $CORE_POSSIBLE) * 60 / 100 + ($DOTNET_EARNED * 100 / $DOTNET_POSSIBLE) * 40 / 100" | bc)
```

---

## State Persistence

Session state (decisions, blockers, history) is stored as a real GitHub Issue on the target repository. See `state-persistence.md` for the complete contract.

Key lookup:

```bash
# Find the state issue
gh issue list --repo {owner}/{repo} --label "ghs:state" --state open \
  --json number,title,body --limit 1
```

---

## Tier System

Health checks are organized into three tiers reflecting their importance:

| Tier | Label | Points per Check | Description |
|------|-------|-----------------|-------------|
| **1** | Required | 4 | Non-negotiable for any public or team-shared repository |
| **2** | Recommended | 2 | Important for maintainability and collaboration |
| **3** | Nice to Have | 1 | Polish items that signal a mature, well-maintained project |

---

## Status Values

### Health Items (via Project Status Column)

| Status Column | Meaning |
|---------------|---------|
| **Todo** | The check did not pass; action required (equivalent to old FAIL) |
| **In Progress** | Fix is being applied (worktree agent active) |
| **Done** | The check passed (equivalent to old PASS) |

WARN items (permission-related, cannot verify) are **not** added to the project. They are reported in terminal output only.

INFO items (informational, no score impact) are also **not** added to the project.

### Issue Items (via Project Status Column)

| Status Column | Meaning |
|---------------|---------|
| **Todo** | Issue is open on GitHub, no PR yet |
| **In Progress** | PR created or implementation underway |
| **Done** | Issue closed or PR merged |
