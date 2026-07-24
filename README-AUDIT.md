# README Audit — Atypical-Consulting Repositories

Per-repo gap analysis against the [standardized README template](README-TEMPLATE.md).

## Section Reference — When to Include What

| Section | Required? | When to include |
|---------|-----------|-----------------|
| Badges (Row 1-2) | Always | Every repo |
| Badges (Row 3 — Build/Coverage) | Always | Every repo with CI |
| Badges (Row 4 — Distribution) | Optional | Only if published to NuGet/npm/Docker |
| Screenshot/Hero image | Optional | GUI apps, web apps, CLI tools with visual output |
| The Problem / The Solution | Always | Every repo — forces clarity of purpose |
| Features checklist | Always | Every repo |
| Tech Stack table | Optional | Polyglot or multi-layer projects |
| Getting Started (multi-path) | Always | At minimum: package manager + source |
| Usage with code examples | Always | Every repo — show, don't tell |
| Architecture diagram | Recommended | Projects with 3+ modules or layers |
| Project Structure tree | Recommended | Projects with non-obvious directory layout |
| Roadmap | Recommended | Active projects seeking contributors |
| Stats (RepoBeats) | Optional | Projects with meaningful activity |
| Contributing | Always | Every repo |
| License | Always | Every repo |
| "Built by Atypical" footer | Always | Brand consistency |
| Contributors image | Optional | Projects with multiple contributors |

---

## Priority 1 — Flagship Repos (fix first)

### VirtualFileSystem (41 stars)

| Section | Status | Action |
|---------|--------|--------|
| Badges | HAS (excellent) | Keep as-is |
| Problem/Solution | MISSING | Add "The Problem" section about testing filesystem code |
| TOC | HAS | Keep |
| Features checklist | HAS (excellent) | Keep |
| Tech Stack table | MISSING | Add (.NET 8, C# 12) |
| Getting Started | HAS (NuGet + source) | Keep |
| Usage + code example | HAS (excellent) | Keep |
| Architecture | MISSING | Add ASCII diagram of VFS core |
| Project Structure | MISSING | Add tree |
| Roadmap | PARTIAL (in features list) | Extract to dedicated section |
| Stats | MISSING | Add RepoBeats |
| Contributing | HAS | Keep |
| License | HAS | Keep |
| Branding footer | MISSING | Add "Built by Atypical" |

### BlazorMVU (13 stars)

| Section | Status | Action |
|---------|--------|--------|
| Badges | HAS (excellent) | Keep |
| Problem/Solution | HAS (as "Motivation") | Rename to Problem/Solution for consistency |
| TOC | HAS | Keep |
| Features | HAS (categorized) | Keep |
| Tech Stack table | MISSING | Add (.NET 10, Blazor, C#) |
| Getting Started | HAS (source only) | Add NuGet install once published |
| Usage | HAS (excellent, progressive) | Keep |
| Architecture | MISSING | Add MVU data flow diagram |
| Project Structure | MISSING | Add tree |
| Roadmap | HAS | Keep |
| Stats | HAS (RepoBeats) | Keep |
| Contributing | HAS | Keep |
| License | HAS | Keep |
| Branding footer | MISSING | Add |

### SalesPitch (8 stars)

| Section | Status | Action |
|---------|--------|--------|
| Badges | MISSING | Add full badge wall |
| Problem/Solution | MISSING | Add — "Writing sales pitches is time-consuming..." |
| TOC | MISSING | Add |
| Features | HAS | Keep |
| Tech Stack table | MISSING | Add (.NET 9, OpenAI GPT-4, Spectre.Console) |
| Getting Started | HAS | Keep |
| Usage | HAS (basic) | Add screenshot of output |
| Architecture | MISSING | Add (simple — CLI → OpenAI API) |
| Project Structure | MISSING | Add tree |
| Roadmap | MISSING | Add |
| Stats | HAS (RepoBeats) | Keep |
| Contributing | MINIMAL | Expand with conventional commits |
| License | HAS | Keep |
| Branding footer | MISSING | Add |

### ts-blockchain (5 stars)

| Section | Status | Action |
|---------|--------|--------|
| Badges | PARTIAL (version/license) | Add build, stars, forks, issues |
| Problem/Solution | MISSING | Add — "Understanding blockchain is hard without building one" |
| TOC | MISSING | Add |
| Features | HAS (brief) | Expand with checklist format |
| Tech Stack table | MISSING | Add (Node.js, Express, TypeScript) |
| Getting Started | MISSING | Add clone + install + run |
| Usage | HAS (endpoints) | Add curl examples |
| Architecture | MISSING | Add P2P node diagram |
| Project Structure | MISSING | Add |
| Roadmap | HAS ("road to v1") | Reformat with checkboxes |
| Contributing | MISSING | Add |
| License | INLINE | Move to LICENSE file, link |
| Branding footer | MISSING | Add |

---

## Priority 2 — Active Repos

### TenantKit (0 stars, excellent README)

| Section | Status | Action |
|---------|--------|--------|
| Badges | HAS | Keep |
| Problem/Solution | HAS (best-in-class) | Keep |
| TOC | MISSING | Add |
| Features | IMPLICIT in resolvers | Add explicit checklist |
| Tech Stack table | MISSING | Add (.NET 10, ASP.NET Core) |
| Getting Started | HAS (excellent) | Keep |
| Usage | HAS (excellent) | Keep |
| Architecture | HAS (ASCII) | Keep |
| Project Structure | HAS | Keep |
| Roadmap | HAS | Keep |
| Stats | MISSING | Add RepoBeats |
| Contributing | MINIMAL | Expand |
| License | HAS | Keep |
| Branding footer | HAS ("Why Atypical") | Standardize wording |

### RoselineMCP (1 star)

| Section | Status | Action |
|---------|--------|--------|
| Badges | HAS | Keep |
| Problem/Solution | MISSING | Add — "C# codebases accumulate quality issues..." |
| TOC | MISSING | Add |
| Features | HAS | Keep |
| Tech Stack table | MISSING | Add (.NET 10, Roslyn, Roslynator) |
| Getting Started | HAS (excellent, 3 paths) | Keep |
| Usage | HAS (tool API docs) | Keep |
| Architecture | MISSING | Add (MCP server ↔ Roslyn pipeline) |
| Project Structure | HAS | Keep |
| Roadmap | MISSING | Add |
| Stats | MISSING | Add RepoBeats |
| Contributing | HAS | Keep |
| License | HAS | Keep |
| Branding footer | MISSING | Add |

### FlowForge (1 star)

| Section | Status | Action |
|---------|--------|--------|
| Badges | MISSING | Add full badge wall |
| Problem/Solution | MISSING | Add — "Git GUIs treat Gitflow as an afterthought..." |
| TOC | MISSING | Add |
| Features | HAS (excellent) | Keep |
| Tech Stack table | HAS (as list) | Convert to table format |
| Getting Started | HAS (release + source) | Keep |
| Usage | MISSING | Add screenshot walkthrough |
| Architecture | MISSING | Add (Tauri/React/Rust layers) |
| Project Structure | HAS | Keep |
| Roadmap | MISSING | Add |
| Stats | MISSING | Add RepoBeats |
| Contributing | HAS (with conventional commits) | Keep |
| License | HAS | Keep |
| Branding footer | MISSING | Add |

### RogueRust / Yendor (0 stars)

| Section | Status | Action |
|---------|--------|--------|
| Badges | MISSING | Add full badge wall |
| Problem/Solution | MISSING | Add — "Classic Rogue deserves a modern native port" |
| TOC | MISSING | Add |
| Features | HAS | Keep |
| Tech Stack table | HAS (excellent) | Keep |
| Getting Started | HAS | Keep |
| Usage | HAS (controls table) | Keep |
| Architecture | HAS (tree + data flow) | Keep |
| Project Structure | IMPLICIT in architecture | Already covered |
| Roadmap | MISSING | Add |
| Stats | MISSING | Add RepoBeats |
| Contributing | MISSING | Add |
| License | HAS | Keep |
| Branding footer | MISSING | Add |

### GitHubSkills (1 star)

| Section | Status | Action |
|---------|--------|--------|
| Badges | PARTIAL (license, health) | Add build, stars, forks |
| Problem/Solution | MISSING | Add — "Managing repo quality at scale is tedious..." |
| TOC | HAS | Keep |
| Features | HAS (as skill tables) | Keep |
| Tech Stack table | MISSING | Add (Claude Code, gh CLI, Python) |
| Getting Started | HAS | Keep |
| Usage | MISSING | Add example session / screenshot |
| Architecture | HAS (mermaid diagrams) | Keep |
| Roadmap | MISSING | Add |
| Stats | MISSING | Add RepoBeats |
| Contributing | MISSING | Add |
| License | HAS | Keep |
| Branding footer | MISSING | Add |

### docker-claude (0 stars)

| Section | Status | Action |
|---------|--------|--------|
| Badges | MISSING | Add (Docker, license, build) |
| Problem/Solution | MISSING | Add — "Running Claude Code requires local setup..." |
| TOC | MISSING | Add |
| Features | HAS (brief) | Expand to checklist |
| Tech Stack table | MISSING | Add (Python 3.10, Node.js, Docker) |
| Getting Started | HAS (3 paths) | Keep |
| Usage | HAS | Keep |
| Architecture | MISSING | Not needed (simple Dockerfile) |
| Project Structure | MISSING | Not needed |
| Roadmap | MISSING | Add |
| Stats | MISSING | Add |
| Contributing | MISSING | Add |
| License | MISSING | Add |
| Branding footer | MISSING | Add |

### ninjadog (1 star)

| Section | Status | Action |
|---------|--------|--------|
| Badges | MISSING | Add full badge wall |
| Problem/Solution | HAS ("The Goal") | Reframe as Problem/Solution |
| TOC | HAS | Keep |
| Features | HAS (generators list) | Keep |
| Tech Stack table | MISSING | Add (.NET 8, Source Generators) |
| Getting Started | PARTIAL ("How to start") | Expand with full commands |
| Usage | MISSING | Add code example |
| Architecture | MISSING | Add (generator pipeline) |
| Project Structure | MISSING | Add |
| Roadmap | HAS ("road to MVP") | Reformat |
| Stats | MISSING | Add |
| Contributing | MISSING | Add |
| License | MISSING | Add |
| Branding footer | MISSING | Add |

---

## Priority 3 — Lower Activity / Niche Repos

### NinjadogEngine (2 stars)

- Rewrite entirely in English
- Add badges, Getting Started, code examples, project structure
- Currently: badges + French description only

### hexagonal-dotnet (1 star)

- Add badges, Problem/Solution, Getting Started, Usage examples
- Keep architecture image
- Currently: architecture diagram + links only

### YendorSupport (0 stars — support/marketing repo)

- Good as-is for its purpose (support hub)
- Add badges and branding footer

### NFT (2 stars — non-code repo)

- Appropriate for its niche
- Add badges and branding footer

---

## Priority 4 — Minimal Repos (need full rewrite from template)

These repos have empty or single-line READMEs and need a full README written from scratch:

| Repo | Current State |
|------|--------------|
| **FastComponents** | Only `# FastComponents` + one line |
| **CGit** | No README |
| **ludifik** | No README |
| **BlockchainDDD** | No README |
| **WebApiGenerator** | No README |
| **scrumap-dotnet** | Only `# scrumap` |
| **ninjadog-product** | Only a title + one line |

---

## Skip — Not Worth Updating Now

| Repo | Reason |
|------|--------|
| **GitHubAutomate** | Default Tauri template — replace when project matures |
| **atypical-website** | Default CRA template — replace when project matures |
| **efesem** | Copied from another repo — replace when project has its own identity |
| **TReport** | Internal POC, low priority |
| **.github** | Org-level config, different purpose |
