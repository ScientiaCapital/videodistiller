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


class HistoryTemplate(PromptTemplate):
    """Template for history and historical events content."""

    def __init__(self):
        super().__init__(
            name="history",
            description="Template for history and historical events"
        )

    def build_prompt(
        self,
        title: str,
        transcript: str,
        channel_title: Optional[str] = None
    ) -> str:
        """Build history-focused prompt."""
        channel_info = f"\nChannel: {channel_title}" if channel_title else ""

        return f"""You are creating a history summary for kids aged 8-11 who want to learn about the past.

{READING_LEVEL_GUIDELINES}

VIDEO INFORMATION:
Title: {title}{channel_info}

TRANSCRIPT:
{transcript}

TASK:
Create a kid-friendly summary that brings history to life for young learners.

{QA_STRUCTURE}

HISTORY-SPECIFIC GUIDELINES:
- Tell history like an exciting story with real people
- Use dates and timelines kids can understand (e.g., "About 100 years ago" or "During your great-grandparents' time")
- Connect historical events to things kids know today
- Explain WHY things happened, not just WHAT happened
- Make historical figures feel like real people with feelings and choices
- Avoid: complex political terms, too many dates, boring lists of facts
- Include: interesting details, "what if" moments, connections to today
- Make it feel like a story, not a textbook

Begin your summary below:"""


class GeographyTemplate(PromptTemplate):
    """Template for geography and world places content."""

    def __init__(self):
        super().__init__(
            name="geography",
            description="Template for geography and world places"
        )

    def build_prompt(
        self,
        title: str,
        transcript: str,
        channel_title: Optional[str] = None
    ) -> str:
        """Build geography-focused prompt."""
        channel_info = f"\nChannel: {channel_title}" if channel_title else ""

        return f"""You are creating a geography summary for kids aged 8-11 who are curious about the world.

{READING_LEVEL_GUIDELINES}

VIDEO INFORMATION:
Title: {title}{channel_info}

TRANSCRIPT:
{transcript}

TASK:
Create a kid-friendly summary that helps kids explore and understand our world.

{QA_STRUCTURE}

GEOGRAPHY-SPECIFIC GUIDELINES:
- Paint a picture of what places look, feel, and sound like
- Compare places to somewhere the kid might know
- Explain how geography affects how people live (weather, food, homes)
- Use simple directions (north, south, near the ocean, in the mountains)
- Make faraway places feel real and interesting
- Avoid: exact coordinates, complex climate zones, technical geography terms
- Include: fun facts, what it's like to live there, unique features
- Help kids imagine being there

Begin your summary below:"""


class ArtTemplate(PromptTemplate):
    """Template for art, music, and creative content."""

    def __init__(self):
        super().__init__(
            name="art",
            description="Template for art, music, and creative content"
        )

    def build_prompt(
        self,
        title: str,
        transcript: str,
        channel_title: Optional[str] = None
    ) -> str:
        """Build art-focused prompt."""
        channel_info = f"\nChannel: {channel_title}" if channel_title else ""

        return f"""You are creating an art summary for kids aged 8-11 who love creativity and making things.

{READING_LEVEL_GUIDELINES}

VIDEO INFORMATION:
Title: {title}{channel_info}

TRANSCRIPT:
{transcript}

TASK:
Create a kid-friendly summary that inspires creativity and appreciation for art.

{QA_STRUCTURE}

ART-SPECIFIC GUIDELINES:
- Describe art in ways kids can picture it (colors, shapes, feelings)
- Connect art to emotions and stories
- Explain techniques like you're teaching a friend
- Compare to art styles or things kids might have seen
- Make art feel fun and accessible, not fancy or difficult
- Avoid: complex art history terms, academic language, artist's full biographies
- Include: what makes it special, how it was made, what it means
- Encourage kids to think about creating their own art

Begin your summary below:"""


class ScienceTemplate(PromptTemplate):
    """Template for science and discovery content."""

    def __init__(self):
        super().__init__(
            name="science",
            description="Template for science and discovery content"
        )

    def build_prompt(
        self,
        title: str,
        transcript: str,
        channel_title: Optional[str] = None
    ) -> str:
        """Build science-focused prompt."""
        channel_info = f"\nChannel: {channel_title}" if channel_title else ""

        return f"""You are creating a science summary for kids aged 8-11 who love asking "why" and "how".

{READING_LEVEL_GUIDELINES}

VIDEO INFORMATION:
Title: {title}{channel_info}

TRANSCRIPT:
{transcript}

TASK:
Create a kid-friendly summary that makes science exciting and understandable.

{QA_STRUCTURE}

SCIENCE-SPECIFIC GUIDELINES:
- Explain science like a cool experiment or discovery story
- Use everyday comparisons (e.g., "Your heart is like a pump")
- Break down processes into simple steps
- Connect to things kids can observe in their own lives
- Make science feel like detective work and discovery
- Avoid: chemical formulas, complex scientific names, heavy jargon
- Include: cool facts, "wow" moments, things kids can try at home
- Encourage curiosity and questions

Begin your summary below:"""


class STEMTemplate(PromptTemplate):
    """Template for STEM (Science, Technology, Engineering, Math) content."""

    def __init__(self):
        super().__init__(
            name="stem",
            description="Template for STEM education content"
        )

    def build_prompt(
        self,
        title: str,
        transcript: str,
        channel_title: Optional[str] = None
    ) -> str:
        """Build STEM-focused prompt."""
        channel_info = f"\nChannel: {channel_title}" if channel_title else ""

        return f"""You are creating a STEM summary for kids aged 8-11 who love building, solving, and figuring things out.

{READING_LEVEL_GUIDELINES}

VIDEO INFORMATION:
Title: {title}{channel_info}

TRANSCRIPT:
{transcript}

TASK:
Create a kid-friendly summary that makes STEM concepts fun and hands-on.

{QA_STRUCTURE}

STEM-SPECIFIC GUIDELINES:
- Show how STEM solves real problems
- Use examples from games, toys, or everyday objects
- Break complex ideas into "building blocks"
- Emphasize the "why" behind how things work
- Make it feel like a fun challenge or puzzle
- Avoid: heavy math, complex equations, abstract theories
- Include: practical examples, "try this" ideas, real-world uses
- Connect to things kids can build or create

Begin your summary below:"""


class ProgrammingTemplate(PromptTemplate):
    """Template for programming and coding content."""

    def __init__(self):
        super().__init__(
            name="programming",
            description="Template for programming and coding content"
        )

    def build_prompt(
        self,
        title: str,
        transcript: str,
        channel_title: Optional[str] = None
    ) -> str:
        """Build programming-focused prompt."""
        channel_info = f"\nChannel: {channel_title}" if channel_title else ""

        return f"""You are creating a programming summary for kids aged 8-11 who want to learn about coding.

{READING_LEVEL_GUIDELINES}

VIDEO INFORMATION:
Title: {title}{channel_info}

TRANSCRIPT:
{transcript}

TASK:
Create a kid-friendly summary that makes programming feel like giving instructions to a friendly robot.

{QA_STRUCTURE}

PROGRAMMING-SPECIFIC GUIDELINES:
- Compare coding to things kids do (giving directions, recipes, game rules)
- Use the idea of "step-by-step instructions"
- Explain coding concepts without actual code
- Show what you can create or make happen with programming
- Make it feel like magic you can control
- Avoid: actual code syntax, complex programming terms, language-specific details
- Include: what programming can do, simple examples, cool projects
- Encourage kids to think like problem-solvers

Begin your summary below:"""


# Template registry
TEMPLATES = {
    "general": GeneralTemplate(),
    "tech_ai": TechAITemplate(),
    "finance": FinanceTemplate(),
    "history": HistoryTemplate(),
    "geography": GeographyTemplate(),
    "art": ArtTemplate(),
    "science": ScienceTemplate(),
    "stem": STEMTemplate(),
    "programming": ProgrammingTemplate(),
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
        Template name
    """
    content = f"{title} {transcript}".lower()

    # Programming keywords (check first - most specific)
    programming_keywords = [
        "code", "coding", "python", "javascript", "programming",
        "function", "variable", "loop", "debug", "syntax",
        "developer", "scratch", "html", "css"
    ]

    # STEM keywords
    stem_keywords = [
        "stem", "engineering", "build", "design", "maker",
        "3d print", "robotics", "circuit", "experiment", "prototype"
    ]

    # Science keywords
    science_keywords = [
        "science", "experiment", "discovery", "biology", "chemistry",
        "physics", "molecule", "cell", "planet", "space",
        "astronaut", "scientist", "lab", "hypothesis"
    ]

    # History keywords
    history_keywords = [
        "history", "ancient", "war", "empire", "century",
        "historical", "past", "civilization", "revolution",
        "president", "king", "queen", "dynasty", "medieval"
    ]

    # Geography keywords
    geography_keywords = [
        "geography", "country", "continent", "ocean", "mountain",
        "river", "city", "climate", "culture", "nation",
        "world", "map", "capital", "region", "territory"
    ]

    # Art keywords
    art_keywords = [
        "art", "paint", "draw", "music", "artist",
        "painting", "sculpture", "museum", "creative", "design",
        "color", "canvas", "musician", "composer", "instrument"
    ]

    # Tech/AI keywords
    tech_keywords = [
        "ai", "artificial intelligence", "machine learning", "robot",
        "computer", "software", "algorithm", "technology",
        "digital", "internet", "app", "data", "neural"
    ]

    # Finance keywords
    finance_keywords = [
        "money", "dollar", "invest", "stock", "market", "bitcoin",
        "crypto", "economy", "finance", "business", "bank", "trade",
        "price", "cost", "wealth", "profit", "revenue"
    ]

    # Count keyword matches
    scores = {
        "programming": sum(1 for kw in programming_keywords if kw in content),
        "stem": sum(1 for kw in stem_keywords if kw in content),
        "science": sum(1 for kw in science_keywords if kw in content),
        "history": sum(1 for kw in history_keywords if kw in content),
        "geography": sum(1 for kw in geography_keywords if kw in content),
        "art": sum(1 for kw in art_keywords if kw in content),
        "tech_ai": sum(1 for kw in tech_keywords if kw in content),
        "finance": sum(1 for kw in finance_keywords if kw in content),
    }

    # Get template with highest score (minimum 2 matches required)
    max_score = max(scores.values())
    if max_score >= 2:
        # Return first template with max score (order matters for ties)
        for template, score in scores.items():
            if score == max_score:
                return template

    return "general"
