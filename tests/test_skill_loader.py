"""Tests for the skill_loader module."""

from pathlib import Path

import pytest

from skills.skill_loader import Skill, SkillLoader


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
