from github import Github # type: ignore
from datetime import datetime, timezone
import json
import os
import re
import time

def parse_changelog(content):
    categories = [
        r'[Aa]dd(?:ed|s|ing)?',
        r'[Cc]hang(?:ed|e|es|ing)?',
        r'[Dd]eprecat(?:ed|e|es|ing)?',
        r'[Rr]emov(?:ed|e|es|ing)?',
        r'[Ff]ix(?:ed|es|ing)?',
        r'[Ss]ecur(?:ity|ed|e|ing)?'
    ]

    version_patterns = [
        r'^#+\s*(?:v|\[)?(\d+\.\d+\.\d+)(?:\])?.*?$',
        r'^#+\s*(\d{4}-\d{2}-\d{2}).*?$',
        r'^#+\s*[Rr]elease\s+(?:v|\[)?(\d+\.\d+\.\d+)(?:\])?.*?$',
        r'^#+\s*[Vv]ersion\s+(?:v|\[)?(\d+\.\d+\.\d+)(?:\])?.*?$',
    ]

    release = []
    lines = content.split('\n')
    current_release = {"version": "unknown", "date": None, "changes": []}

    for line in lines:
        matched_version = False
        for pattern in version_patterns:
            match = re.search(pattern, line)
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
                matched_version = True
                break

        if matched_version:
            continue

        matched_category = False
        for category_pattern in categories:
            category_match = re.search(
                rf'(?:^#+\s*|^\s*-\s*\*\*|\s+-\s+)({category_pattern})[:\s]*$',
                line, re.IGNORECASE
            )
            if category_match:
                category = category_match.group(1)
                current_release["changes"].append({"category": category, "items": []})
                matched_category = True
                break

        if matched_category:
            continue

        if current_release["changes"] and (
            line.strip().startswith('-') or line.strip().startswith('*')
        ):
            item_text = line.strip()[1:].strip()
            skip_prefixes = ['added', 'changed', 'deprecated', 'removed', 'fixed', 'security']
            if item_text and not any(
                item_text.lower().startswith(cat) for cat in skip_prefixes
            ):
                current_release["changes"][-1]["items"].append(item_text)

    if current_release["changes"]:
        release.append(current_release)

    return release

class ChangelogGenerator:
    def __init__(self, token, filename=None,log_history_start=None, log_history_end=None):
        self.now = datetime.now(timezone.utc)
        self.log_history_start = log_history_start
        self.log_history_end = log_history_end

        self.timestamp = self.now.strftime("%Y-%m-%d")
        self.start_date = datetime.strptime(self.log_history_start, "%Y-%m-%d") if log_history_start else None
        self.end_date = datetime.strptime(self.log_history_end, "%Y-%m-%d") if log_history_end else None

        self.filename = filename
        self.token = token

        self.g = Github(token, per_page=100, lazy=True)
        
    def _check_rate_limit(self, buffer=200):
        try:
            core = self.g.get_rate_limit().resources.core
            if core.remaining < buffer:
                reset_time = core.reset.replace(tzinfo=timezone.utc)
                # Calculate total wait duration including a 5-second safety buffer
                wait_seconds = (reset_time - datetime.now(timezone.utc)).total_seconds() + 5
                
                if wait_seconds > 0:
                    print(f"Rate limit low: ({core.remaining} requests remaining). "
                          f"Sleeping {int(wait_seconds)}s until reset.")
                    time.sleep(wait_seconds)
        except Exception as e:
            print(f"Could not check rate limit: {e}")
            
    def _in_period(self, dt):
        if self.start_date and dt.replace(tzinfo=None) < self.start_date:
            return False
        if self.end_date and dt.replace(tzinfo=None) > self.end_date:
            return False
        return True

    def get_contributors(self, repo, data):
        
        data.setdefault("contributors", [])
        
        try:
            stats = repo.get_stats_contributors()

            new_users = {}

            for contributor in stats:
                author = contributor.author  
                if author is None:
                    continue  

                had_prior_activity = any(
                    w.c > 0 and w.w.replace(tzinfo=None) < self.start_date
                    for w in contributor.weeks
                )
                if had_prior_activity:
                    continue 
                
                weeks_in_period = [
                    w for w in contributor.weeks
                    if w.c > 0 and self._in_period(w.w)
                ]
                if not weeks_in_period:
                    continue  

                new_users[author.login] = {
                    "name": author.login,
                    "company": author.company,
                    "created_at": None,  
                    "email": None,       
                }

            for login, user_data in new_users.items():
                try:
                    author_commits = repo.get_commits(
                        since=self.start_date, until=self.end_date, author=login
                    )
                    first_commit = None
                    for c in author_commits:
                        first_commit = c  

                    if first_commit is not None:
                        user_data["created_at"] = first_commit.commit.author.date.isoformat()
                        user_data["email"] = first_commit.commit.author.email
                except Exception as e:
                    print(f"Error getting first commit for {login}: {e}")

            for user_data in new_users.values():
                data["contributors"].append(user_data)

            print(f"Found {len(new_users)} new contributors")

        except Exception as e:
            print(f"Error getting contributors: {e}")

    def get_issues_and_prs(self, repo, data):
        try:
            if not self.start_date:
                return 
            
            issues_and_prs = repo.get_issues(state="all", since=self.start_date)
            
            num_issues = 0
            num_prs = 0
            
            for item in issues_and_prs:
                
                is_pr = item.pull_request is not None
                
                if not is_pr:
                    num_issues += 1
                    data["issues"].append({
                        "title": item.title,
                        "url": item.html_url,
                        "created_at": item.created_at.isoformat(),
                        "state": item.state,
                        "author": item.user.login if item.user else None,
                        "is_new": item.created_at.replace(tzinfo=None) >= self.start_date
                    })
                else:
                    num_prs += 1
                    try:
                        pr = repo.get_pull(item.number)
                        data["pulls"].append({
                            "title": pr.title,
                            "url": pr.html_url,
                            "created_at": pr.created_at.isoformat(),
                            "updated_at": pr.updated_at.isoformat(),
                            "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                            "state": pr.state,
                            "merged": pr.is_merged(),
                            "author": pr.user.login if pr.user else None,
                            "is_new": pr.created_at.replace(tzinfo=None) >= self.start_date
                        })
                    except Exception as e:
                        print(f"Error getting PR details for #{item.number}: {e}")
                    
            print(f"Found {num_issues} issues")
            print(f"Found {num_prs} pull requests")
                    
        except Exception as e:
                print(f"Error getting issues and PRs: {e}")
            
    def get_releases(self, repo, data):
        try:
            releases = repo.get_releases()
            fetched_releases = []

            for release in releases:
                published = release.published_at
                if published is None:
                    continue

                if self.start_date and published.replace(tzinfo=None) < self.start_date:
                    continue

                fetched_releases.append({
                    "name": release.name or release.tag_name,
                    "body": release.body,
                    "url": release.html_url,
                    "published_at": published.isoformat(),
                    "created_at": release.created_at.isoformat() if release.created_at else None,
                    "is_draft": release.draft,
                    "is_prerelease": release.prerelease,
                    "author": release.author.login if release.author else None,
                    "tag_name": release.tag_name
                })
            
            data["releases"] = fetched_releases
            print(f"Found {len(fetched_releases)} release(s)")
        except Exception as e:
            print(f"Error getting releases for {repo.name}: {e}")
            data["releases"] = []


    def get_data(self, org_name, archival=False):
        try:
            org = self.g.get_organization(org_name)
        except Exception as e:
            print(f"Error getting organization {org_name}: {e}")
            raise

        data = {
            "repos": [],
            "period": {
                "start": self.log_history_start,
                "end": self.log_history_end
            },
            "generated_at": self.now.isoformat(),
            "total_repo_count": 0
        }

        total_repos = 0
        for repo in org.get_repos(type="public"):
            self._check_rate_limit()
            total_repos += 1
            print(f"Processing repo: {repo.name}")

            repo_data = {
                "name": repo.name,
                "url": repo.html_url,
                "description": repo.description,
                "archived": repo.archived,
                "issues": [],
                "pulls": [],
                "commits": [],
                "releases": []
            }
            
            if repo.archived:
                print(f"Skipping archived repo: {repo.name}")
                data["repos"].append(repo_data)
                continue
            
            if not archival:
                try:
                    topics = repo.get_topics()
                    repo_data["topics"] = list(topics) if isinstance(topics, (list, tuple)) else []
                except Exception as e:
                    print(f"Error getting topics for {repo.name}: {e}")

            try:
                self.get_issues_and_prs(repo, repo_data)
            except Exception as e:
                print(f"Error fetching issues and pull_requests for {repo.name}: {str(e)}")
            
            if not archival:
                try:
                    self.get_contributors(repo, repo_data)
                    
                except Exception as e:
                    print(f"Error fetching contributors for {repo.name}: {str(e)}")


            try:
                if self.start_date:
                    for commit in repo.get_commits(since=self.start_date, until=self.end_date):
                        repo_data["commits"].append({
                            "message": commit.commit.message,
                            "url": commit.html_url,
                            "author": commit.commit.author.name,
                            "created_at": commit.commit.author.date.isoformat()
                        })
            except Exception as e:
                print(f"Error fetching commits for {repo.name}: {str(e)}")
            
            if not archival:
                try:
                    changelog_files = [
                        "CHANGELOG.md",
                        "Changelog.md",
                        "changelog.md",
                        "CHANGELOG",
                        "Changelog",
                        "changelog"
                    ]

                    repo_data["changelog_entries"] = []
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
                                            if entry_date >= self.start_date:
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

            try:
                self.get_releases(repo, repo_data)
            except Exception as e:
                print(f"Error fetching releases for {repo.name}: {str(e)}")
            
            if not archival: 
                if  (repo_data["issues"] or repo_data["pulls"] or
                    repo_data["commits"] or repo_data["changelog_entries"] or repo_data["releases"]):
                    data["repos"].append(repo_data)
            else: 
                data["repos"].append(repo_data)
                        
        data["total_repo_count"] = total_repos
        return data
              
    def save_data(self, data):
        if not self.filename:
            return None
        
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        with open(self.filename, "w") as f:
            json.dump(data, f, indent=2)
        
        return self.filename
    
    def get_and_save_data(self,org_name, archival=False):
        data = self.get_data(org_name, archival)
        return self.save_data(data)