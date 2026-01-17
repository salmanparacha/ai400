---
name: skill-updater
description: Track and check for updates to external skills from GitHub repositories. Use when user asks to check for skill updates, discover new skills, see if skills are current, or run a full skills check. Replaces manual GitHub browsing by automatically comparing local vs remote skill versions using GitHub MCP.
---

# Skill Updater

Automatically track external skills and check for updates using `.claude/skills/skill-sources.json` and GitHub MCP.

**What it replaces:** Manually checking GitHub repos to see if skills have updates (20 min → 30 sec)

## Operations

### 1. Check for Updates

**When:** User asks "Check for skill updates", "Are my skills up to date?", or similar

**Process:**
1. Read `.claude/skills/skill-sources.json`
2. Filter skills where `source != "local"`
3. For each external skill:
   - Get repo config: `repos[skill.source]` contains `owner`, `repo`, `branch`, `skills_directory`
   - Call GitHub MCP `get_file_contents(owner, repo, path)` to get current file SHA
   - Compare `synced_from_remote_hash` vs current remote SHA
   - Set `update_available = true` if different, `false` if same
   - Update `last_checked`, `last_known_remote_file_hash`
   - Optionally get commit info via `list_commits(owner, repo, path, perPage: 1)` for metadata
4. Update `metadata.last_update_check` with current ISO 8601 timestamp
5. Save updated JSON
6. Generate report (see references/example-output.md)

**GitHub MCP calls:**
```javascript
// Get file SHA
mcp__github__get_file_contents({
  owner: "anthropics",
  repo: "skills",
  path: "skills/skill-creator/SKILL.md"
})
// Returns: [{ sha: "b7f86598...", ... }]
// The 'sha' field is the file blob SHA - use this for comparison

// Get commit metadata (optional, for last updated date)
mcp__github__list_commits({
  owner: "anthropics",
  repo: "skills",
  sha: "main",
  path: "skills/skill-creator/SKILL.md",
  perPage: 1
})
// Returns: [{ sha: "69c0b1a0...", commit: { author: { date: "..." } } }]
```

**Update logic:**
```
if synced_from_remote_hash == null:
  update_available = null  // Never synced
else if synced_from_remote_hash != current_remote_sha:
  update_available = true
else:
  update_available = false
```

**API budget:** N calls (one per external skill)

### 2. Discover New Skills

**When:** User asks "Discover new skills", "What new skills are available?", or similar

**Process:**
1. Read skill-sources.json
2. For each repo in `repos`:
   - Call GitHub MCP `get_file_contents(owner, repo, skills_directory)`
   - Extract directory names (type: "dir") from response
   - Get list of skills you have where `source == repo_key`
   - Find new skills: `remote_skills - your_skills`
3. Update `metadata.last_discovery_check` with current timestamp
4. Save updated JSON
5. Generate report (see references/example-output.md)

**GitHub MCP call:**
```javascript
mcp__github__get_file_contents({
  owner: "panaversity",
  repo: "claude-code-skills-lab",
  path: ".claude/skills"
})
// Returns: [
//   { name: "browsing-with-playwright", type: "dir", ... },
//   { name: "fetch-library-docs", type: "dir", ... }
// ]
// Filter where type == "dir" to get skill folders
```

**API budget:** R calls (one per tracked repo)

### 3. Full Check

**When:** User asks "Full skills check", "Check everything", or similar

**Process:** Execute Operation 1 (Check for Updates), then Operation 2 (Discover New Skills)

**API budget:** N + R calls

## Constraints

1. **Read-only** - Never modify external skill files, only update metadata in skill-sources.json
2. **SHA comparison only** - Don't fetch or diff file contents, just compare file blob SHAs
3. **Local skills ignored** - Skip any skill with `source: "local"` (all hash fields are null)
4. **Preserve JSON structure** - When updating skill-sources.json, maintain all existing fields
5. **ISO 8601 timestamps** - Use format: `new Date().toISOString()` → "2026-01-11T12:30:00Z"

## Error Handling

| Error | Action |
|-------|--------|
| File not found (404) | Set `update_available: "error"`, report as "Source Removed ❓" |
| Network/API failure | Use cached `last_known_remote_file_hash`, report "Check Failed ⚡" |
| Rate limit exceeded | Report partial results, note which skills couldn't be checked |
| Invalid JSON in skill-sources.json | Report error, don't save changes |

## Report Generation

Generate markdown reports using templates in references/example-output.md:

- **Update Check Report**: Shows current/outdated/local skills with summary
- **Discovery Report**: Lists new skills by repository
- **Full Check Report**: Combines both reports

Keep reports concise and actionable. Use icons: ✅ Current, ⚠️ Update Available, 🏠 Local, 🆕 New, ❓ Error, ⚡ Failed

## JSON Schema Reference

```json
{
  "metadata": {
    "schema_version": "2.0",
    "last_update_check": "ISO 8601 datetime",
    "last_discovery_check": "ISO 8601 datetime"
  },
  "repos": {
    "repo_key": {
      "owner": "string",
      "repo": "string",
      "branch": "string",
      "skills_directory": "string"
    }
  },
  "skills": {
    "skill-name": {
      "source": "repo_key | 'local'",
      "path": "string",
      "synced_from_remote_hash": "string | null",
      "synced_at": "ISO 8601 | null",
      "last_checked": "ISO 8601 | null",
      "last_known_remote_file_hash": "string | null",
      "last_known_remote_commit_hash": "string | null",
      "last_known_remote_commit_date": "ISO 8601 | null",
      "update_available": "boolean | null"
    }
  }
}
```

**Key fields:**
- `synced_from_remote_hash`: File SHA when last synced/copied locally
- `last_known_remote_file_hash`: Current remote file SHA (updated each check)
- `update_available`: True if hashes differ, false if same, null for local skills
