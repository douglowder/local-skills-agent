"""Skills discovery and loading."""

from pathlib import Path
from typing import Any, Optional


class Skill:
    """Represents a skill that can be invoked by the agent."""

    def __init__(
        self,
        name: str,
        description: str,
        content: str,
        path: Path,
        metadata: Optional[dict[str, Any]] = None,
    ):
        self.name = name
        self.description = description
        self.content = content
        self.path = path
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return f"Skill(name={self.name!r}, description={self.description!r})"


def _strip_quotes(value: str) -> str:
    """Strip a single pair of surrounding double or single quotes, if present."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def _parse_frontmatter(text: str) -> tuple[Optional[dict[str, str]], str]:
    """Parse a YAML-style frontmatter block from the top of `text`.

    Recognizes blocks delimited by lines containing only `---`. Only flat
    `key: value` pairs are supported; quoted string values are unquoted.
    Lines that don't match `key: value` are ignored.

    Returns (frontmatter_dict, body). If no frontmatter is present,
    returns (None, original_text).
    """
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None, text

    # Find the closing fence
    close_idx: Optional[int] = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            close_idx = i
            break
    if close_idx is None:
        return None, text

    fm: dict[str, str] = {}
    for raw in lines[1:close_idx]:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if not key:
            continue
        fm[key] = _strip_quotes(value.strip())

    body = "".join(lines[close_idx + 1 :])
    # A blank line right after the closing fence is conventional; drop one.
    if body.startswith("\n"):
        body = body[1:]
    return fm, body


def _first_prose_line(text: str) -> Optional[str]:
    """Return the first non-blank line that isn't a markdown heading."""
    for raw in text.splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            return line
    return None


class SkillLoader:
    """Loads and manages skills."""

    def __init__(self, skills_dir: str | Path = ".skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: dict[str, Skill] = {}

    def discover_skills(self) -> list[Skill]:
        """Discover all available skills in the skills directory.

        Two layouts are supported:
        - Flat: `<skills_dir>/<slug>.md` (the original format)
        - Nested: `<skills_dir>/<slug>/SKILL.md` (Anthropic / Expo format,
          with YAML frontmatter)
        """
        if not self.skills_dir.exists():
            return []

        seen: set[Path] = set()
        discovered: list[Skill] = []

        # Flat top-level .md files (excluding any stray top-level SKILL.md,
        # which has no parent slug to identify it).
        for skill_file in sorted(self.skills_dir.glob("*.md")):
            if skill_file.name == "SKILL.md":
                continue
            resolved = skill_file.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            skill = self._load_skill(skill_file)
            if skill:
                discovered.append(skill)
                self.skills[skill.name] = skill

        # One level of nesting: <slug>/SKILL.md
        for skill_file in sorted(self.skills_dir.glob("*/SKILL.md")):
            resolved = skill_file.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            skill = self._load_skill(skill_file)
            if skill:
                discovered.append(skill)
                self.skills[skill.name] = skill

        return discovered

    def _load_skill(self, skill_path: Path) -> Optional[Skill]:
        """Load a single skill from a markdown file.

        Supports YAML frontmatter (Anthropic / Expo skill format) and falls
        back to the original heuristic for skills without frontmatter.
        """
        try:
            content = skill_path.read_text()

            frontmatter, body = _parse_frontmatter(content)

            # Name resolution
            if frontmatter and frontmatter.get("name"):
                name = frontmatter["name"]
            elif skill_path.name == "SKILL.md":
                name = skill_path.parent.name
            else:
                name = skill_path.stem

            # Description resolution
            if frontmatter and frontmatter.get("description"):
                description = frontmatter["description"]
            else:
                description = _first_prose_line(body) or f"Skill: {name}"

            # Everything in frontmatter besides name/description is metadata
            metadata: dict[str, Any] = {}
            if frontmatter:
                metadata = {
                    k: v
                    for k, v in frontmatter.items()
                    if k not in ("name", "description")
                }

            return Skill(
                name=name,
                description=description,
                content=content,
                path=skill_path,
                metadata=metadata,
            )
        except Exception as e:
            print(f"Warning: Failed to load skill from {skill_path}: {e}")
            return None

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        return self.skills.get(name)

    def get_skills_summary(self) -> str:
        """Get a summary of all available skills for the LLM context."""
        if not self.skills:
            return "No skills available."

        summary = "Available skills:\n"
        for skill in self.skills.values():
            try:
                rel_path = skill.path.resolve().relative_to(
                    self.skills_dir.resolve()
                )
                shown_path = f"{self.skills_dir}/{rel_path}"
            except (OSError, ValueError):
                shown_path = str(skill.path)
            summary += f"- {skill.name}: {skill.description}\n"
            summary += f"  Path: {shown_path}\n"

        summary += (
            "\nTo use a skill, use the read_file tool to read its content "
            "from the listed Path, then follow the instructions."
        )

        return summary

    def get_skill_names(self) -> list[str]:
        """Get a list of all skill names."""
        return list(self.skills.keys())
