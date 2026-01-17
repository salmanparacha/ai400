#!/usr/bin/env python3
"""
Strands Agent Project Generator

Creates new Strands agent projects from templates.
"""

import sys
import shutil
import argparse
from pathlib import Path

TEMPLATES = {
    "minimal": "Simple agent with built-in tools",
    "custom-tools": "Agent with custom tool examples",
    "multi-agent": "Sequential workflow with specialized agents",
    "production": "Production-ready with Bedrock, logging, and error handling"
}

def get_template_dir(template_name: str) -> Path:
    """Get the path to a template directory."""
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent
    template_dir = skill_dir / "assets" / template_name

    if not template_dir.exists():
        raise ValueError(f"Template '{template_name}' not found at {template_dir}")

    return template_dir

def create_project(template_name: str, project_name: str, output_dir: Path = None):
    """
    Create a new Strands agent project from a template.

    Args:
        template_name: Name of the template to use
        project_name: Name for the new project
        output_dir: Directory to create the project in (default: current directory)
    """
    if template_name not in TEMPLATES:
        print(f"Error: Unknown template '{template_name}'")
        print(f"\nAvailable templates:")
        for name, desc in TEMPLATES.items():
            print(f"  {name:15} - {desc}")
        sys.exit(1)

    # Get template directory
    template_dir = get_template_dir(template_name)

    # Determine output directory
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)

    # Create project directory
    project_dir = output_dir / project_name

    if project_dir.exists():
        print(f"Error: Directory '{project_dir}' already exists")
        sys.exit(1)

    # Copy template
    print(f"Creating '{template_name}' project: {project_name}")
    print(f"Location: {project_dir}")

    try:
        shutil.copytree(template_dir, project_dir)
        print(f"\n✓ Project created successfully!")

        # Print next steps
        print(f"\nNext steps:")
        print(f"1. cd {project_name}")
        print(f"2. pip install -r requirements.txt")

        if template_name == "production":
            print(f"3. cp .env.example .env")
            print(f"4. Edit .env with your AWS credentials")
            print(f"5. python main.py")
        else:
            print(f"3. python main.py")

        print(f"\n📚 Documentation:")
        print(f"   - Custom tools: See references/custom-tools-patterns.md")
        print(f"   - Multi-agent: See references/multi-agent-patterns.md")
        print(f"   - Model config: See references/model-configuration.md")
        print(f"   - Logging: See references/callback-handlers.md")

    except Exception as e:
        print(f"Error creating project: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Create a new Strands agent project from a template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available templates:
{chr(10).join(f"  {name:15} - {desc}" for name, desc in TEMPLATES.items())}

Examples:
  {sys.argv[0]} minimal my-agent
  {sys.argv[0]} production my-production-agent
  {sys.argv[0]} custom-tools my-tools --output-dir /path/to/projects
        """
    )

    parser.add_argument(
        "template",
        choices=list(TEMPLATES.keys()),
        help="Template to use"
    )

    parser.add_argument(
        "project_name",
        help="Name for the new project"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to create the project in (default: current directory)"
    )

    args = parser.parse_args()

    create_project(args.template, args.project_name, args.output_dir)

if __name__ == "__main__":
    main()
