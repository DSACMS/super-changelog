import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any
import urllib.parse

def generate_summary(data_file: str) -> Dict[str, Any]:
    """Generate a summary from changelog data."""
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading data file {data_file}: {e}")
        raise

    if "repos" not in data:
        print("Invalid data structure: missing 'repos' key")
        raise ValueError("Invalid data structure: missing 'repos' key")

    summary = {
        "period": data.get("period", {}),
        "generated_at": data.get("generated_at"),
        "total_repos": len(data["repos"]),
        "active_repos": 0,
        "total_issues": 0,
        "total_pulls": 0,
        "total_commits": 0,
        "total_changelog_entries": 0,
        "repos_with_activity": [],
        "key_changes": []
    }

    for repo_data in data.get("repos", []):
        try:
            repo_name = repo_data.get("name", "Unknown")
            has_activity = False

            repo_summary = {
                "name": repo_name,
                "url": repo_data["url"],
                "issues": len(repo_data["issues"]),
                "pulls": len(repo_data["pulls"]),
                "commits": len(repo_data["commits"]),
                "changelog_entries": len(repo_data.get("changelog_entries", [])),
                "highlights": []
            }

            summary["total_issues"] += len(repo_data.get("issues", []))
            summary["total_pulls"] += len(repo_data.get("pulls", []))
            summary["total_commits"] += len(repo_data.get("commits", []))
            summary["total_changelog_entries"] += len(repo_data.get("changelog_entries", []))

            if (repo_data.get("issues") or repo_data.get("pulls") or
                repo_data.get("commits") or repo_data.get("changelog_entries")):
                has_activity = True
                summary["active_repos"] += 1

            for entry in repo_data.get("changelog_entries", []):
                for change in entry.get("changes", []):
                    category = change.get("category", "")
                    items = change.get("items", [])

                    if category.lower().startswith(('add', 'new')):
                        for item in items[:2]:
                            repo_summary["highlights"].append(f"Added: {item}")
                            summary["key_changes"].append(f"{repo_name}: Added {item}")
                    
                    elif category.lower().startswith(('fix', 'bug')):
                        for item in items[:2]:
                            repo_summary["highlights"].append(f"Fixed: {item}")
                            summary["key_changes"].append(f"{repo_name}: Fixed {item}")

                    elif category.lower().startswith(('chang')):
                        for item in items[:1]:
                            repo_summary["highlights"].append(f"Changed: {item}")
                            summary["key_changes"].append(f"{repo_name}: Changed {item}")

            merged_prs = [pr for pr in repo_data["pulls"] if pr.get("merged")]
            if merged_prs:
                repo_summary["highlights"].append(f"{len(merged_prs)} PR(s) merged")

            new_issues = [issue for issue in repo_data["issues"] if issue.get("is_new")]
            if new_issues:
                repo_summary["highlights"].append(f"{len(new_issues)} new issue(s)")

            summary["repos_with_activity"].append(repo_summary)
        
        except Exception as e:
            print(f"Error processing repo {repo_data.get('name', 'Unknown')}: {e}")
            continue

    return summary

def create_mailto_link(summary: Dict[str, Any]) -> str:
    """Create a mailto link with summary that fits within character limits."""
    period = summary.get("period", {})
    start_date = period.get("start", "")
    end_date = period.get("end", "")

    subject = f"Weekly Changelog Summary ({start_date} to {end_date})"

    body_lines = [
        f"Weekly Developement Summary: {start_date} to {end_date}",
        "",
        f"Overview:",
        f"• {summary.get('active_repos', 0)} of {summary.get('total_repos', 0)} repos with activity",
        f"• {summary.get('total_commits', 0)} commits, {summary.get('total_pulls', 0)} PRs, {summary.get('total_issues', 0)} issues",
        ""
    ]

    if summary.get('key_changes'):
        body_lines.append("Key Changes:")
        for change in summary['key_changes'][:10]:
            if len(' '.join(body_lines)) + len(f"• {change}") < 1500:
                body_lines.append(f"• {change}")
            else:
                body_lines.append("• ... and more")
                break
        body_lines.append("")

    if summary.get('repos_with_activity'):
        body_lines.append("Most Active Repos:")
        sorted_repos = sorted(summary['repos_with_activity'],
                              key=lambda x: x.get('commits', 0) + x.get('pulls', 0), reverse=True)
        for repo in sorted_repos[:5]:
            if len(' '.join(body_lines)) + len(f"• {repo['name']}") < 1800:
                body_lines.append(f"• {repo['name']}: {repo.get('commits', 0)} commits, {repo.get('pulls', 0)} PRs")
            else:
                break

    body = '\n'.join(body_lines)

    subject_encoded = urllib.parse.quote(subject)
    body_encoded = urllib.parse.quote(body)

    mailto_link = f"mailto:?subject={subject_encoded}&body={body_encoded}"

    return mailto_link

def create_slack_message(summary: Dict[str, Any]) -> str:
    """Create a Slack message."""
    period = summary.get("period", {})
    start_date = period.get("start", "")
    end_date = period.get("end", "")

    message_blocks = [
         f"Weekly Changelog Summary* ({start_date} to {end_date})",
        "",
        f"• {summary.get('active_repos', 0)} of {summary.get('total_repos', 0)} repos with activity",
        f"• {summary.get('total_commits', 0)} commits | {summary.get('total_pulls', 0)} PRs | {summary.get('total_issues', 0)} issues",
        ""
    ]

    if summary.get('key_changes'):
        message_blocks.append("*Key Changes:*")
        for change in summary['key_changes'][:8]:
           message_blocks.append(f"• {change}")
        message_blocks.append("")

    if summary['repos_with_activity']:
        message_blocks.append("*Most Active Repos:*")
        sorted_repos = sorted(summary['repos_with_activity'],
                              key=lambda x: x.get('commits', 0) + x.get('pulls', 0), reverse=True)
        for repo in sorted_repos[:5]:
            message_blocks.append(f"• *{repo['name']}*: {repo.get('commits', 0)} commits, {repo.get('pulls', 0)} PRs")

    return '\n'.join(message_blocks)

def create_pr_content(summary: Dict[str, Any]) -> tuple:
    """Create PR title and body content."""
    period = summary.get("period", {})
    start_date = period.get("start", "")
    end_date = period.get("end", "")

    title = f"Weekly Changelog Summary: {start_date} to {end_date}"

    body_sections = [
        f"# Weekly Development Summary",
        f"**Period**: {start_date} to {end_date}",
        "",
        "## Overview",
        f"- **Active Repositories**: {summary.get('active_repos', 0)} of {summary.get('total_repos', 0)} total repos",
        f"- **Commits**: {summary.get('total_commits', 0)}",
        f"- **Pull Requests**: {summary.get('total_pulls', 0)}",
        f"- **Issues**: {summary.get('total_issues', 0)}",
        f"- **Changelog Entries**: {summary.get('total_changelog_entries', 0)}",
        ""
    ]

    if summary['key_changes']:
        body_sections.extend([
            "## Key Changes",
            ""
        ])

        changes_by_repo = {}
        for change in summary['key_changes']:
            repo_name = change.split(':')[0]
            change_text = ':'.join(change.split(':')[1:]).strip()
            if repo_name not in changes_by_repo:
                changes_by_repo[repo_name] = []
            changes_by_repo[repo_name].append(change_text)

        for repo_name, changes in changes_by_repo.items():
            body_sections.append(f"### {repo_name}")
            for change in changes:
                body_sections.append(f"- {change}")
            body_sections.append("")

    if summary['repos_with_activity']:
        body_sections.extend([
            "## Repository Activity Details",
            ""
        ])

        sorted_repos = sorted(summary["repos_with_activity"],
                              key=lambda x: x.get('commits', 0) + x.get('pulls', 0), reverse=True)
        
        for repo in sorted_repos:
            body_sections.append(f"### [{repo['name']}]({repo.get('url', '')})")
            body_sections.append(f"- **Commits**: {repo.get('commits', 0)}")
            body_sections.append(f"- **Pull Request**: {repo.get('pulls', 0)}")
            body_sections.append(f"- **Issues**: {repo.get('issues', 0)}")
            body_sections.append(f"- **Changelog Entries**: {repo.get('changelog_entries', 0)}")

            if repo['highlights']:
                body_sections.append("- **Highlights**:")
                for highlight in repo['highlights']:
                    body_sections.append(f" - {highlight}")

            body_sections.append("")

    body_sections.extend([
        "---",
        f"*Generated automatically on {summary.get('generated_at', 'Unknoen')}*"
    ])

    return title, '\n'.join(body_sections)

def main():
    """Main function to generate all summary formats."""
    try:
        data_dir = "changelog_data/data"
        if not os.path.exists(data_dir):
            print("Data directory not found. Run the weekly changelog generator first.")
            return
        
        weekly_files = [f for f in os.listdir(data_dir) if f.startswith("weekly_changelog_")]
        if not weekly_files:
            print("No weekly changelog files found.")
            return
        
        latest_file = sorted(weekly_files)[-1]
        data_file = os.path.join(data_dir, latest_file)

        print(f"Generated summary from {latest_file}")

        summary = generate_summary(data_file)

        print(f"Summary stats: {summary.get('active_repos', 0)} active repos out of {summary.get('total_repos', 0)} total")

        output_dir = "changelog_data/summaries"
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%y-%m-%d")
        summary_file = os.path.join(output_dir, f"summary_{timestamp}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        mailto_link = create_mailto_link(summary)
        mailto_file = os.path.join(output_dir, f"mailto_{timestamp}.txt")
        with open(mailto_file, 'w') as f:
            f.write(mailto_link)

        slack_message = create_slack_message(summary)
        slack_file = os.path.join(output_dir, f"slack_{timestamp}.txt")
        with open(slack_file, 'w') as f:
            f.write(slack_message)

        pr_title, pr_body = create_pr_content(summary)
        pr_title_file = os.path.join(output_dir, f"pr_title_{timestamp}.txt")
        pr_body_file = os.path.join(output_dir, f"pr_body_{timestamp}.md")

        with open(pr_title_file, 'w') as f:
            f.write(pr_title)

        with open(pr_body_file, 'w') as f:
            f.write(pr_body)

        print(f"Summary generated successfully!")
        print(f"Files saved to {output_dir}/")
        print(f"Mailto link: {mailto_file}")
        print(f"Slack message: {slack_file}")
        print(f"PR content: {pr_title_file}, {pr_body_file}")

        return summary_file
    
    except Exception as e:
        print(f"Error generating summary: {e}")
        raise

if __name__ == "__main__":
    main()
