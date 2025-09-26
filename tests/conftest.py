import pytest
import os
import json
import tempfile
# import sys
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
from github import Github, Repository, NamedUser, PullRequest, Issue


@pytest.fixture
def mock_github_token():
    """Provide a mock GitHub token for testing."""
    return "ghp_mock_token_for_testing"

@pytest.fixture
def mock_repo_data():
    """Sample repo data for testing."""
    return {
        "name": "test-repo",
        "url": "https://github.com/DSACMS/test-repo",
        "description": "A test repo",
        "issues": [
            {
                "title": "Test issue",
                "url": "https://github.com/DSACMS/test-repo/issues/1",
                "created_at": "2025-06-23T19:26:03+00:00",
                "state": "open",
                "is_new": True
            }
        ],
        "pulls": [
            {
                "title": "Test PR",
                "url": "https://github.com/DSACMS/test-repo/pull/1",
                "created_at": "2025-06-24T19:48:58+00:00",
                "updated_at": "2025-06-24T19:48:58+00:00",
                "state": "open",
                "merged": False,
                "is_new": True
            }
        ],
        "commits": [
            {
                "message": "Test commit",
                "url": "https://github.com/DSACMS/test-repo/commit/abc123",
                "author": "Test Author",
                "created_at": "2025-06-22T16:01:50+00:00"
            }
        ],
        "contributors": [],
        "changelog_entries": [
            {
                "version": "1.0.0",
                "date": "2025-01-01",
                "changes": [
                    {
                        "category": "Added",
                        "items": ["New feature X", "New feature Y"]
                    },
                    {
                        "category": "Fixed",
                        "items": ["Bug fix A", "Bug fix B"]
                    }
                ]
            }
        ]
    }

@pytest.fixture
def mock_changelog_data(mock_repo_data):
    """Complete changelog data structure for testing."""
    return {
        "repos": [mock_repo_data],
        "period": {
            "start": "2025-01-01",
            "end": "2025-01-08"
        },
        "generated_at": "2024-01-08T12:00:00Z"
    }

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def mock_env_vars():
    """Mock environmental variables."""
    env_vars = {
        "GH_TOKEN": "test_token",
        "GITHUB_REPOSITORY": "DSACMS/test-repo"
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def mock_github_api():
    """Mock GitHub API objects"""
    mock_repo = Mock(spec=Repository.Repository)
    mock_repo.name = "test-repo"
    mock_repo.html_url = "https://github.com/DSACMS/test-repo"
    mock_repo.description = "Test repository"

    mock_issue = Mock(spec=Issue.Issue)
    mock_issue.title = "Test Issue"
    mock_issue.html_url = "https://github.com/DSACMS/test-repo/issues/1"
    mock_issue.created_at = datetime.now(timezone.utc)
    mock_issue.updated_at = datetime.now(timezone.utc)
    mock_issue.state = "open"
    mock_issue.pull_request = None
    mock_issue.number = 1

    mock_github = Mock(spec=Github)
    mock_org = Mock()
    mock_org.get_repos.return_value = [mock_repo]
    mock_github.get_organization.return_value = mock_org
    mock_repo.get_issues.return_value = [mock_issue]

    return {
        'github': mock_github,
        'org': mock_org,
        'repo': mock_repo,
        'issue': mock_issue
    }

@pytest.fixture
def sample_changelog_content():
    """Sample changelog content for parsing tests."""
    return """# Changelog

## [1.2.0] - 2025-01-08

### Added
- New authentication
- Error handling
- Search function

### Fixed
- UI bug
- Incorrect date formatting
- Missing validation

### Changed
- Updated dependencies
- Improved data cache

## [1.1.0] - 2025-06-15

### Added
- Initial release
- Basic functionality

### Fixed
- Critical initial bug
"""
