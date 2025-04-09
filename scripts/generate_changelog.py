from github import Github # type: ignore
import json
import os

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
        "pulls": []
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

    data["repos"].append(repo_data)

with open("data/changelog.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ Changelog data written to data/changelog.json")