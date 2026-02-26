# ghs-profile

Display a full 360-degree view of a GitHub user: profile info, repository portfolio, pinned repos, contribution stats, open work, organization memberships, and recent activity.

## When to Use

Use this skill to view a GitHub user's complete profile — your own or someone else's. Defaults to the authenticated user when no username is given.

**Trigger phrases:** "show my profile", "github profile", "who is {user}", "show @me", "my github stats", "what repos does {user} have", "contribution summary", "profile overview", "360 view"

## What It Does

1. **Resolves** the target user (argument or `@me`) and sets an IS_VIEWER flag
2. **Fetches profile data** — name, bio, company, location, followers, member since
3. **Lists repositories** — top 5 by stars, language breakdown, fork ratio
4. **Shows pinned repos** — up to 6 pinned repositories via GraphQL
5. **Contribution stats** — commits, PRs, issues, reviews for the current year (IS_VIEWER only)
6. **Open work** — authored PRs, assigned issues, review requests (IS_VIEWER only)
7. **Organizations** — public org memberships
8. **Recent activity** — last 10 public events
9. **Suggests next steps** — routes to repo-scan, issue-triage, backlog-board

## IS_VIEWER Flag

When viewing your own profile (`@me`), the skill has access to full data including contribution stats and open work. When viewing another user, those sections display an `[INFO]` note and are skipped — GitHub's API restricts that data to the authenticated user.

| Section | @me | Other user |
|---------|-----|------------|
| Profile info | Full | Full |
| Repositories | Full | Full (public only) |
| Pinned repos | Full | Full |
| Contribution stats | Full | `[INFO]` skipped |
| Open work | Full | `[INFO]` skipped |
| Organizations | Full | Public only |
| Recent activity | Full | Public only |

## Example

```
You: show my profile

## GitHub Profile: @phmatray

  phmatray (Philippe Matray)
  Bio:      Software architect & open-source contributor
  Location: Belgium
  Member since: 2018-03-15 (8 years)

  Followers: 42  |  Following: 18  |  Public repos: 35  |  Gists: 3
  https://github.com/phmatray

---

### Repository Portfolio — 35 public repos

  Top by Stars:
  ★ 128  phmatray/NewSLN  — .NET solution template
  ★  45  phmatray/GitHubSkills  — Claude Code skills for GitHub
  ★  22  phmatray/BlazorApp  — Blazor component library
  ★  12  phmatray/DotNetUtils  — .NET utility collection
  ★   8  phmatray/ConfigTool  — Configuration management
  ... and 30 more repos

  Language Breakdown:
  C#:         ████████████░░░░ 18 repos (51%)
  TypeScript: ████░░░░░░░░░░░░  6 repos (17%)
  Python:     ███░░░░░░░░░░░░░  4 repos (11%)

### Pinned Repositories
  1. phmatray/NewSLN  ★ 128  — .NET solution template (C#)
  2. phmatray/GitHubSkills  ★ 45  — Claude Code skills for GitHub (Markdown)

### Contribution Stats — 2026
  Commits:  ████████████████ 847
  PRs:      ████████░░░░░░░░ 412
  Issues:   ████░░░░░░░░░░░░ 156
  Reviews:  ██░░░░░░░░░░░░░░  89

### Open Work

  Open PRs authored (3):
  [OPEN] #42  Fix login validation  phmatray/NewSLN  (2d ago)
  [OPEN] #15  Add dark mode support  phmatray/BlazorApp  (5d ago)
  [OPEN] #7   Update dependencies  phmatray/ConfigTool  (1w ago)

### Organizations (2)
  @Atypical-Consulting  — Software consulting firm
  @dotnet-community  — .NET open-source community

### Recent Activity (last 10 events)
  2026-02-26  PushEvent          phmatray/GitHubSkills  pushed 3 commits
  2026-02-25  PullRequestEvent   phmatray/NewSLN        opened PR #42
  2026-02-24  IssuesEvent        phmatray/BlazorApp     opened issue #15

---

### Next Steps
  /ghs-repo-scan phmatray/NewSLN  — scan the top repository
  /ghs-issue-triage phmatray/NewSLN  — triage issues
  /ghs-backlog-board  — view backlog dashboard
```

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| User not found (404) | `[FAIL] User not found` — stops gracefully |
| Bot/org account | `[INFO] Account is a {type}` — shows available data, skips contributions |
| No pinned repos | Section is skipped entirely |
| No public repos | Shows `No public repositories.` |
| Rate limit hit | `[WARN]` — shows whatever data was already fetched |

## Requirements

| Tool | Required |
|------|----------|
| `gh` CLI | Yes (authenticated) |
| Network | Yes |

## Related Skills

- [ghs-repo-scan](/skills/ghs-repo-scan) --- scan a repo from the user's portfolio
- [ghs-issue-triage](/skills/ghs-issue-triage) --- triage issues on the user's repos
- [ghs-backlog-board](/skills/ghs-backlog-board) --- view backlog dashboard across audited repos
