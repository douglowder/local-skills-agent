"""Tests for the skill_loader module."""

from pathlib import Path
from typing import Optional

import pytest

from skills.skill_loader import (
    Plugin,
    Skill,
    SkillLoader,
    _first_prose_line,
    _parse_frontmatter,
)


class TestSkill:
    """Test the Skill class."""

    def test_skill_initialization(self):
        """Test Skill initialization."""
        skill = Skill(
            name="test_skill",
            description="A test skill",
            content="Skill content here",
            path=Path("/tmp/test.md"),
        )

        assert skill.name == "test_skill"
        assert skill.description == "A test skill"
        assert skill.content == "Skill content here"
        assert skill.path == Path("/tmp/test.md")

    def test_skill_repr(self):
        """Test Skill __repr__ method."""
        skill = Skill(
            name="test_skill",
            description="A test skill",
            content="Content",
            path=Path("/tmp/test.md"),
        )

        repr_str = repr(skill)
        assert "test_skill" in repr_str
        assert "A test skill" in repr_str


class TestSkillLoader:
    """Test the SkillLoader class."""

    def test_skill_loader_initialization(self, temp_dir):
        """Test SkillLoader initialization."""
        loader = SkillLoader(skills_dir=temp_dir / ".skills")
        assert loader.skills_dir == temp_dir / ".skills"
        assert loader.skills == {}

    def test_discover_skills_success(self, sample_skill_dir):
        """Test discovering skills successfully."""
        loader = SkillLoader(skills_dir=sample_skill_dir)
        skills = loader.discover_skills()

        assert len(skills) == 2
        assert "test_skill" in loader.skills
        assert "another_skill" in loader.skills

    def test_discover_skills_no_directory(self, temp_dir):
        """Test discovering skills when directory doesn't exist."""
        loader = SkillLoader(skills_dir=temp_dir / "nonexistent")
        skills = loader.discover_skills()

        assert len(skills) == 0
        assert loader.skills == {}

    def test_discover_skills_empty_directory(self, temp_dir):
        """Test discovering skills in an empty directory."""
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()

        loader = SkillLoader(skills_dir=skills_dir)
        skills = loader.discover_skills()

        assert len(skills) == 0

    def test_load_skill_with_description(self, temp_dir):
        """Test loading a skill with a clear description."""
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()

        skill_file = skills_dir / "my_skill.md"
        skill_file.write_text("""# My Skill

This is the description.

## Instructions

Do something.
""")

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()

        skill = loader.get_skill("my_skill")
        assert skill is not None
        assert skill.name == "my_skill"
        assert skill.description == "This is the description."

    def test_load_skill_without_description(self, temp_dir):
        """Test loading a skill without a clear description."""
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()

        skill_file = skills_dir / "minimal_skill.md"
        skill_file.write_text("""# Minimal Skill

## Instructions

Just instructions, no description.
""")

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()

        skill = loader.get_skill("minimal_skill")
        assert skill is not None
        assert skill.name == "minimal_skill"
        # Should fall back to default description
        assert "Skill: minimal_skill" in skill.description or "Just instructions" in skill.description

    def test_load_skill_with_only_headers(self, temp_dir):
        """Test loading a skill with only headers."""
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()

        skill_file = skills_dir / "header_skill.md"
        skill_file.write_text("""# Header Skill

## Section One

## Section Two
""")

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()

        skill = loader.get_skill("header_skill")
        assert skill is not None
        assert skill.name == "header_skill"

    def test_load_skill_corrupted_file(self, temp_dir, capsys):
        """Test handling of corrupted skill files."""
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()

        skill_file = skills_dir / "bad_skill.md"
        skill_file.write_text("Valid content")

        # Manually create an unreadable scenario by mocking
        loader = SkillLoader(skills_dir=skills_dir)

        # Create a file, then make the loader fail to read it
        import unittest.mock as mock

        with mock.patch.object(Path, "read_text", side_effect=Exception("Read error")):
            skills = loader.discover_skills()

        # Should handle the error gracefully
        captured = capsys.readouterr()
        assert "Warning" in captured.out or "bad_skill" not in loader.skills

    def test_get_skill_exists(self, sample_skill_dir):
        """Test getting an existing skill."""
        loader = SkillLoader(skills_dir=sample_skill_dir)
        loader.discover_skills()

        skill = loader.get_skill("test_skill")
        assert skill is not None
        assert skill.name == "test_skill"

    def test_get_skill_not_exists(self, sample_skill_dir):
        """Test getting a non-existent skill."""
        loader = SkillLoader(skills_dir=sample_skill_dir)
        loader.discover_skills()

        skill = loader.get_skill("nonexistent_skill")
        assert skill is None

    def test_get_skills_summary_with_skills(self, sample_skill_dir):
        """Test getting skills summary when skills exist."""
        loader = SkillLoader(skills_dir=sample_skill_dir)
        loader.discover_skills()

        summary = loader.get_skills_summary()

        assert "Available skills:" in summary
        assert "test_skill" in summary
        assert "another_skill" in summary
        assert "read_file" in summary  # Should mention how to use skills

    def test_get_skills_summary_no_skills(self, temp_dir):
        """Test getting skills summary when no skills exist."""
        loader = SkillLoader(skills_dir=temp_dir / "nonexistent")
        loader.discover_skills()

        summary = loader.get_skills_summary()
        assert "No skills available" in summary

    def test_get_skill_names(self, sample_skill_dir):
        """Test getting list of skill names."""
        loader = SkillLoader(skills_dir=sample_skill_dir)
        loader.discover_skills()

        skill_names = loader.get_skill_names()

        assert len(skill_names) == 2
        assert "test_skill" in skill_names
        assert "another_skill" in skill_names

    def test_get_skill_names_empty(self, temp_dir):
        """Test getting skill names when no skills exist."""
        loader = SkillLoader(skills_dir=temp_dir / "nonexistent")
        loader.discover_skills()

        skill_names = loader.get_skill_names()
        assert len(skill_names) == 0

    def test_skill_loader_with_string_path(self, temp_dir):
        """Test SkillLoader with string path instead of Path object."""
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()

        loader = SkillLoader(skills_dir=str(skills_dir))
        assert isinstance(loader.skills_dir, Path)

    def test_skill_content_preservation(self, temp_dir):
        """Test that skill content is preserved exactly."""
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()

        original_content = """# Test Skill

Description here.

## Instructions

1. Step one
2. Step two

Some **markdown** formatting.
"""
        skill_file = skills_dir / "content_test.md"
        skill_file.write_text(original_content)

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()

        skill = loader.get_skill("content_test")
        assert skill.content == original_content


class TestFrontmatterParser:
    """Tests for the YAML frontmatter parser."""

    def test_no_frontmatter_returns_original_text(self):
        text = "# Heading\n\nbody text\n"
        fm, body = _parse_frontmatter(text)
        assert fm is None
        assert body == text

    def test_simple_frontmatter(self):
        text = "---\nname: foo\ndescription: A foo skill\n---\n\nbody\n"
        fm, body = _parse_frontmatter(text)
        assert fm == {"name": "foo", "description": "A foo skill"}
        assert body == "body\n"

    def test_quoted_value_with_colon(self):
        text = (
            "---\n"
            'description: "Check the health: crash rates, install counts"\n'
            "---\n"
            "body\n"
        )
        fm, body = _parse_frontmatter(text)
        assert fm["description"] == "Check the health: crash rates, install counts"

    def test_quoted_value_with_backticks(self):
        text = (
            "---\n"
            'description: "`@expo/ui/jetpack-compose` package"\n'
            "---\n"
            "body\n"
        )
        fm, _ = _parse_frontmatter(text)
        assert fm["description"] == "`@expo/ui/jetpack-compose` package"

    def test_extra_keys_preserved(self):
        text = (
            "---\n"
            "name: foo\n"
            "description: a thing\n"
            "version: 1.2.3\n"
            "license: MIT\n"
            'allowed-tools: "Read,Bash(eas *)"\n'
            "---\n"
        )
        fm, _ = _parse_frontmatter(text)
        assert fm["version"] == "1.2.3"
        assert fm["license"] == "MIT"
        assert fm["allowed-tools"] == "Read,Bash(eas *)"

    def test_unterminated_frontmatter_falls_back(self):
        text = "---\nname: foo\nno closing fence ever comes\n"
        fm, body = _parse_frontmatter(text)
        assert fm is None
        assert body == text

    def test_first_prose_line_skips_headings(self):
        text = "# Heading\n\n## Subheading\n\nFirst real line.\nSecond line.\n"
        assert _first_prose_line(text) == "First real line."


class TestExpoSkillFormat:
    """Tests for loading Anthropic/Expo-style skills with frontmatter."""

    def _write_expo_skill(
        self, skills_dir: Path, slug: str, frontmatter: str, body: str = ""
    ) -> Path:
        skill_dir = skills_dir / slug
        skill_dir.mkdir()
        path = skill_dir / "SKILL.md"
        path.write_text(f"---\n{frontmatter}---\n\n{body}")
        return path

    def test_loads_skill_with_frontmatter(self, temp_dir):
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()
        self._write_expo_skill(
            skills_dir,
            "expo-module",
            "name: expo-module\n"
            "description: Guide for writing Expo native modules.\n"
            "version: 1.0.0\n"
            "license: MIT\n",
            "# Writing Expo Modules\n\nContent here.\n",
        )

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()

        skill = loader.get_skill("expo-module")
        assert skill is not None
        assert skill.name == "expo-module"
        assert skill.description == "Guide for writing Expo native modules."
        assert skill.metadata == {"version": "1.0.0", "license": "MIT"}
        # Content is preserved including frontmatter
        assert skill.content.startswith("---\n")

    def test_name_falls_back_to_directory_when_missing(self, temp_dir):
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()
        # No `name:` key — should use parent directory
        self._write_expo_skill(
            skills_dir,
            "fallback-named",
            "description: Some skill\n",
        )

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()
        assert loader.get_skill("fallback-named") is not None

    def test_description_falls_back_to_body_when_missing(self, temp_dir):
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()
        self._write_expo_skill(
            skills_dir,
            "no-desc",
            "name: no-desc\n",
            "# Title\n\nFirst body line.\n",
        )
        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()
        assert loader.get_skill("no-desc").description == "First body line."

    def test_flat_and_nested_skills_coexist(self, temp_dir):
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()

        # Flat
        (skills_dir / "legacy.md").write_text(
            "# Legacy\n\nA legacy-format skill.\n"
        )
        # Nested (expo format)
        self._write_expo_skill(
            skills_dir,
            "modern",
            "name: modern\ndescription: Modern format skill\n",
        )

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()
        names = set(loader.get_skill_names())
        assert names == {"legacy", "modern"}
        assert loader.get_skill("legacy").metadata == {}
        assert loader.get_skill("modern").description == "Modern format skill"

    def test_does_not_recurse_into_supporting_subdirs(self, temp_dir):
        """Markdown files inside supporting subdirs (templates/, etc.) must
        not be picked up as skills — only `<slug>/SKILL.md`."""
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()
        # Real skill
        self._write_expo_skill(
            skills_dir,
            "real-skill",
            "name: real-skill\ndescription: real\n",
        )
        # A template that happens to be .md inside a deeper subdir — must
        # NOT be discovered as a skill
        templates = skills_dir / "real-skill" / "templates"
        templates.mkdir()
        (templates / "report.md").write_text("# Just a template\n")

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()
        assert loader.get_skill_names() == ["real-skill"]

    def test_summary_includes_paths_for_both_formats(self, temp_dir):
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()
        (skills_dir / "legacy.md").write_text("# Legacy\n\nDoes things.\n")
        self._write_expo_skill(
            skills_dir,
            "modern",
            "name: modern\ndescription: Modern.\n",
        )

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()
        summary = loader.get_skills_summary()
        assert "legacy.md" in summary
        assert "modern/SKILL.md" in summary

    def test_real_world_expo_module_frontmatter(self, temp_dir):
        """Smoke-check against a real-world skill from the expo-skills repo."""
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()
        self._write_expo_skill(
            skills_dir,
            "expo-module",
            "name: expo-module\n"
            "description: Guide for writing Expo native modules and views "
            "using the Expo Modules API (Swift, Kotlin, TypeScript). Covers "
            "module definition DSL, native views, shared objects, config "
            "plugins, lifecycle hooks, autolinking, and type system. Use "
            "when building or modifying native modules for Expo.\n"
            "version: 1.0.0\n"
            "license: MIT\n",
        )
        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()
        s = loader.get_skill("expo-module")
        assert s.name == "expo-module"
        assert s.description.startswith("Guide for writing Expo native modules")
        assert s.metadata["version"] == "1.0.0"
        assert s.metadata["license"] == "MIT"


def _write_plugin(
    skills_dir: Path,
    plugin_name: str,
    plugin_json: Optional[dict] = None,
    skill_slugs: Optional[list[str]] = None,
) -> Path:
    """Build `<skills_dir>/plugins/<plugin_name>/...` matching the Claude
    Code marketplace layout. Returns the plugin directory path."""
    import json as _json

    plugin_dir = skills_dir / "plugins" / plugin_name
    plugin_dir.mkdir(parents=True)
    if plugin_json is not None:
        (plugin_dir / ".claude-plugin").mkdir()
        (plugin_dir / ".claude-plugin" / "plugin.json").write_text(
            _json.dumps(plugin_json)
        )
    skills_subdir = plugin_dir / "skills"
    skills_subdir.mkdir()
    for slug in skill_slugs or []:
        s_dir = skills_subdir / slug
        s_dir.mkdir()
        (s_dir / "SKILL.md").write_text(
            f"---\nname: {slug}\ndescription: {slug} skill\nversion: 1.0.0\n---\n\n"
            f"# {slug}\n\nBody.\n"
        )
    return plugin_dir


class TestPluginLayout:
    """Tests for the .skills/plugins/<plugin>/skills/<slug>/SKILL.md layout."""

    def test_discovers_plugin_and_its_skills(self, temp_dir):
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()
        _write_plugin(
            skills_dir,
            "expo",
            plugin_json={
                "name": "expo",
                "version": "1.0.0",
                "description": "Official Expo skills",
                "author": {"name": "Expo Team", "email": "support@expo.dev"},
            },
            skill_slugs=["expo-module", "building-native-ui"],
        )

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()

        assert "expo" in loader.plugins
        plugin = loader.plugins["expo"]
        assert plugin.name == "expo"
        assert plugin.version == "1.0.0"
        assert plugin.description == "Official Expo skills"
        assert plugin.author == {"name": "Expo Team", "email": "support@expo.dev"}
        assert len(plugin.skills) == 2

    def test_skill_names_are_namespaced(self, temp_dir):
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()
        _write_plugin(skills_dir, "expo", plugin_json={"name": "expo"}, skill_slugs=["foo"])

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()
        s = loader.get_skill("expo:foo")
        assert s is not None
        assert s.plugin == "expo"
        assert s.slug == "foo"
        # Bare slug doesn't collide with the namespaced key
        assert loader.get_skill("foo") is None

    def test_summary_groups_by_plugin(self, temp_dir):
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()
        _write_plugin(
            skills_dir,
            "expo",
            plugin_json={
                "name": "expo",
                "version": "1.2.3",
                "description": "Official Expo skills",
            },
            skill_slugs=["alpha", "beta"],
        )
        # Add a standalone too
        (skills_dir / "legacy.md").write_text("# Legacy\n\nA legacy skill.\n")

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()
        summary = loader.get_skills_summary()

        assert "[Plugin: expo v1.2.3] Official Expo skills" in summary
        assert "expo:alpha" in summary
        assert "expo:beta" in summary
        assert "[Standalone skills]" in summary
        assert "legacy" in summary

    def test_missing_plugin_json_is_ok(self, temp_dir):
        """A plugin directory without plugin.json still yields skills,
        just with empty plugin metadata."""
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()
        _write_plugin(
            skills_dir,
            "anon",
            plugin_json=None,  # no .claude-plugin/plugin.json
            skill_slugs=["one"],
        )

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()
        assert "anon" in loader.plugins
        assert loader.plugins["anon"].version == ""
        assert loader.plugins["anon"].description == ""
        assert loader.get_skill("anon:one") is not None

    def test_malformed_plugin_json_does_not_crash(self, temp_dir, capsys):
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()
        plugin_dir = _write_plugin(
            skills_dir, "broken", plugin_json={}, skill_slugs=["x"]
        )
        # Replace plugin.json with garbage
        (plugin_dir / ".claude-plugin" / "plugin.json").write_text("{not json")

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        # Skill is still loaded; plugin exists with empty metadata
        assert loader.get_skill("broken:x") is not None
        assert loader.plugins["broken"].description == ""

    def test_all_three_layouts_coexist(self, temp_dir):
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()
        # Flat
        (skills_dir / "flat.md").write_text("# Flat\n\nA flat skill.\n")
        # Nested standalone
        nested = skills_dir / "nested"
        nested.mkdir()
        (nested / "SKILL.md").write_text(
            "---\nname: nested\ndescription: Nested standalone\n---\n\n"
            "# Nested\n"
        )
        # Plugin-scoped
        _write_plugin(
            skills_dir, "myplug", plugin_json={"name": "myplug"}, skill_slugs=["task"]
        )

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()
        names = set(loader.get_skill_names())
        assert names == {"flat", "nested", "myplug:task"}

    def test_plugins_dir_is_not_treated_as_a_nested_skill(self, temp_dir):
        """`<dir>/plugins/SKILL.md` should not be loaded as a standalone
        skill — the `plugins/` directory is reserved."""
        skills_dir = temp_dir / ".skills"
        skills_dir.mkdir()
        plugins_dir = skills_dir / "plugins"
        plugins_dir.mkdir()
        # A stray SKILL.md directly under plugins/ — must be ignored
        (plugins_dir / "SKILL.md").write_text(
            "---\nname: bogus\ndescription: nope\n---\n"
        )
        # And a legitimate plugin alongside it
        _write_plugin(
            skills_dir, "real", plugin_json={"name": "real"}, skill_slugs=["s"]
        )

        loader = SkillLoader(skills_dir=skills_dir)
        loader.discover_skills()
        assert "bogus" not in loader.skills
        assert loader.get_skill("real:s") is not None
