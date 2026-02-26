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

Re-authenticate with the correct scopes:

```bash
gh auth login --scopes repo,read:org
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

## Python Scripts

### `python3: command not found`

Some skills use Python for score calculation. Install Python 3:

::: code-group
```bash [macOS]
brew install python3
```

```bash [Linux (Debian/Ubuntu)]
sudo apt install python3
```

```bash [Windows]
winget install Python.Python.3
```
:::

### `ModuleNotFoundError`

GHS Python scripts use only the standard library — no `pip install` needed. If you see a module error, ensure you're using Python 3.8+:

```bash
python3 --version
```

## Backlog Issues

### Stale scan data

If your backlog seems outdated, re-scan the repository:

```
scan owner/repo
```

The scan overwrites the existing backlog with fresh results. The SUMMARY.md includes a timestamp so you can verify when the last scan ran.

### Reset the backlog

To start fresh, delete the repository's backlog directory:

```bash
rm -rf backlog/owner_repo/
```

Then re-scan.

### Duplicate backlog items

This can happen if you rename a repository between scans. Delete the old directory and re-scan with the current name.

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
