from github import Github # type: ignore
from datetime import datetime, timezone, timedelta
import json
import os
import re

def main():
    timestamp = datetime.now(timezone.utc).strftime("%y-%m-%d")
    filename = f"changelog_data/data/changelog{timestamp}.json"
    # since = datetime.now(timezone.utc) - timedelta(days=7)

    os.makedirs("data", exist_ok=True)

    token = os.getenv("GH_TOKEN") or os.getenv("REPOLINTER_AUTO_TOKEN")
    if not token:
        raise ValueError("Github token not found in environmental variables")
    
    org_name = "DSACMS"

    g = Github(token)
    org = g.get_organization(org_name)

    data = {"repos": [], "generate_at": datetime.now(timezone.utc).isoformat()}

    for repo in org.get_repos(type="public"):
        repo_data = {
            "name": repo.name,
            "url": repo.html_url,
            "description": repo.description,
            "issues": [],
            "pulls": [],
            "commits": [],
            "changelog_entries": []
        }

        try:
            for issue in repo.get_issues(state="all"):
                if issue.pull_request is None:
                    repo_data["issues"].append({
                        "title": issue.title,
                        "url": issue.html_url,
                        "created_at": issue.created_at.isoformat(),
                        "state": issue.state
                })
        except Exception as e:
            print(f"Error fetching issues for {repo.name}: {str(e)}")

        try:
            for pr in repo.get_pulls(state="all"):
                repo_data["pulls"].append({
                    "title": pr.title,
                    "url": pr.html_url,
                    "created_at": pr.created_at.isoformat(),
                    "state": pr.state,
                    "merged": pr.merged
                })
        except Exception as e:
            print(f"Error fetching PRs for {repo.name}: {str(e)}")

        try:
            for commit in repo.get_commits():
                repo_data["commits"].append({
                    "message": commit.commit.message,
                    "url": commit.html_url,
                    "author": commit.commit.author.name,
                    "created_at": commit.commit.author.date.isoformat()
                })
        except Exception as e:
            print(f"Error fetching commits for {repo.name}: {str(e)}")

        try:
            changelog_files = [
                "CHANGELOG.md",
                "Changelog.md",
                "changelog.md",
                "CHANGELOG",
                "Changelog",
                "changelog"
            ]

            for changelog_file in changelog_files:
                try:
                    content = repo.get_contents(changelog_file)
                    if content:
                        changelog_text = content.decoded_content.decode('utf-8')
                        changelog_entries = parse_changelog(changelog_text)
                        repo_data["changelog_entries"] = changelog_entries
                        break
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Error checking changelog for {repo.name}: {str(e)}")

        data["repos"].append(repo_data)

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Changelog data written to {filename}")
    return filename

def parse_changelog(content):
    entries = []

    categories = [
        r'[Aa]dd(?:ed|s|ing)?',
        r'[Cc]hang(?:ed|e|es|ing)?',
        r'[Dd]eprecat(?:ed|e|es|ing)?',
        r'[Rr]emov(?:ed|e|es|ing)?',
        r'[Ff]ix(?:ed|es|ing)?',
        r'[Ss]ecur(?:ity|ed|e|ing)?'
    ]

    version_patterns = [
        r'^#+\s*(?:v|\[)?(\d+\.\d+\.\d+)(?:\])?.*?$'
        r'^#+\s*(\d{4}-\d{2}-\d{2}).*?$'
        r'^#+\s*[Rr]elease\s+(?:v|\[)?(\d+\.\d+\.\d+)(?:\])?.*?$'
        r'^#+\s*[Vv]ersion\s+(?:v|\[)?(\d+\.\d+\.\d+)(?:\])?.*?$'
    ]

    release = []
    lines = content.split('\n')
    current_release = {"version": "unknown", "date": None, "changes": []}

    for line in lines:
        for pattern in version_patterns:
            match = re.search(current_release)
            if match:
                if current_release["changes"]:
                    release.append(current_release)

                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
                release_date = date_match.group(1) if date_match else None

                current_release = {
                    "version": match.group(1),
                    "date": release_date,
                    "changes": []
                }
                break

        for category_pattern in categories:
            category_match = re.search(rf'(?:^#+\s*|^\s*-\s*\*\*|\s+-\s+)({category_pattern})[:\s]*$', line, re.IGNORECASE)
            if category_match:
                category = category_match.group(1)
                current_release["changes"].append({"category": category, "items": []})
                continue

            if current_release["changes"] and (line.strip().startswith('-') or line.strip().startswith('*')):
                item_text = line.strip()[1:].strip()
                if item_text and not any(item_text.lower().startwith(cat.lower()) for cat in ['added', 'changed', 'depreciated', 'removed', 'fixed', 'security']):
                    if current_release["changes"]:
                        current_release["changes"][-1]["items"].append(item_text)

    if current_release["changes"]:
        release.append(current_release)

    return

if __name__ == "__main__":
    main()