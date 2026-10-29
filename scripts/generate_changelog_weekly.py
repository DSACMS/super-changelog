from github import Github, Auth
from datetime import datetime, timezone, timedelta
import json
import os
from util import ChangelogGenerator

def main():
    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)
    start_date = one_week_ago.strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")
    filename = f"changelog_data/data/weekly_changelog_{start_date}_to_{end_date}.json"
    os.makedirs("changelog_data/data", exist_ok=True)

    app_id = os.getenv("GH_APP_ID")
    private_key = os.getenv("GH_APP_PRIVATE_KEY")
    installation_id = os.getenv("GH_APP_INSTALLATION_ID")

    fallback_token = os.getenv("GH_TOKEN") or os.getenv("REPOLINTER_AUTO_TOKEN")
    if not fallback_token:
        raise ValueError("Fallback GitHub token not found in environmental variables")

    org_configs = [
        {"name": "DSACMS", "use_app": True},
        {"name": "GSA-SHARE-IT", "use_app": False},
        {"name": "CMS-Enterprise", "use_app": False},
    ]

    combined_data = {}
    for org in org_configs:
        print(f"Fetching data for {org['name']}...")
        if org["use_app"]:
            gen = ChangelogGenerator(
                token=fallback_token,
                filename=None,
                log_history_start=start_date,
                log_history_end=end_date,
                app_id=app_id,
                private_key=private_key,
                installation_id=installation_id,
            )
        else:
            gen = ChangelogGenerator(
                token=fallback_token,
                filename=None,
                log_history_start=start_date,
                log_history_end=end_date,
            )
        combined_data[org["name"]] = gen.get_data(org["name"])

    with open(filename, "w") as f:
        json.dump(combined_data, f, indent=2)
    print(f"Saved combined changelog for {len(org_configs)} orgs to {filename}")

if __name__ == "__main__":
    main()