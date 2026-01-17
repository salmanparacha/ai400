# AI400

A skills-based development platform for building AI agents and FastAPI applications using Claude Code.

## Overview

AI400 provides a modular skill system for rapid development of FastAPI applications and AI agents powered by AWS Strands SDK. The platform emphasizes quick project scaffolding, best practices through templates, and extensible architecture.

## Features

- **7 Specialized Skills** for FastAPI development, AI agent building, documentation fetching, and more
- **Project Templates** ranging from minimal starters to production-ready setups
- **GitHub-Synced Skills** with automatic update tracking
- **Modern Python Tooling** using Python 3.14 and `uv` package manager

## Quick Start

### FastAPI Development

```bash
# Navigate to the example project
cd fastapi-hello

# Run development server
fastapi dev main.py

# Run production server
fastapi run main.py
```

### Creating New Projects

```bash
# Create FastAPI project (templates: minimal, crud, microservice, ml)
python .claude/skills/fastapi/scripts/create_project.py <template> <project-name>

# Create AI agent project (templates: minimal, custom-tools, multi-agent, production)
python .claude/skills/strands-agents/scripts/create_project.py <template> <project-name>
```

## Available Skills

1. **fastapi** - FastAPI development from hello world to production
2. **strands-agents** - AWS Strands SDK agent building with multi-agent workflows
3. **fetch-library-docs** - Documentation fetching for 40+ libraries
4. **skill-creator** - Guide for creating effective Claude skills
5. **browsing-with-playwright** - Browser automation via Playwright MCP
6. **skill-updater** - Skill update checker
7. **skill-sources-init** - Skill source initialization

## Technology Stack

- **Python**: 3.14
- **Package Manager**: uv
- **Web Framework**: FastAPI 0.128.0+
- **AI Framework**: AWS Strands SDK
- **Database**: PostgreSQL (in templates)
- **Server**: Uvicorn 0.40.0+

## Project Structure

```
.
├── .claude/              # Claude configuration and skills
│   └── skills/           # Installed skills (7 total)
├── fastapi-hello/        # Example FastAPI application
├── fastapi.skill         # Packaged FastAPI skill
├── skill-updater.skill   # Packaged skill updater
└── skill-sources-init.skill  # Packaged skill initializer
```

## Documentation

For detailed development guidance, refer to [CLAUDE.md](CLAUDE.md) for instructions on working with this codebase.

## Contributing

This repository is in early development. The skill infrastructure is established, and we're building out the project templates and examples.

## License

[Add your license here]
