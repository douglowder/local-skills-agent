# Analyze Code Skill

**Quick code analysis - delegates to code_quality_analyzer for detailed metrics**

## Purpose

This skill provides basic code insights. For comprehensive analysis with industry benchmarks, it automatically delegates to the `code_quality_analyzer` skill.

## Instructions

When analyzing code:

### 1. Determine Analysis Depth Needed

- User mentions **"quality"**, **"metrics"**, **"benchmarks"**, or **"detailed"** → Use `code_quality_analyzer` skill
- User wants quick overview only → Proceed with basic analysis

### 2. For Detailed Analysis (RECOMMENDED)

**Automatically invoke code_quality_analyzer skill:**

```
read_file(".skills/code_quality_analyzer.md")
```

Then follow instructions in that skill. It includes:
- Industry-standard complexity benchmarks
- Maintainability index calculations
- Supporting analysis scripts
- Professional report generation

### 3. For Basic Analysis Only

If user just wants a quick summary:
1. Read the target Python file
2. Provide overview of:
   - Code structure and organization
   - Function and class definitions
   - Basic observations
   - Simple improvement suggestions

## Skill Composition Example

**User:** "Analyze this code"
**Agent:** Should use `code_quality_analyzer` for comprehensive analysis

**User:** "What does this function do?"
**Agent:** Can use basic analysis from this skill

## Key Principle

When in doubt, use the **more comprehensive skill** (`code_quality_analyzer`). Users benefit from industry-benchmarked analysis over generic observations.
