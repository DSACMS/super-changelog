import pytest
import json
import os
import subprocess
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


class TestGetContributorsViaGit:
    """Test ChangelogGenerator._get_contributors_via_git."""

    def _git_log_result(self, lines):
        """Helper to build a mock CompletedProcess for the git log subprocess call."""
        result = Mock()
        result.stdout = "\n".join(lines) + "\n" if lines else ""
        return result

    @patch("scripts.util.shutil.rmtree")
    @patch("scripts.util.subprocess.run")
    @patch("scripts.util.tempfile.mkdtemp")
    def test_identifies_contributor_whose_first_commit_is_in_period(
        self, mock_mkdtemp, mock_run, mock_rmtree, mock_github_token
    ):
        """A contributor whose earliest commit falls within [start_date, end_date]
        should be recorded, using the earliest of their commit dates."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01", log_history_end="2024-12-31"
        )

        mock_mkdtemp.return_value = "/tmp/fake_clone_dir"

        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.clone_url = "https://github.com/test/repo.git"

        clone_result = Mock()
        log_result = self._git_log_result([
            "Jane Doe <jane@example.com>|2024-03-10T12:00:00+00:00",
            "Jane Doe <jane@example.com>|2024-06-01T09:30:00+00:00",  # later commit, should be ignored
        ])
        mock_run.side_effect = [clone_result, log_result]

        data = {"contributors": []}
        generator._get_contributors_via_git(mock_repo, data)

        assert len(data["contributors"]) == 1
        contributor = data["contributors"][0]
        assert contributor["name"] == "Jane Doe"
        assert contributor["email"] == "jane@example.com"
        assert contributor["created_at"] == "2024-03-10T12:00:00"
        assert contributor["company"] is None

        # Verify clone used token-authenticated URL
        clone_call_args = mock_run.call_args_list[0][0][0]
        assert any("x-access-token" in arg for arg in clone_call_args)
        mock_rmtree.assert_called_once_with("/tmp/fake_clone_dir", ignore_errors=True)

    @patch("scripts.util.subprocess.run")
    @patch("scripts.util.tempfile.mkdtemp")
    def test_excludes_contributor_whose_first_commit_is_before_start_date(
        self, mock_mkdtemp, mock_run, mock_github_token
    ):
        """A contributor whose earliest commit predates start_date is a veteran
        and should be excluded, even if they also have commits inside the period."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01", log_history_end="2024-12-31"
        )
        mock_mkdtemp.return_value = "/tmp/fake_clone_dir"

        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.clone_url = "https://github.com/test/repo.git"

        clone_result = Mock()
        log_result = self._git_log_result([
            "Veteran Dev <vet@example.com>|2023-05-01T00:00:00+00:00",
            "Veteran Dev <vet@example.com>|2024-06-01T00:00:00+00:00",
        ])
        mock_run.side_effect = [clone_result, log_result]

        data = {"contributors": []}
        generator._get_contributors_via_git(mock_repo, data)

        assert data["contributors"] == []

    @patch("scripts.util.subprocess.run")
    @patch("scripts.util.tempfile.mkdtemp")
    def test_excludes_contributor_whose_first_commit_is_after_end_date(
        self, mock_mkdtemp, mock_run, mock_github_token
    ):
        """A contributor whose earliest commit falls after end_date should be excluded."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01", log_history_end="2024-06-30"
        )
        mock_mkdtemp.return_value = "/tmp/fake_clone_dir"

        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.clone_url = "https://github.com/test/repo.git"

        clone_result = Mock()
        log_result = self._git_log_result([
            "Future Dev <future@example.com>|2024-09-01T00:00:00+00:00",
        ])
        mock_run.side_effect = [clone_result, log_result]

        data = {"contributors": []}
        generator._get_contributors_via_git(mock_repo, data)

        assert data["contributors"] == []

    @patch("scripts.util.subprocess.run")
    @patch("scripts.util.tempfile.mkdtemp")
    def test_handles_author_without_email_angle_brackets(
        self, mock_mkdtemp, mock_run, mock_github_token
    ):
        """If a log line's author string has no '<email>' portion, name/email
        parsing should degrade gracefully (name=full string, email=None)."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01", log_history_end="2024-12-31"
        )
        mock_mkdtemp.return_value = "/tmp/fake_clone_dir"

        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.clone_url = "https://github.com/test/repo.git"

        clone_result = Mock()
        log_result = self._git_log_result([
            "NoEmailUser|2024-04-01T00:00:00+00:00",
        ])
        mock_run.side_effect = [clone_result, log_result]

        data = {"contributors": []}
        generator._get_contributors_via_git(mock_repo, data)

        assert len(data["contributors"]) == 1
        assert data["contributors"][0]["name"] == "NoEmailUser"
        assert data["contributors"][0]["email"] is None
        assert data["contributors"][0]["created_at"] == "2024-04-01T00:00:00"

    @patch("scripts.util.subprocess.run")
    @patch("scripts.util.tempfile.mkdtemp")
    def test_skips_blank_and_malformed_lines(
        self, mock_mkdtemp, mock_run, mock_github_token
    ):
        """Blank lines and lines without a '|' separator should be skipped
        without raising."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01", log_history_end="2024-12-31"
        )
        mock_mkdtemp.return_value = "/tmp/fake_clone_dir"

        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.clone_url = "https://github.com/test/repo.git"

        clone_result = Mock()
        log_result = self._git_log_result([
            "",
            "malformed line with no pipe",
            "Valid User <valid@example.com>|2024-05-01T00:00:00+00:00",
        ])
        mock_run.side_effect = [clone_result, log_result]

        data = {"contributors": []}
        generator._get_contributors_via_git(mock_repo, data)

        assert len(data["contributors"]) == 1
        assert data["contributors"][0]["name"] == "Valid User"

    @patch("scripts.util.shutil.rmtree")
    @patch("scripts.util.subprocess.run")
    @patch("scripts.util.tempfile.mkdtemp")
    def test_clone_failure_is_caught_and_temp_dir_still_cleaned_up(
        self, mock_mkdtemp, mock_run, mock_rmtree, mock_github_token
    ):
        """If git clone raises (e.g. CalledProcessError), the exception should be
        caught, no contributors added, and the temp dir still removed in `finally`."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01", log_history_end="2024-12-31"
        )
        mock_mkdtemp.return_value = "/tmp/fake_clone_dir"

        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.clone_url = "https://github.com/test/repo.git"

        mock_run.side_effect = subprocess.CalledProcessError(1, "git clone")

        data = {"contributors": []}
        generator._get_contributors_via_git(mock_repo, data)

        assert data["contributors"] == []
        mock_rmtree.assert_called_once_with("/tmp/fake_clone_dir", ignore_errors=True)

    @patch("scripts.util.subprocess.run")
    @patch("scripts.util.tempfile.mkdtemp")
    def test_clone_url_uses_plain_https_when_no_token(
        self, mock_mkdtemp, mock_run
    ):
        """When no authentication token is provided, the clone URL should 
        remain a plain HTTPS URL without embedded credentials."""
        generator = ChangelogGenerator(
            token=None, log_history_start="2024-01-01", log_history_end="2024-12-31"
        )
        mock_mkdtemp.return_value = "/tmp/fake_clone_dir"

        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.clone_url = "https://github.com/test/repo.git"

        clone_result = Mock()
        log_result = self._git_log_result([])
        mock_run.side_effect = [clone_result, log_result]

        data = {"contributors": []}
        generator._get_contributors_via_git(mock_repo, data)

        # Retrieve the command list passed to the first subprocess.run call
        command_list = mock_run.call_args_list[0][0][0]

        # Verify that the exact original clone_url was passed (at index 3)
        assert command_list[3] == "https://github.com/test/repo.git"
        
        # Verify no access token was inserted anywhere in the command
        assert not any("x-access-token" in arg for arg in command_list)


class TestGetStatsContributors:
    """Test ChangelogGenerator.get_contributors. Calling get_stats_contributors()."""

    def _week(self, start_time, commit_count):
        """Helper to build a mock weekly-stats entry."""
        week = Mock()
        week.w = start_time
        week.c = commit_count
        return week
    
    def _mock_repo_under_contributor_cap(self, count=50):
        """Helper: build a mock_repo whose get_contributors().totalCount is
        below the 100-contributor threshold, so get_contributors takes the
        get_stats_contributors path instead of falling through to git log."""
        mock_repo = Mock()
        mock_repo.get_contributors.return_value.totalCount = count
        return mock_repo

    def test_identifies_new_contributor_and_excludes_veteran(self, mock_github_token):
        """A contributor with weekly activity only after start_date is 'new' and
        should be included; a contributor with activity before start_date is a
        veteran and should be excluded."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )
        mock_repo = self._mock_repo_under_contributor_cap()

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
        mock_repo = self._mock_repo_under_contributor_cap()

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

        mock_repo = self._mock_repo_under_contributor_cap()

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
        mock_repo = self._mock_repo_under_contributor_cap()

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

        mock_repo = self._mock_repo_under_contributor_cap()
        mock_repo.get_stats_contributors.side_effect = Exception("API Error")

        data = {}
        generator.get_contributors(mock_repo, data)

        # Asserts 'contributors' key exists and was initialized to an empty list
        assert "contributors" in data
        assert data["contributors"] == []
    
    
class TestGetContributorsBranching:
    """Test that get_contributors correctly branches between the
    get_stats_contributors path and the local git log fallback, based on
    contributor count."""
    
    @patch("scripts.util.ChangelogGenerator._get_contributors_via_git")
    def test_stats_returning_none_falls_back_to_git_log(
        self, mock_git_fallback, mock_github_token
    ):
        """If get_stats_contributors() returns None (e.g. 202 response/GitHub still computing
        stats), get_contributors should fall back to _get_contributors_via_git
        rather than just returning early."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )
        mock_repo = Mock()
        mock_repo.get_contributors.return_value.totalCount = 50
        mock_repo.name = "test-repo"
        mock_repo.get_stats_contributors.return_value = None

        data = {}
        generator.get_contributors(mock_repo, data)

        mock_git_fallback.assert_called_once_with(mock_repo, data)
        
    @patch("scripts.util.ChangelogGenerator._get_contributors_via_git")
    def test_contributors_count_lookup_failure_falls_back_to_git_log_branch(
        self, mock_git_fallback, mock_github_token
    ):
        """If repo.get_contributors() itself raises, contributors_count should
        default to 101, which routes to the >100 branch (_get_contributors_via_git)
        rather than get_stats_contributors."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.get_contributors.side_effect = Exception("API Error")

        data = {}
        generator.get_contributors(mock_repo, data)

        mock_git_fallback.assert_called_once_with(mock_repo, data)
        mock_repo.get_stats_contributors.assert_not_called()

    @patch("scripts.util.ChangelogGenerator._get_contributors_via_git")
    def test_uses_stats_contributors_when_count_at_or_under_100(
        self, mock_git_fallback, mock_github_token
    ):
        """A repo with exactly 100 contributors should use get_stats_contributors,
        not the git log fallback (boundary is inclusive: <= 100)."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )
        mock_repo = Mock()
        mock_repo.get_contributors.return_value.totalCount = 100
        mock_repo.get_stats_contributors.return_value = []

        data = {}
        generator.get_contributors(mock_repo, data)

        mock_repo.get_stats_contributors.assert_called_once()
        mock_git_fallback.assert_not_called()

    @patch("scripts.util.ChangelogGenerator._get_contributors_via_git")
    def test_uses_git_log_fallback_when_count_over_100(
        self, mock_git_fallback, mock_github_token
    ):
        """A repo with more than 100 contributors should skip
        get_stats_contributors entirely and delegate to _get_contributors_via_git."""
        generator = ChangelogGenerator(
            mock_github_token, log_history_start="2024-01-01"
        )
        mock_repo = Mock()
        mock_repo.name = "big-repo"
        mock_repo.get_contributors.return_value.totalCount = 150

        data = {}
        generator.get_contributors(mock_repo, data)

        mock_git_fallback.assert_called_once_with(mock_repo, data)
        mock_repo.get_stats_contributors.assert_not_called()
        
        
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
        
class TestChangelogEntryFiltering:
    """Test the changelog entry date filtering logic."""

    def _get_filtered_entries(self, mock_github_token, content):
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.html_url = "https://github.com/test/repo"
        mock_repo.description = "Test repository"
        mock_repo.archived = False
        mock_repo.get_topics.return_value = []
        mock_repo.get_issues.return_value = []
        
        mock_commit = Mock()
        mock_commit.commit.author.date = datetime(2024, 6, 1, tzinfo=timezone.utc)
        mock_repo.get_commits.return_value = [mock_commit]
        mock_repo.get_releases.return_value = []
        
        mock_content = Mock(decoded_content=content.encode("utf-8"))
        
        def get_contents_side_effect(path):
            if path == "CHANGELOG.md":
                return mock_content
            raise Exception("not found")

        mock_repo.get_contents.side_effect = get_contents_side_effect
        
        mock_github = Mock()
        mock_github.get_organization.return_value = _make_mock_org(mock_repo)

        generator = ChangelogGenerator(
            mock_github_token,
            log_history_start="2024-01-01",
            log_history_end="2024-12-31",
        )
        generator.g = mock_github
        
        data = generator.get_data("test-org")
        return data["repos"][0]["changelog_entries"]

    @pytest.mark.parametrize(
        "date_str, expected_count",
        [
            ("2024-06-15", 1),  # Inside period
            ("2023-12-01", 0),  # Before start date
            ("2025-03-01", 0),  # After end date
        ],
    )
    def test_dated_entry_period_filtering(self, mock_github_token, date_str, expected_count):
        """Verify dated entries are filtered according to start_date and end_date."""
        content = f"## [1.0.0] - {date_str}\n### Added\n- Feature\n"
        entries = self._get_filtered_entries(mock_github_token, content)
        assert len(entries) == expected_count

    @pytest.mark.parametrize(
        "changelog_content, expected_version",
        [
            ("## [1.0.0] - invalid-date\n### Added\n- Feature\n", "1.0.0"),
            ("## [1.0.0]\n### Added\n- Feature\n", "1.0.0"),
        ],
        ids=["unparseable_date", "missing_date"]
    )
    def test_changelog_date_fallbacks(self, mock_github_token, changelog_content, expected_version):
        """Verify changelog entries with bad or missing dates fall back gracefully."""
        entries = self._get_filtered_entries(mock_github_token, changelog_content)

        assert len(entries) == 1
        assert entries[0]["version"] == expected_version