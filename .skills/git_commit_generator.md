# Git Commit Generator

**Generate a conventional commit message based on staged changes**

## Purpose
This skill inspects the current git staging area, summarizes the changes, and proposes a conventional commit message (e.g., `feat: add user authentication`). It is useful when a developer wants a quick, consistent commit message without manually drafting one.

## Instructions
When this skill is invoked:

1. **Read the current staged changes**
   ```
   bash("git diff --cached --name-status > .git/staged_changes.txt")
   ```
   This command writes a list of changed files and their status (A, M, D) to `staged_changes.txt`.

2. **Count added and removed lines**
   ```
   bash("git diff --cached --numstat > .git/staged_numstat.txt")
   ```
   The `numstat` file contains a tab‑separated line for each file: `<added> <removed> <path>`.

3. **Analyze the files to infer a commit type**
   * Read the two temporary files using `read_file`.
   * Look for common keywords:
     * `feat`, `feature`, `new`, `add` → `feat`
     * `fix`, `bug`, `error` → `fix`
     * `docs`, `readme` → `docs`
     * `style`, `format` → `style`
     * `refactor` → `refactor`
     * `perf`, `performance` → `perf`
     * `test`, `tests` → `test`
     * `chore` or no clear intent → `chore`
   * If multiple types are present, prefer the most impactful: `feat` > `fix` > `refactor` > others.

4. **Build a concise subject line**
   * Use the first line of the most recent commit as a template if the user wants to edit.
   * Otherwise, generate a default: `[type]: <short description>`.
   * The short description can be derived from the most changed file names or the user’s prompt.

5. **Output the commit message**
   * Print the suggested message to the user.
   * Optionally, write it to a temporary file `commit_message.txt` for easy use.

## Tools Used
- `bash`: Execute git commands.
- `read_file`: Read temporary staging files.
- `write_file`: Write the final commit message.

## Example Usage
```
User: "Generate a commit message for my staged changes"
Assistant: (Runs the skill and outputs)

Suggested commit:
feat: add login endpoint

Files changed:
  A   src/api/login.py
  M   src/models/user.py
  D   docs/old.md

```
