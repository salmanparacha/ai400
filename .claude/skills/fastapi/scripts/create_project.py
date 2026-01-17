#!/usr/bin/env python3
"""
FastAPI Project Generator
Creates a new FastAPI project from templates.
"""
import argparse
import shutil
from pathlib import Path


def create_project(template: str, project_name: str, output_dir: str = "."):
    """
    Create a new FastAPI project from a template.

    Args:
        template: Template name (minimal, crud, microservice, ml)
        project_name: Name of the project
        output_dir: Output directory (default: current directory)
    """
    # Get the skill directory (parent of scripts/)
    skill_dir = Path(__file__).parent.parent
    template_dir = skill_dir / "assets" / f"{template}-starter" if template == "minimal" else skill_dir / "assets" / f"{template}-api" if template == "crud" or template == "ml" else skill_dir / "assets" / template

    if not template_dir.exists():
        print(f"❌ Template '{template}' not found at {template_dir}")
        return False

    # Create output directory
    output_path = Path(output_dir) / project_name
    if output_path.exists():
        print(f"❌ Directory '{output_path}' already exists")
        return False

    # Copy template
    try:
        shutil.copytree(template_dir, output_path)
        print(f"✅ Created {template} project: {output_path}")
        print(f"\nNext steps:")
        print(f"  cd {project_name}")
        print(f"  pip install -r requirements.txt")
        print(f"  fastapi dev main.py")
        return True
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Create a new FastAPI project")
    parser.add_argument(
        "template",
        choices=["minimal", "crud", "microservice", "ml"],
        help="Template to use"
    )
    parser.add_argument("project_name", help="Name of the project")
    parser.add_argument(
        "--output",
        "-o",
        default=".",
        help="Output directory (default: current directory)"
    )

    args = parser.parse_args()
    create_project(args.template, args.project_name, args.output)


if __name__ == "__main__":
    main()
