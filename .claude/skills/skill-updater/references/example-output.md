# Example Output Formats

## Update Check Report

```markdown
# Skills Update Check
**Checked:** January 11, 2026 at 12:30 PM

## Summary
✅ Current: 3 | ⚠️ Updates Available: 2 | 🏠 Local: 2

---

## ⚠️ Updates Available

| Skill | Source | Last Synced | Remote Updated |
|-------|--------|-------------|----------------|
| skill-creator | anthropic | Dec 15, 2025 | Dec 20, 2025 |
| fetch-library-docs | panaversity | Jan 1, 2026 | Jan 4, 2026 |

---

## ✅ Current

- browsing-with-playwright (panaversity)

---

## 🏠 Local Skills (Not Checked)

- fastapi
- strands-agents
```

## Discovery Report

```markdown
# New Skills Discovery
**Checked:** January 11, 2026 at 12:30 PM

## 🆕 New Skills Available

### anthropics/skills
- code-review
- testing-patterns

### panaversity/claude-code-skills-lab
- interview-prep

---

**Summary:** 3 new skills found across 2 repositories
```

## Full Check Report

```markdown
# Skills Full Check
**Date:** January 11, 2026

## Part 1: Update Status

[Include Update Check Report here]

---

## Part 2: New Skills

[Include Discovery Report here]
```
