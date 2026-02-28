# Argument Parsing

Standardized rules for how all GHS skills parse `$ARGUMENTS` --- the raw string passed when a user invokes a skill.

## Invocation Example

```
/ghs-backlog-fix owner/repo --item tier-1--license --dry-run
```

## Repo Detection

Skills auto-detect the target repository using this priority:

| Priority | Source | Pattern |
|----------|--------|---------|
| 1 | First positional arg | `owner/repo` |
| 2 | Full GitHub URL | `https://github.com/owner/repo` --- extract `owner/repo` |
| 3 | Auto-detect | `gh repo view --json nameWithOwner -q .nameWithOwner` |
| 4 | Prompt | Ask user if detection fails |

**URL normalization:**
- Strip `https://github.com/` prefix
- Strip trailing `/`, `.git`, `/issues/...`, `/pulls/...`
- Result must match `^[^/]+/[^/]+$`

## Flag Extraction

All flags use `--` prefix. No short flags (e.g., `-d`) are supported.

### Boolean Flags

| Flag | Behavior |
|------|----------|
| `--dry-run` | Show what would happen without executing |
| `--all` | Process all eligible items instead of prompting to select |
| `--auto` | Skip interactive confirmations |
| `--resume` | Resume from last persisted state |

### Value Flags

| Flag | Value Type | Example |
|------|-----------|---------|
| `--item <slug>` | string | `--item tier-1--license` |
| `--tier <N>` | integer (1--3) | `--tier 2` |
| `--pr <number>` | integer | `--pr 42` |
| `--budget <N>` | integer | `--budget 5` |
| `--bump <level>` | `major\|minor\|patch` | `--bump minor` |
| `--stages <list>` | comma-separated | `--stages pull,scan,fix` |

## Issue/PR Number Parsing

| Input Format | Result |
|-------------|--------|
| `#42` | issue/PR number `42` |
| bare `42` (after repo arg) | issue/PR number `42` |
| `owner/repo#42` | repo = `owner/repo`, number = `42` |
| `https://github.com/owner/repo/issues/42` | repo = `owner/repo`, number = `42` |
| `https://github.com/owner/repo/pull/42` | repo = `owner/repo`, number = `42` |

**Disambiguation:** If a bare integer appears without explicit `--pr` or `--item`, treat as an issue/PR number only when the skill context expects one (e.g., `ghs-issue-implement`, `ghs-review-pr`).

## Item Slug Normalization

Project item slugs use kebab-case with double-dash tier prefix: `tier-1--license`, `ci-workflow-health`.

| Input | Normalized Match |
|-------|-----------------|
| `tier-1--license` | exact match |
| `license` | partial match --- `tier-1--license` (first match wins) |
| `ci-workflow` | partial match --- `ci-workflow-health` |
| `TIER-1--LICENSE` | case-insensitive match |

**Partial match rule:** Match any slug that contains the input as a substring (case-insensitive). If multiple slugs match, prefer the one with the shortest total length.

## Defaults When No Arguments

| Scenario | Behavior |
|----------|----------|
| No args at all | Auto-detect repo from `gh repo view`; use skill defaults for all flags |
| Repo not detectable | Prompt: "Which repo? (owner/repo)" |
| Flag omitted | Use skill-defined default (documented per skill) |
| Ambiguous partial slug | List matches and prompt user to select |

## Common Flag Patterns

Universally available flags across skills:

| Flag | Type | Skills That Use It | Behavior |
|------|------|--------------------|----------|
| `--dry-run` | boolean | backlog-fix, backlog-sync, merge-prs, orchestrate, release | Show what would happen without executing |
| `--all` | boolean | backlog-fix, issue-triage, merge-prs | Process all items instead of selecting |
| `--auto` | boolean | issue-triage, orchestrate | Skip interactive confirmations |
| `--resume` | boolean | orchestrate | Resume from last persisted state |

## Parsing Order

Recommended parse order from `$ARGUMENTS`:

```
1. Extract owner/repo   --- first positional token matching owner/repo or full URL
2. Extract issue/PR #   --- token matching #N, bare N (context-dependent), or URL
3. Extract flags        --- all --prefixed tokens and their values
4. Remaining tokens     --- free-form identifiers: slugs, descriptions, search terms
```

**Priority conflicts:** Explicit `--pr` or `--item` flags override positional detection.
