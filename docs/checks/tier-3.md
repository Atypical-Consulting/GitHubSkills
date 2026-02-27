# Core — Tier 3 — Nice to Have

Tier 3 core checks verify polish and completeness items. Scored checks are worth **1 point** each. Three checks are **INFO only** (no score impact). These checks run for all repositories regardless of tech stack.

## Scored Checks (1 pt each)

### Workflow Naming

| Slug | Category |
|------|----------|
| `workflow-naming` | CI/CD |

Every workflow file should have a top-level `name:` field. Without it, GitHub displays the filename (e.g., `ci.yml`) instead of a descriptive name in the Actions tab and PR status checks.

---

### Workflow Timeouts

| Slug | Category |
|------|----------|
| `workflow-timeouts` | CI/CD |

All jobs should declare `timeout-minutes` to prevent hung runners from consuming CI minutes. The default timeout is 6 hours — a stuck build can silently waste resources.

---

### Workflow Concurrency

| Slug | Category |
|------|----------|
| `workflow-concurrency` | CI/CD |

PR-triggered workflows should use `concurrency:` groups with `cancel-in-progress: true`. Without them, pushing 5 quick commits creates 5 parallel CI runs when only the last one matters.

---

### SECURITY.md

| Slug | Category |
|------|----------|
| `security-md` | Community |

A security policy tells researchers how to responsibly disclose vulnerabilities. Without one, they may open a public issue — or not report it at all.

---

### CONTRIBUTING.md

| Slug | Category |
|------|----------|
| `contributing-md` | Documentation |

A contributing guide lowers the barrier for new contributors. It should explain how to set up the dev environment, coding standards, and the PR process.

---

### Security Alerts

| Slug | Category |
|------|----------|
| `security-alerts` | Security |

Checks that GitHub security alerts (Dependabot alerts) are enabled. These notify you of known vulnerabilities in your dependencies.

---

### .editorconfig Drift

| Slug | Category |
|------|----------|
| `editorconfig-drift` | Dev Config |

Checks that the `.editorconfig` file matches the expected configuration for the project's tech stack. Catches settings that have drifted from best practices.

---

### Code of Conduct

| Slug | Category |
|------|----------|
| `code-of-conduct` | Documentation |

A code of conduct sets behavioral expectations for community interaction. The Contributor Covenant is the most widely adopted standard.

---

### Homepage URL

| Slug | Category |
|------|----------|
| `homepage-url` | Repo Settings |

A homepage URL in the repo settings links to documentation, a project website, or a demo. Helps visitors find more information.

**Fix:** `gh repo edit --homepage "https://your-site.com"`

---

### .gitattributes

| Slug | Category |
|------|----------|
| `gitattributes` | Dev Config |

Controls line ending normalization, diff behavior, and merge strategies per file type. Prevents cross-platform line ending issues.

---

### Version Pinning

| Slug | Category |
|------|----------|
| `version-pinning` | Dev Config |

Checks that dependency versions are pinned (lock files exist). Unpinned dependencies can cause "works on my machine" issues and non-reproducible builds.

---

### Dependency Update Config

| Slug | Category |
|------|----------|
| `dependency-update-config` | Security |

A Dependabot or Renovate configuration file exists. Automated dependency updates keep your project secure and up-to-date without manual effort.

---

### README Table of Contents

| Slug | Category |
|------|----------|
| `readme-toc` | Documentation |

For longer READMEs, a table of contents helps readers navigate to the section they need. Recommended for READMEs with more than 3-4 sections.

---

### README License Mention

| Slug | Category |
|------|----------|
| `readme-license-mention` | Documentation |

The README should mention the license type and link to the LICENSE file. This makes the licensing clear without requiring readers to open a separate file.

---

## INFO Checks (0 pts)

These checks are reported but do not affect the score. They represent optional practices that may not apply to every project.

### Funding

| Slug | Category |
|------|----------|
| `funding` | Documentation |

Checks for a `.github/FUNDING.yml` file. This enables the "Sponsor" button on your repo. Only relevant if you accept sponsorships.

---

### Discussions Enabled

| Slug | Category |
|------|----------|
| `discussions-enabled` | Repo Settings |

Checks if GitHub Discussions is enabled. Useful for community Q&A and RFC-style conversations, but not necessary for every project.

---

### Commit Signoff

| Slug | Category |
|------|----------|
| `commit-signoff` | Repo Settings |

Checks if commit signoff is required. This is a DCO (Developer Certificate of Origin) requirement used by some organizations. Not common for personal projects.
