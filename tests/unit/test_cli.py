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
