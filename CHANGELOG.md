# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Documentation site powered by VitePress
- GitHub issue templates (bug report, feature request, new check proposal)
- Pull request template
- CODEOWNERS file
- CONTRIBUTING.md guide
- CODE_OF_CONDUCT.md (Contributor Covenant)
- SECURITY.md policy
- GitHub Actions workflow for docs deployment to GitHub Pages

## [0.1.0] - 2025-01-01

### Added

- Initial skill collection (9 skills)
  - `ghs-repo-scan` — Repository health scanning with 38 checks
  - `ghs-backlog-board` — Backlog dashboard across audited repos
  - `ghs-backlog-fix` — Parallel worktree-based fix agents
  - `ghs-backlog-score` — Health score calculator
  - `ghs-backlog-next` — Highest-impact recommendation engine
  - `ghs-issue-triage` — Issue labeling with 15-label taxonomy
  - `ghs-issue-analyze` — Deep issue analysis with GitHub comment posting
  - `ghs-issue-implement` — Issue implementation with worktree agents
  - `ghs-merge-prs` — CI-aware PR merging
- 38-check health registry across 7 categories
- Shared configuration: scoring, backlog format, agent contracts
- Backlog storage system with structured markdown
