import pytest
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock, mock_open, call
from github import Github, GithubException
from scripts.create_pr import (
    get_latest_summary_files,
    create_branch_and_commit,
    create_pull_request_with_api,
    create_pull_request_with_cli,
    main
)


class TestGetLatestSummaryFiles:
    """Test getting latest summary files."""
   
    def test_get_latest_summary_files_success(self, temp_dir):
        """Test successfully getting latest summary files."""
        # Create summaries directory
        summaries_dir = os.path.join(temp_dir, "changelog_data", "summaries")
        os.makedirs(summaries_dir, exist_ok=True)
       
        # Create test files
        timestamp1 = "25-01-01"
        timestamp2 = "25-01-08"
       
        open(os.path.join(summaries_dir, f"pr_title_{timestamp1}.txt"), 'w').close()
        open(os.path.join(summaries_dir, f"pr_title_{timestamp2}.txt"), 'w').close()
        open(os.path.join(summaries_dir, f"pr_body_{timestamp1}.md"), 'w').close()
        open(os.path.join(summaries_dir, f"pr_body_{timestamp2}.md"), 'w').close()
       
        # Change to temp directory
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)
           
            title_file, body_file = get_latest_summary_files()
           
            # Should get the latest files (timestamp2)
            assert f"pr_title_{timestamp2}.txt" in title_file
            assert f"pr_body_{timestamp2}.md" in body_file
        finally:
            os.chdir(original_dir)
   
    def test_get_latest_summary_files_missing_directory(self, temp_dir):
        """Test error when summaries directory doesn't exist."""
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)
           
            with pytest.raises(FileNotFoundError, match="summaries directory not found"):
                get_latest_summary_files()
        finally:
            os.chdir(original_dir)
   
    def test_get_latest_summary_files_missing_title_files(self, temp_dir):
        """Test error when PR title files are missing."""
        summaries_dir = os.path.join(temp_dir, "changelog_data", "summaries")
        os.makedirs(summaries_dir, exist_ok=True)
       
        # Create only body files
        open(os.path.join(summaries_dir, "pr_body_25-01-01.md"), 'w').close()
       
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)
           
            with pytest.raises(FileNotFoundError, match="PR title or body files not found"):
                get_latest_summary_files()
        finally:
            os.chdir(original_dir)
   
    def test_get_latest_summary_files_missing_body_files(self, temp_dir):
        """Test error when PR body files are missing."""
        summaries_dir = os.path.join(temp_dir, "changelog_data", "summaries")
        os.makedirs(summaries_dir, exist_ok=True)
       
        # Create only title files
        open(os.path.join(summaries_dir, "pr_title_25-01-01.txt"), 'w').close()
       
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)
           
            with pytest.raises(FileNotFoundError, match="PR title or body files not found"):
                get_latest_summary_files()
        finally:
            os.chdir(original_dir)


class TestCreateBranchAndCommit:
    """Test git branch and commit operations."""
   
    @patch('subprocess.run')
    def test_create_branch_and_commit_success(self, mock_run):
        """Test successful branch creation and commit."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
       
        branch_name = create_branch_and_commit()
       
        # Verify branch name format
        assert branch_name.startswith("weekly-changelog-")
        assert len(branch_name) > len("weekly-changelog-")
       
        # Verify git commands were called in correct order
        calls = mock_run.call_args_list
       
        # Should have 5 calls: config email, config name, checkout, add, commit, push
        assert len(calls) >= 6
       
        # Check git config calls
        assert calls[0][0][0] == ["git", "config", "--local", "user.email", "action@github.com"]
        assert calls[1][0][0] == ["git", "config", "--local", "user.name", "GitHub Action"]
       
        # Check checkout call
        assert calls[2][0][0][0:3] == ["git", "checkout", "-b"]
       
        # Check add call
        assert calls[3][0][0] == ["git", "add", "changelog_data/"]
       
        # Check commit call
        assert calls[4][0][0][0:3] == ["git", "commit", "-sm"]
       
        # Check push call
        assert calls[5][0][0][0:3] == ["git", "push", "origin"]
   
    @patch('subprocess.run')
    def test_create_branch_and_commit_git_config_fails(self, mock_run):
        """Test handling of git config failure."""
        error = subprocess.CalledProcessError(1, "git config")
        error.stderr = "error"
        mock_run.side_effect = error
       
        with pytest.raises(subprocess.CalledProcessError):
            create_branch_and_commit()
   
    @patch('subprocess.run')
    def test_create_branch_and_commit_checkout_fails(self, mock_run):
        """Test handling of git checkout failure."""
        # First two calls succeed (config), third fails (checkout)
        error = subprocess.CalledProcessError(1, "git checkout")
        error.stderr = "branch exists"
        mock_run.side_effect = [
            Mock(returncode=0),  # config email
            Mock(returncode=0),  # config name
            error
        ]
       
        with pytest.raises(subprocess.CalledProcessError):
            create_branch_and_commit()
   
    @patch('subprocess.run')
    def test_create_branch_and_commit_push_fails(self, mock_run):
        """Test handling of git push failure."""
        # All succeed except last (push)
        error = subprocess.CalledProcessError(1, "git push")
        error.stderr = "remote error"
        mock_run.side_effect = [
            Mock(returncode=0),  # config email
            Mock(returncode=0),  # config name
            Mock(returncode=0),  # checkout
            Mock(returncode=0),  # add
            Mock(returncode=0),  # commit
            error
        ]
       
        with pytest.raises(subprocess.CalledProcessError):
            create_branch_and_commit()


class TestCreatePullRequestWithAPI:
    """Test PR creation using GitHub API."""
   
    @patch('scripts.create_pr.Github')
    def test_create_pr_with_api_success(self, mock_github_class, mock_env_vars):
        """Test successful PR creation via API."""
        # Setup mocks
        mock_github = Mock(spec=Github)
        mock_github_class.return_value = mock_github
       
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.html_url = "https://github.com/DSACMS/test-repo/pull/123"
       
        mock_repo.create_pull.return_value = mock_pr
        mock_github.get_repo.return_value = mock_repo
       
        # Call function
        title = "Test PR Title"
        body = "Test PR Body"
        branch_name = "test-branch"
       
        result = create_pull_request_with_api(title, body, branch_name)
       
        # Verify
        assert result == mock_pr
        mock_github_class.assert_called_once_with("test_token")
        mock_github.get_repo.assert_called_once_with("DSACMS/test-repo")
        mock_repo.create_pull.assert_called_once_with(
            title=title,
            body=body,
            head=branch_name,
            base="main"
        )
   
    @patch('scripts.create_pr.Github')
    def test_create_pr_with_api_adds_labels(self, mock_github_class, mock_env_vars):
        """Test that PR labels are added."""
        mock_github = Mock(spec=Github)
        mock_github_class.return_value = mock_github
       
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.html_url = "https://github.com/DSACMS/test-repo/pull/123"
       
        mock_repo.create_pull.return_value = mock_pr
        mock_github.get_repo.return_value = mock_repo
       
        create_pull_request_with_api("Title", "Body", "branch")
       
        # Verify labels were attempted
        mock_pr.add_to_labels.assert_called_once_with("changelog", "automated")
   
    @patch('scripts.create_pr.Github')
    def test_create_pr_with_api_label_failure_handled(self, mock_github_class, mock_env_vars):
        """Test that label addition failures don't crash the function."""
        mock_github = Mock(spec=Github)
        mock_github_class.return_value = mock_github
       
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.html_url = "https://github.com/DSACMS/test-repo/pull/123"
        mock_pr.add_to_labels.side_effect = Exception("Label error")
       
        mock_repo.create_pull.return_value = mock_pr
        mock_github.get_repo.return_value = mock_repo
       
        # Should not raise despite label error
        result = create_pull_request_with_api("Title", "Body", "branch")
        assert result == mock_pr
   
    def test_create_pr_with_api_no_token(self):
        """Test error when GitHub token is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GitHub token not found"):
                create_pull_request_with_api("Title", "Body", "branch")
   
    def test_create_pr_with_api_no_repo_env(self, mock_env_vars):
        """Test error when GITHUB_REPOSITORY is not set."""
        with patch.dict(os.environ, {"GH_TOKEN": "test_token"}, clear=True):
            with pytest.raises(ValueError, match="GITHUB_REPOSITORY environment variable not set"):
                create_pull_request_with_api("Title", "Body", "branch")
   
    @patch('scripts.create_pr.Github')
    def test_create_pr_with_api_github_exception(self, mock_github_class, mock_env_vars):
        """Test handling of GitHub API exceptions."""
        mock_github = Mock(spec=Github)
        mock_github_class.return_value = mock_github
       
        mock_repo = Mock()
        mock_repo.create_pull.side_effect = GithubException(422, "Validation failed")
        mock_github.get_repo.return_value = mock_repo
       
        with pytest.raises(GithubException):
            create_pull_request_with_api("Title", "Body", "branch")


class TestCreatePullRequestWithCLI:
    """Test PR creation using GitHub CLI."""
   
    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_create_pr_with_cli_success(self, mock_unlink, mock_tempfile, mock_run):
        """Test successful PR creation via CLI."""
        # Setup temp file mock
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_body.md"
        mock_file.__enter__.return_value = mock_file
        mock_tempfile.return_value = mock_file
       
        # Setup subprocess mock
        mock_result = Mock()
        mock_result.stdout = "https://github.com/DSACMS/test-repo/pull/123\n"
        mock_run.return_value = mock_result
       
        title = "Test PR"
        body = "Test Body"
        branch_name = "test-branch"
       
        result = create_pull_request_with_cli(title, body, branch_name)
       
        # Verify
        assert result == "https://github.com/DSACMS/test-repo/pull/123"
       
        # Verify gh command was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0:3] == ["gh", "pr", "create"]
        assert "--title" in call_args
        assert title in call_args
        assert "--base" in call_args
        assert "main" in call_args
        assert "--head" in call_args
        assert branch_name in call_args
       
        # Verify temp file was cleaned up
        mock_unlink.assert_called_once_with("/tmp/test_body.md")
   
    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    def test_create_pr_with_cli_not_found(self, mock_tempfile, mock_run):
        """Test handling when gh CLI is not installed."""
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_body.md"
        mock_file.__enter__.return_value = mock_file
        mock_tempfile.return_value = mock_file
       
        mock_run.side_effect = FileNotFoundError("gh not found")
       
        result = create_pull_request_with_cli("Title", "Body", "branch")
       
        # Should return None to signal fallback
        assert result is None
   
    @patch('os.unlink')
    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    def test_create_pr_with_cli_command_fails(self, mock_tempfile, mock_run, mock_unlink):
        """Test handling of gh CLI command failure."""
        # Setup temp file mock
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_body.md"
        mock_file.write = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file
       
        # Create the error
        error = subprocess.CalledProcessError(1, ["gh", "pr", "create"])
        error.stdout = ""
        error.stderr = "error creating PR"
       
        # Mock subprocess.run to raise
        mock_run.side_effect = error
       
        # Should raise the CalledProcessError
        with pytest.raises(subprocess.CalledProcessError):
            create_pull_request_with_cli("Title", "Body", "branch")
       
        # Verify cleanup still happened
        mock_unlink.assert_called_once_with("/tmp/test_body.md")


@pytest.mark.integration
class TestMainFunction:
    """Test the main PR creation workflow."""
   
    @patch('scripts.create_pr.create_pull_request_with_cli')
    @patch('scripts.create_pr.create_branch_and_commit')
    @patch('scripts.create_pr.get_latest_summary_files')
    @patch('builtins.open', new_callable=mock_open, read_data="Test Title")
    def test_main_success_with_cli(self, mock_file, mock_get_files,
                                     mock_create_branch, mock_create_pr_cli):
        """Test successful main execution using CLI."""
        # Setup mocks
        mock_get_files.return_value = ("title.txt", "body.md")
        mock_create_branch.return_value = "weekly-changelog-2025-01-08"
        mock_create_pr_cli.return_value = "https://github.com/DSACMS/test-repo/pull/123"
       
        # Configure file reading
        mock_file.return_value.read.side_effect = [
            "Test PR Title",
            "Test PR Body"
        ]
       
        result = main()
       
        # Verify workflow
        assert result == "https://github.com/DSACMS/test-repo/pull/123"
        mock_get_files.assert_called_once()
        mock_create_branch.assert_called_once()
        mock_create_pr_cli.assert_called_once_with(
            "Test PR Title",
            "Test PR Body",
            "weekly-changelog-2025-01-08"
        )
   
    @patch('scripts.create_pr.create_pull_request_with_api')
    @patch('scripts.create_pr.create_pull_request_with_cli')
    @patch('scripts.create_pr.create_branch_and_commit')
    @patch('scripts.create_pr.get_latest_summary_files')
    @patch('builtins.open', new_callable=mock_open, read_data="Test Title")
    def test_main_fallback_to_api(self, mock_file, mock_get_files,
                                   mock_create_branch, mock_create_pr_cli,
                                   mock_create_pr_api):
        """Test fallback to API when CLI fails."""
        # Setup mocks
        mock_get_files.return_value = ("title.txt", "body.md")
        mock_create_branch.return_value = "weekly-changelog-2025-01-08"
        mock_create_pr_cli.side_effect = FileNotFoundError("gh not found")
       
        mock_pr = Mock()
        mock_pr.html_url = "https://github.com/DSACMS/test-repo/pull/123"
        mock_create_pr_api.return_value = mock_pr
       
        mock_file.return_value.read.side_effect = [
            "Test PR Title",
            "Test PR Body"
        ]
       
        result = main()
       
        # Verify API was called after CLI failed
        assert result == "https://github.com/DSACMS/test-repo/pull/123"
        mock_create_pr_cli.assert_called_once()
        mock_create_pr_api.assert_called_once()
   
    @patch('scripts.create_pr.get_latest_summary_files')
    def test_main_get_files_fails(self, mock_get_files):
        """Test main handles file retrieval failure."""
        mock_get_files.side_effect = FileNotFoundError("Files not found")
       
        with pytest.raises(FileNotFoundError):
            main()
   
    @patch('scripts.create_pr.create_branch_and_commit')
    @patch('scripts.create_pr.get_latest_summary_files')
    @patch('builtins.open', new_callable=mock_open, read_data="Test Title")
    def test_main_git_operations_fail(self, mock_file, mock_get_files, mock_create_branch):
        """Test main handles git operation failures."""
        mock_get_files.return_value = ("title.txt", "body.md")
        error = subprocess.CalledProcessError(1, "git")
        error.stderr = "error"
        mock_create_branch.side_effect = error
       
        mock_file.return_value.read.side_effect = [
            "Test PR Title",
            "Test PR Body"
        ]
       
        with pytest.raises(subprocess.CalledProcessError):
            main()
   
    @patch('scripts.create_pr.create_pull_request_with_cli')
    @patch('scripts.create_pr.create_pull_request_with_api')
    @patch('scripts.create_pr.create_branch_and_commit')
    @patch('scripts.create_pr.get_latest_summary_files')
    @patch('builtins.open', new_callable=mock_open, read_data="Test Title")
    def test_main_both_pr_methods_fail(self, mock_file, mock_get_files,
                                        mock_create_branch, mock_create_pr_api,
                                        mock_create_pr_cli):
        """Test main handles failure of both PR creation methods."""
        mock_get_files.return_value = ("title.txt", "body.md")
        mock_create_branch.return_value = "weekly-changelog-2025-01-08"
        error = subprocess.CalledProcessError(1, "gh")
        error.stderr = "error"
        mock_create_pr_cli.side_effect = error
        mock_create_pr_api.side_effect = GithubException(422, "API error")
       
        mock_file.return_value.read.side_effect = [
            "Test PR Title",
            "Test PR Body"
        ]
       
        with pytest.raises(GithubException):
            main()