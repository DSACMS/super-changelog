from github import Github # type: ignore
from datetime import datetime, timezone, timedelta
import json
import os

timestamp = datetime.now(timezone.utc).strftime("%y-%m-%d")
filename = f"data/changelog{timestamp}.json"

token = os.getenv("GH_TOKEN")
org_name = "DSACMS"

g = Github(token)
org = g.get_organization(org_name)

data = {"repos" : []}

for repo in org.get_repos(type="public"):
    repo_data = {
        "name": repo.name,
        "url": repo.html_url,
        "description": repo.description,
        "issues": [],
        "pulls": [],
        "commits": []
    }

    for issue in repo.get_issues(state="open"):
        if issue.pull_request is None:
            repo_data["issues"].append({
                "title": issue.title,
                "url": issue.html_url,
                "created_at": issue.created_at.isoformat()
            })

    for pr in repo.get_pulls(state="open"):
        if issue.pull_request is None:
            repo_data["pulls"].append({
                "title": pr.title,
                "url": pr.html_url,
                "created_at": pr.created_at.isoformat()
            })

    for commit in repo.get_commits():
        if issue.pull_request is None:
            repo_data["commits"].append({
                "message": commit.commit.message,
                "url": commit.html_url,
                "author": commit.commit.author.name,
                "created_at": commit.commit.author.date.isoformat()
            })

    data["repos"].append(repo_data)

with open(filename, "w") as f:
    json.dump(data, f, indent=2)

print("✅ Changelog data written to data/changelog.json")