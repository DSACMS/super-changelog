import pytest
import json
import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from scripts.util import ChangelogGenerator, parse_changelog

from tests.fixtures import (
    mock_github_token,
    temp_dir,
    sample_changelog_content,
)


class TestParseChangelog:
    """Test the parse_changelog function."""

    def test_parse_changelog_basic(self, sample_changelog_content):
        """Test basic changelog parsing with expected fixture data."""
        entries = parse_changelog(sample_changelog_content)

        # 1. Verify exact number of releases parsed
        assert len(entries) == 2

        # 2. Verify Release 1 (1.2.0)
        rel1 = entries[0]
        assert rel1["version"] == "1.2.0"
        assert rel1["date"] == "2025-01-08"
        assert len(rel1["changes"]) == 3

        # Check 'Added' category & items
        assert rel1["changes"][0]["category"] == "Added"
        assert rel1["changes"][0]["items"] == [
            "New authentication",
            "Error handling",
            "Search function",
        ]

        # Check 'Fixed' category & items
        assert rel1["changes"][1]["category"] == "Fixed"
        assert rel1["changes"][1]["items"] == [
            "UI bug",
            "Incorrect date formatting",
            "Missing validation",
        ]

        # Check 'Changed' category & items
        assert rel1["changes"][2]["category"] == "Changed"
        assert rel1["changes"][2]["items"] == [
            "Updated dependencies",
            "Improved data cache",
        ]

        # 3. Verify Release 2 (1.1.0)
        rel2 = entries[1]
        assert rel2["version"] == "1.1.0"
        assert rel2["date"] == "2025-06-15"
        assert len(rel2["changes"]) == 2

        assert rel2["changes"][0]["category"] == "Added"
        assert rel2["changes"][0]["items"] == [
            "Initial release",
            "Basic functionality",
        ]

        assert rel2["changes"][1]["category"] == "Fixed"
        assert rel2["changes"][1]["items"] == ["Critical initial bug"]

    def test_parse_changelog_empty_content(self):
        """Test parsing empty changelog content produces an empty list."""
        entries = parse_changelog("")
        assert entries == []
    
    def test_version_without_date(self):
        """Headers without ISO dates should parse version with date as None."""
        content = """
## [2.0.0]

### Added
- Unreleased feature
"""
        entries = parse_changelog(content)

        assert entries == [{
            "version": "2.0.0",
            "date": None,
            "changes": [
                {"category": "Added", "items": ["Unreleased feature"]}
            ]
        }]

    def test_preamble_content_before_first_version(self):
        """Items/text prior to the first release header should be safely ignored."""
        content = """
# Project Changelog
All notable changes to this project will be documented here.

- Unattached list item that should not crash or bleed into a release

## [1.0.0] - 2025-01-01
### Added
- Valid feature
"""
        entries = parse_changelog(content)

        assert len(entries) == 1
        assert entries[0]["version"] == "1.0.0"
        assert entries[0]["changes"] == [
            {"category": "Added", "items": ["Valid feature"]}
        ]

    def test_item_matching_category_name_prefix(self):
        #FLAG - test currently fails
        """Items starting with category keywords (e.g. 'Added ...') shouldn't be dropped by skip_prefixes."""
        content = """
## [1.0.0] - 2025-01-01

### Added
- Added support for WebSockets
- Additional configuration flags
"""
        entries = parse_changelog(content)

        assert len(entries) == 1
        assert entries[0]["changes"][0]["category"] == "Added"
        assert entries[0]["changes"][0]["items"] == [
            "Added support for WebSockets",
            "Additional configuration flags",
        ]

    def test_multiple_categories_with_empty_sections(self):
        """Categories declared without list items beneath them should retain empty lists."""
        content = """
## [1.0.0] - 2025-01-01

### Added
- Feature A

### Security

### Fixed
- Bug fix 1
"""
        entries = parse_changelog(content)

        assert entries[0]["changes"] == [
            {"category": "Added", "items": ["Feature A"]},
            {"category": "Security", "items": []},
            {"category": "Fixed", "items": ["Bug fix 1"]}
        ]


class TestChangelogGeneratorInit:
    """Test ChangelogGenerator construction."""

    def test_init_with_token_only(self, mock_github_token):
        """When only a token is given, all optional fields should default to None."""
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
        """When every parameter is given, they should all be stored and parsed."""
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

    def test_init_creates_github_client_with_expected_arguments(self, mock_github_token):
        """The underlying Github client should be constructed with per_page and lazy set."""
        with patch("scripts.util.Github") as mock_github_class:
            ChangelogGenerator(mock_github_token)

            mock_github_class.assert_called_once_with(
                mock_github_token, per_page=100, lazy=True
            )


class TestSaveData:
    """Test ChangelogGenerator.save_data."""

    def test_save_data_writes_json_to_filename(self, mock_github_token, temp_dir):
        """save_data should write the given dict as JSON to self.filename and return that path."""
        filename = os.path.join(temp_dir, "test_output.json")
        generator = ChangelogGenerator(mock_github_token, filename=filename)

        test_data = {"test": "data", "repos": []}

        result = generator.save_data(test_data)

        assert result == filename
        assert os.path.exists(filename)

        with open(filename, "r") as f:
            saved_data = json.load(f)
        assert saved_data == test_data

    def test_save_data_returns_none_when_no_filename_set(self, mock_github_token):
        """save_data should no-op and return None if the generator has no filename."""
        generator = ChangelogGenerator(mock_github_token)

        result = generator.save_data({"test": "data"})

        assert result is None


class TestGetIssuesAndPrs:
    """Test ChangelogGenerator.get_issues_and_prs."""

    def test_records_a_plain_issue(self, mock_github_token):
        """An item with pull_request=None should be recorded under data['issues']."""
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

    def test_records_a_pull_request(self, mock_github_token):
        """An item with a pull_request attribute should trigger a get_pull lookup
        and be recorded under data['pulls']."""
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

    def test_does_nothing_when_no_start_date_set(self, mock_github_token):
        """If log_history_start was never provided, get_issues_and_prs should return
        immediately without calling the GitHub API."""
        generator = ChangelogGenerator(mock_github_token)

        mock_repo = Mock()
        data = {"issues": [], "pulls": []}

        generator.get_issues_and_prs(mock_repo, data)

        mock_repo.get_issues.assert_not_called()
        assert data == {"issues": [], "pulls": []}


class TestGetContributors:
    """Test ChangelogGenerator.get_contributors."""

    def _week(self, start_time, commit_count):
        """Helper to build a mock weekly-stats entry."""
        week = Mock()
        week.w = start_time
        week.c = commit_count
        return week

    def test_identifies_new_contributor_and_excludes_veteran(self, mock_github_token):
        """A contributor with weekly activity only after start_date is 'new' and
        should be included; a contributor with activity before start_date is a
        veteran and should be excluded."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )
        mock_repo = Mock()

        veteran_stat = Mock()
        veteran_stat.author.login = "veteran"
        veteran_stat.author.company = None
        veteran_stat.weeks = [
            self._week(datetime(2023, 12, 15, tzinfo=timezone.utc), 5)
        ]

        new_stat = Mock()
        new_stat.author.login = "newuser"
        new_stat.author.company = "OpenSource Corp"
        new_stat.weeks = [
            self._week(datetime(2024, 1, 15, tzinfo=timezone.utc), 3)
        ]

        mock_repo.get_stats_contributors.return_value = [veteran_stat, new_stat]

        new_commit = Mock()
        new_commit.commit.author.date = datetime(2024, 1, 15, tzinfo=timezone.utc)
        new_commit.commit.author.email = "new@example.com"
        mock_repo.get_commits.return_value = [new_commit]

        data = {}
        generator.get_contributors(mock_repo, data)

        mock_repo.get_stats_contributors.assert_called_once()
        mock_repo.get_commits.assert_called_once_with(
            since=generator.start_date, until=generator.end_date, author="newuser"
        )

        assert len(data["contributors"]) == 1
        contributor = data["contributors"][0]
        assert contributor["name"] == "newuser"
        assert contributor["company"] == "OpenSource Corp"
        assert contributor["email"] == "new@example.com"
        assert contributor["created_at"] == "2024-01-15T00:00:00+00:00"

    def test_skips_stats_with_no_author_and_includes_valid_new_contributor(
        self, mock_github_token
    ):
        """Stat entries with author=None should be skipped safely; 
        contributors missing optional profile fields should still be recorded."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )
        mock_repo = Mock()

        no_author_stat = Mock()
        no_author_stat.author = None
        no_author_stat.weeks = [
            self._week(datetime(2024, 1, 10, tzinfo=timezone.utc), 5)
        ]

        ghost_stat = Mock()
        ghost_stat.author.login = "ghost"
        ghost_stat.author.company = None
        ghost_stat.weeks = [
            self._week(datetime(2024, 2, 1, tzinfo=timezone.utc), 1)
        ]

        mock_repo.get_stats_contributors.return_value = [no_author_stat, ghost_stat]

        ghost_commit = Mock()
        ghost_commit.commit.author.date = datetime(2024, 2, 1, tzinfo=timezone.utc)
        ghost_commit.commit.author.email = "ghost@example.com"
        mock_repo.get_commits.return_value = [ghost_commit]

        data = {}  
        generator.get_contributors(mock_repo, data)

        assert len(data["contributors"]) == 1
        assert data["contributors"][0]["name"] == "ghost"
        assert data["contributors"][0]["company"] is None
        assert data["contributors"][0]["email"] == "ghost@example.com"

    def test_excludes_contributor_with_no_activity_in_period(self, mock_github_token):
        """A contributor whose activity has c == 0 (no commits) or falls outside the period
        should not be counted as a new contributor."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )

        generator.start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        generator.end_date = datetime(2024, 2, 1, tzinfo=timezone.utc)

        mock_repo = Mock()

        # Case 1: Active week within period, but 0 commits (c == 0)
        idle_stat = Mock()
        idle_stat.author.login = "idle_user"
        idle_stat.author.company = None
        idle_stat.weeks = [
            self._week(datetime(2024, 1, 15, tzinfo=timezone.utc), 0)
        ]

        # Case 2: Commits (c > 0), but week falls completely OUTSIDE the period
        out_of_bounds_stat = Mock()
        out_of_bounds_stat.author.login = "out_of_bounds_user"
        out_of_bounds_stat.author.company = None
        out_of_bounds_stat.weeks = [
            self._week(datetime(2024, 3, 1, tzinfo=timezone.utc), 5)
        ]

        mock_repo.get_stats_contributors.return_value = [idle_stat, out_of_bounds_stat]

        data = {}
        generator.get_contributors(mock_repo, data)

        # Assert neither user was added
        assert data.get("contributors", []) == []
        mock_repo.get_commits.assert_not_called()

    def test_missing_commit_lookup_still_records_contributor_with_nulls(
        self, mock_github_token
    ):
        """If the get_commits backfill for a new contributor raises, the
        contributor should still be recorded, just with created_at/email left None."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )
        mock_repo = Mock()

        new_stat = Mock()
        new_stat.author.login = "flaky"
        new_stat.author.company = "Acme"
        new_stat.weeks = [
            self._week(datetime(2024, 1, 20, tzinfo=timezone.utc), 2)
        ]

        mock_repo.get_stats_contributors.return_value = [new_stat]
        mock_repo.get_commits.side_effect = Exception("API hiccup")

        data = {}
        generator.get_contributors(mock_repo, data)

        assert len(data["contributors"]) == 1
        contributor = data["contributors"][0]
        assert contributor["name"] == "flaky"
        assert contributor["company"] == "Acme"
        assert contributor["created_at"] is None
        assert contributor["email"] is None

    def test_handles_exceptions_without_raising(self, mock_github_token):
        """If the GitHub API raises while fetching contributor stats,
        get_contributors should catch the exception and leave data['contributors'] as an empty list (or untouched)."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )

        mock_repo = Mock()
        mock_repo.get_stats_contributors.side_effect = Exception("API Error")

        data = {}
        generator.get_contributors(mock_repo, data)

        # Asserts 'contributors' key exists and was initialized to an empty list
        assert "contributors" in data
        assert data["contributors"] == []
        
        
class TestGetReleases:
    """Test ChangelogGenerator.get_releases."""

    def test_filters_by_start_date_and_populates_data(self, mock_github_token):
        """Releases published before start_date, or never published (drafts),
        should be excluded. Releases with no name should fall back to tag_name."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )
        mock_repo = Mock()

        old_release = Mock()
        old_release.published_at = datetime(2023, 12, 31, tzinfo=timezone.utc)

        new_release = Mock()
        new_release.name = "v1.0.0 Release"
        new_release.tag_name = "v1.0.0"
        new_release.body = "Initial release notes"
        new_release.html_url = "https://github.com/test/repo/releases/v1.0.0"
        new_release.published_at = datetime(2024, 1, 15, 12, tzinfo=timezone.utc)
        new_release.created_at = datetime(2024, 1, 14, 12, tzinfo=timezone.utc)
        new_release.draft = False
        new_release.prerelease = False
        new_release.author.login = "octocat"

        draft_release = Mock()
        draft_release.published_at = None  # never published, should be skipped

        no_name_release = Mock()
        no_name_release.name = None  # should fall back to tag_name
        no_name_release.tag_name = "v1.1.0-beta"
        no_name_release.body = "Beta release"
        no_name_release.html_url = "https://github.com/test/repo/releases/v1.1.0-beta"
        no_name_release.published_at = datetime(2024, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
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

        assert len(data["releases"]) == 2

        rel1 = data["releases"][0]
        assert rel1["name"] == "v1.0.0 Release"
        assert rel1["tag_name"] == "v1.0.0"
        assert rel1["author"] == "octocat"
        assert rel1["published_at"] == "2024-01-15T12:00:00+00:00"
        assert rel1["created_at"] == "2024-01-14T12:00:00+00:00"

        rel2 = data["releases"][1]
        assert rel2["name"] == "v1.1.0-beta"
        assert rel2["author"] is None
        assert rel2["created_at"] is None
        assert rel2["is_prerelease"] is True

    def test_handles_exception_by_resetting_releases_to_empty_list(self, mock_github_token):
        """If get_releases raises on the GitHub API call, data['releases'] should
        be reset to an empty list rather than left with stale data."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )

        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.get_releases.side_effect = Exception("GitHub API Error")

        data = {"releases": ["stale_data"]}
        generator.get_releases(mock_repo, data)

        assert data["releases"] == []


def _make_mock_org(mock_repo):
    """Build a mock GitHub organization whose get_repos() returns the given repo.

    Shared by the get_data tests below, since each test only needs to vary the
    repo itself, not the org/get_repos wiring around it.
    """
    mock_org = Mock()
    mock_org.get_repos.return_value = [mock_repo]
    return mock_org


class TestGetData:
    """Test ChangelogGenerator.get_data."""

    def test_archival_mode_skips_topics_and_changelog_fetching(self, mock_github_token):
        """When archival=True, get_data should skip repo.get_topics() and
        repo.get_contents() (changelog lookup), and the resulting repo dict should
        have no 'topics' or 'changelog_entries' keys."""
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.html_url = "https://github.com/test/repo"
        mock_repo.description = "Test repository"
        mock_repo.archived = False
        mock_repo.get_issues.return_value = []
        mock_repo.get_commits.return_value = []
        mock_repo.get_releases.return_value = []

        mock_github = Mock()
        mock_github.get_organization.return_value = _make_mock_org(mock_repo)

        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2025-01-01"
        )
        generator.g = mock_github

        data = generator.get_data("test-org", archival=True)

        repo_data = data["repos"][0]
        assert "topics" not in repo_data
        assert "changelog_entries" not in repo_data

        mock_repo.get_topics.assert_not_called()
        mock_repo.get_contents.assert_not_called()

    def test_archived_repos_are_included_but_not_deeply_processed(self, mock_github_token):
        """A repo marked archived=True should still appear in the results, but
        get_data should skip fetching its commits (and other deep API calls)."""
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.html_url = "https://github.com/test/repo"
        mock_repo.description = "Test repository"
        mock_repo.archived = True

        mock_github = Mock()
        mock_github.get_organization.return_value = _make_mock_org(mock_repo)

        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2025-01-01"
        )
        generator.g = mock_github

        data = generator.get_data("test-org")

        assert data["total_repo_count"] == 1
        assert data["repos"][0]["archived"] is True
        mock_repo.get_issues_and_prs.assert_not_called()
        mock_repo.get_commits.assert_not_called()
        mock_repo.get_releases.assert_not_called()


class TestGetAndSaveData:
    """Test ChangelogGenerator.get_and_save_data end to end."""

    def test_fetches_data_and_writes_it_to_the_configured_file(
        self, mock_github_token, temp_dir
    ):
        """get_and_save_data should call get_data, then save the result to
        self.filename, returning that path."""
        filename = os.path.join(temp_dir, "integration_test.json")

        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.html_url = "https://github.com/test/repo"
        mock_repo.description = "Test repository"
        mock_repo.archived = False
        mock_repo.get_topics.return_value = []
        mock_repo.get_issues.return_value = []
        mock_repo.get_stats_contributors.return_value = []
        mock_repo.get_commits.return_value = []
        mock_repo.get_releases.return_value = []
        mock_repo.get_contents.return_value = None

        mock_github = Mock()
        mock_github.get_organization.return_value = _make_mock_org(mock_repo)

        generator = ChangelogGenerator(
            mock_github_token,
            filename=filename,
            log_history_start="2024-01-01",
        )
        generator.g = mock_github

        result = generator.get_and_save_data("test-org")

        assert result == filename
        assert os.path.exists(filename)

        with open(filename, "r") as f:
            data = json.load(f)
        assert "repos" in data
        assert "period" in data
        assert "generated_at" in data


@pytest.mark.integration
class TestChangelogGeneratorIntegration:
    """Integration-style tests that exercise date handling without mocking the
    GitHub client at all."""

    def test_date_handling(self, mock_github_token):
        """start_date, end_date, and timestamp should all be populated and of the
        expected types when both history bounds are given."""
        start_date = "2025-01-01"
        end_date = "2025-01-31"

        generator = ChangelogGenerator(
            mock_github_token,
            log_history_start=start_date,
            log_history_end=end_date,
        )

        assert generator.start_date is not None
        assert generator.end_date is not None
        assert generator.timestamp is not None
        assert isinstance(generator.start_date, datetime)
        assert isinstance(generator.end_date, datetime)
        assert len(generator.timestamp) > 0