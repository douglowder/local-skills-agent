---
name: skill_creator
description: Create new skill definitions (with YAML frontmatter) for the local skills agent and place them under the correct plugin directory. Use when the user requests a capability that doesn't yet exist as a skill.
version: 1.0.0
---

# Skill Creator

**Create new skills for the skills system - the meta-skill that extends the agent's capabilities**

## Purpose

This skill enables you to create new skill definitions for the local skills agent. When a user requests functionality that doesn't exist yet, use this skill to generate a properly formatted SKILL.md file under the appropriate plugin.

## Instructions

When the user asks to create a new skill or requests functionality that would benefit from a reusable skill:

### 1. Understand the Requirement

Ask clarifying questions if needed:
- What should the skill do?
- What inputs does it need?
- What output should it produce?
- Are there any specific tools it should use?
- Which plugin does it belong to? (Default to `python` for this project.)
- Should it be simple or multi-file (with supporting resources)?

### 2. Choose Plugin and Slug

Skills live under `.skills/plugins/<plugin>/skills/<slug>/SKILL.md`. The plugin
groups related skills (e.g. `python` for Python-development skills); the slug
is the bare skill identifier and should be lowercase with underscores
(`my_new_skill`).

If the user hasn't said otherwise, place new skills in the `python` plugin
that ships with this project.

### 3. Choose Skill Type

**Simple Skill** — Single `SKILL.md` file
- Quick tasks (file operations, simple analysis)
- Uses only the core tools (read_file, write_file, bash, list_directory)
- Example: `write_hello_world`

**Multi-File Skill** — `SKILL.md` plus sibling subdirectories
- Complex analysis or generation tasks
- Needs scripts, benchmarks, templates, or data files
- All resources live next to `SKILL.md` under
  `.skills/plugins/<plugin>/skills/<slug>/`
- Example: `code_quality_analyzer` (has `benchmarks/`, `scripts/`, `templates/`)

### 4. Create the Skill File

**File location:** `.skills/plugins/<plugin>/skills/<slug>/SKILL.md`

**Format:**
```markdown
---
name: <slug>
description: <one-line summary the agent uses to match user requests to this skill>
version: 1.0.0
---

# Skill Name

**Brief one-line description**

## Purpose

Explain what this skill does and when it should be used.

## Instructions

Step-by-step instructions for the LLM to follow:

### 1. First Step
Clear instructions...

### 2. Second Step
More instructions...

## Tools Used

- tool_name: What it's used for
- tool_name: What it's used for

## Example Usage

Provide examples of how the skill would be invoked.
```

**Frontmatter rules:**
- `name` should match the directory slug.
- `description` is the single most important field — the agent reads it on
  startup and uses it to decide when to invoke the skill. Make it specific:
  start with what the skill does, then mention when to use it. Avoid generic
  phrases like "this skill helps with X".
- `version` is informational; bump it when the skill changes meaningfully.

### 5. For Multi-File Skills

Create the supporting directory structure alongside `SKILL.md`:

```
.skills/plugins/<plugin>/skills/<slug>/
├── SKILL.md              # Main skill file (frontmatter + instructions)
├── scripts/              # Python scripts or other executables
├── benchmarks/           # Reference data, standards
├── templates/            # Output templates
└── data/                 # Other data files
```

**Important:** The main skill file MUST instruct the LLM to read supporting
files as the FIRST step, using the full path under
`.skills/plugins/<plugin>/skills/<slug>/`.

### 6. Skill Writing Best Practices

**Clear Instructions:**
- Use numbered steps
- Be explicit about which tools to call
- Specify exact file paths (always including the
  `.skills/plugins/<plugin>/skills/<slug>/` prefix when referring to your
  own supporting files)
- Include error handling guidance

**Progressive Disclosure:**
- Don't include all supporting file contents in the main skill
- Instruct the LLM to read them as needed
- Use list_directory to discover available resources

**Automatic Invocation:**
- Make the frontmatter `description` precise — that's what the agent matches against
- Include trigger phrases users might say
- Make the skill slug descriptive

**Composability:**
- Skills can invoke other skills using read_file, e.g.
  `read_file(".skills/plugins/python/skills/code_quality_analyzer/SKILL.md")`
- Mention related skills in the Purpose section
- Delegate complex subtasks to specialized skills

## Skill Templates

### Template: Simple Task Skill

```markdown
---
name: <slug>
description: <one-line summary>
version: 1.0.0
---

# [Skill Name]

**[One-line description]**

## Purpose

This skill [does what] when the user [asks for what].

## Instructions

When this skill is invoked:

1. [Step 1 - often involves reading or listing files]
2. [Step 2 - processing or transformation]
3. [Step 3 - output or confirmation]

## Tools Used

- read_file: [purpose]
- write_file: [purpose]
- bash: [purpose]
- list_directory: [purpose]

## Example

User: "[typical request]"
Action: [what the skill does]
```

### Template: Analysis Skill

```markdown
---
name: <slug>
description: <one-line summary>
version: 1.0.0
---

# [Skill Name]

**Analyze [what] and provide [output]**

## Purpose

This skill analyzes [subject] to identify [findings] and provides [recommendations/report].

## Instructions

### 1. Identify Target Files
Ask the user which files to analyze, or use context clues from their request.

### 2. Read Source Files
Use read_file to load the target files:
```
read_file("[file_path]")
```

### 3. Perform Analysis
[Specific analysis steps]
- Check for [criteria 1]
- Evaluate [criteria 2]
- Measure [metric 3]

### 4. Generate Report
Create a structured report with:
- Executive summary
- Detailed findings
- Recommendations
- [Other sections]

## Output Format

[Describe the expected output format]
```

### Template: Generator Skill

```markdown
---
name: <slug>
description: <one-line summary>
version: 1.0.0
---

# [Skill Name]

**Generate [artifact] based on [input]**

## Purpose

This skill creates [what] when the user needs [use case].

## Instructions

### 1. Gather Requirements
[What information to collect from user or context]

### 2. Generate Content
[Algorithm or template for generation]

### 3. Write Output
Use write_file to create the artifact:
```
write_file("[output_path]", "[content]")
```

### 4. Confirm Success
Tell the user what was created and where to find it.
```

### Template: Multi-File Complex Skill

```markdown
---
name: <slug>
description: <one-line summary>
version: 1.0.0
---

# [Skill Name]

**[Comprehensive description]**

## Overview

This skill provides [detailed capabilities].

## Usage

### 1. Load Required Resources (REQUIRED FIRST STEP)

**IMPORTANT:** Before proceeding, read the required data files:

```
read_file(".skills/plugins/<plugin>/skills/<slug>/<resource_type>/<file>.json")
```

### 2. Identify Targets
[How to determine what to process]

### 3. Execute Analysis/Generation
[Main processing steps]

### 4. Generate Output
[Output creation using templates/data]

## Supporting Resources

### Scripts
- `.skills/plugins/<plugin>/skills/<slug>/scripts/analyzer.py` - [Description]

### Benchmarks
- `.skills/plugins/<plugin>/skills/<slug>/benchmarks/standards.json` - [Description]

### Templates
- `.skills/plugins/<plugin>/skills/<slug>/templates/report.md` - [Description]
```

## Example: Creating a Simple Skill

**User request:** "Create a skill that counts lines in Python files"

**Steps:**
1. Use write_file to create `.skills/plugins/python/skills/count_python_lines/SKILL.md`:

```markdown
---
name: count_python_lines
description: Count total lines of code across Python files in a directory tree. Use when the user wants to measure codebase size.
version: 1.0.0
---

# Count Python Lines

**Count total lines of code in Python files**

## Purpose

This skill counts the total lines in Python files when the user wants to measure codebase size.

## Instructions

### 1. Find Python Files
Use list_directory or bash to find .py files:
```
bash("find . -name '*.py' -type f")
```

### 2. Count Lines
For each file, use bash to count lines:
```
bash("wc -l [file_path]")
```

### 3. Report Total
Sum up all lines and report to the user with:
- Total lines across all files
- Number of files analyzed
- Breakdown by file (optional)

## Tools Used

- bash: Find files and count lines
- list_directory: Browse directories if needed
```

2. Confirm the skill was created
3. The skill is now automatically available to the agent on next startup

## Testing New Skills

After creating a skill, suggest the user test it:
```
"I've created the [skill_name] skill under the [plugin] plugin. Restart the agent and you can use it by saying: '[example trigger phrase]'"
```

## Notes

- Skill slugs should be lowercase with underscores: `my_skill_name`
- The directory name and the frontmatter `name` should match
- All skills are auto-discovered on agent startup
- Skills can be updated by editing the SKILL.md file
- Use clear, imperative language in instructions
- Think about error cases and edge conditions
