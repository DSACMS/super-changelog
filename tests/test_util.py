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
        assert generator.log_history_end is None
        assert generator.start_date is None
        assert generator.end_date is None
        assert generator.now is not None
        assert generator.timestamp is not None
        

    def test_init_with_all_parameters(self, mock_github_token, temp_dir):
        """Test ChangelogGenerator initialization with all parameters."""
        filename = os.path.join(temp_dir, "test_changelog.json")
        start_date_str = "2025-01-01"
        end_date_str = "2025-01-31"

        generator = ChangelogGenerator(
            token=mock_github_token,
            filename=filename,
            log_history_start=start_date_str,
            log_history_end=end_date_str,
        )

        assert generator.token == mock_github_token
        assert generator.filename == filename
        assert generator.log_history_start == start_date_str
        assert generator.log_history_end == end_date_str
        assert generator.start_date == datetime.strptime(start_date_str, "%Y-%m-%d")
        assert generator.end_date == datetime.strptime(end_date_str, "%Y-%m-%d")
        
   
    def test_init_creates_github_client(self, mock_github_token):
        """Test that initialization creates a GitHub client."""
        with patch('scripts.util.Github') as mock_github_class:
            generator = ChangelogGenerator(mock_github_token)
            mock_github_class.assert_called_once_with(mock_github_token, per_page=100, lazy=True)
            
   
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
        
   
    def test_get_issues(self, mock_github_token):
        """Test fetching and parsing standard issues."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )

        mock_issue = Mock()
        mock_issue.created_at = datetime(2024, 1, 15, 12, tzinfo=timezone.utc)
        mock_issue.title = "Test Issue"
        mock_issue.html_url = "https://github.com/test/repo/issues/1"
        mock_issue.state = "open"
        mock_issue.pull_request = None
        mock_issue.user.login = "octocat"

        mock_repo = Mock()
        mock_repo.get_issues.return_value = [mock_issue]

        data = {"issues": [], "pulls": []}

        generator.get_issues_and_prs(mock_repo, data)

        mock_repo.get_issues.assert_called_once_with(
            state="all", since=generator.start_date
        )
        assert len(data["issues"]) == 1
        assert data["issues"][0]["title"] == "Test Issue"
        assert data["issues"][0]["author"] == "octocat"
        assert data["issues"][0]["is_new"] is True
        
        
    def test_get_pull_requests(self, mock_github_token):
        """Test fetching and parsing pull requests."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )

        mock_item = Mock()
        mock_item.number = 42
        mock_item.pull_request = Mock()  

        mock_pr = Mock()
        mock_pr.title = "Test PR"
        mock_pr.html_url = "https://github.com/test/repo/pull/42"
        mock_pr.created_at = datetime(2024, 1, 20, 10, tzinfo=timezone.utc)
        mock_pr.updated_at = datetime(2024, 1, 21, 10, tzinfo=timezone.utc)
        mock_pr.merged_at = datetime(2024, 1, 22, 10, tzinfo=timezone.utc)
        mock_pr.state = "closed"
        mock_pr.is_merged.return_value = True
        mock_pr.user.login = "developer"

        mock_repo = Mock()
        mock_repo.get_issues.return_value = [mock_item]
        mock_repo.get_pull.return_value = mock_pr

        data = {"issues": [], "pulls": []}

        generator.get_issues_and_prs(mock_repo, data)

        mock_repo.get_pull.assert_called_once_with(42)
        assert len(data["pulls"]) == 1
        assert data["pulls"][0]["title"] == "Test PR"
        assert data["pulls"][0]["merged"] is True
        assert data["pulls"][0]["author"] == "developer"
        
    
    def test_get_contributors_identifies_new_vs_veteran_contributors(
        self, mock_github_token
    ):
        """Test that new contributors are added to data, but veteran authors are excluded."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )
        mock_repo = Mock()

        mock_contributors_list = Mock()
        mock_contributors_list.totalCount = 2
        mock_repo.get_contributors.return_value = mock_contributors_list

        veteran_commit = Mock()
        veteran_commit.commit.author.name = "Veteran User"

        new_commit = Mock()
        new_commit.commit.author.name = "New Contributor"
        new_commit.commit.author.email = "new@example.com"
        new_commit.commit.author.date = datetime(
            2024, 1, 15, tzinfo=timezone.utc
        )
        new_commit.author.company = "OpenSource Corp"

        mock_repo.get_commits.side_effect = [
            [veteran_commit],  # Call with `until=...`
            [
                veteran_commit,
                new_commit,
            ],  # Call with `since=...` (includes both)
        ]

        data = {}
        generator.get_contributors(mock_repo, data)

        mock_repo.get_commits.assert_any_call(until=generator.start_date)
        mock_repo.get_commits.assert_any_call(since=generator.start_date)

        assert "contributors" in data
        assert len(data["contributors"]) == 1

        contributor = data["contributors"][0]
        assert contributor["name"] == "New Contributor"
        assert contributor["company"] == "OpenSource Corp"
        assert contributor["email"] == "new@example.com"
        assert contributor["created_at"] == "2024-01-15T00:00:00+00:00"
        
    
    def test_get_contributors_handles_missing_author_fields(
        self, mock_github_token
    ):
        """Test that commits with missing author information are skipped safely."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )
        mock_repo = Mock()

        # Commit with no author name inside commit object
        nameless_commit = Mock()
        nameless_commit.commit.author.name = None

        # Commit with author name, but no associated GitHub user object
        no_user_obj_commit = Mock()
        no_user_obj_commit.commit.author.name = "Ghost Author"
        no_user_obj_commit.commit.author.email = "ghost@example.com"
        no_user_obj_commit.commit.author.date = datetime(
            2024, 2, 1, tzinfo=timezone.utc
        )
        no_user_obj_commit.author = None  # No GitHub user object attached

        mock_repo.get_commits.side_effect = [
            [],  # Past commits (until)
            [nameless_commit, no_user_obj_commit],  # Current commits (since)
        ]

        data = {}
        generator.get_contributors(mock_repo, data)

        assert len(data["contributors"]) == 1
        assert data["contributors"][0]["name"] == "Ghost Author"
        assert data["contributors"][0]["company"] is None
        
   
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
        
    
    def test_get_releases_filters_by_start_date_and_populates_data(
        self, mock_github_token
    ):
        """Test that releases are correctly fetched and filtered based on start_date."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )
        mock_repo = Mock()

        old_release = Mock()
        old_release.published_at = datetime(
            2023, 12, 31, tzinfo=timezone.utc
        )

        new_release = Mock()
        new_release.name = "v1.0.0 Release"
        new_release.tag_name = "v1.0.0"
        new_release.body = "Initial release notes"
        new_release.html_url = "https://github.com/test/repo/releases/v1.0.0"
        new_release.published_at = datetime(
            2024, 1, 15, 12, tzinfo=timezone.utc
        )
        new_release.created_at = datetime(
            2024, 1, 14, 12, tzinfo=timezone.utc
        )
        new_release.draft = False
        new_release.prerelease = False
        new_release.author.login = "octocat"

        # 3. Draft/Unpublished Release (published_at is None - should be skipped)
        draft_release = Mock()
        draft_release.published_at = None

        # 4. Release with no name (should fall back to tag_name)
        no_name_release = Mock()
        no_name_release.name = None
        no_name_release.tag_name = "v1.1.0-beta"
        no_name_release.body = "Beta release"
        no_name_release.html_url = (
            "https://github.com/test/repo/releases/v1.1.0-beta"
        )
        no_name_release.published_at = datetime(
            2024, 2, 1, 12, 0, 0, tzinfo=timezone.utc
        )
        no_name_release.created_at = None
        no_name_release.draft = False
        no_name_release.prerelease = True
        no_name_release.author = None 

        mock_repo.get_releases.return_value = [
            old_release,
            new_release,
            draft_release,
            no_name_release,
        ]

        data = {}
        generator.get_releases(mock_repo, data)

        assert "releases" in data
        assert len(data["releases"]) == 2

        rel1 = data["releases"][0]
        assert rel1["name"] == "v1.0.0 Release"
        assert rel1["tag_name"] == "v1.0.0"
        assert rel1["author"] == "octocat"
        assert rel1["published_at"] == "2024-01-15T12:00:00+00:00"
        assert rel1["created_at"] == "2024-01-14T12:00:00+00:00"

        rel2 = data["releases"][1]
        assert (
            rel2["name"] == "v1.1.0-beta"
        )
        assert rel2["author"] is None
        assert rel2["created_at"] is None
        assert rel2["is_prerelease"] is True
        

    def test_get_releases_handles_exception(self, mock_github_token):
        """Test that get_releases catches exceptions gracefully and resets data['releases'] to an empty list."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )

        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.get_releases.side_effect = Exception("GitHub API Error")

        data = {"releases": ["stale_data"]}
        generator.get_releases(mock_repo, data)

        assert data["releases"] == []
   
   
    @patch("scripts.util.parse_changelog")
    def test_get_data_archival_mode_skips_extra_fetching(
        self, mock_github_api, mock_github_token
    ):
        """Test get_data when archival=True to verify topics and changelog extraction are skipped."""
        mock_github = mock_github_api["github"]
        mock_repo = mock_github_api["repo"]

        mock_repo.archived = False
        mock_repo.get_commits.return_value = []
        mock_repo.get_releases.return_value = []

        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2025-01-01"
        )
        generator.g = mock_github

        # Execute with archival=True
        data = generator.get_data("DSACMS", archival=True)

        repo_data = data["repos"][0]

        assert "topics" not in repo_data
        assert "changelog_entries" not in repo_data

        mock_repo.get_topics.assert_not_called()
        mock_repo.get_contents.assert_not_called()

    def test_get_data_skips_processing_archived_repos(
        self, mock_github_api, mock_github_token
    ):
        """Test that archived repos are added to data but skipped for deep API checks."""
        mock_github = mock_github_api["github"]
        mock_repo = mock_github_api["repo"]

        mock_repo.archived = True

        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2025-01-01"
        )
        generator.g = mock_github

        data = generator.get_data("DSACMS")

        assert data["total_repo_count"] == 1
        assert data["repos"][0]["archived"] is True

        mock_repo.get_commits.assert_not_called()


    @patch('scripts.util.Github')
    def test_get_data_archival_mode_skips_extra_fetching(
        self, mock_github_class, mock_github_token
    ):
        """Test get_data when archival=True to verify topics and changelog extraction are skipped."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_repo = Mock()
        mock_repo.name = "archived-repo-run"
        mock_repo.archived = False
        mock_repo.get_issues.return_value = []
        mock_repo.get_commits.return_value = []
        mock_repo.get_releases.return_value = []

        mock_org = Mock()
        mock_org.get_repos.return_value = [mock_repo]
        mock_github.get_organization.return_value = mock_org

        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2025-01-01"
        )

        data = generator.get_data("test-org", archival=True)

        repo_data = data["repos"][0]

        assert "topics" not in repo_data
        assert "changelog_entries" not in repo_data

        mock_repo.get_topics.assert_not_called()
        mock_repo.get_contents.assert_not_called()
   
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
            mock_repo.archived = False
            mock_repo.get_topics.return_value = []
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
        end_date = "2025-01-31"
        
        generator = ChangelogGenerator(
            mock_github_token,
            log_history_start=start_date,
            log_history_end=end_date
        )
       
        assert generator.start_date is not None
        assert generator.end_date is not None
        assert generator.timestamp is not None
        
        assert isinstance(generator.start_date, datetime)
        assert isinstance(generator.end_date, datetime)
       
        assert len(generator.timestamp) > 0