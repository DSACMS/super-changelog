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