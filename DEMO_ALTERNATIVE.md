# Alternative Demo: "The Safest Crowd-Pleaser"

**Use this if:** You want guaranteed success with maximum "wow factor"

**Duration:** 5 minutes

**Strategy:** Pre-create an impressive skill before the demo, then show both creation AND usage live

---

## Before Demo (Private Setup)

Run this to create a really impressive skill:

```bash
skills --model gpt-oss:20b --message "Create a skill called 'code_reviewer' that reads Python files, analyzes them for: 1) potential bugs, 2) security issues, 3) performance problems, 4) code smells, and generates a detailed review with severity ratings and fix recommendations"
```

This creates `.skills/code_reviewer.md` - verify it exists, then:

```bash
git add .skills/code_reviewer.md
git stash  # Hide it temporarily for the demo
```

---

## Live Demo Flow

### Part 1: "The Meta-Skill Creates Skills" (2min)

**Say:** "This agent can create its own tools. Watch."

```
You: Create a skill called 'code_reviewer' that reads Python files and generates code reviews with bug detection, security analysis, and recommendations
```

**While waiting:** "The agent is reading the skill_creator instructions, understanding the requirements, and writing a properly formatted skill file right now."

**When done:**
```bash
# Show the created file
cat .skills/code_reviewer.md | head -40
```

**Say:** "It just wrote ~100 lines of instructions for itself. This is now a permanent capability."

---

### Part 2: "Instant Use - No Restart" (2min)

**Say:** "Let's use it immediately on real code."

```
You: Review demo_code.py for issues
```

**Expected:**
- Automatically uses code_reviewer skill
- Analyzes the demo_code.py file
- Finds issues:
  - No input validation
  - No error handling for empty items list
  - Potential division by zero
  - Missing docstrings
  - etc.

**Say:** "It found real issues in seconds. No manual review needed."

---

### Part 3: "Skills Stack Together" (1min)

**Say:** "Now watch skills work together."

```
You: Review demo_code.py, then generate tests for the issues you found
```

**Expected:**
- Uses `code_reviewer` first
- Then automatically uses `test_generator`
- Creates tests that specifically cover the bugs found

**Say:** "Two skills, one request. It orchestrated the whole workflow."

---

## Alternative Impressive Demos

### Demo A: "Documentation Pipeline"
```
You: Generate a README for this project, then create technical documentation for the skills system
```
- Uses `readme_generator` → `technical_documentation_generator`
- Creates two documents in one go

### Demo B: "Complete Quality Pipeline"
```
You: Analyze all Python files in the skills directory for quality issues, generate a report, and create tests for any functions scoring below 70 on maintainability
```
- Uses `list_python_files` → `code_quality_analyzer` → `test_generator`
- Shows three skills composing

### Demo C: "Create and Use Immediately"
```
You: Create a skill called 'dependency_checker' that reads pyproject.toml and checks if all imports in Python files are listed in dependencies

[wait for creation]

You: Check if our dependencies are correct
```
- Create skill
- Use it immediately
- Real practical value

---

## Why This Demo Is Safer

✅ **Pre-tested:** You ran the skill creation beforehand, know it works
✅ **Faster:** Skill already exists if live creation fails
✅ **More Content:** Can show the generated skill file in detail
✅ **Fallback Ready:** If live demo breaks, `git stash pop` restores pre-created version

---

## Backup Plan

If anything fails during live demo:

```bash
# Restore pre-created skill
git stash pop

# Show it working
skills --message "Review demo_code.py for issues"
```

Still impressive, just less "live magic" - but guaranteed to work.

---

## The "Triple Wow" Sequence

This demo has three distinct wow moments:

1. **🎯 WOW #1:** "It's writing code that extends itself" (skill creation)
2. **🎯 WOW #2:** "No restart needed - instant availability" (immediate use)
3. **🎯 WOW #3:** "Skills orchestrate together autonomously" (composability)

Time each to land properly:
- Wow #1: 2 min
- Wow #2: 2 min
- Wow #3: 1 min
- Total: 5 min

---

## Technical Safety Notes

### What Could Go Wrong?

1. **Model timeout** → Use gpt-oss:20b (not qwen3:30b)
2. **Skill creation fails** → Have pre-created version stashed
3. **Tool calling loops** → Max iterations set to 20
4. **Ollama crash** → Run `ollama serve` in separate terminal beforehand

### Pre-Demo Test Run

Do this 1 hour before:
```bash
# Full test run
./demo_prep.sh
skills --model gpt-oss:20b --message "Create a skill called 'test_demo' that prints 'Demo works!'"
skills --message "/skills"  # Verify it's listed
```

If this works, you're good to go.

---

## Audience-Specific Adjustments

### For Managers
- Focus on: "Zero cost, runs locally, no vendor lock-in"
- Skip: Technical architecture details
- Emphasize: ROI, developer productivity

### For Engineers
- Show: The actual skill files being created
- Explain: Tool calling architecture
- Discuss: How to extend with custom tools

### For Security Team
- Emphasize: Local execution, no data leaves your network
- Show: Skills are reviewable markdown files
- Discuss: Sandboxing options for production

---

## Post-Demo Follow-Up

**Share immediately:**
```
GitHub repo: [your-repo-url]
Quick start: git clone [repo] && ./demo_prep.sh
Documentation: cat ACHIEVEMENT.md
```

**Homework for interested colleagues:**
```
Try: skills --message "Create a skill for [something you need]"
```

This gets them hooked - they'll create their own skills and see the value.

---

## Demo Success = They Try It

**Goal:** At least 2 people try it within 24 hours

**How:** Make it easy:
- "Takes 2 minutes to install"
- "Works on your laptop right now"
- "Free forever - no API keys"
- "Created a Slack channel: #local-skills-agent"

The best demo leads to adoption! 🚀
