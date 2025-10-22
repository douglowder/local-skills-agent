# Technical Documentation Generator

**Automatically generates comprehensive, professional technical documentation for Python projects.**

## Overview

This skill creates structured, industry-standard documentation including:
- API reference documentation
- Architecture overviews
- Setup and installation guides
- Usage examples and tutorials
- Troubleshooting guides

## Usage

When asked to generate documentation, follow these steps:

### 1. Analyze Project Structure

First, understand the project layout:
- Use `list_directory` to explore the codebase structure
- Identify main modules, packages, and entry points
- Look for existing documentation (README.md, docs/)

### 2. Read Key Files

Read critical files to understand the project:
- `read_file` on main Python files to understand functionality
- Check `pyproject.toml` or `setup.py` for dependencies and metadata
- Read existing README.md or CLAUDE.md for context

### 3. Extract Documentation Elements

For each Python file, extract:

**Module-Level Information:**
- Module docstring (first string after imports)
- Purpose and responsibility
- Key exports (classes, functions)

**Class Documentation:**
- Class docstring
- Constructor parameters
- Public methods and their signatures
- Usage examples

**Function Documentation:**
- Function/method docstring
- Parameters with types
- Return values
- Exceptions raised
- Examples

### 4. Generate Documentation Structure

Create documentation following this template:

```markdown
# Project Name

[Brief one-liner description]

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [API Reference](#api-reference)
5. [Examples](#examples)
6. [Contributing](#contributing)

## Installation

\`\`\`bash
# Installation commands from pyproject.toml or setup.py
\`\`\`

## Quick Start

[Minimal example showing main use case]

## Architecture

### Project Structure
[Directory tree showing main components]

### Component Overview
[Description of major components and their interactions]

### Design Patterns
[Key patterns used: Factory, Strategy, Observer, etc.]

## API Reference

### Module: [module_name]

[Module description]

#### Classes

##### ClassName

[Class description]

**Constructor:**
\`\`\`python
def __init__(self, param1: type, param2: type):
    \"\"\"Constructor description\"\"\"
\`\`\`

**Parameters:**
- `param1` (type): Description
- `param2` (type): Description

**Methods:**

###### method_name

\`\`\`python
def method_name(self, arg1: type) -> return_type:
    \"\"\"Method description\"\"\"
\`\`\`

**Parameters:**
- `arg1` (type): Description

**Returns:**
- return_type: Description

**Example:**
\`\`\`python
obj = ClassName(param1, param2)
result = obj.method_name(arg1)
\`\`\`

#### Functions

##### function_name

\`\`\`python
def function_name(arg1: type, arg2: type) -> return_type:
    \"\"\"Function description\"\"\"
\`\`\`

[Parameter and return documentation]

## Examples

### Example 1: Basic Usage
[Code example with explanation]

### Example 2: Advanced Features
[More complex example]

## Troubleshooting

### Common Issues

**Issue**: [Problem description]
**Solution**: [How to fix]

## Contributing

[Guidelines for contributions, if applicable]

## License

[License information from project files]
```

### 5. Documentation Best Practices

Follow these guidelines:

**Structure:**
- Start with overview and installation
- Progress from simple to complex examples
- Include table of contents for long documents
- Use clear section headers

**Code Examples:**
- Show complete, runnable examples
- Include expected output
- Demonstrate error handling
- Show both basic and advanced usage

**Clarity:**
- Write in active voice
- Use consistent terminology
- Define technical terms
- Avoid jargon where possible

**Completeness:**
- Document all public APIs
- Include edge cases and limitations
- Explain design decisions
- Link related concepts

### 6. API Documentation Format

For API reference sections, use this format:

```markdown
#### Function/Method Name

**Signature:**
\`\`\`python
def function_name(
    param1: Type1,
    param2: Type2 = default,
    *args,
    **kwargs
) -> ReturnType:
\`\`\`

**Description:**
[What the function does, when to use it]

**Parameters:**
- `param1` (Type1): [Description, constraints]
- `param2` (Type2, optional): [Description]. Defaults to [default].
- `*args`: [Variable positional arguments description]
- `**kwargs`: [Variable keyword arguments description]

**Returns:**
- ReturnType: [What is returned, format, possible values]

**Raises:**
- ExceptionType: [When this exception occurs]

**Examples:**
\`\`\`python
# Basic usage
result = function_name(value1, value2)

# Advanced usage with kwargs
result = function_name(value1, value2, option="custom")
\`\`\`

**See Also:**
- [Related function/class]
- [Relevant module]
```

### 7. Architecture Documentation

For architecture overviews, include:

**System Diagram (ASCII):**
```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│  CLI Layer  │─────▶│  Core Logic  │
└─────────────┘      └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   Storage    │
                     └──────────────┘
```

**Component Descriptions:**
- **Component Name**: Purpose and responsibilities
- **Key Classes**: Main classes in this component
- **Dependencies**: What it depends on
- **Interface**: How other components interact with it

**Data Flow:**
1. [Step-by-step description of data flow]
2. [Through the system]
3. [To final output]

### 8. Advanced Features

**Versioning Documentation:**
Track documentation versions with code versions:
```markdown
## Version History

### v1.2.0 (2025-01-15)
- Added new feature X
- Deprecated function Y
- Breaking change: Z parameter now required

### v1.1.0 (2024-12-01)
- Initial release
```

**Migration Guides:**
When APIs change, provide migration paths:
```markdown
## Migrating from v1.x to v2.x

### Breaking Changes

**Old API:**
\`\`\`python
result = old_function(param)
\`\`\`

**New API:**
\`\`\`python
result = new_function(param, new_param="default")
\`\`\`

**Migration Steps:**
1. Update all calls to new_function
2. Add new_param where custom behavior needed
3. Test thoroughly
```

## Example Workflow

**User Request:** "Generate documentation for the skills package"

**Agent Steps:**
1. List files in skills/ directory
2. Read each .py file (agent.py, tools.py, etc.)
3. Extract docstrings and signatures
4. Read pyproject.toml for dependencies
5. Generate comprehensive documentation with:
   - Installation instructions from pyproject.toml
   - Architecture overview from code structure
   - API reference from docstrings
   - Usage examples from main.py
6. Write documentation to DOCUMENTATION.md

## Tips

- **Automation**: Generate documentation that stays synchronized with code
- **Examples**: Include working code that can be copy-pasted
- **Context**: Explain *why* not just *what*
- **Maintenance**: Note where manual updates are needed vs. auto-generated
- **Audience**: Tailor detail level to intended readers (beginners vs. experts)

## Output Format

Write generated documentation to a file using `write_file`:
- Main docs: `DOCUMENTATION.md` or `docs/README.md`
- API reference: `docs/api.md`
- Examples: `docs/examples.md`
- Architecture: `docs/architecture.md`

Always inform the user about:
- What was documented
- Where files were created
- Any gaps or areas needing manual attention
- Suggestions for improvement

---

*This skill helps maintain high-quality, professional documentation that evolves with your codebase.*
