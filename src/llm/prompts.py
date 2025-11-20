"""Prompt templates for LLM-powered video summarization."""

from typing import Optional

# Reading level guidelines
READING_LEVEL_GUIDELINES = """
TARGET READING LEVEL: Grade 5-6 (Ages 10-12)

Writing Guidelines:
- Use simple, clear sentences (10-15 words average)
- Avoid complex vocabulary - use everyday words
- Break up long explanations into short paragraphs
- Use concrete examples kids can relate to
- Avoid jargon - explain technical terms simply
- Use active voice ("Scientists discovered" not "It was discovered by scientists")
- Keep paragraphs to 3-4 sentences maximum
"""

# Q&A Format Structure
QA_STRUCTURE = """
Answer these questions in order:

1. **What is this about?**
   Write 2-3 sentences explaining the main topic in simple terms.

2. **Why should I care?**
   Explain in 2-3 sentences why this topic matters or is interesting.

3. **How does it work?**
   Break down the key ideas or processes in 4-5 short bullet points.

4. **What can I learn from this?**
   List 3-4 key takeaways or lessons in simple language.
"""


class PromptTemplate:
    """Base class for prompt templates."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def build_prompt(
        self,
        title: str,
        transcript: str,
        channel_title: Optional[str] = None
    ) -> str:
        """Build the complete prompt for summarization.

        Args:
            title: Video title
            transcript: Full video transcript
            channel_title: Channel name (optional)

        Returns:
            Complete prompt ready for LLM
        """
        raise NotImplementedError


class GeneralTemplate(PromptTemplate):
    """General-purpose template for educational content."""

    def __init__(self):
        super().__init__(
            name="general",
            description="General template for educational content"
        )

    def build_prompt(
        self,
        title: str,
        transcript: str,
        channel_title: Optional[str] = None
    ) -> str:
        """Build general education prompt."""
        channel_info = f"\nChannel: {channel_title}" if channel_title else ""

        return f"""You are creating a summary for kids aged 8-11 who want to learn from YouTube videos.

{READING_LEVEL_GUIDELINES}

VIDEO INFORMATION:
Title: {title}{channel_info}

TRANSCRIPT:
{transcript}

TASK:
Create a kid-friendly summary that makes this content easy to understand.

{QA_STRUCTURE}

IMPORTANT:
- Write at a Grade 5-6 reading level (like you're talking to a 10-year-old)
- Use simple words and short sentences
- Make it engaging and fun to read
- Focus on the most interesting and important ideas
- Skip boring or overly technical parts
- Use examples kids can relate to

Begin your summary below:"""


class TechAITemplate(PromptTemplate):
    """Template for technology and AI-related content."""

    def __init__(self):
        super().__init__(
            name="tech_ai",
            description="Template for technology and AI content"
        )

    def build_prompt(
        self,
        title: str,
        transcript: str,
        channel_title: Optional[str] = None
    ) -> str:
        """Build tech/AI-focused prompt."""
        channel_info = f"\nChannel: {channel_title}" if channel_title else ""

        return f"""You are creating a tech summary for kids aged 8-11 who are curious about computers, AI, and technology.

{READING_LEVEL_GUIDELINES}

VIDEO INFORMATION:
Title: {title}{channel_info}

TRANSCRIPT:
{transcript}

TASK:
Create a kid-friendly summary that explains this technology in a way kids can understand.

{QA_STRUCTURE}

TECH-SPECIFIC GUIDELINES:
- Compare technology to everyday things kids know (e.g., "AI is like a super smart robot brain")
- Break down complex tech terms into simple ideas
- Use analogies and comparisons kids can relate to
- Focus on what the technology DOES, not how it's programmed
- Make it sound exciting and cool (because tech IS cool!)
- Avoid: code, algorithms, technical jargon
- Include: real-world examples, fun facts, "Did you know?" moments

Begin your summary below:"""


class FinanceTemplate(PromptTemplate):
    """Template for finance and economics content."""

    def __init__(self):
        super().__init__(
            name="finance",
            description="Template for finance and economics content"
        )

    def build_prompt(
        self,
        title: str,
        transcript: str,
        channel_title: Optional[str] = None
    ) -> str:
        """Build finance-focused prompt."""
        channel_info = f"\nChannel: {channel_title}" if channel_title else ""

        return f"""You are creating a finance summary for kids aged 8-11 who want to learn about money and how the world of business works.

{READING_LEVEL_GUIDELINES}

VIDEO INFORMATION:
Title: {title}{channel_info}

TRANSCRIPT:
{transcript}

TASK:
Create a kid-friendly summary that explains these money concepts in a way kids can understand.

{QA_STRUCTURE}

FINANCE-SPECIFIC GUIDELINES:
- Use examples with allowance, saving, or buying things kids want
- Compare financial concepts to simple trades or exchanges
- Avoid: stock tickers, complex market terms, percentages
- Include: real-world examples kids can relate to
- Make connections to things kids do (saving, spending, earning)
- Use simple comparisons (e.g., "The stock market is like a big store where people buy tiny pieces of companies")
- Focus on the big picture, not detailed numbers
- Make it practical and relevant to kids' lives

Begin your summary below:"""


# Template registry
TEMPLATES = {
    "general": GeneralTemplate(),
    "tech_ai": TechAITemplate(),
    "finance": FinanceTemplate(),
}


def get_template(name: str = "general") -> PromptTemplate:
    """Get a prompt template by name.

    Args:
        name: Template name (general, tech_ai, finance)

    Returns:
        PromptTemplate instance

    Raises:
        ValueError: If template name not found
    """
    if name not in TEMPLATES:
        raise ValueError(
            f"Unknown template: {name}. "
            f"Available templates: {list(TEMPLATES.keys())}"
        )
    return TEMPLATES[name]


def auto_detect_template(title: str, transcript: str) -> str:
    """Auto-detect the best template based on content.

    Args:
        title: Video title
        transcript: Video transcript

    Returns:
        Template name (general, tech_ai, finance)
    """
    content = f"{title} {transcript}".lower()

    # Tech/AI keywords
    tech_keywords = [
        "ai", "artificial intelligence", "machine learning", "robot",
        "computer", "software", "algorithm", "programming", "code",
        "technology", "digital", "internet", "app", "data", "neural"
    ]

    # Finance keywords
    finance_keywords = [
        "money", "dollar", "invest", "stock", "market", "bitcoin",
        "crypto", "economy", "finance", "business", "bank", "trade",
        "price", "cost", "wealth", "profit", "revenue"
    ]

    # Count keyword matches
    tech_score = sum(1 for kw in tech_keywords if kw in content)
    finance_score = sum(1 for kw in finance_keywords if kw in content)

    # Return template with highest score
    # Prefer tech when scores are equal
    if tech_score >= finance_score and tech_score >= 2:
        return "tech_ai"
    elif finance_score >= 2:
        return "finance"
    else:
        return "general"
