"""Skills discovery and loading."""

import json
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
        plugin: Optional[str] = None,
        slug: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.content = content
        self.path = path
        self.metadata = metadata or {}
        # For plugin-scoped skills, `plugin` is the plugin name and `slug` is
        # the bare skill identifier; for standalone skills both are None and
        # `name` is the slug.
        self.plugin = plugin
        self.slug = slug or name

    def __repr__(self) -> str:
        return f"Skill(name={self.name!r}, description={self.description!r})"


class Plugin:
    """A bundle of skills with associated plugin.json metadata."""

    def __init__(
        self,
        name: str,
        path: Path,
        description: str = "",
        version: str = "",
        author: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        self.name = name
        self.path = path
        self.description = description
        self.version = version
        self.author = author or {}
        # Any plugin.json fields besides the well-known ones live here.
        self.metadata = metadata or {}
        self.skills: list[Skill] = []

    def __repr__(self) -> str:
        return f"Plugin(name={self.name!r}, skills={len(self.skills)})"


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


def _load_plugin_json(plugin_dir: Path) -> dict[str, Any]:
    """Read `<plugin_dir>/.claude-plugin/plugin.json` if present.

    Missing file or malformed JSON yields an empty dict rather than raising —
    the plugin is still usable for skill discovery, just without metadata.
    """
    candidate = plugin_dir / ".claude-plugin" / "plugin.json"
    if not candidate.exists():
        return {}
    try:
        return json.loads(candidate.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: Failed to read {candidate}: {e}")
        return {}


class SkillLoader:
    """Loads and manages skills (and the plugins that contain them)."""

    def __init__(self, skills_dir: str | Path = ".skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: dict[str, Skill] = {}
        self.plugins: dict[str, Plugin] = {}

    def discover_skills(self) -> list[Skill]:
        """Discover all available skills in the skills directory.

        Three layouts are supported, and may coexist:
        - Flat:           `<skills_dir>/<slug>.md`
        - Nested:         `<skills_dir>/<slug>/SKILL.md`
        - Plugin-scoped:  `<skills_dir>/plugins/<plugin>/skills/<slug>/SKILL.md`
                          (paired with `.../<plugin>/.claude-plugin/plugin.json`)

        Plugin-scoped skills are stored under the key `<plugin>:<slug>` so
        they don't collide with same-named standalone skills.
        """
        if not self.skills_dir.exists():
            return []

        seen: set[Path] = set()
        discovered: list[Skill] = []

        def add(skill: Optional[Skill]) -> None:
            if skill is None:
                return
            discovered.append(skill)
            self.skills[skill.name] = skill

        # 1. Flat top-level .md files.
        for skill_file in sorted(self.skills_dir.glob("*.md")):
            if skill_file.name == "SKILL.md":
                continue
            resolved = skill_file.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            add(self._load_skill(skill_file))

        # 2. Nested standalone: <slug>/SKILL.md at top level.
        #    (Skip the reserved "plugins" directory — handled in step 3.)
        for skill_file in sorted(self.skills_dir.glob("*/SKILL.md")):
            if skill_file.parent.name == "plugins":
                continue
            resolved = skill_file.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            add(self._load_skill(skill_file))

        # 3. Plugin-scoped: plugins/<plugin>/skills/<slug>/SKILL.md
        plugins_dir = self.skills_dir / "plugins"
        if plugins_dir.is_dir():
            for plugin_dir in sorted(p for p in plugins_dir.iterdir() if p.is_dir()):
                plugin = self._load_plugin(plugin_dir)
                self.plugins[plugin.name] = plugin
                skills_subdir = plugin_dir / "skills"
                if not skills_subdir.is_dir():
                    continue
                for skill_file in sorted(skills_subdir.glob("*/SKILL.md")):
                    resolved = skill_file.resolve()
                    if resolved in seen:
                        continue
                    seen.add(resolved)
                    skill = self._load_skill(skill_file, plugin=plugin.name)
                    if skill is not None:
                        plugin.skills.append(skill)
                    add(skill)

        return discovered

    def _load_plugin(self, plugin_dir: Path) -> Plugin:
        """Construct a Plugin from `<plugin_dir>/.claude-plugin/plugin.json`.

        The directory name is the authoritative plugin identifier; the
        `name` field in plugin.json is treated as metadata and not used as
        the lookup key (so a typo there doesn't break skill namespacing).
        """
        data = _load_plugin_json(plugin_dir)
        known = {"name", "description", "version", "author"}
        return Plugin(
            name=plugin_dir.name,
            path=plugin_dir,
            description=data.get("description", ""),
            version=data.get("version", ""),
            author=data.get("author") or {},
            metadata={k: v for k, v in data.items() if k not in known},
        )

    def _load_skill(
        self,
        skill_path: Path,
        plugin: Optional[str] = None,
    ) -> Optional[Skill]:
        """Load a single skill from a markdown file.

        Supports YAML frontmatter (Anthropic / Expo skill format) and falls
        back to the original heuristic for skills without frontmatter. When
        `plugin` is set, the skill's lookup name is namespaced as
        `<plugin>:<slug>`.
        """
        try:
            content = skill_path.read_text()

            frontmatter, body = _parse_frontmatter(content)

            # Slug resolution (the bare skill identifier)
            if frontmatter and frontmatter.get("name"):
                slug = frontmatter["name"]
            elif skill_path.name == "SKILL.md":
                slug = skill_path.parent.name
            else:
                slug = skill_path.stem

            # Description resolution
            if frontmatter and frontmatter.get("description"):
                description = frontmatter["description"]
            else:
                description = _first_prose_line(body) or f"Skill: {slug}"

            # Everything in frontmatter besides name/description is metadata
            metadata: dict[str, Any] = {}
            if frontmatter:
                metadata = {
                    k: v
                    for k, v in frontmatter.items()
                    if k not in ("name", "description")
                }

            name = f"{plugin}:{slug}" if plugin else slug

            return Skill(
                name=name,
                slug=slug,
                description=description,
                content=content,
                path=skill_path,
                metadata=metadata,
                plugin=plugin,
            )
        except Exception as e:
            print(f"Warning: Failed to load skill from {skill_path}: {e}")
            return None

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name (e.g. `legacy_skill` or `expo:expo-module`)."""
        return self.skills.get(name)

    def _show_path(self, skill_path: Path) -> str:
        try:
            rel = skill_path.resolve().relative_to(self.skills_dir.resolve())
            return f"{self.skills_dir}/{rel}"
        except (OSError, ValueError):
            return str(skill_path)

    def get_skills_summary(self) -> str:
        """Get a summary of all available skills for the LLM context.

        Skills are grouped by plugin when present; standalone skills appear
        under their own heading.
        """
        if not self.skills:
            return "No skills available."

        # Partition skills into plugin-scoped and standalone.
        standalone = [s for s in self.skills.values() if s.plugin is None]
        plugins_with_skills = [
            p for p in self.plugins.values() if p.skills
        ]

        parts: list[str] = ["Available skills:"]

        for plugin in plugins_with_skills:
            header = f"\n[Plugin: {plugin.name}"
            if plugin.version:
                header += f" v{plugin.version}"
            header += "]"
            if plugin.description:
                header += f" {plugin.description}"
            parts.append(header)
            for skill in plugin.skills:
                parts.append(f"- {skill.name}: {skill.description}")
                parts.append(f"  Path: {self._show_path(skill.path)}")

        if standalone:
            if plugins_with_skills:
                parts.append("\n[Standalone skills]")
            for skill in standalone:
                parts.append(f"- {skill.name}: {skill.description}")
                parts.append(f"  Path: {self._show_path(skill.path)}")

        parts.append(
            "\nTo use a skill, use the read_file tool to read its content "
            "from the listed Path, then follow the instructions."
        )

        return "\n".join(parts) + "\n"

    def get_skill_names(self) -> list[str]:
        """Get a list of all skill names."""
        return list(self.skills.keys())
