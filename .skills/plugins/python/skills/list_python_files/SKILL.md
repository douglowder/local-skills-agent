---
name: list_python_files
description: Find and list all Python files in a directory tree, optionally excluding __pycache__ and dotfiles. Use when the user asks "what Python files are in this project" or wants an inventory.
version: 1.0.0
---

# List Python Files Skill

Find and list all Python files in a directory tree.

## Instructions

When this skill is invoked, you should:

1. Ask the user which directory to search (or use current directory if not specified)
2. Use the `bash` tool to find all Python files recursively
3. Execute: `find <directory> -name "*.py" -type f`
4. Present the results in a clear, organized format
5. Optionally, provide a count of files found

## Additional Information

You can enhance the output by:
- Grouping files by directory
- Showing file sizes
- Excluding common directories like `__pycache__`, `.venv`, etc.
- Sorting by name or path

Use: `find <directory> -name "*.py" -type f -not -path "*/.*" -not -path "*/__pycache__/*"`
