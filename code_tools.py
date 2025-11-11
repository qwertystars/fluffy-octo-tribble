"""
Code Generation Tools
Provides high-level tools for code generation, project structure creation, etc.
"""

import os
import json
from typing import List
from langchain_core.tools import tool


@tool
def generate_code(description: str, language: str = "python", file_path: str = None) -> str:
    """Generate code from a natural language description.

    This tool signals your intent to generate code. After calling this,
    you MUST use write_file to actually write the generated code to disk.

    Args:
        description: Natural language description of the code to generate
        language: Programming language (default: python)
        file_path: Optional suggested file path for the code

    Returns:
        Acknowledgment message
    """
    result = f"Code generation requested:\n"
    result += f"  • Description: {description}\n"
    result += f"  • Language: {language}\n"
    if file_path:
        result += f"  • Suggested path: {file_path}\n"
    result += f"\n⚠️  Remember to use write_file tool to save the generated code!"
    return result


@tool
def create_project_structure(project_name: str, structure: str) -> str:
    """Create a complete project structure with multiple files and directories.

    Args:
        project_name: Name of the project (will be the root directory)
        structure: JSON string describing the project structure.
                  Format: {"file.txt": "content", "dir/": {"nested.py": "content"}}

    Returns:
        Summary of created files and directories

    Example structure:
    {
        "README.md": "# My Project\\nDescription here",
        "src/": {
            "main.py": "def main():\\n    pass",
            "utils.py": "# Utilities"
        },
        "tests/": {
            "test_main.py": "# Tests"
        }
    }
    """
    try:
        # Parse the structure
        structure_data = json.loads(structure)

        # Get output directory
        output_dir = os.getenv("OUTPUT_DIR", "./generated_code")
        project_path = os.path.join(output_dir, project_name)

        # Track created items
        created_files = []
        created_dirs = []

        def create_item(base_path: str, name: str, content):
            """Recursively create files and directories."""
            item_path = os.path.join(base_path, name)

            if isinstance(content, dict):
                # It's a directory
                os.makedirs(item_path, exist_ok=True)
                created_dirs.append(item_path)

                # Process children
                for child_name, child_content in content.items():
                    create_item(item_path, child_name, child_content)

            elif name.endswith('/'):
                # Empty directory
                dir_path = item_path.rstrip('/')
                os.makedirs(dir_path, exist_ok=True)
                created_dirs.append(dir_path)

            else:
                # It's a file
                os.makedirs(os.path.dirname(item_path), exist_ok=True)
                with open(item_path, 'w', encoding='utf-8') as f:
                    f.write(str(content))
                created_files.append(item_path)

        # Create the project structure
        os.makedirs(project_path, exist_ok=True)
        for item_name, item_content in structure_data.items():
            create_item(project_path, item_name, item_content)

        # Build result message
        result = [f"✓ Created project '{project_name}' at {project_path}\n"]
        result.append(f"📁 Directories: {len(created_dirs)}")
        for dir_path in created_dirs:
            result.append(f"  • {os.path.relpath(dir_path, output_dir)}/")

        result.append(f"\n📄 Files: {len(created_files)}")
        for file_path in created_files:
            size = os.path.getsize(file_path)
            result.append(f"  • {os.path.relpath(file_path, output_dir)} ({size} bytes)")

        return "\n".join(result)

    except json.JSONDecodeError as e:
        return f"✗ Error: Invalid JSON structure: {str(e)}"
    except Exception as e:
        return f"✗ Error creating project structure: {str(e)}"


@tool
def analyze_code(file_path: str) -> str:
    """Analyze existing code and provide the content for review.

    Use this tool to read and analyze code that already exists.
    The code content will be returned for your analysis.

    Args:
        file_path: Path to the code file to analyze

    Returns:
        Code content for analysis
    """
    try:
        # Get the output directory from environment
        output_dir = os.getenv("OUTPUT_DIR", "./generated_code")

        # If path is not absolute, make it relative to output_dir
        if not os.path.isabs(file_path):
            file_path = file_path.lstrip("./")
            file_path = os.path.join(output_dir, file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        result = f"Code from {file_path}:\n"
        result += "=" * 50 + "\n"
        result += content
        result += "\n" + "=" * 50
        result += "\n\nPlease analyze this code and provide suggestions."

        return result

    except FileNotFoundError:
        return f"✗ Error: File not found: {file_path}"
    except Exception as e:
        return f"✗ Error analyzing code: {str(e)}"


@tool
def generate_tests(file_path: str, framework: str = "pytest") -> str:
    """Generate test cases for existing code.

    Args:
        file_path: Path to the code file to generate tests for
        framework: Testing framework to use (default: pytest)

    Returns:
        Acknowledgment and suggested test file path
    """
    try:
        # Determine test file path
        output_dir = os.getenv("OUTPUT_DIR", "./generated_code")

        if not os.path.isabs(file_path):
            file_path = file_path.lstrip("./")
            full_path = os.path.join(output_dir, file_path)
        else:
            full_path = file_path

        # Read the source file
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Suggest test file path
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        test_file = f"test_{base_name}"

        if dir_name:
            test_path = os.path.join(dir_name, "tests", test_file)
        else:
            test_path = os.path.join("tests", test_file)

        result = f"Test generation requested:\n"
        result += f"  • Source file: {file_path}\n"
        result += f"  • Framework: {framework}\n"
        result += f"  • Suggested test path: {test_path}\n\n"
        result += f"Source code to test:\n"
        result += "=" * 50 + "\n"
        result += content
        result += "\n" + "=" * 50
        result += f"\n\n⚠️  Remember to use write_file tool to save the generated tests to {test_path}!"

        return result

    except FileNotFoundError:
        return f"✗ Error: File not found: {file_path}"
    except Exception as e:
        return f"✗ Error preparing test generation: {str(e)}"


def get_code_tools() -> List:
    """Returns a list of all code generation tools."""
    return [
        generate_code,
        create_project_structure,
        analyze_code,
        generate_tests
    ]
