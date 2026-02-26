# Tier 1 — Required

Tier 1 checks verify the absolute fundamentals every repository must have. Each check is worth **4 points**.

## README

| Property | Value |
|----------|-------|
| Slug | `readme` |
| Category | Documentation |
| Points | 4 |

**What it checks:** A `README.md` (or `README`) file exists in the repository root.

**Why it matters:** The README is the front door of your project. Without one, visitors have no idea what the project does, how to use it, or how to contribute. It's the single most important documentation file.

**How to fix:** Create a `README.md` in the repo root with at minimum: a project title, a one-line description, and basic usage instructions.

---

## LICENSE

| Property | Value |
|----------|-------|
| Slug | `license` |
| Category | Documentation |
| Points | 4 |

**What it checks:** A `LICENSE` (or `LICENSE.md`) file exists in the repository root.

**Why it matters:** Without a license, the code is technically "all rights reserved" by default. Contributors and users need a clear license to know what they can and cannot do with the code.

**How to fix:** Add a `LICENSE` file. For open source projects, MIT and Apache 2.0 are popular choices. Use [choosealicense.com](https://choosealicense.com/) for guidance.

---

## Description

| Property | Value |
|----------|-------|
| Slug | `description` |
| Category | Repo Settings |
| Points | 4 |

**What it checks:** The GitHub repository has a non-empty description set.

**Why it matters:** The description appears in search results, the repo header, and organization listings. It's the first thing people see and helps them quickly decide if the project is relevant.

**How to fix:** Go to your repo's Settings page or run:
```bash
gh repo edit --description "Your project description here"
```

---

## Branch Protection

| Property | Value |
|----------|-------|
| Slug | `branch-protection` |
| Category | Repo Settings |
| Points | 4 |

**What it checks:** The default branch (usually `main`) has branch protection rules enabled.

**Why it matters:** Branch protection prevents force-pushes to the main branch, requires PR reviews, and can enforce CI checks before merging. It's essential for maintaining code quality and preventing accidental data loss.

**How to fix:** Go to Settings > Branches > Add rule for your default branch. At minimum, enable "Require a pull request before merging."

::: warning Note
This check may return `[WARN]` if the authenticated user doesn't have admin access to the repository. WARN results are excluded from the score calculation.
:::
