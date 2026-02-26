# Contributing to GitHubSkills

Welcome, and thank you for your interest in contributing to GHS! Whether you are fixing a typo, improving an existing check, or building an entirely new skill, your help is appreciated.

## Ways to Contribute

There are three main contribution paths:

1. **Fix docs** — Improve README, skill descriptions, or inline comments.
2. **Improve a check** — Make an existing health check more accurate or add better remediation guidance.
3. **Add a new skill** — Build a brand-new GHS skill that solves a real problem for repo maintainers.

## Development Setup

1. **Clone** the repository:
   ```bash
   git clone https://github.com/Atypical-Consulting/GitHubSkills.git
   cd GitHubSkills
   ```

2. **Ensure the `gh` CLI is installed and authenticated:**
   ```bash
   gh auth status
   ```

3. **Open the project in Claude Code** — skills are loaded automatically.

## How to Add a New Health Check

1. Create a new file in `.claude/skills/shared/checks/{category}/` following the naming and format of existing checks.
2. Register the check in the category index file (`index.md`).
3. Test by running `ghs-repo-scan` against a sample repository and verifying the check appears in the report.

## How to Add a New Skill

1. Create a directory `.claude/skills/ghs-{name}/` with a `SKILL.md` file inside.
2. Follow the frontmatter format used by existing skills. Required fields:
   - `name` — Must use the `ghs-` prefix with kebab-case.
   - `description` — Include natural-language trigger phrases so Claude Code can discover the skill.
   - `allowed-tools` — List the tools the skill needs.
   - `compatibility` — Specify compatible platforms.
3. Define the skill's Prerequisites, Input, Steps, and Output Format.
4. Update the "Available Skills" list in `CLAUDE.md`.

## Naming Conventions

- Skill names use the `ghs-` prefix: `ghs-repo-scan`, `ghs-backlog-fix`, etc.
- Use `kebab-case` for all identifiers.
- Include trigger phrases in the skill description so Claude Code can match user intent.

## PR Guidelines

- **One logical change per PR.** Keep PRs focused and reviewable.
- **Descriptive title.** Summarize what the PR does in the title (e.g., "Add CODEOWNERS health check").
- **Test your changes.** Run the relevant skill against at least one repository before opening a PR.
- **Follow the conventions** described in `CLAUDE.md`.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold its terms.
