# Installation

## Prerequisites

GHS requires two tools:

1. **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** — Anthropic's CLI agent that runs the skills
2. **[GitHub CLI (`gh`)](https://cli.github.com/)** — GitHub's official command-line interface for API interactions

## Setup

### 1. Install Claude Code

Follow the [official installation guide](https://docs.anthropic.com/en/docs/claude-code/getting-started):

```bash
npm install -g @anthropic-ai/claude-code
```

Verify the installation:

```bash
claude --version
```

### 2. Install and Authenticate the GitHub CLI

Install `gh` using your package manager:

::: code-group
```bash [macOS]
brew install gh
```

```bash [Linux (Debian/Ubuntu)]
sudo apt install gh
```

```bash [Windows]
winget install GitHub.cli
```
:::

Then authenticate with your GitHub account:

```bash
gh auth login
```

Follow the interactive prompts to authenticate via browser or token. GHS needs at minimum **read access** to scan repositories, and **write access** to create branches, push commits, and open pull requests.

Verify authentication:

```bash
gh auth status
```

### 3. Clone GHS

```bash
git clone https://github.com/Atypical-Consulting/GitHubSkills.git
cd GitHubSkills
```

### 4. Verify

Open Claude Code in the GHS directory:

```bash
claude
```

Skills are auto-discovered from `.claude/skills/`. To confirm everything is working, type:

```
What skills are available?
```

Claude will list all 9 GHS skills with their descriptions and trigger phrases.

## Optional: Python 3

Some skills use Python scripts for score calculation and backlog parsing. Most systems have Python 3 pre-installed. Verify with:

```bash
python3 --version
```

## Next Steps

- [Run your first scan](/getting-started/first-scan) to see GHS in action
- [Learn the core concepts](/getting-started/concepts) behind the health loop and scoring system
