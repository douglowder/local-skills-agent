# README Generator

**Generate a professional README.md for a Python project by analyzing the codebase**

## Purpose

This skill creates a comprehensive README.md file when the user asks to document their project or generate README documentation.

## Instructions

When this skill is invoked:

### 1. Discover Project Structure

Use list_directory to explore the project:
```
list_directory(".")
```

Look for key files:
- `pyproject.toml` or `setup.py` (project metadata)
- `requirements.txt` (dependencies)
- `LICENSE` (license info)
- Python source files (for structure)
- Test directories

### 2. Read Project Metadata

If `pyproject.toml` exists, read it:
```
read_file("pyproject.toml")
```

If `setup.py` exists, read it:
```
read_file("setup.py")
```

Extract:
- Project name
- Version
- Description
- Author/maintainer info

### 3. Analyze Project Structure

Use bash to get directory tree:
```
bash("find . -type f -name '*.py' | head -20")
```

Or for a prettier tree:
```
bash("tree -L 2 -I '__pycache__|*.pyc|.git' 2>/dev/null || ls -R | grep ':' | sed 's/:$//' | head -20")
```

### 4. Check for Dependencies

If `requirements.txt` exists, read it:
```
read_file("requirements.txt")
```

### 5. Generate README Content

Create a README with these sections:

**Title and Description**
```markdown
# [Project Name]

[Description from metadata or first docstring]
```

**Installation**
```markdown
## Installation

\```bash
pip install -e .
# or
pip install -r requirements.txt
\```
```

**Usage**
```markdown
## Usage

[Basic usage example based on main module]
```

**Project Structure**
```markdown
## Project Structure

\```
[Tree output from step 3]
\```
```

**Development**
```markdown
## Development

[Testing instructions if test directory found]
```

**License**
```markdown
## License

[License type if LICENSE file found]
```

### 6. Write README

Use write_file to create README.md:
```
write_file("README.md", [generated_content])
```

### 7. Confirm Success

Tell the user:
- README.md was created
- What sections were included
- Any missing information they should add manually

## Tools Used

- list_directory: Discover project files
- read_file: Read metadata and config files
- bash: Get directory tree structure
- write_file: Create README.md

## Example Usage

User: "Generate a README for this project"
Action: Analyzes project structure and creates comprehensive README.md

User: "Document this codebase"
Action: Same as above

## Example Output
```markdown
# My Awesome Project

A brief description of what this project does and why it matters.

## Installation
```bash
pip install my-awesome-project
```

## Usage
```python
from my_package import foo
print(foo())
```

## Project Structure
```
my_package/
├── __init__.py
├── foo.py
└── bar.py
```

## Testing
```bash
pytest
```

## Contributing
Please read `CONTRIBUTING.md` for details.

## License
MIT License
```