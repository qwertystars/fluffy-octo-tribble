"""
File Operation Tools
Provides tools for file system operations: read, write, list, search, etc.
"""

import os
import glob
from typing import List
from langchain_core.tools import tool


@tool
def write_file(file_path: str, content: str) -> str:
    """Write content to a file. Creates directories if needed.

    **REQUIRED PARAMETERS:**
    - file_path: Path to write to (can be relative or absolute)
    - content: **REQUIRED** - Complete file content as string

    Args:
        file_path: Path where the file should be written
        content: Complete content to write to the file

    Returns:
        Success message with file path and character count
    """
    try:
        # Get the output directory from environment
        output_dir = os.getenv("OUTPUT_DIR", "./generated_code")

        # If path is not absolute, make it relative to output_dir
        if not os.path.isabs(file_path):
            # Remove leading ./ if present
            file_path = file_path.lstrip("./")
            file_path = os.path.join(output_dir, file_path)

        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"✓ Successfully wrote {len(content)} characters to {file_path}"
    except Exception as e:
        return f"✗ Error writing file: {str(e)}"


@tool
def read_file(file_path: str) -> str:
    """Read content from a file.

    Args:
        file_path: Path to the file to read

    Returns:
        File content or error message
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

        return f"Content of {file_path}:\n\n{content}"
    except FileNotFoundError:
        return f"✗ Error: File not found: {file_path}"
    except Exception as e:
        return f"✗ Error reading file: {str(e)}"


@tool
def list_files(directory: str = ".") -> str:
    """List files and directories in the specified directory.

    Args:
        directory: Directory to list (default: current directory)

    Returns:
        Formatted list of files and directories
    """
    try:
        # Get the output directory from environment
        output_dir = os.getenv("OUTPUT_DIR", "./generated_code")

        # If path is not absolute, make it relative to output_dir
        if not os.path.isabs(directory):
            directory = directory.lstrip("./")
            if directory == "" or directory == ".":
                directory = output_dir
            else:
                directory = os.path.join(output_dir, directory)

        items = os.listdir(directory)
        if not items:
            return f"Directory {directory} is empty"

        result = [f"Contents of {directory}:\n"]
        for item in sorted(items):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                result.append(f"📁 {item}/")
            else:
                size = os.path.getsize(item_path)
                result.append(f"📄 {item} ({size} bytes)")

        return "\n".join(result)
    except Exception as e:
        return f"✗ Error listing directory: {str(e)}"


@tool
def create_directory(directory_path: str) -> str:
    """Create a new directory (and parent directories if needed).

    Args:
        directory_path: Path to the directory to create

    Returns:
        Success or error message
    """
    try:
        # Get the output directory from environment
        output_dir = os.getenv("OUTPUT_DIR", "./generated_code")

        # If path is not absolute, make it relative to output_dir
        if not os.path.isabs(directory_path):
            directory_path = directory_path.lstrip("./")
            directory_path = os.path.join(output_dir, directory_path)

        os.makedirs(directory_path, exist_ok=True)
        return f"✓ Successfully created directory: {directory_path}"
    except Exception as e:
        return f"✗ Error creating directory: {str(e)}"


@tool
def search_files(pattern: str, directory: str = ".") -> str:
    """Search for files matching a pattern (supports wildcards like *.py, *.txt).

    Args:
        pattern: File pattern to search for (e.g., "*.py", "test_*.txt")
        directory: Directory to search in (default: current directory)

    Returns:
        List of matching files
    """
    try:
        # Get the output directory from environment
        output_dir = os.getenv("OUTPUT_DIR", "./generated_code")

        # If path is not absolute, make it relative to output_dir
        if not os.path.isabs(directory):
            directory = directory.lstrip("./")
            if directory == "" or directory == ".":
                directory = output_dir
            else:
                directory = os.path.join(output_dir, directory)

        search_pattern = os.path.join(directory, "**", pattern)
        matching_files = glob.glob(search_pattern, recursive=True)

        if not matching_files:
            return f"No files matching '{pattern}' found in {directory}"

        result = [f"Found {len(matching_files)} files matching '{pattern}':\n"]
        for file_path in sorted(matching_files):
            rel_path = os.path.relpath(file_path, directory)
            result.append(f"  • {rel_path}")

        return "\n".join(result)
    except Exception as e:
        return f"✗ Error searching files: {str(e)}"


def get_file_tools() -> List:
    """Returns a list of all file operation tools."""
    return [
        write_file,
        read_file,
        list_files,
        create_directory,
        search_files
    ]
