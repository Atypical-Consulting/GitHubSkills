---
name: README Usage Examples
slug: readme-usage
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# README Usage Examples

## Verification

```bash
README_CONTENT=$(gh api repos/{owner}/{repo}/readme --jq '.content' 2>/dev/null | base64 -d 2>/dev/null)
if [ -z "$README_CONTENT" ]; then
  echo "SKIP: README not found"
  exit 0
fi

# Count triple-backtick lines (each fenced block has an opening and closing line)
BACKTICK_LINES=$(echo "$README_CONTENT" | grep -c '^\s*```' || true)
echo "Backtick fence lines found: $BACKTICK_LINES"
```

### Pass Condition

2 or more backtick fence lines found (indicating at least 1 complete fenced code block).

### Status Rules

- **PASS**: 2+ backtick fence lines found (at least 1 code block)
- **FAIL**: Fewer than 2 backtick fence lines
- **SKIP**: README is missing (the Tier 1 `readme` check handles that)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

The README does not contain any fenced code blocks showing usage examples.

### Why It Matters

Code examples are the fastest way for developers to understand how to use a project. Without them, users must read source code or tests to figure out the API. Projects with clear code examples in the README see significantly higher adoption because developers can copy-paste and start experimenting immediately.

### Quick Fix

Add at least one usage example to your README:

```markdown
## Usage

```csharp
var result = MyLibrary.DoSomething("input");
Console.WriteLine(result);
```
```

### Full Solution

Add a dedicated Usage section with multiple code examples showing common use cases:

```markdown
## Usage

### Basic Example

```csharp
// Show the simplest possible usage
var widget = new Widget("example");
var result = widget.Process();
```

### Advanced Example

```csharp
// Show a more realistic use case
var builder = new WidgetBuilder()
    .WithOption("key", "value")
    .WithLogging(true);

var widget = builder.Build();
await widget.RunAsync();
```
```

Tips for good code examples:
- Start with the simplest possible example
- Show real, working code (not pseudocode)
- Include comments explaining key steps
- Cover the most common use cases
- Use the language's idioms and conventions

### Acceptance Criteria

- [ ] README contains at least one fenced code block (triple-backtick block)
- [ ] Code examples demonstrate actual usage of the project

### References

- https://www.makeareadme.com/#usage
