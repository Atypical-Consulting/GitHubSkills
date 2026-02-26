---
name: ghs-profile
description: >
  Display a full 360-degree profile view of a GitHub user — profile info, repository portfolio,
  pinned repos, contribution stats, open work, organization memberships, and recent activity.
  Defaults to the authenticated user when no username is given. Use this skill whenever the user
  wants to see a GitHub profile, review their own activity, check someone's GitHub presence, or
  says things like "show my profile", "github profile", "who is {user}", "show @me",
  "my github stats", "what repos does {user} have", "contribution summary", "profile overview",
  "show github activity for {user}", "360 view", "user summary", or "profile report".
  Do NOT use for scanning repository health (use ghs-repo-scan), managing issues
  (use ghs-issue-triage), or fixing code (use ghs-backlog-fix).
allowed-tools: "Bash(gh:*) Read"
compatibility: "Requires gh CLI (authenticated), network access"
license: MIT
metadata:
  author: phmatray
  version: 1.0.0
routes-to:
  - ghs-repo-scan
  - ghs-issue-triage
  - ghs-backlog-board
routes-from: []
---

# GitHub Profile Viewer

Display a full 360-degree view of a GitHub user: profile, repos, contributions, open work, orgs, and activity.

<context>
Purpose: Read-only profile renderer that fetches and displays GitHub user data via the gh CLI.

Roles:
1. **Profile Renderer** (you) — fetches user data via gh CLI, formats the display, suggests next actions

No sub-agents — this is a read-only skill that renders API data.

Shared references (use these, do not duplicate their logic):
- `../shared/references/gh-cli-patterns.md` — auth checks, API calls, error handling (404/403)
- `../shared/references/output-conventions.md` — status indicators, progress bars, table patterns
</context>

## Anti-Patterns

| Do NOT | Do Instead |
|--------|-----------|
| Use raw `curl` to api.github.com | Use `gh api` for all GitHub API calls — it handles auth and rate limits |
| Fail hard when viewing another user's private data | Set IS_VIEWER flag; show `[INFO] Contribution stats are only available for the authenticated user` for non-@me targets |
| Show all repositories in the terminal | Cap at top 5 by stars; note total count (e.g., "showing 5 of 42 repos") |
| Show absolute timestamps for events | Use relative timestamps (e.g., "2d ago", "3h ago") or short dates (YYYY-MM-DD) |
| Paginate through all events | Fetch first page only (up to 30), slice to 10 with `--jq '.[:10]'` |
| Call `viewer` GraphQL queries for other users | Gate contribution stats and review requests behind the IS_VIEWER flag |
| Render rows for null/empty profile fields | Only render non-null fields — skip bio/company/twitter/blog rows if empty |

<objective>
Display a comprehensive GitHub profile report with the following sections:

1. **Profile Header** — username, name, bio, company, location, blog, member since, follower/following counts
2. **Repository Portfolio** — top 5 repos by stars, language breakdown, fork ratio, popular topics
3. **Pinned Repositories** — up to 6 pinned repos (if any)
4. **Contribution Stats** — commits, PRs, issues, reviews for current year (IS_VIEWER only)
5. **Open Work** — open PRs authored, issues assigned, review requests (IS_VIEWER only)
6. **Organizations** — org memberships with descriptions
7. **Recent Activity** — last 10 public events
8. **Next Steps** — routing suggestions to other skills

Next routing:
- Suggest `/ghs-repo-scan {user}/{top-repo}` to scan the user's top repository
- Suggest `/ghs-issue-triage {user}/{repo}` if the user has repos with open issues
- Suggest `/ghs-backlog-board` for cross-repo overview
</objective>

<process>

## Input

Optional argument: a GitHub username (e.g., `phmatray`, `torvalds`).

- If no username provided, default to the authenticated user (`@me`)
- Accept formats: `username`, `@username`, `@me`

## Phase 1 — Auth & User Resolution

1. Verify authentication:
   ```bash
   gh auth status
   ```
   If this fails, tell the user to run `gh auth login` and stop.

2. Resolve the authenticated user's login:
   ```bash
   gh api user --jq '.login'
   ```

3. Determine the target user:
   - If no argument or `@me`: target = authenticated user
   - If a username is provided: target = that username

4. Set the **IS_VIEWER** flag:
   - `IS_VIEWER = true` when target login matches the authenticated user's login
   - `IS_VIEWER = false` otherwise

> **Rule:** Always set IS_VIEWER before making any data calls.
>
> **Trigger:** Every invocation — needed to decide which queries to run.
>
> **Example:** User says "show profile for torvalds" → target = `torvalds`, IS_VIEWER = false → skip contribution stats and review requests.

## Phase 2 — Profile Data

Fetch the user's profile information:

```bash
# For @me (IS_VIEWER = true)
gh api user --jq '{login, name, bio, company, location, blog, twitter_username, followers, following, public_repos, public_gists, created_at}'

# For other users (IS_VIEWER = false)
gh api users/{username} --jq '{login, name, bio, company, location, blog, twitter_username, followers, following, public_repos, public_gists, created_at, type}'
```

Render the profile header. Only include non-null, non-empty fields:

```
## GitHub Profile: @{username}

  {username} ({name})
  Bio:      {bio}
  Company:  {company}
  Location: {location}
  Blog:     {blog}
  Twitter:  @{twitter_username}
  Member since: {YYYY-MM-DD} ({N} years)

  Followers: {N}  |  Following: {N}  |  Public repos: {N}  |  Gists: {N}
  https://github.com/{username}
```

## Phase 3 — Repository Portfolio

Fetch the user's repositories (up to 30 for analysis, display top 5):

```bash
gh repo list {username} --limit 30 --json name,nameWithOwner,description,stargazerCount,forkCount,primaryLanguage,isFork,isArchived,updatedAt --sort stars
```

### Top Repos by Stars

Display the top 5 non-fork, non-archived repos sorted by stars:

```
### Repository Portfolio — {total_count} public repos

  Top by Stars:
  ★ {N}  {owner}/{repo}  — {description}
  ★ {N}  {owner}/{repo}  — {description}
  ...
```

If total repos > 5, add: `  ... and {N} more repos`

### Language Breakdown

Aggregate `primaryLanguage` across all fetched repos. Display as a 16-char bar:

```
  Language Breakdown:
  C#:         ████████░░░░░░░░ {N} repos ({pct}%)
  TypeScript: ████░░░░░░░░░░░░ {N} repos ({pct}%)
  Python:     ██░░░░░░░░░░░░░░ {N} repos ({pct}%)
  ...
```

Bar width: 16 characters. Filled: `█` (U+2588). Empty: `░` (U+2591). Show top 5 languages.

### Additional Stats

```
  Forks: {N} of {total} repos are forks ({pct}%)
  Archived: {N} repos archived
```

Only show fork/archived lines if count > 0.

## Phase 4 — Pinned Repositories

Fetch pinned repos via GraphQL:

```bash
gh api graphql -f query='
  query($login: String!) {
    user(login: $login) {
      pinnedItems(first: 6, types: REPOSITORY) {
        nodes {
          ... on Repository {
            nameWithOwner
            description
            stargazerCount
            primaryLanguage { name }
          }
        }
      }
    }
  }
' -f login='{username}' --jq '.data.user.pinnedItems.nodes'
```

Display if any pinned repos exist:

```
### Pinned Repositories
  1. {owner}/{repo}  ★ {N}  — {description} ({lang})
  2. {owner}/{repo}  ★ {N}  — {description} ({lang})
  ...
```

If no pinned repos, skip this section entirely (do not show an empty heading).

## Phase 5 — Contribution Stats (IS_VIEWER only)

> **Rule:** Only fetch contribution stats when IS_VIEWER = true.
>
> **Trigger:** Target user is the authenticated user.
>
> **Example:** IS_VIEWER = false → display `[INFO] Contribution stats are only available for the authenticated user (@me)` and skip this phase.

```bash
gh api graphql -f query='
  query {
    viewer {
      contributionsCollection {
        totalCommitContributions
        totalPullRequestContributions
        totalIssueContributions
        totalPullRequestReviewContributions
        restrictedContributionsCount
      }
    }
  }
' --jq '.data.viewer.contributionsCollection'
```

Display with relative progress bars (largest value gets full 16-char bar, others scale proportionally):

```
### Contribution Stats — {year}
  Commits:  ████████████████ {N}
  PRs:      ████████░░░░░░░░ {N}
  Issues:   ████░░░░░░░░░░░░ {N}
  Reviews:  ██░░░░░░░░░░░░░░ {N}
```

If all values are 0, show: `  No contributions recorded for {year} yet.`

## Phase 6 — Open Work (IS_VIEWER only)

> **Rule:** Only fetch open work when IS_VIEWER = true.
>
> **Trigger:** Target user is the authenticated user.

### Open PRs Authored

```bash
gh pr list --author @me --state open --json number,title,repository,createdAt --limit 10
```

### Issues Assigned

```bash
gh issue list --assignee @me --state open --json number,title,repository,createdAt --limit 10
```

### Review Requests

```bash
gh search prs --review-requested=@me --state=open --json number,title,repository --limit 10
```

Display:

```
### Open Work

  Open PRs authored ({N}):
  [OPEN] #{N}  {title}  {repo}  ({age})
  ...

  Issues assigned ({N}):
  [OPEN] #{N}  {title}  {repo}  ({age})
  ...

  Review requests ({N}):
  [OPEN] #{N}  {title}  {repo}
  ...
```

If IS_VIEWER = false, display:
```
### Open Work
  [INFO] Open work details are only available for the authenticated user (@me)
```

## Phase 7 — Organizations

```bash
# For @me
gh api user/orgs --jq '.[] | {login, description}'

# For other users
gh api users/{username}/orgs --jq '.[] | {login, description}'
```

Display:

```
### Organizations ({N})
  @{org}  — {description}
  @{org}  — {description}
  ...
```

If no organizations, show: `  No public organization memberships.`

## Phase 8 — Recent Activity

Fetch the last 10 public events (first page only, no pagination):

```bash
gh api users/{username}/events --jq '[.[:10][] | {type, repo: .repo.name, created_at}]'
```

Display:

```
### Recent Activity (last 10 events)
  {date}  {EventType}       {repo}              {summary}
  {date}  PushEvent         user/repo           pushed {N} commits
  {date}  CreateEvent       user/repo           created branch {ref}
  {date}  IssuesEvent       user/repo           opened issue #{N}
  {date}  PullRequestEvent  user/repo           opened PR #{N}
  {date}  WatchEvent        user/repo           starred
  {date}  ForkEvent         user/repo           forked to user/fork
  ...
```

### Event Type Summaries

| Event Type | Summary Format |
|-----------|---------------|
| PushEvent | `pushed {size} commits` |
| CreateEvent | `created {ref_type} {ref}` |
| DeleteEvent | `deleted {ref_type} {ref}` |
| IssuesEvent | `{action} issue #{number}` |
| PullRequestEvent | `{action} PR #{number}` |
| WatchEvent | `starred` |
| ForkEvent | `forked to {forkee}` |
| IssueCommentEvent | `commented on #{number}` |
| ReleaseEvent | `released {tag_name}` |
| Other | `{type}` (raw event type) |

If no events found, show: `  No recent public activity.`

## Phase 9 — Render Report & Next Steps

Assemble all sections from Phases 2–8 into the final report. Then add routing suggestions:

```
---

### Next Steps
  /ghs-repo-scan {username}/{top-repo}  — scan the top repository for health issues
  /ghs-backlog-board                     — view backlog dashboard across all audited repos
```

If IS_VIEWER = true, also suggest:
```
  /ghs-issue-triage {username}/{top-repo}  — triage issues on the top repository
```

</process>

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| User not found (404) | `[FAIL] User "{username}" not found on GitHub.` — stop gracefully |
| Bot/org account (`type: "Bot"` or `type: "Organization"`) | `[INFO] @{username} is a {type} account.` — show available data, skip contribution stats |
| No pinned repos | Skip the Pinned Repositories section entirely |
| No public repos | Show `No public repositories.` in the portfolio section |
| Rate limit hit (403/429) | `[WARN] GitHub API rate limit reached. Try again in a few minutes.` — show whatever data was already fetched |
| Null profile fields (bio, company, twitter, blog) | Skip those rows — do not render empty lines |
| GraphQL errors for pinned repos | `[WARN] Could not fetch pinned repositories.` — continue with other sections |

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `gh auth status` fails | Not logged in | Run `gh auth login` |
| Contribution stats show `[INFO]` for @me | IS_VIEWER flag not set correctly | Ensure the target matches `gh api user --jq '.login'` |
| Recent activity is empty | User has no public events | Normal for private-only users — show informational message |
| Organizations list is empty | User has no public org memberships, or orgs are hidden | Show `No public organization memberships.` |
| Pinned repos query fails | User may have no pinned items, or GraphQL permission issue | Show `[WARN]` and continue |

## Routing Suggestions

| After ghs-profile | Suggest |
|-------------------|---------|
| User viewed own profile | `/ghs-repo-scan {user}/{top-repo}`, `/ghs-issue-triage`, `/ghs-backlog-board` |
| User viewed another profile | `/ghs-repo-scan {user}/{top-repo}`, `/ghs-backlog-board` |
| User says "scan that repo" | Invoke `/ghs-repo-scan {user}/{repo}` |
| User says "triage my issues" | Invoke `/ghs-issue-triage` |
