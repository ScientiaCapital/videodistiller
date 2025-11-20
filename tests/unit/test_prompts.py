"""Tests for prompt templates."""

import pytest

from src.llm.prompts import (
    GeneralTemplate,
    TechAITemplate,
    FinanceTemplate,
    HistoryTemplate,
    GeographyTemplate,
    ArtTemplate,
    ScienceTemplate,
    STEMTemplate,
    ProgrammingTemplate,
    get_template,
    auto_detect_template,
    TEMPLATES,
)


class TestPromptTemplates:
    """Test prompt template classes."""

    def test_general_template_creation(self):
        """Test creating general template."""
        template = GeneralTemplate()
        assert template.name == "general"
        assert template.description == "General template for educational content"

    def test_tech_ai_template_creation(self):
        """Test creating tech/AI template."""
        template = TechAITemplate()
        assert template.name == "tech_ai"
        assert template.description == "Template for technology and AI content"

    def test_finance_template_creation(self):
        """Test creating finance template."""
        template = FinanceTemplate()
        assert template.name == "finance"
        assert template.description == "Template for finance and economics content"

    def test_general_template_build_prompt(self):
        """Test building prompt with general template."""
        template = GeneralTemplate()
        prompt = template.build_prompt(
            title="How Plants Grow",
            transcript="Plants need water and sunlight to grow...",
            channel_title="Science for Kids"
        )

        assert "How Plants Grow" in prompt
        assert "Science for Kids" in prompt
        assert "Plants need water and sunlight to grow" in prompt
        assert "Grade 5-6" in prompt
        assert "What is this about?" in prompt
        assert "Why should I care?" in prompt
        assert "How does it work?" in prompt
        assert "What can I learn from this?" in prompt

    def test_general_template_without_channel(self):
        """Test building prompt without channel title."""
        template = GeneralTemplate()
        prompt = template.build_prompt(
            title="Test Video",
            transcript="Test content"
        )

        assert "Test Video" in prompt
        assert "Test content" in prompt
        assert "Channel:" not in prompt

    def test_tech_ai_template_build_prompt(self):
        """Test building prompt with tech/AI template."""
        template = TechAITemplate()
        prompt = template.build_prompt(
            title="How AI Works",
            transcript="Artificial intelligence uses neural networks...",
            channel_title="Tech Explained"
        )

        assert "How AI Works" in prompt
        assert "Tech Explained" in prompt
        assert "Artificial intelligence uses neural networks" in prompt
        assert "tech" in prompt.lower() or "technology" in prompt.lower()
        assert "robot brain" in prompt.lower() or "analogies" in prompt.lower()

    def test_finance_template_build_prompt(self):
        """Test building prompt with finance template."""
        template = FinanceTemplate()
        prompt = template.build_prompt(
            title="Understanding the Stock Market",
            transcript="Stocks represent ownership in companies...",
            channel_title="Money 101"
        )

        assert "Understanding the Stock Market" in prompt
        assert "Money 101" in prompt
        assert "Stocks represent ownership in companies" in prompt
        assert "money" in prompt.lower() or "finance" in prompt.lower()
        assert "allowance" in prompt.lower() or "saving" in prompt.lower()

    def test_history_template_build_prompt(self):
        """Test building prompt with history template."""
        template = HistoryTemplate()
        prompt = template.build_prompt(
            title="The American Revolution",
            transcript="In 1776, the colonies declared independence...",
            channel_title="History for Kids"
        )

        assert "The American Revolution" in prompt
        assert "History for Kids" in prompt
        assert "In 1776, the colonies declared independence" in prompt
        assert "history" in prompt.lower() or "historical" in prompt.lower()
        assert "story" in prompt.lower() or "past" in prompt.lower()

    def test_geography_template_build_prompt(self):
        """Test building prompt with geography template."""
        template = GeographyTemplate()
        prompt = template.build_prompt(
            title="Exploring the Amazon Rainforest",
            transcript="The Amazon is the largest rainforest...",
            channel_title="World Explorers"
        )

        assert "Exploring the Amazon Rainforest" in prompt
        assert "World Explorers" in prompt
        assert "The Amazon is the largest rainforest" in prompt
        assert "geography" in prompt.lower() or "world" in prompt.lower()
        assert "place" in prompt.lower() or "imagine" in prompt.lower()

    def test_art_template_build_prompt(self):
        """Test building prompt with art template."""
        template = ArtTemplate()
        prompt = template.build_prompt(
            title="Understanding Impressionism",
            transcript="Impressionist painters used light and color...",
            channel_title="Art Adventures"
        )

        assert "Understanding Impressionism" in prompt
        assert "Art Adventures" in prompt
        assert "Impressionist painters used light and color" in prompt
        assert "art" in prompt.lower() or "creative" in prompt.lower()
        assert "color" in prompt.lower() or "create" in prompt.lower()

    def test_science_template_build_prompt(self):
        """Test building prompt with science template."""
        template = ScienceTemplate()
        prompt = template.build_prompt(
            title="How Photosynthesis Works",
            transcript="Plants convert sunlight into energy...",
            channel_title="Science Explorers"
        )

        assert "How Photosynthesis Works" in prompt
        assert "Science Explorers" in prompt
        assert "Plants convert sunlight into energy" in prompt
        assert "science" in prompt.lower() or "scientific" in prompt.lower()
        assert "experiment" in prompt.lower() or "discovery" in prompt.lower()

    def test_stem_template_build_prompt(self):
        """Test building prompt with STEM template."""
        template = STEMTemplate()
        prompt = template.build_prompt(
            title="Building Bridges",
            transcript="Engineers design bridges to be strong...",
            channel_title="STEM Kids"
        )

        assert "Building Bridges" in prompt
        assert "STEM Kids" in prompt
        assert "Engineers design bridges to be strong" in prompt
        assert "stem" in prompt.lower() or "build" in prompt.lower()
        assert "engineer" in prompt.lower() or "problem" in prompt.lower()

    def test_programming_template_build_prompt(self):
        """Test building prompt with programming template."""
        template = ProgrammingTemplate()
        prompt = template.build_prompt(
            title="Introduction to Coding",
            transcript="Programming is giving instructions to computers...",
            channel_title="Code Academy Kids"
        )

        assert "Introduction to Coding" in prompt
        assert "Code Academy Kids" in prompt
        assert "Programming is giving instructions to computers" in prompt
        assert "programming" in prompt.lower() or "coding" in prompt.lower()
        assert "robot" in prompt.lower() or "instructions" in prompt.lower()


class TestGetTemplate:
    """Test template retrieval function."""

    def test_get_general_template(self):
        """Test getting general template."""
        template = get_template("general")
        assert isinstance(template, GeneralTemplate)

    def test_get_tech_ai_template(self):
        """Test getting tech/AI template."""
        template = get_template("tech_ai")
        assert isinstance(template, TechAITemplate)

    def test_get_finance_template(self):
        """Test getting finance template."""
        template = get_template("finance")
        assert isinstance(template, FinanceTemplate)

    def test_get_history_template(self):
        """Test getting history template."""
        template = get_template("history")
        assert isinstance(template, HistoryTemplate)

    def test_get_geography_template(self):
        """Test getting geography template."""
        template = get_template("geography")
        assert isinstance(template, GeographyTemplate)

    def test_get_art_template(self):
        """Test getting art template."""
        template = get_template("art")
        assert isinstance(template, ArtTemplate)

    def test_get_science_template(self):
        """Test getting science template."""
        template = get_template("science")
        assert isinstance(template, ScienceTemplate)

    def test_get_stem_template(self):
        """Test getting STEM template."""
        template = get_template("stem")
        assert isinstance(template, STEMTemplate)

    def test_get_programming_template(self):
        """Test getting programming template."""
        template = get_template("programming")
        assert isinstance(template, ProgrammingTemplate)

    def test_get_default_template(self):
        """Test getting default template."""
        template = get_template()
        assert isinstance(template, GeneralTemplate)

    def test_get_invalid_template(self):
        """Test error on invalid template name."""
        with pytest.raises(ValueError) as exc_info:
            get_template("nonexistent")

        assert "Unknown template" in str(exc_info.value)
        assert "nonexistent" in str(exc_info.value)


class TestAutoDetectTemplate:
    """Test auto-detection of templates."""

    def test_detect_tech_ai_template(self):
        """Test detecting tech/AI template."""
        result = auto_detect_template(
            title="How Artificial Intelligence Works",
            transcript="Machine learning and neural networks use algorithms..."
        )
        assert result == "tech_ai"

    def test_detect_tech_ai_from_keywords(self):
        """Test detecting tech/AI from various keywords."""
        result = auto_detect_template(
            title="Building Apps",
            transcript="Programming software with code and algorithms..."
        )
        assert result == "tech_ai"

    def test_detect_finance_template(self):
        """Test detecting finance template."""
        result = auto_detect_template(
            title="Understanding Bitcoin",
            transcript="Cryptocurrency and investing in the stock market..."
        )
        assert result == "finance"

    def test_detect_finance_from_keywords(self):
        """Test detecting finance from various keywords."""
        result = auto_detect_template(
            title="Making Money",
            transcript="Learn about profit, revenue, and business economics..."
        )
        assert result == "finance"

    def test_detect_general_template_fallback(self):
        """Test fallback to general template."""
        result = auto_detect_template(
            title="Interesting Facts About Elephants",
            transcript="Elephants are amazing animals that live in groups..."
        )
        assert result == "general"

    def test_detect_with_low_keyword_count(self):
        """Test general template when keyword count is low."""
        result = auto_detect_template(
            title="Interesting Topic",
            transcript="This is about something with one AI mention but mostly other stuff..."
        )
        # Should be general because tech_score < 2
        assert result == "general"

    def test_detect_programming_template(self):
        """Test detecting programming template."""
        result = auto_detect_template(
            title="Learn Python Programming",
            transcript="In this coding tutorial, we'll learn about variables and loops in Python..."
        )
        assert result == "programming"

    def test_detect_stem_template(self):
        """Test detecting STEM template."""
        result = auto_detect_template(
            title="Build a Robot",
            transcript="Engineering and design come together when we build robots using circuits..."
        )
        assert result == "stem"

    def test_detect_science_template(self):
        """Test detecting science template."""
        result = auto_detect_template(
            title="Biology Experiment",
            transcript="Scientists discover how cells work through experiments in the lab..."
        )
        assert result == "science"

    def test_detect_history_template(self):
        """Test detecting history template."""
        result = auto_detect_template(
            title="Ancient Rome",
            transcript="The Roman Empire was a civilization that ruled for many centuries in history..."
        )
        assert result == "history"

    def test_detect_geography_template(self):
        """Test detecting geography template."""
        result = auto_detect_template(
            title="World Geography",
            transcript="This country is located on the continent near the ocean with many mountains..."
        )
        assert result == "geography"

    def test_detect_art_template(self):
        """Test detecting art template."""
        result = auto_detect_template(
            title="Painting Techniques",
            transcript="Artists use color and paint to create beautiful art on canvas..."
        )
        assert result == "art"

    def test_detect_priority_order(self):
        """Test that more specific templates are detected first."""
        # Programming should be detected before tech_ai
        result = auto_detect_template(
            title="Python Coding Tutorial",
            transcript="Learn to code with Python programming and computer software..."
        )
        assert result == "programming"


class TestTemplateRegistry:
    """Test template registry."""

    def test_all_templates_registered(self):
        """Test that all templates are in registry."""
        assert "general" in TEMPLATES
        assert "tech_ai" in TEMPLATES
        assert "finance" in TEMPLATES
        assert "history" in TEMPLATES
        assert "geography" in TEMPLATES
        assert "art" in TEMPLATES
        assert "science" in TEMPLATES
        assert "stem" in TEMPLATES
        assert "programming" in TEMPLATES

    def test_registry_templates_are_instances(self):
        """Test that registry contains template instances."""
        assert isinstance(TEMPLATES["general"], GeneralTemplate)
        assert isinstance(TEMPLATES["tech_ai"], TechAITemplate)
        assert isinstance(TEMPLATES["finance"], FinanceTemplate)
        assert isinstance(TEMPLATES["history"], HistoryTemplate)
        assert isinstance(TEMPLATES["geography"], GeographyTemplate)
        assert isinstance(TEMPLATES["art"], ArtTemplate)
        assert isinstance(TEMPLATES["science"], ScienceTemplate)
        assert isinstance(TEMPLATES["stem"], STEMTemplate)
        assert isinstance(TEMPLATES["programming"], ProgrammingTemplate)
