#!/usr/bin/env python3
"""Create a new Strands agent project from templates.

Usage:
    python create_project.py <project_name> [--template minimal|custom-tools|multi-agent|production]
"""

import argparse
import shutil
from pathlib import Path


TEMPLATES = ["minimal", "custom-tools", "multi-agent", "production"]
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR.parent / "assets"


def create_project(project_name: str, template: str = "minimal") -> Path:
    """Create a new project from template.

    Args:
        project_name: Name of the project directory to create
        template: Template to use (minimal, custom-tools, multi-agent, production)

    Returns:
        Path to created project
    """
    if template not in TEMPLATES:
        raise ValueError(f"Template must be one of: {TEMPLATES}")

    template_dir = ASSETS_DIR / template
    if not template_dir.exists():
        raise FileNotFoundError(f"Template not found: {template_dir}")

    project_dir = Path.cwd() / project_name

    if project_dir.exists():
        raise FileExistsError(f"Directory already exists: {project_dir}")

    # Copy template
    shutil.copytree(template_dir, project_dir)

    print(f"Created project: {project_dir}")
    print(f"Template: {template}")
    print()
    print("Next steps:")
    print(f"  cd {project_name}")
    print(f"  pip install -r requirements.txt")
    print(f"  python main.py")

    return project_dir


def main():
    parser = argparse.ArgumentParser(
        description="Create a new Strands agent project"
    )
    parser.add_argument(
        "project_name",
        help="Name of the project directory"
    )
    parser.add_argument(
        "--template", "-t",
        choices=TEMPLATES,
        default="minimal",
        help="Project template to use (default: minimal)"
    )

    args = parser.parse_args()
    create_project(args.project_name, args.template)


if __name__ == "__main__":
    main()
