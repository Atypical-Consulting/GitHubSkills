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
| `[PASS]` | Check is passing — no action needed |
| `[FAIL]` | Check is failing — a backlog item is created |
| `[WARN]` | Unable to check — usually a permission issue (excluded from score) |
| `[INFO]` | Informational only — no points, no penalty |

### Issues Table

Open GitHub issues are listed with their number, title, labels, age, and assignee. If the repository has more than 20 issues, the terminal shows the 20 most recent with a note about the rest.

## Step 3: Review the Backlog

After scanning, GHS saves all findings to structured markdown files:

```
backlog/phmatray_my-project/
  SUMMARY.md              # Unified repo summary with scores and tables
  health/
    tier-1--readme.md     # One file per failing/warning health check
    tier-1--license.md
    tier-2--ci-cd.md
    ...
  issues/
    issue-42--login-bug.md    # One file per open GitHub issue
    issue-108--dark-mode.md
    ...
```

Each health item file contains the check name, tier, points, status, acceptance criteria, and a fix strategy. Each issue file contains the issue metadata and body.

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
