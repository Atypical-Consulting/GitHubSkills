# GitHub Projects Format

GHS stores all scan results, health findings, and issue tracking as items in a **GitHub Project (ProjectsV2)**. There are no local markdown files — everything lives on GitHub.

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

# Find the project number for a specific repo
gh project list --owner {owner} --format json \
  --jq '.projects[] | select(.title == "[GHS] {owner}/{repo}") | .number'
```

## Board Layout

The project uses the **Board layout** (Kanban) as the default view, grouped by the built-in **Status** field.

| Column | Meaning | Contains |
|--------|---------|----------|
| `Todo` | Awaiting action | FAIL health findings, open issues awaiting triage |
| `In Progress` | Currently being worked on | Items with active worktree agents |
| `Done` | Resolved | PASS findings, closed issues, merged PRs |

WARN items (permission-related, cannot verify) are not added to the project. They appear in terminal output only.

## Custom Fields

Each project is provisioned with 9 custom fields:

| Field | Type | Options / Format | Purpose |
|-------|------|------------------|---------|
| `Source` | Single Select | `Health Check`, `GitHub Issue` | Distinguish health findings from issues |
| `Module` | Single Select | `core`, `dotnet` | Which module detected the finding |
| `Tier` | Single Select | `1 — Required`, `2 — Recommended`, `3 — Nice to Have` | Importance tier |
| `Points` | Number | 4, 2, or 1 | Point value for scoring |
| `Slug` | Text | e.g., `readme`, `license` | Machine-readable check identifier |
| `Category` | Single Select | `A — API-only`, `B — File changes`, `CI` | Fix classification |
| `Detected` | Date | `YYYY-MM-DD` | Date of first scan |
| `PR URL` | Text | URL string | Link to the fix PR |
| `Score` | Number | 0–100 | Health score percentage (score record only) |

Field creation is idempotent — GHS looks up existing fields before creating new ones.

## Item Types

### Health Findings (Draft Issues)

Created by `ghs-repo-scan` for each FAIL check result.

| Property | Value |
|----------|-------|
| Title | `[Health] {Check Name}` (e.g., `[Health] README`, `[Health] License`) |
| Type | Draft issue |
| Status | `Todo` (FAIL) or `Done` (PASS) |
| Body | Description of what is missing and how to fix it |
| Source | `Health Check` |
| Module | `core` or `dotnet` |
| Tier | `1 — Required`, `2 — Recommended`, or `3 — Nice to Have` |
| Points | 4, 2, or 1 |
| Slug | Check slug (e.g., `readme`, `license`) |
| Category | `A — API-only`, `B — File changes`, or `CI` |
| Detected | Date of scan |

The `[Health] {Check Name}` title convention enables deduplication — re-scanning updates existing items rather than creating duplicates.

### GitHub Issues (Linked Items)

Added by `ghs-repo-scan` for open GitHub issues on the repository.

| Property | Value |
|----------|-------|
| Status | `Todo` (open) or `Done` (closed) |
| Source | `GitHub Issue` |

Linked issues carry their own title and body from GitHub. The `Source` custom field is set after adding.

### Score Record (Draft Issue)

A single draft item per project that stores the computed health score.

| Property | Value |
|----------|-------|
| Title | `[GHS Score]` |
| Type | Draft issue |
| Body | JSON with score breakdown |
| Score field | Health score percentage (0–100) |

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

Session state (decisions, blockers, history) is stored as a real GitHub Issue on the target repository — not as a project draft item.

| Property | Value |
|----------|-------|
| Title | `[GHS State] {owner}/{repo}` |
| Label | `ghs:state` |
| State | Open (always — closed only when repo is removed from GHS) |

```bash
# Look up the state issue
gh issue list --repo {owner}/{repo} --label "ghs:state" --state open \
  --json number,title,body --limit 1
```

## Scoring via jq

Health score is calculated by querying project items directly — no local files or scripts required.

```bash
# Get all project items
ITEMS=$(gh project item-list $PROJECT_NUM --owner {owner} --format json --limit 500)

# Count earned points (Done health checks)
EARNED=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .status == "Done") | .points] | add // 0')

# Count possible points (Todo + Done health checks)
POSSIBLE=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and (.status == "Todo" or .status == "Done")) | .points] | add // 0')

# Calculate percentage
SCORE=$(echo "scale=0; $EARNED * 100 / $POSSIBLE" | bc)
```

Items with status `In Progress` are counted as `Todo` for scoring — they have not passed yet. WARN items are never added to the project, so they are automatically excluded.

### Per-Module Scoring

For repos with language modules, filter by the `Module` field:

```bash
# Core module score
CORE_EARNED=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .module == "core" and .status == "Done") | .points] | add // 0')
CORE_POSSIBLE=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .module == "core" and (.status == "Todo" or .status == "Done")) | .points] | add // 0')

# .NET module score
DOTNET_EARNED=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .module == "dotnet" and .status == "Done") | .points] | add // 0')
DOTNET_POSSIBLE=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .module == "dotnet" and (.status == "Todo" or .status == "Done")) | .points] | add // 0')

# Combined weighted score
COMBINED=$(echo "scale=0; ($CORE_EARNED * 100 / $CORE_POSSIBLE) * 60 / 100 + ($DOTNET_EARNED * 100 / $DOTNET_POSSIBLE) * 40 / 100" | bc)
```

## Tier System

| Tier | Label | Points | Description |
|------|-------|--------|-------------|
| 1 | Required | 4 | Non-negotiable for any public or team-shared repository |
| 2 | Recommended | 2 | Important for maintainability and collaboration |
| 3 | Nice to Have | 1 | Polish items that signal a mature, well-maintained project |
