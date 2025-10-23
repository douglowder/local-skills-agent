# Live Demo Script: Self-Extending AI Agent

**Duration:** 5-10 minutes
**Audience:** Technical colleagues
**Goal:** Show a local AI agent that can extend itself with new capabilities

---

## Setup (Before Demo)

```bash
# Terminal 1: Ensure Ollama is running
ollama serve

# Terminal 2: Navigate to project
cd ~/src/skills
source .venv/bin/activate  # or activate your venv
```

---

## Demo Flow

### Act 1: "It's just an AI assistant" (30 seconds)

**Show:** Basic interaction

```bash
skills --model gpt-oss:20b
```

```
You: What can you do?
```

**Expected:** Agent lists available skills (8 skills including skill_creator)

**Say:** "This is a local AI agent running on Ollama. Notice it has 'skills' - pre-built capabilities. But watch what happens next..."

---

### Act 2: "The agent creates its own tools" (2 minutes)

**Say:** "Let's ask it to create a NEW capability it doesn't have yet."

```
You: Create a skill called 'git_commit_generator' that analyzes staged changes and generates a conventional commit message
```

**Expected:**
- Agent reads `skill_creator.md`
- Creates `.skills/git_commit_generator.md`
- Shows success message

**Show:** Verify the file was created
```bash
ls -la .skills/git_commit_generator.md
cat .skills/git_commit_generator.md | head -30
```

**Say:** "The agent just wrote code that extends itself. This skill is now permanently available."

---

### Act 3: "It immediately uses what it created" (2 minutes)

**Say:** "Let's use the skill we just created - without restarting anything."

First, make some changes:
```bash
echo "# Demo change" >> DEMO.md
git add DEMO.md
```

Then use the new skill:
```
You: Generate a commit message for my staged changes
```

**Expected:**
- Agent automatically discovers and uses `git_commit_generator`
- Reads git diff
- Generates a conventional commit message
- Shows the message

**Say:** "Notice it didn't need to be told which skill to use - it matched our intent automatically."

---

### Act 4: "Skills compose together" (2 minutes)

**Say:** "Skills can call other skills. Watch this multi-step workflow."

Create a test file:
```bash
cat > demo_code.py << 'EOF'
def calculate_discount(price, discount_percent):
    if discount_percent > 100:
        discount_percent = 100
    if discount_percent < 0:
        discount_percent = 0
    discount = price * (discount_percent / 100)
    return price - discount

def process_order(items):
    total = 0
    for item in items:
        if item['quantity'] > 0:
            total += item['price'] * item['quantity']
    return total
EOF
```

Now ask for analysis:
```
You: Analyze demo_code.py for code quality and generate tests for it
```

**Expected:**
- Agent uses `code_quality_analyzer` skill
- Reads industry benchmarks from `.skills/code_quality_analyzer/benchmarks/industry_standards.json`
- Analyzes cyclomatic complexity, maintainability
- Then uses `test_generator` skill
- Creates test stubs for both functions

**Say:** "One request triggered multiple skills working together - analyzing code quality with real industry benchmarks, then generating test scaffolding."

---

### Act 5: "The meta-programming loop" (1 minute)

**Say:** "Here's the architecture that makes this possible..."

Show diagram on screen or whiteboard:

```
┌─────────────────────────────────────┐
│  skill_creator.md (meta-skill)      │
│  ↓                                  │
│  Creates new skills                 │
│  ↓                                  │
│  git_commit_generator.md            │
│  readme_generator.md                │
│  test_generator.md                  │
│  ↓                                  │
│  All immediately usable             │
└─────────────────────────────────────┘
```

**Say:** "This is a self-extending system. The agent can:
1. Create new capabilities from natural language
2. Use them immediately
3. Compose them together
4. All running locally on Ollama - no API calls"

---

### Act 6: "Real-world scenario" (2 minutes - OPTIONAL)

**Say:** "Let me show you a real workflow we might use daily."

```
You: Create a skill called 'pr_description_generator' that reads git diff, analyzes the changes, and generates a GitHub PR description with summary, changes, and test plan sections
```

Wait for skill creation...

Then:
```
You: I'm about to create a PR for all these demo changes. Generate a PR description.
```

**Expected:**
- Agent creates the skill
- Uses git diff to see changes
- Generates formatted PR description with:
  - Summary
  - Changes made
  - Testing checklist

**Say:** "In 30 seconds, we created and used a tool that would take hours to build traditionally."

---

## Key Points to Emphasize

### 🎯 **Three "Wow" Moments**

1. **Self-Extension:** "It writes its own capabilities"
2. **Immediate Use:** "No restart, no deployment - instant availability"
3. **Composability:** "Skills work together autonomously"

### 💡 **Technical Highlights**

- **100% Local:** Runs on Ollama (gpt-oss:20b model)
- **No Vendor Lock-in:** Not dependent on OpenAI/Anthropic APIs
- **Progressive Disclosure:** Multi-file skills with supporting resources
- **Tool Calling:** Proper agentic architecture with read/write/bash tools
- **Tested:** 80 unit tests, all passing

### 🚀 **Practical Applications**

- "Need a new workflow? Describe it, the agent builds it"
- "Code analysis with real industry standards"
- "Documentation generation that stays in sync"
- "Test scaffolding in seconds"
- "Commit messages, PR descriptions, code reviews"

---

## Backup Demo (If Issues Occur)

If live demo has issues, show pre-recorded evidence:

```bash
# Show the generated files
cat README.md.generated
cat .skills/readme_generator.md
cat .skills/test_generator.md

# Show test results
pytest -v
```

---

## Q&A Prep

**Q:** "How does it know which skill to use?"
**A:** "The system prompt includes all skill descriptions. The LLM pattern-matches user intent to available skills, then reads the full skill file for instructions."

**Q:** "What if it creates a bad skill?"
**A:** "Skills are just markdown files in `.skills/` - you can edit or delete them. They're version-controlled and reviewable."

**Q:** "Can it create malicious skills?"
**A:** "Skills can only use four tools: read_file, write_file, bash, list_directory. The bash tool has a 30s timeout. You review what gets committed to the repo."

**Q:** "What models work?"
**A:** "Best: gpt-oss:20b, llama3.1:8b. Don't use reasoning models like qwen3:30b - they're too verbose for tool calling."

**Q:** "How much does it cost?"
**A:** "Zero. Completely local on Ollama. No API costs ever."

**Q:** "Can we use it in production?"
**A:** "It's production-ready for developer tools and workflows. For user-facing products, you'd want to add skill approval workflows and sandboxing."

---

## Demo Success Criteria

✅ **Must achieve:**
- Show skill_creator creating a new skill
- Use the newly created skill successfully
- Demonstrate composability (one request → multiple skills)

✅ **Nice to have:**
- Show multi-file skill with benchmarks
- Live code analysis
- Test generation

✅ **Avoid:**
- Don't use qwen3:30b (will fail)
- Don't create complex multi-step skills during demo (may timeout)
- Don't rely on WiFi (everything is local!)

---

## Post-Demo

**Share:**
- GitHub repo link
- ACHIEVEMENT.md for detailed technical overview
- SKILL_CREATOR_DEMO.md for self-study

**Call to Action:**
"Try it yourself: `git clone <repo> && uv pip install -e . && skills`"

---

## Time Allocation

- **Act 1:** 30 sec - Basic intro
- **Act 2:** 2 min - Create skill
- **Act 3:** 2 min - Use new skill
- **Act 4:** 2 min - Composability
- **Act 5:** 1 min - Architecture
- **Act 6:** 2 min - Real scenario (optional)
- **Q&A:** 3-5 min

**Total:** 7-12 minutes

---

## Visual Aids (Prepare These)

1. **Architecture Diagram:**
   ```
   User Request
        ↓
   [Agent Loop] ←→ [Ollama: gpt-oss:20b]
        ↓
   [Tool Calls: read/write/bash/list]
        ↓
   [Skills System]
        ↓
   [skill_creator] → Creates New Skills
   ```

2. **Skills List Terminal Output:**
   Save a screenshot of `/skills` command output

3. **Before/After:**
   - Before: 6 skills
   - After demo: 8+ skills

---

## One-Liner Hook

**Opening:** "What if your AI assistant could build its own tools?"

**Closing:** "We've built a system that extends itself. Every new capability makes it more capable. And it's running entirely on our own hardware."

---

Good luck with the demo! 🚀
# Demo change
