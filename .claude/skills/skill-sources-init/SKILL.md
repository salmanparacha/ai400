---
name: skill-sources-init
description: Initialize .claude/skills/skill-sources.json to track external skills from GitHub repositories. Use when user wants to set up skill tracking for the first time, needs to create the skill-sources.json file, or wants to configure which GitHub repos to track for skill updates. This is a one-time setup skill that asks users to classify their local skills and fetches metadata from GitHub MCP.
---

# Skill Sources Initialization

Initialize `.claude/skills/skill-sources.json` through guided setup that asks which GitHub repos to track and how to classify each local skill.

**What it replaces:** Manual JSON creation and figuring out commit hashes (30 min → 2-3 min)

## Pre-conditions & Validation

Before starting, validate:

1. **Check if skill-sources.json exists:**
   ```bash
   ls .claude/skills/skill-sources.json
   ```
   If exists → Error: "skill-sources.json already exists. Delete or rename it first if you want to reinitialize."

2. **Check if .claude/skills/ directory exists:**
   ```bash
   ls .claude/skills/
   ```
   If not exists → Error: "Local skills directory not found at .claude/skills/"

## Workflow

### Step 1: Ask Which Repos to Track

Use AskUserQuestion with multi-select:

```
Question: "Which GitHub repositories contain skills you want to track?"
Header: "Repos to track"
Multi-select: true
Options:
  1. label: "anthropics/skills (Official Anthropic skills)"
     description: "Official skills from Anthropic"

  2. label: "panaversity/claude-code-skills-lab (Community skills)"
     description: "Community-contributed skills"

  3. label: "Other (add custom repository)"
     description: "Add your own GitHub repository"
```

**If "Other" selected:**
- Follow up with text input asking: "Enter GitHub repository in format: owner/repo (e.g., mycompany/custom-skills)"
- Parse input to extract owner and repo
- Validate repo exists using GitHub MCP:
  ```javascript
  mcp__github__get_file_contents({
    owner: "owner",
    repo: "repo",
    path: ""
  })
  ```
  If 404 → Error: "Repository not found. Check owner/repo format."

**Store result:** List of repos selected, e.g., `["anthropics/skills", "panaversity/claude-code-skills-lab"]`

### Step 2: Discover Skills Directories

For each selected repo, find the skills directory:

**Try common paths in order:**
1. `skills/`
2. `.claude/skills/`
3. `claude/skills/`

For each path, call:
```javascript
mcp__github__get_file_contents({
  owner: owner,
  repo: repo,
  path: path
})
```

**If found (returns directory listing):**
- Store: `repos[repo_key].skills_directory = path`
- Continue to next repo

**If none found (all return 404):**
- Ask user with AskUserQuestion:
  ```
  Question: "What is the skills directory path in {owner}/{repo}?"
  Header: "Skills path"
  Options:
    1. label: "skills/"
    2. label: ".claude/skills/"
    3. label: "Other (custom path)"
       description: "Enter custom directory path"
  ```

### Step 3: Discover Remote Skills

For each repo with known `skills_directory`:

Call GitHub MCP:
```javascript
mcp__github__get_file_contents({
  owner: owner,
  repo: repo,
  path: skills_directory
})
```

**Extract skill names:**
- Filter results where `type === "dir"`
- Store: `remote_skills[repo_key] = [skill_names]`

Example result:
```javascript
{
  "anthropic": ["skill-creator", "code-review", "pdf-editor"],
  "panaversity": ["browsing-with-playwright", "fetch-library-docs"]
}
```

### Step 4: Scan Local Skills

**List local skill directories:**
```bash
ls .claude/skills/
```

**For each directory, check if SKILL.md exists:**
```bash
ls .claude/skills/{skill-name}/SKILL.md
```

**Store:** `local_skills = [list of directories with SKILL.md]`

Example: `["browsing-with-playwright", "fetch-library-docs", "skill-creator", "fastapi", "strands-agents"]`

### Step 5: Ask User to Classify Each Local Skill

**Critical: No auto-matching. User explicitly selects source for each skill.**

For EACH local skill, use AskUserQuestion:

```
Question: "Where did '{skill-name}' come from?"
Header: "Skill source"
Options:
  - Show repo options ONLY if skill exists in that repo
  - Always show "Local-only" option
```

**Example for "browsing-with-playwright":**
```
Question: "Where did 'browsing-with-playwright' come from?"
Options:
  1. label: "panaversity/claude-code-skills-lab"
     description: "This skill exists in panaversity/claude-code-skills-lab"
     (only show if "browsing-with-playwright" in remote_skills["panaversity"])

  2. label: "Local-only (I created it myself)"
     description: "This is a custom skill, not from any tracked repo"
```

**Example for "fastapi" (not found in any remote):**
```
Question: "Where did 'fastapi' come from?"
Options:
  1. label: "Local-only (I created it myself)"
     description: "This is a custom skill, not from any tracked repo"
```

**Store result:** `skill_sources[skill_name] = repo_key | "local"`

### Step 6: Fetch Metadata for Remote Skills

For each skill where user selected a remote repo:

**Get file SHA:**
```javascript
mcp__github__get_file_contents({
  owner: repos[repo_key].owner,
  repo: repos[repo_key].repo,
  path: repos[repo_key].skills_directory + skill_name + "/SKILL.md"
})
// Returns: { sha: "b7f86598...", ... }
```

**Get commit metadata:**
```javascript
mcp__github__list_commits({
  owner: repos[repo_key].owner,
  repo: repos[repo_key].repo,
  sha: repos[repo_key].branch,
  path: repos[repo_key].skills_directory + skill_name + "/SKILL.md",
  perPage: 1
})
// Returns: [{ sha: "69c0b1a0...", commit: { author: { date: "..." } } }]
```

**Populate skill entry:**
```json
{
  "source": "repo_key",
  "path": "skills_directory/skill-name/SKILL.md",
  "synced_from_remote_hash": "current_file_sha",
  "synced_at": "current_timestamp",
  "last_checked": "current_timestamp",
  "last_known_remote_file_hash": "current_file_sha",
  "last_known_remote_commit_hash": "commit_sha",
  "last_known_remote_commit_date": "commit_date",
  "update_available": false
}
```

**For local-only skills:**
```json
{
  "source": "local",
  "path": null,
  "synced_from_remote_hash": null,
  "synced_at": null,
  "last_checked": null,
  "last_known_remote_file_hash": null,
  "last_known_remote_commit_hash": null,
  "last_known_remote_commit_date": null,
  "update_available": null
}
```

### Step 7: Generate skill-sources.json

Create complete JSON structure (see references/schema-example.md for format):

```json
{
  "metadata": {
    "schema_version": "2.0",
    "last_update_check": "current_timestamp",
    "last_discovery_check": "current_timestamp"
  },
  "repos": {
    "anthropic": {
      "owner": "anthropics",
      "repo": "skills",
      "branch": "main",
      "skills_directory": "skills/"
    },
    ...
  },
  "skills": {
    "skill-name": { ... },
    ...
  }
}
```

**Write to file:**
```
.claude/skills/skill-sources.json
```

Use proper JSON formatting with 2-space indentation.

### Step 8: Success Report

Generate markdown report:

```markdown
✅ Skill Sources Initialized

## Repositories Tracked
- anthropics/skills (skills/)
- panaversity/claude-code-skills-lab (.claude/skills/)

## Skills Registered

### From anthropics/skills
✓ skill-creator
  - Synced from: b7f86598...
  - Last commit: Dec 20, 2025

### From panaversity/claude-code-skills-lab
✓ browsing-with-playwright
  - Synced from: 92f9249c...
  - Last commit: Jan 4, 2026

### Local-Only Skills
✓ fastapi
✓ strands-agents

---

**Total:** 5 skills registered (3 remote, 2 local)
**File created:** .claude/skills/skill-sources.json

**Next steps:**
- Run "Check for skill updates" to verify tracking
```

## Error Handling

| Error | Action |
|-------|--------|
| skill-sources.json exists | Error: "File already exists. Delete first to reinitialize." |
| .claude/skills/ not found | Error: "Local skills directory not found." |
| Invalid repo format | Prompt again: "Use format: owner/repo" |
| Repo not found (404) | Error: "Repository not found. Check owner/repo." |
| Skills directory not found | Ask user for correct path |
| Network/API failure | Report error, suggest retry |

## Repo Key Generation

For repo keys in JSON:
- `anthropics/skills` → `"anthropic"`
- `panaversity/claude-code-skills-lab` → `"panaversity"`
- Custom repos → use owner name or ask user for short key

## Timestamps

Use ISO 8601 format: `new Date().toISOString()` → "2026-01-11T13:15:00Z"

## API Budget

Typical setup (2 repos, 3 remote skills):
- Validate repos: 2 calls
- Discover skills directories: 2-4 calls
- List remote skills: 2 calls
- Get file SHA for 3 skills: 3 calls
- Get commit metadata for 3 skills: 3 calls
- **Total: 12-14 API calls** (one-time)
