# skill-sources.json Schema & Example

## Complete Schema

```json
{
  "metadata": {
    "schema_version": "2.0",
    "last_update_check": "ISO 8601 datetime string",
    "last_discovery_check": "ISO 8601 datetime string"
  },
  "repos": {
    "repo_key": {
      "owner": "github_username_or_org",
      "repo": "repository_name",
      "branch": "main",
      "skills_directory": "path/to/skills/"
    }
  },
  "skills": {
    "skill-name": {
      "source": "repo_key | 'local'",
      "path": "path/to/skill/SKILL.md | null",
      "synced_from_remote_hash": "file_sha | null",
      "synced_at": "ISO 8601 datetime | null",
      "last_checked": "ISO 8601 datetime | null",
      "last_known_remote_file_hash": "file_sha | null",
      "last_known_remote_commit_hash": "commit_sha | null",
      "last_known_remote_commit_date": "ISO 8601 datetime | null",
      "update_available": "boolean | null"
    }
  }
}
```

## Example with Real Data

```json
{
  "metadata": {
    "schema_version": "2.0",
    "last_update_check": "2026-01-11T13:15:00Z",
    "last_discovery_check": "2026-01-11T13:15:00Z"
  },
  "repos": {
    "anthropic": {
      "owner": "anthropics",
      "repo": "skills",
      "branch": "main",
      "skills_directory": "skills/"
    },
    "panaversity": {
      "owner": "panaversity",
      "repo": "claude-code-skills-lab",
      "branch": "main",
      "skills_directory": ".claude/skills/"
    }
  },
  "skills": {
    "skill-creator": {
      "source": "anthropic",
      "path": "skills/skill-creator/SKILL.md",
      "synced_from_remote_hash": "b7f86598b002c99a6be96026443217b6af3c561d",
      "synced_at": "2026-01-11T13:15:00Z",
      "last_checked": "2026-01-11T13:15:00Z",
      "last_known_remote_file_hash": "b7f86598b002c99a6be96026443217b6af3c561d",
      "last_known_remote_commit_hash": "69c0b1a0674149f27b61b2635f935524b6add202",
      "last_known_remote_commit_date": "2025-12-20T18:09:44Z",
      "update_available": false
    },
    "browsing-with-playwright": {
      "source": "panaversity",
      "path": ".claude/skills/browsing-with-playwright/SKILL.md",
      "synced_from_remote_hash": "92f9249c47c8fca031ca8861f5b30f10cf289ae0",
      "synced_at": "2026-01-11T13:15:00Z",
      "last_checked": "2026-01-11T13:15:00Z",
      "last_known_remote_file_hash": "92f9249c47c8fca031ca8861f5b30f10cf289ae0",
      "last_known_remote_commit_hash": "2fe59436aabece20ea4dc2c91bd9f2211a2dcc3f",
      "last_known_remote_commit_date": "2026-01-04T07:19:14Z",
      "update_available": false
    },
    "fastapi": {
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
  }
}
```

## Field Explanations

### metadata
- `schema_version`: Version of JSON schema (currently "2.0")
- `last_update_check`: Last time update check was run
- `last_discovery_check`: Last time discovery was run

### repos
- `owner`: GitHub username or organization
- `repo`: Repository name
- `branch`: Git branch to track (usually "main")
- `skills_directory`: Path within repo where skills are located

### skills (Remote)
- `source`: Key from repos section
- `path`: Full path to SKILL.md in remote repo
- `synced_from_remote_hash`: File SHA when skill was last synced locally
- `synced_at`: Timestamp when skill was last synced
- `last_checked`: Last time remote was checked for updates
- `last_known_remote_file_hash`: Current remote file SHA
- `last_known_remote_commit_hash`: Latest commit affecting this file
- `last_known_remote_commit_date`: Date of latest commit
- `update_available`: True if remote has changes, false if current

### skills (Local)
- `source`: Always "local"
- All other fields: `null`
