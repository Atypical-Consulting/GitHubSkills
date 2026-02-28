# Your First Scan

This guide walks you through scanning a repository for the first time with GHS.

## Step 1: Start a Scan

Open Claude Code in the GHS directory and tell it which repository to scan:

```
scan phmatray/my-project
```

If you are already inside a cloned repository, you can simply say:

```
scan my repo
```

GHS detects the repository from the git remote and begins the scan automatically.

## Step 2: Understand the Output

The scan spawns 4 parallel agents (one per tier plus an issues agent) and produces a terminal report with several sections:

### Score Line

```
Health Score: 14/51 (27%)
```

The score is calculated from all passing checks. WARN items (permission issues) are excluded from both the earned and possible totals. INFO items carry no points.

### Progress Bars

```
Tier 1:  8/16  ████░░░░ (50%)
Tier 2:  6/26  ██░░░░░░ (23%)
Tier 3:  0/9   ░░░░░░░░ (0%)
```

Each tier gets its own progress bar showing points earned versus points possible. The bar is 8 characters wide, using filled blocks and empty blocks.

### Check Results

Each check is displayed with a status badge:

| Badge | Meaning |
|-------|---------|
| `[PASS]` | Check is passing — added to the GitHub Project as Done |
| `[FAIL]` | Check is failing — added to the GitHub Project as Todo |
| `[WARN]` | Unable to check — usually a permission issue (excluded from score, not added to project) |
| `[INFO]` | Informational only — no points, no penalty, not added to project |

### Issues Table

Open GitHub issues are listed with their number, title, labels, age, and assignee. If the repository has more than 20 issues, the terminal shows the 20 most recent with a note about the rest.

## Step 3: Review the GitHub Project

After scanning, GHS saves all findings as items in a GitHub Project named `[GHS] phmatray/my-project`. You can view it directly on GitHub, or use the dashboard skill:

```
show me the backlog board
```

The project uses a Kanban board with three columns:

| Column | Contents |
|--------|----------|
| `Todo` | FAIL health findings and open issues — action required |
| `In Progress` | Items being actively fixed |
| `Done` | PASS findings and resolved items |

Each health finding is a draft item titled `[Health] {Check Name}` with custom fields for tier, points, module, category, and detection date. Open GitHub issues are linked directly into the project. A `[GHS Score]` item stores the computed health score as JSON for quick retrieval.

## Step 4: What's Next?

After your first scan, you have several options:

### View the dashboard

```
show me the backlog board
```

This displays a cross-repo dashboard with scores, progress bars, and item counts. If you have scanned multiple repos, they all appear in a single table.

### Fix the backlog

```
fix the backlog
```

GHS classifies each failing item, creates git worktrees, spawns parallel agents to fix them, and opens pull requests. You confirm the plan before anything changes.

### Get a recommendation

```
what should I fix next?
```

GHS applies a priority algorithm to recommend the single highest-impact item across all your audited repos: lowest-scoring repo first, health over issues, lowest tier first, highest points first.

### Triage issues

```
triage my issues
```

If your repository has unlabeled issues, GHS can classify them by type and priority using a consistent label taxonomy.
