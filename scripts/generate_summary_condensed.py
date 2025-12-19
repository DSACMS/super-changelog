import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Any


EMOJI_MAP = {
        'added': {
                'emoji': '✅',
                'patterns': [r'[Aa]dd(?:ed|s|ing)?', r'[Nn]ew'],
                'keywords': ['add', 'added', 'adds', 'adding', 'new']
        },
        'fixed': {
                'emoji': '🪲',
                'patterns': [r'[Ff]ix(?:ed|es|ing)?', r'[Bb]ug'],
                'keywords': ['fix', 'fixed', 'fixes', 'fixing', 'bug', 'bugfix']
        },
        'changed': {
                'emoji': '🔧',
                'patterns': [
                    r'[Cc]hang(?:ed|e|es|ing)?', 
                    r'[Mm]odif(?:y|ied|ies|ying)?', 
                    r'[Uu]pdat(?:ed|e|es|ing)?',
                    r'[Ii]prov(?:ed|e|es|ing|evement)?'
                ],
                'keywords': [
                    'change',
                    'changed',
                    'changes',
                    'changing',
                    'modify',
                    'modified',
                    'modifies',
                    'modifying',
                    'update',
                    'updated',
                    'updates',
                    'updating',
                    'improve',
                    'improved',
                    'improvement'
                ]
        },
        'deprecated': {
                'emoji': '⚠️',
                'patterns': [r'[Dd]eprecat(?:ed|e|es|ing)?'],
                'keywords': ['deprecate', 'deprecated', 'deprecates', 'deprecating']
        },
        'removed': {
                'emoji': '🗑️',
                'patterns': [r'[Rr]emov(?:ed|e|es|ing)?', r'[Dd]elet(?:ed|e|es|ing)?'],
                'keywords': ['remove', 'removed', 'removes', 'removing', 'delete', 'deleted', 'deletes', 'deleting']
        },
        'security': {
                'emoji': '🔒',
                'patterns': [r'[Ss]ecur(?:ity|ed|e|ing)?',],
                'keywords': ['security', 'secure', 'secured', 'securing']
        },
        'performance': {
                'emoji': '⚡️',
                'patterns': [r'[Pp]erforman(?:ce|t)?', r'[Oo]ptimi(?:ze|zed|zes|zing|zation)?'],
                'keywords': ['performance', 'performant', 'optimize', 'optimized', 'optimizes', 'optimizing', 'optimization']
        },
        'documentation': {
                'emoji': '📚',
                'patterns': [r'[Dd]ocument(?:ation)?', r'[Dd]ocs?'],
                'keywords': ['documentation', 'document', 'docs', 'doc']
        },
}


def get_emoji_for_category(category: str) -> tuple:
    """Gets the emoji for category"""
    category_lower = category.lower()

    for category_key, config in EMOJI_MAP.items():
        for pattern in config['patterns']:
            if re.search(pattern, category, re.IGNORECASE):
                return (config['emoji'], category_key)
            
        for keyword in config['keywords']:
            if keyword in category_lower:
                return (config['emoji'], category_key)
            
    return ('❓', 'other')


def categorize_changes(data: Dict[str, Any]) -> Dict[str, List[Dict]]:
    """Categorize all of the changes in the data."""
    categorized = {
        'added': [],
        'fixed': [],
        'changed': [],
        'deprecated': [],
        'removed': [],
        'security': [],
        'performance': [],
        'documentation': [],
        'other': []
    }

    for repo_data in data.get("repos", []):
        repo_name = repo_data.get("name", "Unknown")

        for entry in repo_data.get("changelog_entries", []):
            for change in entry.get("change", []):
                category = change.get("category", "")
                items = change.get("items", [])

                emoji, bucket = get_emoji_for_category(category)

                for item in items:
                    categorized[bucket].append({
                        'repo': repo_name,
                        'text': item,
                        'category': category,
                        'emoji': emoji
                    })

        merged_prs = [pr for pr in repo_data.get("pulls", []) if pr.get("merged")]
        if merged_prs:
            for pr in merged_prs[:3]:
                title = pr.get("title", "")
                emoji, bucket = get_emoji_for_category(title)

                categorized[bucket].append({
                    'repo': repo_name,
                    'text': title,
                    'url': pr.get("url", ""),
                    'type': 'pr',
                    'emoji': emoji
                })

        print(categorized)
        return categorized
    

def generate_condensed_summary(data_file: str) -> Dict[str, Any]:
    """Generate a styled, condensed summary."""
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading data file {data_file}: {e}")
        raise
    
    if "repos" not in data:
        raise ValueError("Invalid data structure: missing 'repos' key")
    
    summary = {
        "period": data.get("period", {}),
        "generated_at": data.get("generated_at"),
        "total_repos": data.get("total_repo_count", len(data["repos"])),
        "active_repos": sum(1 for r in data["repos"] if
                            r.get("issues") or r.get("pulls") or
                            r.get("commits") or r.get("changelog_entries")),
        "total_commits": sum(len(r.get("commits", [])) for r in data["repos"]),
        "total_pulls": sum(len(r.get("pulls", [])) for r in data["repos"]),
        "total_issues": sum(len(r.get("issues", [])) for r in data["repos"]),
        "total_changelog_entries": sum(len(r.get("changelog_entries", [])) for r in data["repos"]),
    }

    summary["categorized_changes"] = categorize_changes(data)

    summary["change_counts"] = {
        category: len(changes)
        for category, changes in summary["categorized_changes"].items()
        if changes
    }

    summary["active_repos_list"] = [
        {
            "name": r.get("name"),
            "url": r.get("url"),
            "commits": len(r.get("commits", [])),
            "pulls": len(r.get("pulls", [])),
            "issues": len(r.get("issues", []))
        }
        for r in data["repos"]
        if r.get("issues") or r.get("pulls") or r.get("commits") or r.get("changelog_entries")
    ]

    return summary


def create_condensed_pr_content(summary: Dict[str, Any]) -> tuple:
    """Create condensed PR title and body with emojis."""
    period = summary.get("period", {})
    start_date = period.get("start", "")
    end_date = period.get("end", "")

    title = f"📋 Changelog Summary: {start_date} to {end_date}"

    body_sections = [
        f"# 📋 Weekly Changelog",
        f"**Period**: {start_date} to {end_date}"
        "",
        "## 📊 Quick Stats",
        f"- **Active Repositories**: {summary.get('active_repos', 0)}/{summary.get('total_repos', 0)}",
        f"- **Commits**: {summary.get('total_commits', 0)} : **Pull Requests**: {summary.get('total_pulls', 0)} | **Issues**: {summary.get('total_issues', 0)}",
        ""
    ]

    categorized = summary.get("categorized_changes", {})
    change_counts = summary.get("change_counts", {})

    category_order = [
        ('added', '✅ Added', 'New features and additions'),
        ('fixed','🪲 Fixed', 'Bug fixes and corrections'),
        ('changed', '🔧 Changed', 'Updates and modifications'),  
        ('deprecated', '⚠️ Deprecated', 'Deprecation notices'),
        ('removed', '🗑️ Removed', 'Deprecations and removals'),
        ('security', '🔒 Security', 'Security improvements'),
        ('performance', '⚡️ Performance', 'Performance optimizations'),
        ('documentation', '📚 Documentation', 'Ducumentation updates'),
    ]

    has_changes = False
    for category_key, category_title, category_desc in category_order:
        changes = categorized.get(category_key, [])
        if not changes:
            continue

        has_changes = True
        body_sections.extend([
            f"## {category_title}",
            f"*{category_desc}*",
            ""
        ])

        changes_by_repo = {}
        for change in changes:
            repo = change['repo']
            if repo not in changes_by_repo:
                changes_by_repo[repo] = []
            changes_by_repo[repo].append(change)

        for repo_name in sorted(changes_by_repo.keys()):
            repo_changes = changes_by_repo[repo_name]
            body_sections.append(f"### {repo_name}")

            for change in repo_changes[:5]:
                if change.get('type') == 'pr' and change.get('url'):
                    body_sections.append(f"- [{change['text']}]({change['url']})")
                else:
                    body_sections.append(f"- {change['text']}")

            if len(repo_changes) > 5:
                body_sections.append(f"- *...and {len(repo_changes) - 5} more*")

            body_sections.append("")

    if not has_changes:
        body_sections.extend([
            "## 📝 Changes",
            "*No categorized changes found in changelogs this week*",
            ""
        ])

    body_sections.extend([
        "## 🚀 Active Repositories",
        ""
    ])

    active_repos = summary.get("active_repos_list", [])
    sorted_repos = sorted(active_repos,
                          key=lambda x: x['commits'] + x['pulls'],
                          reverse=True)
    
    for repo in sorted_repos[:10]:
        activity_parts =[]
        if repo['commits']:
            activity_parts.append(f"{repo['commits']} commits")
        if repo['pulls']:
            activity_parts.append(f"{repo['pulls']} pulls")
        if repo['issues']:
            activity_parts.append(f"{repo['issues']} issues")

        activity_str = ", ".join(activity_parts)
        body_sections.append(f"- **[{repo['name']}]({repo['url']})**: {activity_str}")

    if len(sorted_repos) > 10:
        body_sections.append(f"- *...and {len(sorted_repos) - 10} more repositories*")

    body_sections.extend([
        "",
        "---",
        f"*🤖 Generated automatically on {summary.get('generated_at', 'Unknown')}*"
    ])

    return title, '\n'.join(body_sections)


def main():
    """Main function."""
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

        print(f"Generating condensed summary from {latest_file}")

        summary = generate_condensed_summary(data_file)

        print(f"Summary stats: {summary.get('active_repos', 0)} active repos")
        print(f"Change counts: {summary.get('change_counts', {})}")

        output_dir = "changelog_data/summaries"
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%y-%m-%d")

        summary_file = os.path.join(output_dir, f"summary_condensed_{timestamp}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        pr_title, pr_body = create_condensed_pr_content(summary)
        pr_title_file = os.path.join(output_dir, f"pr_title_condensed_{timestamp}.txt")
        pr_body_file = os.path.join(output_dir, f"pr_body_condensed_{timestamp}.md")

        with open(pr_title_file, 'w') as f:
            f.write(pr_title)

        with open(pr_body_file, 'w') as f:
            f.write(pr_body)

        print(f"Condensed summary generated successfully!")
        print(f"Files saved to {output_dir}/")
        print(f"PR content: {pr_title_file}, {pr_body_file}")

        return summary_file
    
    except Exception as e:
        print(f"Error generating condensed summary: {e}")
        raise
    
if __name__ == "__main__":
    main()