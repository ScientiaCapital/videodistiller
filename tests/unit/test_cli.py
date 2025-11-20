"""Tests for CLI interface."""
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from src.cli.main import cli


def test_cli_help():
    """Test CLI shows help message."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])

    assert result.exit_code == 0
    assert 'VideoDistiller' in result.output


def test_extract_command_help():
    """Test extract command shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ['extract', '--help'])

    assert result.exit_code == 0
    assert 'Extract' in result.output


@patch('src.cli.main.Config')
@patch('src.cli.main.setup_logging')
@patch('src.cli.main.YouTubeExtractor')
@patch('src.cli.main.JSONRepository')
@patch('src.cli.main.Pipeline')
def test_extract_single_video(mock_pipeline_class, mock_repo, mock_extractor, mock_logging, mock_config):
    """Test extract command with single video."""
    # Setup mocks
    mock_config_instance = Mock()
    mock_config_instance.youtube_api_key = "test_key"
    mock_config_instance.data_dir = Path("/tmp/data")
    mock_config_instance.log_dir = Path("/tmp/logs")
    mock_config_instance.log_level = "INFO"
    mock_config.return_value = mock_config_instance

    mock_logger = Mock()
    mock_logging.return_value = mock_logger

    mock_video = Mock()
    mock_video.id = "abc123"
    mock_video.title = "Test Video"
    mock_video.channel = "Test Channel"
    mock_video.duration = 300
    mock_video.transcript = Mock()
    mock_video.transcript.text = "Test transcript"

    mock_pipeline = Mock()
    mock_pipeline.process_video.return_value = mock_video
    mock_pipeline_class.return_value = mock_pipeline

    runner = CliRunner()
    result = runner.invoke(cli, ['extract', '--url', 'https://youtube.com/watch?v=abc123'])

    assert result.exit_code == 0
    assert 'Test Video' in result.output
    mock_pipeline.process_video.assert_called_once_with('abc123')


@patch('src.cli.main.Config')
@patch('src.cli.main.setup_logging')
@patch('src.cli.main.YouTubeExtractor')
@patch('src.cli.main.JSONRepository')
@patch('src.cli.main.Pipeline')
def test_extract_playlist(mock_pipeline_class, mock_repo, mock_extractor, mock_logging, mock_config):
    """Test extract command with playlist."""
    # Setup mocks
    mock_config_instance = Mock()
    mock_config_instance.youtube_api_key = "test_key"
    mock_config_instance.data_dir = Path("/tmp/data")
    mock_config_instance.log_dir = Path("/tmp/logs")
    mock_config_instance.log_level = "INFO"
    mock_config.return_value = mock_config_instance

    mock_logger = Mock()
    mock_logging.return_value = mock_logger

    mock_pipeline = Mock()
    mock_pipeline.process_playlist.return_value = [Mock(), Mock()]
    mock_pipeline_class.return_value = mock_pipeline

    runner = CliRunner()
    result = runner.invoke(cli, ['extract', '--playlist', 'PLabc123'])

    assert result.exit_code == 0
    assert 'Completed: 2 videos' in result.output
    mock_pipeline.process_playlist.assert_called_once_with('PLabc123')


@patch('src.cli.main.Config')
@patch('src.cli.main.setup_logging')
@patch('src.cli.main.YouTubeExtractor')
@patch('src.cli.main.JSONRepository')
@patch('src.cli.main.Pipeline')
def test_extract_channel(mock_pipeline_class, mock_repo, mock_extractor, mock_logging, mock_config):
    """Test extract command with channel."""
    # Setup mocks
    mock_config_instance = Mock()
    mock_config_instance.youtube_api_key = "test_key"
    mock_config_instance.data_dir = Path("/tmp/data")
    mock_config_instance.log_dir = Path("/tmp/logs")
    mock_config_instance.log_level = "INFO"
    mock_config.return_value = mock_config_instance

    mock_logger = Mock()
    mock_logging.return_value = mock_logger

    mock_pipeline = Mock()
    mock_pipeline.process_channel.return_value = [Mock(), Mock(), Mock()]
    mock_pipeline_class.return_value = mock_pipeline

    runner = CliRunner()
    result = runner.invoke(cli, ['extract', '--channel', 'UCabc123', '--limit', '10'])

    assert result.exit_code == 0
    assert 'Completed: 3 videos' in result.output
    mock_pipeline.process_channel.assert_called_once_with('UCabc123', 10)


@patch('src.cli.main.Config')
@patch('src.cli.main.setup_logging')
def test_extract_missing_api_key(mock_logging, mock_config):
    """Test extract command fails without API key."""
    mock_config_instance = Mock()
    mock_config_instance.youtube_api_key = None
    mock_config_instance.data_dir = Path("/tmp/data")
    mock_config_instance.log_dir = Path("/tmp/logs")
    mock_config_instance.log_level = "INFO"
    mock_config_instance.ensure_directories_exist = Mock()
    mock_config.return_value = mock_config_instance

    runner = CliRunner()
    result = runner.invoke(cli, ['extract', '--url', 'https://youtube.com/watch?v=abc123'])

    assert result.exit_code == 1
    assert 'YOUTUBE_API_KEY not configured' in result.output


def test_extract_no_arguments():
    """Test extract command fails without arguments."""
    runner = CliRunner()
    result = runner.invoke(cli, ['extract'])

    # Should show error about missing arguments
    assert result.exit_code == 1


@patch('src.utils.config.Config')
def test_validate_command_success(mock_config):
    """Test validate command shows success."""
    mock_config_instance = Mock()
    mock_config_instance.youtube_api_key = "test_key"
    mock_config_instance.ensure_directories_exist = Mock()
    mock_config.return_value = mock_config_instance

    runner = CliRunner()
    result = runner.invoke(cli, ['validate'])

    # The validate command checks for dependencies that are installed,
    # so it should succeed
    assert result.exit_code == 0
    assert 'YouTube API key configured' in result.output


@patch('src.cli.main.Config')
def test_validate_command_missing_key(mock_config):
    """Test validate command fails without API key."""
    mock_config_instance = Mock()
    mock_config_instance.youtube_api_key = None
    mock_config.return_value = mock_config_instance

    runner = CliRunner()
    result = runner.invoke(cli, ['validate'])

    assert result.exit_code == 1
    assert 'YOUTUBE_API_KEY not configured' in result.output


def test_summarize_command_help():
    """Test summarize command shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ['summarize', '--help'])

    assert result.exit_code == 0
    assert 'Generate kid-friendly summaries' in result.output


@patch('src.cli.main.Config')
@patch('src.cli.main.setup_logging')
def test_summarize_command_missing_api_key(mock_logging, mock_config):
    """Test summarize command fails without OpenRouter API key."""
    mock_config_instance = Mock()
    mock_config_instance.openrouter_api_key = None
    mock_config.return_value = mock_config_instance

    mock_logger = Mock()
    mock_logging.return_value = mock_logger

    runner = CliRunner()
    result = runner.invoke(cli, ['summarize', 'test123'])

    assert result.exit_code == 1
    assert 'OPENROUTER_API_KEY not configured' in result.output


@patch('src.cli.main.Config')
@patch('src.cli.main.setup_logging')
@patch('src.cli.main.ContentAnalyzer')
@patch('src.cli.main.OpenRouterClient')
@patch('src.cli.main.CostTracker')
def test_summarize_single_video(mock_cost_tracker_class, mock_client_class, mock_analyzer_class, mock_logging, mock_config):
    """Test summarize command with single video."""
    # Setup mocks
    mock_config_instance = Mock()
    mock_config_instance.openrouter_api_key = "test_key"
    mock_config_instance.llm_model = "qwen/qwen-2.5-72b-instruct"
    mock_config_instance.max_monthly_cost = 10.0
    mock_config_instance.warn_at_cost = 8.0
    mock_config_instance.data_dir = Path("/tmp/data")
    mock_config.return_value = mock_config_instance

    mock_logger = Mock()
    mock_logging.return_value = mock_logger

    mock_tracker = Mock()
    mock_tracker.max_monthly_cost = 10.0
    mock_tracker.get_usage_summary.return_value = {
        'total_cost': 0.5,
        'budget_used_percent': 5.0,
        'remaining_budget': 9.5
    }
    mock_cost_tracker_class.return_value = mock_tracker

    mock_client = Mock()
    mock_client_class.return_value = mock_client

    mock_summary = Mock()
    mock_summary.title = "Test Video"
    mock_summary.video_id = "test123"
    mock_summary.template_used = "general"
    mock_summary.tokens_used = 150
    mock_summary.cost = 0.0525
    mock_summary.summary_text = "Test summary"

    mock_analyzer = Mock()
    mock_analyzer.summarize_batch.return_value = [mock_summary]
    mock_analyzer_class.return_value = mock_analyzer

    runner = CliRunner()
    result = runner.invoke(cli, ['summarize', 'test123'])

    assert result.exit_code == 0
    assert 'Generated 1 summaries' in result.output
    assert 'Test Video' in result.output
