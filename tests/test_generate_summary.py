import pytest
import json
import os
import tempfile
from datetime import datetime, timezone
from scripts.generate_summary import (
    generate_summary,
    create_mailto_link,
    create_slack_message,
    create_pr_content,
    main
)


class TestGenerateSummary:
    """Test to generate_summary function"""

    def test_generate_summary_basic_structure(self, mock_changelog_data, temp_dir):
        """Test that generate_summary returns correct structure."""
        data_file = os.path.join(temp_dir, "test_data.json")
        with open(data_file, 'w') as f:
            json.dump(mock_changelog_data, f)

        summary = generate_summary(data_file)

        assert "period" in summary
        assert "generated_at" in summary
        assert "total_repos" in summary
        assert "active_repos" in summary
        assert "total_issues" in summary
        assert "total_pulls" in summary
        assert "total_commits" in summary
        assert "repos_with_activity" in summary
        assert "key_changes" in summary

    def test_generate_summary_counts(self, mock_changelog_data, temp_dir):
        """Test that summary correctly counts items"""
        data_file = os.path.join(temp_dir, "test_data.json")
        with open(data_file, 'w') as f:
            json.dump(mock_changelog_data, f)

        summary = generate_summary(data_file)

        assert summary["total_repos"] == 1
        assert summary["active_repos"] == 1
        assert summary["total_issues"] == 1
        assert summary["total_pulls"] == 1
        assert summary["total_commits"] == 1
        assert summary["total_changelog_entries"] == 1

    def test_generate_summary_key_changes(self, mock_changelog_data, temp_dir):
        """Test key changes are extracted correctly."""
        data_file = os.path.join(temp_dir, "test_data.json")
        with open(data_file, 'w') as f:
            json.dump(mock_changelog_data, f)

        summary = generate_summary(data_file)

        assert len(summary["key_changes"]) > 0
        assert any("Added" in change for change in summary["key_changes"])

    def test_generate_summary_file_not_found(self):
        """Test handling of missing file."""
        with pytest.raises(FileNotFoundError):
            generate_summary("noneexistent_file.json")

    def test_generate_summary_invalid_json(self, temp_dir):
        """Test handling of invalid JSON."""
        data_file = os.path.join(temp_dir, "invalid.json")
        with open(data_file, 'w') as f:
            f.write("not valid json{{{")

        with pytest.raises(json.JSONDecodeError):
            generate_summary(data_file)

    def test_generate_summary_missing_repos_key(self, temp_dir):
        """Test handling of invalid data structure."""
        data_file = os.path.join(temp_dir, "bad_structure.json")
        with open(data_file, 'w') as f:
            json.dump({"period": {}, "generated_at": "2025-01-01"}, f)

        with pytest.raises(ValueError):
            generate_summary(data_file)


class TestCreateMailToLink:
    """Test mailto link creation."""

    def test_mailto_link_structure(self, mock_changelog_data, temp_dir):
        """Test that mailto link is properly formatted."""
        data_file = os.path.join(temp_dir, "test_data.json")
        with open(data_file, 'w') as f:
            json.dump(mock_changelog_data, f)

        summary = generate_summary(data_file)
        mailto_link = create_mailto_link(summary)

        assert mailto_link.startswith("mailto:?")
        assert "subject=" in mailto_link
        assert "body=" in mailto_link

    def test_mailto_link_contains_key_info(self, mock_changelog_data, temp_dir):
        """Test that mailto link contains important info."""
        data_file = os.path.join(temp_dir, "test_data.json")
        with open(data_file, 'w') as f:
            json.dump(mock_changelog_data, f)

        summary = generate_summary(data_file)
        mailto_link = create_mailto_link(summary)

        assert "2025-01-01" in mailto_link or "2025%2D01%2D01" in mailto_link


class TestCreateSlackMessage:
    """Test Slack message creation."""

    def test_slack_message_format(self, mock_changelog_data, temp_dir):
        """Test Slack message is properly formatted."""
        data_file = os.path.join(temp_dir, "test_data.json")
        with open(data_file, 'w') as f:
            json.dump(mock_changelog_data, f)

        summary = generate_summary(data_file)
        slack_message = create_slack_message(summary)

        assert isinstance(slack_message, str)
        assert len(slack_message) > 0
        assert "Weekly Changelog Summary" in slack_message

    def test_slack_message_contains_stats(self, mock_changelog_data, temp_dir):
        """Test that Slack massage contains stats."""
        data_file = os.path.join(temp_dir, "test_data.json")
        with open(data_file, 'w') as f:
            json.dump(mock_changelog_data, f)

        summary = generate_summary(data_file)
        slack_message = create_slack_message(summary)

        assert "1" in slack_message
        assert "commits" in slack_message.lower()
        assert "PRs" in slack_message or "prs" in slack_message.lower()


class TestCreatePRContent:
    """Test PR content creation."""

    def test_pr_content_returns_tuple(self, mock_changelog_data, temp_dir):
        """Test that create_pr_content returns a title and body."""
        data_file = os.path.join(temp_dir, "test_data.json")
        with open(data_file, 'w') as f:
            json.dump(mock_changelog_data, f)

        summary = generate_summary(data_file)
        result = create_pr_content(summary)

        assert isinstance(result, tuple)
        assert len(result) == 2

        title, body = result
        assert isinstance(title, str)
        assert isinstance(body, str)

    def test_pr_title_format(self, mock_changelog_data, temp_dir):
        """Test PR title format"""
        data_file = os.path.join(temp_dir, "test_data.json")
        with open(data_file, 'w') as f:
            json.dump(mock_changelog_data, f)

        summary = generate_summary(data_file)
        title, _ = create_pr_content(summary)

        assert "Weekly Changelog Summary" in title
        assert "2025-01-01" in title
        assert "2025-01-08" in title

    def test_pr_body_markdown_format(self, mock_changelog_data, temp_dir):
        """Test that PR body uses markdown formatting."""
        data_file = os.path.join(temp_dir, "test_data.json")
        with open(data_file, 'w') as f:
            json.dump(mock_changelog_data, f)

        summary = generate_summary(data_file)
        _, body = create_pr_content(summary)

        assert "#" in body
        assert "-" in body
        assert "Overview" in body
        assert "Repository Activity" in body

    def test_body_includes_repo_details(self, mock_changelog_data, temp_dir):
        """Test that PR body includes repo details."""
        data_file = os.path.join(temp_dir, "test_data.json")
        with open(data_file, 'w') as f:
            json.dump(mock_changelog_data, f)

        summary = generate_summary(data_file)
        _, body = create_pr_content(summary)

        assert "test-repo" in body
        assert "https://github.com" in body


@pytest.mark.integration
class TestMainFunction:
    """Test the main function integration"""

    def test_main_creates_output_files(self, mock_changelog_data, temp_dir, monkeypatch):
        """Test that main creates all expected output files."""
        data_dir = os.path.join(temp_dir, "changelog_data", "data")
        os.makedirs(data_dir, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%y-%m-%d")
        data_file = os.path.join(data_dir, f"weekly_changelog_{timestamp}.json")
        with open(data_file, 'w') as f:
            json.dump(mock_changelog_data, f)

        monkeypatch.chdir(temp_dir)

        result = main()

        summary_dir = os.path.join(temp_dir, "changelog_data", "summaries")
        assert os.path.exists(summary_dir)

        files = os.listdir(summary_dir)
        assert any(f.startswith("summary_") for f in files)
        assert any(f.startswith("mailto_") for f in files)
        assert any(f.startswith("slack_") for f in files)
        assert any(f.startswith("pr_title_") for f in files)
        assert any(f.startswith("pr_body_") for f in files)

    def test_main_no_data_directory(self, temp_dir, monkeypatch):
        """Test handles missing data directory."""
        monkeypatch.chdir(temp_dir)

        result = main()
        assert result is None

    def test_main_no_weekly_files(self, temp_dir, monkeypatch):
        """Test main handles missing weekly changelog files."""
        data_dir = os.path.join(temp_dir, "changelog_data", "data")
        os.makedirs(data_dir, exist_ok=True)

        monkeypatch.chdir(temp_dir)

        result = main()
        assert result is None