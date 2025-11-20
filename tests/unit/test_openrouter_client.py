"""Tests for OpenRouter API client."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
import pytest

from src.llm.openrouter_client import (
    BudgetExceededError,
    CostTracker,
    ModelPricing,
    OpenRouterClient,
    UsageMetrics,
    MODEL_PRICING,
)


class TestUsageMetrics:
    """Test UsageMetrics dataclass."""

    def test_usage_metrics_creation(self):
        """Test creating usage metrics."""
        metrics = UsageMetrics(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            cost=0.0525,
            model="qwen/qwen-2.5-72b-instruct"
        )

        assert metrics.prompt_tokens == 100
        assert metrics.completion_tokens == 50
        assert metrics.total_tokens == 150
        assert metrics.cost == 0.0525
        assert metrics.model == "qwen/qwen-2.5-72b-instruct"
        assert isinstance(metrics.timestamp, datetime)

    def test_usage_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = UsageMetrics(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            cost=0.0525,
            model="qwen/qwen-2.5-72b-instruct"
        )

        data = metrics.to_dict()

        assert data["prompt_tokens"] == 100
        assert data["completion_tokens"] == 50
        assert data["total_tokens"] == 150
        assert data["cost"] == 0.0525
        assert data["model"] == "qwen/qwen-2.5-72b-instruct"
        assert "timestamp" in data


class TestCostTracker:
    """Test CostTracker."""

    def test_cost_tracker_initialization(self):
        """Test initializing cost tracker."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = CostTracker(
                data_dir=Path(tmpdir),
                max_monthly_cost=10.0,
                warn_at_cost=8.0
            )

            assert tracker.max_monthly_cost == 10.0
            assert tracker.warn_at_cost == 8.0
            assert tracker.cost_file.exists()

    def test_track_usage(self):
        """Test tracking usage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = CostTracker(data_dir=Path(tmpdir))

            metrics = UsageMetrics(
                prompt_tokens=1000,
                completion_tokens=500,
                total_tokens=1500,
                cost=0.525,
                model="qwen/qwen-2.5-72b-instruct"
            )

            tracker.track_usage(metrics)

            # Verify cost was tracked
            assert tracker.get_month_cost() == 0.525

    def test_budget_exceeded(self):
        """Test budget exceeded error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = CostTracker(
                data_dir=Path(tmpdir),
                max_monthly_cost=1.0
            )

            metrics = UsageMetrics(
                prompt_tokens=5_000_000,
                completion_tokens=5_000_000,
                total_tokens=10_000_000,
                cost=3.5,  # Exceeds budget
                model="qwen/qwen-2.5-72b-instruct"
            )

            with pytest.raises(BudgetExceededError):
                tracker.track_usage(metrics)

    def test_get_remaining_budget(self):
        """Test getting remaining budget."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = CostTracker(
                data_dir=Path(tmpdir),
                max_monthly_cost=10.0
            )

            assert tracker.get_remaining_budget() == 10.0

            metrics = UsageMetrics(
                prompt_tokens=1000,
                completion_tokens=500,
                total_tokens=1500,
                cost=2.5,
                model="qwen/qwen-2.5-72b-instruct"
            )
            tracker.track_usage(metrics)

            assert tracker.get_remaining_budget() == 7.5

    def test_get_usage_summary(self):
        """Test getting usage summary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = CostTracker(data_dir=Path(tmpdir))

            metrics = UsageMetrics(
                prompt_tokens=1000,
                completion_tokens=500,
                total_tokens=1500,
                cost=0.525,
                model="qwen/qwen-2.5-72b-instruct"
            )
            tracker.track_usage(metrics)

            summary = tracker.get_usage_summary()

            assert summary["total_requests"] == 1
            assert summary["total_tokens"] == 1500
            assert summary["total_cost"] == 0.525
            assert summary["remaining_budget"] == 9.475
            assert abs(summary["budget_used_percent"] - 5.25) < 0.0001

    def test_cost_persistence(self):
        """Test that costs persist across instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first tracker and add cost
            tracker1 = CostTracker(data_dir=Path(tmpdir))
            metrics = UsageMetrics(
                prompt_tokens=1000,
                completion_tokens=500,
                total_tokens=1500,
                cost=0.525,
                model="qwen/qwen-2.5-72b-instruct"
            )
            tracker1.track_usage(metrics)

            # Create second tracker and verify cost is loaded
            tracker2 = CostTracker(data_dir=Path(tmpdir))
            assert tracker2.get_month_cost() == 0.525


class TestOpenRouterClient:
    """Test OpenRouterClient."""

    def test_client_initialization(self):
        """Test initializing client."""
        client = OpenRouterClient(
            api_key="test_key",
            model="qwen/qwen-2.5-72b-instruct"
        )

        assert client.api_key == "test_key"
        assert client.model == "qwen/qwen-2.5-72b-instruct"
        assert client.max_retries == 3
        assert client.timeout == 60

    def test_calculate_cost(self):
        """Test cost calculation."""
        client = OpenRouterClient(
            api_key="test_key",
            model="qwen/qwen-2.5-72b-instruct"
        )

        # Test with Qwen pricing ($0.35 per 1M tokens)
        cost = client._calculate_cost(
            prompt_tokens=1_000_000,
            completion_tokens=1_000_000
        )

        # $0.35 + $0.35 = $0.70
        assert cost == 0.70

    def test_calculate_cost_small_request(self):
        """Test cost calculation for small request."""
        client = OpenRouterClient(
            api_key="test_key",
            model="qwen/qwen-2.5-72b-instruct"
        )

        # Test with 1000/500 tokens
        cost = client._calculate_cost(
            prompt_tokens=1000,
            completion_tokens=500
        )

        # (1000/1M * 0.35) + (500/1M * 0.35) = 0.000525
        assert abs(cost - 0.000525) < 0.0000001

    @patch('src.llm.openrouter_client.httpx.Client')
    def test_complete_success(self, mock_client_class):
        """Test successful completion."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "This is a test summary."
                }
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }

        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = OpenRouterClient(api_key="test_key")
        completion, metrics = client.complete("Test prompt")

        assert completion == "This is a test summary."
        assert metrics.prompt_tokens == 100
        assert metrics.completion_tokens == 50
        assert metrics.total_tokens == 150
        assert metrics.model == "qwen/qwen-2.5-72b-instruct"

    @patch('src.llm.openrouter_client.httpx.Client')
    def test_complete_with_cost_tracking(self, mock_client_class):
        """Test completion with cost tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock response
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "Test summary"
                    }
                }],
                "usage": {
                    "prompt_tokens": 1000,
                    "completion_tokens": 500,
                    "total_tokens": 1500
                }
            }

            mock_client = Mock()
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            tracker = CostTracker(data_dir=Path(tmpdir))
            client = OpenRouterClient(
                api_key="test_key",
                cost_tracker=tracker
            )

            completion, metrics = client.complete("Test prompt")

            # Verify cost was tracked
            assert tracker.get_month_cost() > 0
            summary = tracker.get_usage_summary()
            assert summary["total_requests"] == 1
            assert summary["total_tokens"] == 1500

    @patch('src.llm.openrouter_client.httpx.Client')
    @patch('src.llm.openrouter_client.time.sleep')
    def test_complete_with_retry(self, mock_sleep, mock_client_class):
        """Test completion with retry on rate limit."""
        # First call fails with 429, second succeeds
        mock_response_error = Mock()
        mock_response_error.status_code = 429
        mock_response_error.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Rate limited",
            request=Mock(),
            response=mock_response_error
        )

        mock_response_success = Mock()
        mock_response_success.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Test summary"
                }
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }

        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.post.side_effect = [
            mock_response_error,
            mock_response_success
        ]
        mock_client_class.return_value = mock_client

        client = OpenRouterClient(api_key="test_key")
        completion, metrics = client.complete("Test prompt")

        assert completion == "Test summary"
        assert mock_sleep.called  # Verify sleep was called for retry

    @patch('src.llm.openrouter_client.httpx.Client')
    def test_complete_budget_exceeded(self, mock_client_class):
        """Test that budget exceeded error is raised."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock response with high token usage
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "Test"
                    }
                }],
                "usage": {
                    "prompt_tokens": 10_000_000,
                    "completion_tokens": 10_000_000,
                    "total_tokens": 20_000_000
                }
            }

            mock_client = Mock()
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            tracker = CostTracker(
                data_dir=Path(tmpdir),
                max_monthly_cost=1.0
            )
            client = OpenRouterClient(
                api_key="test_key",
                cost_tracker=tracker
            )

            with pytest.raises(BudgetExceededError):
                client.complete("Test prompt")


def test_model_pricing_exists():
    """Test that model pricing is defined."""
    assert "qwen/qwen-2.5-72b-instruct" in MODEL_PRICING
    assert isinstance(MODEL_PRICING["qwen/qwen-2.5-72b-instruct"], ModelPricing)

    pricing = MODEL_PRICING["qwen/qwen-2.5-72b-instruct"]
    assert pricing.prompt_cost_per_million == 0.35
    assert pricing.completion_cost_per_million == 0.35
