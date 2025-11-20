"""OpenRouter API client with cost tracking and retry logic."""

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class ModelPricing(BaseModel):
    """Pricing information for an LLM model."""

    prompt_cost_per_million: float  # Cost per 1M prompt tokens
    completion_cost_per_million: float  # Cost per 1M completion tokens


# Model pricing (as of 2024, from OpenRouter)
MODEL_PRICING = {
    "qwen/qwen-2.5-72b-instruct": ModelPricing(
        prompt_cost_per_million=0.35,
        completion_cost_per_million=0.35
    ),
    "anthropic/claude-3-haiku": ModelPricing(
        prompt_cost_per_million=0.25,
        completion_cost_per_million=1.25
    ),
    "meta-llama/llama-3.1-8b-instruct": ModelPricing(
        prompt_cost_per_million=0.06,
        completion_cost_per_million=0.06
    ),
}


@dataclass
class UsageMetrics:
    """Token usage and cost metrics for a single API call."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    model: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost": self.cost,
            "model": self.model,
            "timestamp": self.timestamp.isoformat()
        }


class CostTracker:
    """Tracks LLM API costs and enforces budget limits."""

    def __init__(
        self,
        data_dir: Path,
        max_monthly_cost: float = 10.0,
        warn_at_cost: float = 8.0
    ):
        """Initialize cost tracker.

        Args:
            data_dir: Directory to store cost tracking data
            max_monthly_cost: Maximum allowed spend per month (USD)
            warn_at_cost: Threshold to log warnings (USD)
        """
        self.data_dir = Path(data_dir)
        self.max_monthly_cost = max_monthly_cost
        self.warn_at_cost = warn_at_cost
        self.cost_file = self.data_dir / "llm_costs.json"

        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load existing costs
        self._costs: dict[str, list[dict]] = self._load_costs()

        # Ensure cost file exists
        if not self.cost_file.exists():
            self._save_costs()

    def _load_costs(self) -> dict[str, list[dict]]:
        """Load cost history from disk."""
        if not self.cost_file.exists():
            return {}

        try:
            with open(self.cost_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load cost history: {e}")
            return {}

    def _save_costs(self) -> None:
        """Save cost history to disk."""
        try:
            with open(self.cost_file, 'w') as f:
                json.dump(self._costs, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save cost history: {e}")

    def _get_current_month_key(self) -> str:
        """Get the key for the current month (YYYY-MM)."""
        return datetime.now().strftime("%Y-%m")

    def track_usage(self, metrics: UsageMetrics) -> None:
        """Track usage metrics and update costs.

        Args:
            metrics: Usage metrics to track
        """
        month_key = self._get_current_month_key()

        if month_key not in self._costs:
            self._costs[month_key] = []

        self._costs[month_key].append(metrics.to_dict())
        self._save_costs()

        # Check budget limits
        current_cost = self.get_month_cost()

        if current_cost >= self.max_monthly_cost:
            raise BudgetExceededError(
                f"Monthly budget exceeded: ${current_cost:.2f} / ${self.max_monthly_cost:.2f}"
            )
        elif current_cost >= self.warn_at_cost:
            logger.warning(
                f"Approaching monthly budget: ${current_cost:.2f} / ${self.max_monthly_cost:.2f}"
            )

    def get_month_cost(self, month_key: Optional[str] = None) -> float:
        """Get total cost for a specific month.

        Args:
            month_key: Month to query (YYYY-MM), defaults to current month

        Returns:
            Total cost in USD
        """
        if month_key is None:
            month_key = self._get_current_month_key()

        costs = self._costs.get(month_key, [])
        return sum(item["cost"] for item in costs)

    def get_remaining_budget(self) -> float:
        """Get remaining budget for current month."""
        return self.max_monthly_cost - self.get_month_cost()

    def get_usage_summary(self) -> dict:
        """Get summary of current month's usage."""
        month_key = self._get_current_month_key()
        costs = self._costs.get(month_key, [])

        total_tokens = sum(item["total_tokens"] for item in costs)
        total_cost = sum(item["cost"] for item in costs)

        return {
            "month": month_key,
            "total_requests": len(costs),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "remaining_budget": self.get_remaining_budget(),
            "budget_used_percent": (total_cost / self.max_monthly_cost) * 100
        }


class BudgetExceededError(Exception):
    """Raised when monthly budget is exceeded."""
    pass


class OpenRouterClient:
    """Client for OpenRouter API with cost tracking and retry logic."""

    def __init__(
        self,
        api_key: str,
        model: str = "qwen/qwen-2.5-72b-instruct",
        cost_tracker: Optional[CostTracker] = None,
        max_retries: int = 3,
        timeout: int = 60
    ):
        """Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key
            model: Model to use for completions
            cost_tracker: Cost tracker instance (optional)
            max_retries: Maximum number of retries on failure
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.cost_tracker = cost_tracker
        self.max_retries = max_retries
        self.timeout = timeout

        self.base_url = "https://openrouter.ai/api/v1"

        # Validate model has pricing info
        if model not in MODEL_PRICING:
            logger.warning(f"No pricing info for model {model}, cost tracking may be inaccurate")

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for a completion.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Total cost in USD
        """
        pricing = MODEL_PRICING.get(self.model)
        if not pricing:
            logger.warning(f"No pricing info for {self.model}, returning 0 cost")
            return 0.0

        prompt_cost = (prompt_tokens / 1_000_000) * pricing.prompt_cost_per_million
        completion_cost = (completion_tokens / 1_000_000) * pricing.completion_cost_per_million

        return prompt_cost + completion_cost

    def complete(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> tuple[str, UsageMetrics]:
        """Generate a completion with retry logic and cost tracking.

        Args:
            prompt: The prompt to complete
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional parameters for the API

        Returns:
            Tuple of (completion_text, usage_metrics)

        Raises:
            BudgetExceededError: If monthly budget is exceeded
            httpx.HTTPError: If all retries fail
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }

        last_exception = None

        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()

                    data = response.json()

                    # Extract completion and usage
                    completion = data["choices"][0]["message"]["content"]
                    usage = data["usage"]

                    # Calculate cost
                    cost = self._calculate_cost(
                        usage["prompt_tokens"],
                        usage["completion_tokens"]
                    )

                    # Create metrics
                    metrics = UsageMetrics(
                        prompt_tokens=usage["prompt_tokens"],
                        completion_tokens=usage["completion_tokens"],
                        total_tokens=usage["total_tokens"],
                        cost=cost,
                        model=self.model
                    )

                    # Track cost
                    if self.cost_tracker:
                        self.cost_tracker.track_usage(metrics)

                    logger.info(
                        f"Completion generated: {usage['total_tokens']} tokens, "
                        f"${cost:.4f} cost"
                    )

                    return completion, metrics

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limit
                    wait_time = (2 ** attempt) * 2  # Exponential backoff
                    logger.warning(f"Rate limited, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    last_exception = e
                elif e.response.status_code >= 500:  # Server error
                    wait_time = (2 ** attempt)
                    logger.warning(f"Server error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    last_exception = e
                else:
                    # Client error, don't retry
                    raise
            except (httpx.RequestError, httpx.TimeoutException) as e:
                wait_time = (2 ** attempt)
                logger.warning(f"Request failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
                last_exception = e

        # All retries exhausted
        raise last_exception or Exception("All retries failed")
