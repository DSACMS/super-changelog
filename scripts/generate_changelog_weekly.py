from github import Github # type: ignore
from datetime import datetime, timezone, timedelta
import json
import os
import re

from util import ChangelogGenerator

def main():
    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)

    start_date = one_week_ago.strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")

    filename = f"changelog_data/data/weekly_changelog_{start_date}_to_{end_date}.json"

    os.makedirs("changelog_data/data", exist_ok=True)

    token = os.getenv("GH_TOKEN") or os.getenv("REPOLINTER_AUTO_TOKEN")
    if not token:
        raise ValueError("Github token not found in environmental variables")
    
    org_names = ["DSACMS", "CMS-Enterprise"]

    gen = ChangelogGenerator(token, filename=filename,log_history_start=start_date)

    combined_data = {}
    for org_name in org_names:
        print(f"Fetching data for {org_name}...")
        combined_data[org_name] = gen.get_data(org_name)

    with open(filename, "w") as f:
        json.dump(combined_data, f, indent=2)

    print(f"Saved combined changelog for {len(org_names)} orgs to {filename}")

if __name__ == "__main__":
    main()