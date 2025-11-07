import os
import json
import subprocess
from datetime import datetime, timezone
from github import Github  # type: ignore

def get_latest_summary_files():
    """Get the paths to the latest summary files."""
    summaries_dir = "changelog_data/summaries"
    if not os.path.exists(summaries_dir):
        raise FileNotFoundError("summaries directory not found")
    
    pr_title_files = [f for f in os.listdir(summaries_dir) if f.startswith("pr_title_")]
    pr_body_files = [f for f in os.listdir(summaries_dir) if f.startswith("pr_body_")]

    if not pr_title_files or not pr_body_files:
        raise FileNotFoundError("PR title or body files not found")
    
    latest_title_file = os.path.join(summaries_dir, sorted(pr_title_files)[-1])
    latest_body_file = os.path.join(summaries_dir, sorted(pr_body_files)[-1])

    return latest_title_file, latest_body_file

def create_branch_and_commit():
    """Create branch and commit the changelog."""
    branch_name = f"weekly-changelog-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"

    try:
        subprocess.run(["git", "config", "--local", "user.email", "action@github.com"], check=True)
        subprocess.run(["git", "config", "--local", "user.name", "GitHub Action"], check=True)

        subprocess.run(["git", "checkout", "-b", branch_name], check=True)

        subprocess.run(["git", "add", "changelog_data/"], check=True)

        commit_message = f"Add weekly changelog summary for {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
        subprocess.run(["git", "commit", "-sm", commit_message], check=True)
        
        subprocess.run(["git", "push", "origin", branch_name], check=True)

        return branch_name
    
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        raise

def create_pull_request_with_api(title, body, branch_name):
    """Create a pull request usin the GitHub API."""
    token = os.getenv("GH_TOKEN") or os.getenv("REPOLINTER_AUTO_TOKEN")
    if not token:
        raise ValueError("GitHub token not found in environmental variables")
    
    g = Github(token)

    repo_name = os.getenv("GITHUB_REPOSITORY")
    if not repo_name:
        raise ValueError("GITHUB_REPOSITORY environment variable not set")
    
    repo = g.get_repo(repo_name)

    try:
        pr = repo.create_pull(
            title=title,
            body=body,
            head=branch_name,
            base="main"
        )

        try:
            pr.add_to_labels("changelog", "automated")
        except Exception as e:
            print(f"Could not add labels: {e}")

        print(f"Pull request created: {pr.html_url}")
        return pr
    
    except Exception as e:
        print(f"Failed to create pull request: {e}")
        raise

def create_pull_request_with_cli(title, body, branch_name):
    """Create a pull request usin the GitHub CLI."""
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(body)
            body_file = f.name

        try:
            cmd = [
                "gh", "pr", "create",
                "--title", title,
                "--body-file", body_file,
                "--base", "main",
                "--head", branch_name,
                "--label", "changelog",
                "--label", "automated"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            pr_url = result.stdout.strip()
            print(f"Pull request created: {pr_url}")
            return pr_url
        
        finally:
            os.unlink(body_file)

    except subprocess.CalledProcessError as e:
        print(f"GitHub CLI failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise
    except FileNotFoundError:
        print("GitHub CLI (gh) not found. Falling back to API method.")
        return None
    
def main():
    """Main function to create pull request."""
    try:
        print("Creating weekly changelog summary PR...")

        title_file, body_file = get_latest_summary_files()

        with open(title_file, 'r') as f:
            title = f.read().strip()

        with open(body_file, 'r') as f:
            body = f.read().strip()

        print(f"PR Title: {title}")

        branch_name = create_branch_and_commit()
        print(f"Created branch: {branch_name}")

        pr_url = None
        try:
            pr_url = create_pull_request_with_cli(title, body, branch_name)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Falling back to API...")
            pr = create_pull_request_with_api(title, body, branch_name)
            pr_url = pr.html_url

        if pr_url:
            print(f"Successfully created pull request: {pr_url}")

            output_dir = "changelog_data/summaries"
            timestamp = datetime.now(timezone.utc).strftime("%y-%m-%d")
            pr_url_file = os.path.join(output_dir, f"pr_url_{timestamp}.txt")
            with open(pr_url_file, 'w') as f:
                f.write(pr_url)

        return pr_url
    
    except Exception as e:
        print(f"Failed to create pull request: {e}")
        raise

if __name__ == "__main__":
    main()
