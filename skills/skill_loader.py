"""Skills discovery and loading."""

import json
from pathlib import Path
from typing import Any


class Skill:
    """Represents a skill that can be invoked by the agent."""

    def __init__(self, name: str, description: str, content: str, path: Path):
        self.name = name
        self.description = description
        self.content = content
        self.path = path

    def __repr__(self) -> str:
        return f"Skill(name={self.name!r}, description={self.description!r})"


class SkillLoader:
    """Loads and manages skills."""

    def __init__(self, skills_dir: str | Path = ".skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: dict[str, Skill] = {}

    def discover_skills(self) -> list[Skill]:
        """Discover all available skills in the skills directory."""
        if not self.skills_dir.exists():
            return []

        discovered_skills = []
        for skill_file in self.skills_dir.glob("*.md"):
            skill = self._load_skill(skill_file)
            if skill:
                discovered_skills.append(skill)
                self.skills[skill.name] = skill

        return discovered_skills

    def _load_skill(self, skill_path: Path) -> Skill | None:
        """Load a single skill from a markdown file."""
        try:
            content = skill_path.read_text()

            # Extract skill name from filename
            name = skill_path.stem

            # Extract description from first line or first paragraph
            lines = content.strip().split("\n")
            description = ""

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    description = line
                    break

            if not description:
                description = f"Skill: {name}"

            return Skill(
                name=name,
                description=description,
                content=content,
                path=skill_path,
            )
        except Exception as e:
            print(f"Warning: Failed to load skill from {skill_path}: {e}")
            return None

    def get_skill(self, name: str) -> Skill | None:
        """Get a skill by name."""
        return self.skills.get(name)

    def get_skills_summary(self) -> str:
        """Get a summary of all available skills for the LLM context."""
        if not self.skills:
            return "No skills available."

        summary = "Available skills:\n"
        for skill in self.skills.values():
            summary += f"- {skill.name}: {skill.description}\n"

        summary += "\nTo use a skill, use the read_file tool to read its content from the .skills/ directory, then follow the instructions."

        return summary

    def get_skill_names(self) -> list[str]:
        """Get a list of all skill names."""
        return list(self.skills.keys())
