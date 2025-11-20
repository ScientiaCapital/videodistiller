"""Tests for prompt templates."""

import pytest

from src.llm.prompts import (
    GeneralTemplate,
    TechAITemplate,
    FinanceTemplate,
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
            title="The History of Ancient Rome",
            transcript="The Roman Empire was a powerful civilization..."
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

    def test_detect_prefers_tech_over_finance(self):
        """Test that tech is preferred when both scores are equal."""
        result = auto_detect_template(
            title="AI for Finance",
            transcript="Machine learning algorithms predict stock market prices using data..."
        )
        # Both tech and finance keywords present, but tech should win
        assert result == "tech_ai"


class TestTemplateRegistry:
    """Test template registry."""

    def test_all_templates_registered(self):
        """Test that all templates are in registry."""
        assert "general" in TEMPLATES
        assert "tech_ai" in TEMPLATES
        assert "finance" in TEMPLATES

    def test_registry_templates_are_instances(self):
        """Test that registry contains template instances."""
        assert isinstance(TEMPLATES["general"], GeneralTemplate)
        assert isinstance(TEMPLATES["tech_ai"], TechAITemplate)
        assert isinstance(TEMPLATES["finance"], FinanceTemplate)
