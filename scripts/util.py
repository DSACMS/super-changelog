from github import Github # type: ignore
from datetime import datetime, timezone, timedelta
import json
import os
import re


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

class ChangelogGenerator:
    def __init__(self, token, filename=None,log_history_start=None):
        self.now = datetime.now(timezone.utc)
        self.log_history_start = log_history_start

        self.timestamp = self.now.strftime("%Y-%m-%d")
        self.start_date = datetime.strptime(self.log_history_start, "%Y-%m-%d") if log_history_start else None
        self.end_date = self.now.strftime("%Y-%m-%d")

        self.filename = filename
        self.token = token

        self.g = Github(token)
    
    def get_data(self,org_name):

        org = self.g.get_organization(org_name)

        data = {
            "repos": [],
            "period": {
                "start": self.log_history_start,
                "end": self.end_date
            },
            "generated_at": self.now.isoformat()
        }

        for repo in org.get_repos(type="public"):
            print(f"Processing repo: {repo.name}")
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
                issues_and_prs = repo.get_issues(state="all")

                num_issues = len([issue for issue in issues_and_prs if issue.pull_request is None])
                print(f"Found {num_issues} issues")

                num_prs = len([issue for issue in issues_and_prs if issue.pull_request])
                print(f"Found {num_prs} pull requests")

                #print(self.start_date)

                for n, issue in enumerate(issues_and_prs):
                    #print(n)
                    #print(issue.created_at)
                    if issue.created_at.replace(tzinfo=None) >= self.start_date or issue.updated_at.replace(tzinfo=None) >= self.start_date:
                        #print(f"GOT ONE {n}")
                        if not issue.pull_request:
                            #print(issue)
                            repo_data["issues"].append({
                                "title": issue.title,
                                "url": issue.html_url,
                                "created_at": issue.created_at.isoformat(),
                                "state": issue.state,
                                "is_new": issue.created_at.replace(tzinfo=None) >= self.start_date
                            })
                        else:
                            pr = repo.get_pull(issue.number)
                            #print(f"Got PULL merged: {pr.is_merged()}")
                            repo_data["pulls"].append({
                                "title":pr.title,
                                "url": pr.html_url,
                                "created_at": pr.created_at.isoformat(),
                                "updated_at": pr.updated_at.isoformat(),
                                "state": pr.state,
                                "merged": pr.is_merged(),
                                "is_new": pr.created_at.replace(tzinfo=None) >= self.start_date
                            })

            except Exception as e:
                print(f"Error fetching issues and pull_requests for {repo.name}: {str(e)}")
            
            try:
                for commit in repo.get_commits(since=self.start_date):
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
                            all_entries = parse_changelog(changelog_text)

                            recent_entries = []

                            for entry in all_entries:
                                if entry.get("date"):
                                    try:
                                        entry_date = datetime.fromisoformat(entry["date"])
                                        if end_date >= one_week_ago:
                                            recent_entries.append(entry)
                                    except (ValueError, TypeError):
                                        if len(recent_entries) < 2 and all_entries.index(entry) < 3:
                                            recent_entries.append(entry)
                                elif all_entries.index(entry) < 2:
                                        recent_entries.append(entry)

                            
                            repo_data["changelog_entries"] = recent_entries
                            break
                    except Exception as e:
                        continue
            except Exception as e:
                print(f"Error checking changelog for {repo.name}: {str(e)}")
            
            if (repo_data["issues"] or repo_data["pulls"] or
                repo_data["commits"] or repo_data["changelog_entries"]):
                data["repos"].append(repo_data)
        
        return data
    
    def save_data(self,data):
        if not self.filename:
            return None


        with open(self.filename, "w") as f:
            json.dump(data, f, indent=2)
        
        return self.filename
    
    def get_and_save_data(self,org_name):
        data = self.get_data(org_name)
        return self.save_data(data)


         

