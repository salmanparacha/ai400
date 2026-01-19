# AI400 Project Instructions

## Environment Details
- **Primary OS**: Linux (WSL Ubuntu-22.04)
- **Host OS**: Windows
- **Python Version**: 3.14
- **Package Manager**: `uv`
- **Shell Rule**: ALWAYS execute commands via WSL Ubuntu-22.04.
  - **Correct Pattern**: `wsl -d Ubuntu-22.04 bash -c "your-command"`
  - **Incorrect Pattern**: Running commands directly in PowerShell.

## Build & Test Commands
- **Install Dependencies**: `wsl -d Ubuntu-22.04 bash -c "uv sync"`
- **Run FastAPI (Dev)**: `wsl -d Ubuntu-22.04 bash -c "cd fastapi-hello && uv run fastapi dev main.py"`
- **Create Project**: `wsl -d Ubuntu-22.04 bash -c "python3 .claude/skills/fastapi/scripts/create_project.py ..."`

## Code Style & Guidelines
- Follow the modular skill structure in `.claude/skills/`.
- Ensure all new files are created with appropriate permissions for the `sparacha` user in WSL.
- Use absolute paths in tools, but relative paths in terminal commands executed via WSL.