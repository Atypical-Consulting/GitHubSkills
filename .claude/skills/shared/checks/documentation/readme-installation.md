---
name: README Installation
slug: readme-installation
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# README Installation

## Verification

```bash
README_CONTENT=$(gh api repos/{owner}/{repo}/readme --jq '.content' 2>/dev/null | base64 -d 2>/dev/null)
if [ -z "$README_CONTENT" ]; then
  echo "SKIP: README not found"
  exit 0
fi

# Search for installation-related headings (H1-H4)
INSTALL_HEADING=$(echo "$README_CONTENT" | grep -ciE '^#{1,4}\s.*(install|getting started|setup|quick start|prerequisit)' || true)
echo "Installation headings found: $INSTALL_HEADING"
```

### Pass Condition

At least one heading (H1-H4) matches installation-related keywords: "install", "getting started", "setup", "quick start", or "prerequisit".

### Status Rules

- **PASS**: 1+ installation-related headings found
- **FAIL**: No installation-related headings found
- **SKIP**: README is missing (the Tier 1 `readme` check handles that)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

The README does not contain an installation or getting started section.

### Why It Matters

Without installation instructions, new users are left guessing how to set up and run the project. Clear installation steps reduce friction, lower the barrier to adoption, and prevent support questions. Every successful open source project provides a clear path from "I found this" to "I'm using this."

### Quick Fix

Add an installation section to your README:

```markdown
## Installation

```bash
dotnet add package {package-name}
```
```

### Full Solution

Add a comprehensive getting started section tailored to your tech stack:

**For .NET library projects:**
```markdown
## Getting Started

### Prerequisites

- .NET 8.0 or later

### Installation

Install via NuGet:

```bash
dotnet add package {package-name}
```

Or via the Package Manager Console:

```powershell
Install-Package {package-name}
```
```

**For .NET application projects:**
```markdown
## Getting Started

### Prerequisites

- .NET 8.0 SDK or later
- (any other dependencies)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/{owner}/{repo}.git
   cd {repo}
   ```

2. Build and run:
   ```bash
   dotnet build
   dotnet run
   ```
```

Include prerequisites, package manager commands, and any environment setup needed.

### Acceptance Criteria

- [ ] README contains a heading with installation/setup instructions (e.g., "Installation", "Getting Started", "Setup", "Quick Start")
- [ ] The section includes actionable commands for setting up the project

### References

- https://www.makeareadme.com/#installation
