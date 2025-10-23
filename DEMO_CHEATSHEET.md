# Demo Cheat Sheet - Print This! 📄

## Pre-Demo Checklist
```bash
./demo_prep.sh                    # Run setup script
source .venv/bin/activate         # Activate environment
skills --model gpt-oss:20b        # Start interactive mode
```

---

## Demo Script (7 minutes)

### 1️⃣ Introduction (30s)
**Say:** "Local AI agent running on Ollama"

```
You: /skills
```
**Point out:** 8 skills including `skill_creator`

---

### 2️⃣ Create a Skill (2min)
**Say:** "Watch it create its own tools"

```
You: Create a skill called 'git_commit_generator' that analyzes staged changes and generates a conventional commit message
```

**Wait for:** `.skills/git_commit_generator.md` created

**Show:**
```bash
ls -la .skills/git_commit_generator.md
```

---

### 3️⃣ Use the New Skill (2min)
**Say:** "Use it immediately - no restart needed"

**Prep:**
```bash
echo "# Demo change" >> DEMO.md
git add DEMO.md
```

**Use it:**
```
You: Generate a commit message for my staged changes
```

**Expected:** Conventional commit message generated

---

### 4️⃣ Composability (2min)
**Say:** "Skills work together automatically"

```
You: Analyze demo_code.py for code quality and generate tests for it
```

**Expected:**
- Reads industry benchmarks
- Analyzes complexity
- Generates test stubs

---

### 5️⃣ Architecture (1min)
**Show diagram:**
```
skill_creator.md
    ↓
Creates new skills
    ↓
Immediately usable
    ↓
Compose together
```

---

## Emergency Backup

If demo fails, show:
```bash
cat .skills/readme_generator.md
cat README.md.generated
pytest -v
```

---

## Key Talking Points

✅ "Creates its own capabilities from natural language"
✅ "100% local - zero API costs"
✅ "Skills compose automatically"
✅ "Production ready - 80 tests passing"

---

## Q&A Answers

**Q: Which skills to use?**
A: "Pattern matches user intent automatically"

**Q: Bad skills?**
A: "Just markdown files - edit or delete them"

**Q: Cost?**
A: "Zero - completely local"

**Q: Production ready?**
A: "Yes for dev tools, add approval workflow for user-facing"

---

## Time Check
- ✅ 2min: Create skill
- ✅ 2min: Use skill
- ✅ 2min: Composability
- ✅ 1min: Wrap up
- Total: 7 min + Q&A

---

## One-Liners

**Opening:** "What if your AI could build its own tools?"

**Closing:** "Self-extending system. Runs on our hardware. Zero API costs."
