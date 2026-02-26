#!/usr/bin/env python3
"""Parse a backlog item markdown file and output structured JSON.

Supports two formats:
  - Health items: files matching tier-*--*.md
  - Issue items:  files matching issue-*--*.md

Usage:
  python parse_backlog_item.py <path-to-backlog-item.md>
  python parse_backlog_item.py --help
"""

import json
import os
import re
import sys


def print_help():
    print(__doc__.strip())
    print()
    print("Arguments:")
    print("  <path>    Path to a backlog item markdown file")
    print("  --help    Show this help message")


def parse_metadata_table(text):
    """Extract key-value pairs from a markdown metadata table.

    Expects rows like: | **Field** | Value |
    """
    metadata = {}
    for match in re.finditer(
        r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|", text, re.MULTILINE
    ):
        key = match.group(1).strip()
        value = match.group(2).strip()
        # Strip backticks from values like `phmatray/NewSLN`
        value = value.strip("`")
        metadata[key] = value
    return metadata


def extract_h1(text):
    """Extract the first H1 title."""
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_section(text, heading):
    """Extract content under a specific H2 heading, up to the next H2 or end."""
    pattern = r"^##\s+" + re.escape(heading) + r"\s*\n(.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def extract_quick_fix(text):
    """Extract the first code block under ### Quick Fix."""
    # Find the Quick Fix subsection first
    pattern = r"###\s+Quick Fix\s*\n(.*?)(?=^###\s+|^##\s+|\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if not match:
        return ""
    section = match.group(1)
    # Extract the first fenced code block
    code_match = re.search(r"```\w*\n(.*?)```", section, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()
    return ""


def parse_acceptance_criteria(text):
    """Parse checkbox lines from the Acceptance Criteria section."""
    section = extract_section(text, "Acceptance Criteria")
    if not section:
        return []
    criteria = []
    for match in re.finditer(r"^-\s+\[[ xX]\]\s+(.+)$", section, re.MULTILINE):
        criteria.append(match.group(1).strip())
    return criteria


def parse_labels(value):
    """Parse labels from a metadata value. Returns a list."""
    if not value or value.lower() == "none":
        return []
    # Handle comma-separated labels, possibly with backticks
    labels = [lbl.strip().strip("`") for lbl in value.split(",")]
    return [lbl for lbl in labels if lbl]


def parse_tier(value):
    """Parse tier number and label from a value like '1 — Required'."""
    match = re.match(r"(\d+)\s*[—\-]+\s*(.+)", value)
    if match:
        return int(match.group(1)), match.group(2).strip()
    # Try just a number
    try:
        return int(value.strip()), ""
    except (ValueError, TypeError):
        return 0, ""


def detect_file_type(filepath):
    """Detect whether this is a health item or issue item based on filename."""
    basename = os.path.basename(filepath)
    if re.match(r"tier-\d+--", basename):
        return "health"
    if re.match(r"issue-\d+--", basename):
        return "issue"
    return "unknown"


def parse_health_item(filepath, text):
    """Parse a health-type backlog item."""
    metadata = parse_metadata_table(text)
    title = extract_h1(text)
    tier_num, tier_label = parse_tier(metadata.get("Tier", ""))

    # Parse optional sync metadata (added by ghs-backlog-sync)
    synced_issue_raw = metadata.get("Synced Issue", "")
    synced_issue = None
    if synced_issue_raw:
        num_match = re.search(r"#?(\d+)", synced_issue_raw)
        if num_match:
            synced_issue = int(num_match.group(1))

    issue_url = metadata.get("Issue URL", "") or None

    result = {
        "type": "health",
        "title": title,
        "repository": metadata.get("Repository", ""),
        "source": metadata.get("Source", "Health Check"),
        "tier": tier_num,
        "tier_label": tier_label,
        "points": int(metadata.get("Points", "0")),
        "status": metadata.get("Status", ""),
        "detected": metadata.get("Detected", ""),
        "whats_missing": extract_section(text, "What's Missing"),
        "quick_fix": extract_quick_fix(text),
        "acceptance_criteria": parse_acceptance_criteria(text),
        "synced_issue": synced_issue,
        "issue_url": issue_url,
    }
    return result


def parse_issue_item(filepath, text):
    """Parse an issue-type backlog item."""
    metadata = parse_metadata_table(text)
    title = extract_h1(text)

    # Extract issue number from Source field like "Issue #42"
    issue_number = 0
    source = metadata.get("Source", "")
    num_match = re.search(r"#(\d+)", source)
    if num_match:
        issue_number = int(num_match.group(1))

    # Extract assignee, handle "unassigned"
    assignee = metadata.get("Assignee", "")
    if assignee.lower() in ("unassigned", "none", ""):
        assignee = None

    # Extract labels
    labels = parse_labels(metadata.get("Labels", ""))

    # Extract GitHub URL from References section
    github_url = ""
    refs_section = extract_section(text, "References")
    if refs_section:
        url_match = re.search(
            r"https://github\.com/[^\s)]+/issues/\d+", refs_section
        )
        if url_match:
            github_url = url_match.group(0)
    # Fallback: try the whole document
    if not github_url:
        url_match = re.search(
            r"https://github\.com/[^\s)]+/issues/\d+", text
        )
        if url_match:
            github_url = url_match.group(0)

    result = {
        "type": "issue",
        "title": title,
        "repository": metadata.get("Repository", ""),
        "source": source,
        "issue_number": issue_number,
        "labels": labels,
        "assignee": assignee,
        "status": metadata.get("Status", ""),
        "created": metadata.get("Created", ""),
        "updated": metadata.get("Updated", ""),
        "description": extract_section(text, "Description"),
        "github_url": github_url,
    }
    return result


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print_help()
        sys.exit(0 if "--help" in sys.argv or "-h" in sys.argv else 1)

    filepath = sys.argv[1]

    if not os.path.isfile(filepath):
        print("Error: File not found: {}".format(filepath), file=sys.stderr)
        sys.exit(1)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except IOError as e:
        print("Error: Could not read file: {}".format(e), file=sys.stderr)
        sys.exit(1)

    file_type = detect_file_type(filepath)

    if file_type == "health":
        result = parse_health_item(filepath, text)
    elif file_type == "issue":
        result = parse_issue_item(filepath, text)
    else:
        # Try to detect from content: if it has a Tier field, treat as health
        metadata = parse_metadata_table(text)
        if "Tier" in metadata:
            result = parse_health_item(filepath, text)
        elif "Labels" in metadata or re.search(r"Issue\s+#\d+", text):
            result = parse_issue_item(filepath, text)
        else:
            print(
                "Error: Cannot determine item type from filename '{}'. "
                "Expected tier-*--*.md or issue-*--*.md".format(
                    os.path.basename(filepath)
                ),
                file=sys.stderr,
            )
            sys.exit(1)

    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    print()  # trailing newline


if __name__ == "__main__":
    main()
