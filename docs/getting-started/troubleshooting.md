# Troubleshooting

Common issues and their solutions when working with GHS.

## GitHub CLI Authentication

### `gh: not authenticated`

You need to authenticate the GitHub CLI before GHS can access repositories.

```bash
gh auth login
```

Follow the interactive prompts to authenticate via browser or token.

### `403 Forbidden` on API calls

Your token may lack the required scopes. GHS needs:

- **`repo`** — full access to private and public repositories
- **`read:org`** — read organization membership (for CODEOWNERS checks)
- **`project`** — read and write GitHub Projects (for storing scan results and scores)

Re-authenticate with the correct scopes:

```bash
gh auth login --scopes repo,read:org,project
```

### `[WARN]` results for branch protection or settings

WARN results typically mean your token doesn't have admin access to the repository. These checks are **excluded from the score** — they don't penalize you. To resolve them:

- Ask a repository admin to run the scan, or
- Request admin access to the repository

## Claude Code

### Skills not detected

If Claude doesn't recognize GHS skills (e.g., "scan my repo" does nothing), verify you're running Claude Code from the GHS directory:

```bash
cd /path/to/GitHubSkills
claude
```

Skills are auto-discovered from `.claude/skills/`. Claude Code only loads skills from the current working directory.

### Agent timeout or context limit

Large repositories with many issues can cause agents to hit context limits. Try:

- Scanning with fewer issues: the scan caps at 20 issues by default
- Running `ghs-backlog-fix` on a single item instead of the full batch
- Ensuring your Claude Code subscription supports extended context

## GitHub Project Issues

### Stale scan data

If your GitHub Project seems outdated, re-scan the repository:

```
scan owner/repo
```

The scan updates existing project items in place — PASS/FAIL status is refreshed, and the `[GHS Score]` item is updated with the new score and timestamp.

### Reset the project

To start fresh, delete the GitHub Project from github.com and re-scan. GHS will create a new project with all fields provisioned automatically.

### Duplicate project items

This can happen if you rename a repository between scans. Delete the old `[GHS] old-owner/old-repo` project on GitHub, then re-scan with the current repository name.

### Project not found after scan

If `ghs-backlog-board` or `ghs-backlog-score` cannot find the project, verify the project owner matches the repository owner. GHS looks for projects using:

```bash
gh project list --owner {owner} --format json \
  --jq '.projects[] | select(.title == "[GHS] {owner}/{repo}")'
```

Ensure your GitHub token has the `project` scope:

```bash
gh auth login --scopes repo,read:org,project
```

## Pull Request Issues

### PR creation fails

Common causes:

- **No upstream branch**: GHS pushes to a new branch before creating the PR. Ensure you have push access to the repository.
- **Branch protection rules**: If the default branch requires PRs from forks, GHS cannot push directly. Clone the fork instead.
- **Rate limiting**: GitHub API rate limits are 5,000 requests/hour for authenticated users. Wait and retry if you hit the limit.

### Merge conflicts

If `ghs-merge-prs` reports conflicts:

1. Open the PR on GitHub
2. Resolve conflicts manually or use GitHub's conflict resolution UI
3. Re-run `merge my PRs` to merge the resolved PR

## Still Stuck?

- Check the [GitHub Issues](https://github.com/Atypical-Consulting/GitHubSkills/issues) for known bugs
- Open a new issue with the error output and your environment details
