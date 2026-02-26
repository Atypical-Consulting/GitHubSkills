# Skills Reference

GHS provides **9 skills** organized into two workflow loops plus a shared merge skill.

## Health Loop

```mermaid
flowchart LR
    scan[ghs-repo-scan] --> board[ghs-backlog-board]
    board --> fix[ghs-backlog-fix]
    fix --> merge[ghs-merge-prs]
    merge --> scan
    board --> score[ghs-backlog-score]
    board --> next[ghs-backlog-next]
    next --> fix
```

The health loop audits repositories against 38 quality checks, displays findings on a dashboard, fixes them with parallel agents, and merges the resulting PRs.

## Issue Loop

```mermaid
flowchart LR
    triage[ghs-issue-triage] --> analyze[ghs-issue-analyze]
    analyze --> implement[ghs-issue-implement]
    implement --> merge[ghs-merge-prs]
```

The issue loop classifies GitHub issues with labels, investigates the codebase for each issue, implements fixes with worktree-based agents, and merges the PRs.

## All Skills

| Skill | Loop | Version | Description |
|-------|------|---------|-------------|
| [ghs-repo-scan](/skills/ghs-repo-scan) | Health | 4.0.0 | Scan a repo for quality best practices and open issues |
| [ghs-backlog-board](/skills/ghs-backlog-board) | Health | 3.0.0 | Dashboard of all backlog items across audited repos |
| [ghs-backlog-fix](/skills/ghs-backlog-fix) | Health | 5.0.0 | Fix backlog items using parallel worktree agents |
| [ghs-backlog-score](/skills/ghs-backlog-score) | Health | 2.0.0 | Calculate and display health score |
| [ghs-backlog-next](/skills/ghs-backlog-next) | Health | 2.0.0 | Recommend highest-impact next fix |
| [ghs-issue-triage](/skills/ghs-issue-triage) | Issue | 2.0.0 | Apply proper labels to GitHub issues |
| [ghs-issue-analyze](/skills/ghs-issue-analyze) | Issue | 2.0.0 | Deep-analyze an issue, post analysis comment |
| [ghs-issue-implement](/skills/ghs-issue-implement) | Issue | 2.0.0 | Implement an issue, create a PR |
| [ghs-merge-prs](/skills/ghs-merge-prs) | Both | 2.0.0 | Merge PRs with CI-aware confirmation |
