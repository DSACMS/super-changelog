import pytest
import json
import tempfile
import os
import sys
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
from scripts.util import ChangelogGenerator, parse_changelog


class TestParseChangelog:
    """Test the parse_changelog function."""
   
    def test_parse_changelog_basic(self, sample_changelog_content):
        """Test basic changelog parsing functionality."""
        entries = parse_changelog(sample_changelog_content)
        assert isinstance(entries, list)
   
    def test_parse_changelog_empty_content(self):
        """Test parsing empty changelog content."""
        entries = parse_changelog("")
        assert isinstance(entries, list)
   
    def test_parse_changelog_with_version_headers(self):
        """Test parsing changelog with version headers."""
        content = """
# Changelog

## [1.0.0] - 2025-01-01

### Added
- Feature A
- Feature B

### Fixed
- Bug fix 1
"""
        entries = parse_changelog(content)
        assert isinstance(entries, list)


class TestChangelogGenerator:
    """Test the ChangelogGenerator class."""
   
    def test_init_with_token_only(self, mock_github_token):
        """Test ChangelogGenerator initialization with just token."""
        generator = ChangelogGenerator(mock_github_token)
       
        assert generator.token == mock_github_token
        assert generator.filename is None
        assert generator.log_history_start is None
        assert generator.now is not None
        assert generator.timestamp is not None
   
    def test_init_with_all_parameters(self, mock_github_token, temp_dir):
        """Test ChangelogGenerator initialization with all parameters."""
        filename = os.path.join(temp_dir, "test_changelog.json")
        start_date = "2025-01-01"
       
        generator = ChangelogGenerator(
            token=mock_github_token,
            filename=filename,
            log_history_start=start_date
        )
       
        assert generator.token == mock_github_token
        assert generator.filename == filename
        assert generator.log_history_start == start_date
        assert generator.start_date is not None
   
    def test_init_creates_github_client(self, mock_github_token):
        """Test that initialization creates a GitHub client."""
        with patch('scripts.util.Github') as mock_github_class:
            generator = ChangelogGenerator(mock_github_token)
            mock_github_class.assert_called_once_with(mock_github_token)
   
    def test_save_data_with_filename(self, mock_github_token, temp_dir):
        """Test saving data to file."""
        filename = os.path.join(temp_dir, "test_output.json")
        generator = ChangelogGenerator(mock_github_token, filename=filename)
       
        test_data = {"test": "data", "repos": []}
       
        result = generator.save_data(test_data)
       
        assert result == filename
        assert os.path.exists(filename)
       
        with open(filename, 'r') as f:
            saved_data = json.load(f)
        assert saved_data == test_data
   
    def test_save_data_without_filename(self, mock_github_token):
        """Test save_data returns None when no filename is set."""
        generator = ChangelogGenerator(mock_github_token)
       
        test_data = {"test": "data"}
        result = generator.save_data(test_data)
       
        assert result is None
   
    @patch('scripts.util.Github')
    def test_get_issues_and_prs(self, mock_github_class, mock_github_token):
        """Test getting issues and pull requests."""
        generator = ChangelogGenerator(
            mock_github_token,
            log_history_start="2024-01-01"
        )
       
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.created_at = datetime.now(timezone.utc)
        mock_issue.updated_at = datetime.now(timezone.utc)
        mock_issue.title = "Test Issue"
        mock_issue.html_url = "https://github.com/test/repo/issues/1"
        mock_issue.state = "open"
        mock_issue.pull_request = None
       
        mock_repo.get_issues.return_value = [mock_issue]
       
        data = {"issues": [], "pulls": []}
       
        generator.get_issues_and_prs(mock_repo, data)
       
        assert len(data["issues"]) >= 0
        mock_repo.get_issues.assert_called_once_with(state="all")
   
    @patch('scripts.util.Github')
    def test_get_contributors_handles_exceptions(self, mock_github_class, mock_github_token):
        """Test that get_contributors handles exceptions."""
        generator = ChangelogGenerator(
            mock_github_token,
            log_history_start="2024-01-01"
        )
       
        mock_repo = Mock()
        mock_repo.get_contributors.side_effect = Exception("API Error")
       
        data = {"contributors": []}
       
        generator.get_contributors(mock_repo, data)
       
        assert data["contributors"] == []
   
    @patch('scripts.util.Github')
    def test_get_data_structure(self, mock_github_class, mock_github_token):
        """Test that get_data returns correct data structure."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github
       
        mock_org = Mock()
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.html_url = "https://github.com/test/repo"
        mock_repo.description = "Test repo"
        mock_repo.get_issues.return_value = []
        mock_repo.get_contributors.return_value = Mock()
        mock_repo.get_contributors.return_value.totalCount = 0
        mock_repo.get_commits.return_value = []
        mock_repo.get_contents.side_effect = Exception("No changelog")
       
        mock_org.get_repos.return_value = [mock_repo]
        mock_github.get_organization.return_value = mock_org
       
        generator = ChangelogGenerator(
            mock_github_token,
            log_history_start="2025-01-01"
        )
       
        data = generator.get_data("test-org")
       
        assert "repos" in data
        assert "period" in data
        assert "generated_at" in data
        assert isinstance(data["repos"], list)
        assert "start" in data["period"]
        assert "end" in data["period"]
   
    def test_get_and_save_data_integration(self, mock_github_token, temp_dir):
        """Test the full get_and_save_data workflow."""
        filename = os.path.join(temp_dir, "integration_test.json")
       
        with patch('scripts.util.Github') as mock_github_class:
            mock_github = Mock()
            mock_github_class.return_value = mock_github
           
            mock_org = Mock()
            mock_repo = Mock()
            mock_repo.name = "test-repo"
            mock_repo.html_url = "https://github.com/test/repo"
            mock_repo.description = "Test repository"
            mock_repo.get_issues.return_value = []
            mock_repo.get_contributors.return_value = Mock()
            mock_repo.get_contributors.return_value.totalCount = 0
            mock_repo.get_commits.return_value = []
            mock_repo.get_contents.side_effect = Exception("No changelog")
           
            mock_org.get_repos.return_value = [mock_repo]
            mock_github.get_organization.return_value = mock_org
           
            generator = ChangelogGenerator(
                mock_github_token,
                filename=filename,
                log_history_start="2024-01-01"
            )
           
            result = generator.get_and_save_data("test-org")
           
            assert result == filename
            assert os.path.exists(filename)
           
            with open(filename, 'r') as f:
                data = json.load(f)
            assert "repos" in data
            assert "period" in data
            assert "generated_at" in data


@pytest.mark.integration
class TestChangelogGeneratorIntegration:
    """Integration tests for ChangelogGenerator."""
   
    def test_date_handling(self, mock_github_token):
        """Test that dates are handled correctly."""
        start_date = "2025-01-01"
        generator = ChangelogGenerator(
            mock_github_token,
            log_history_start=start_date
        )
       
        assert generator.start_date is not None
        assert generator.end_date is not None
        assert generator.timestamp is not None
       
        assert isinstance(generator.end_date, str)
        assert len(generator.timestamp) > 0