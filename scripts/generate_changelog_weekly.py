from github import Github # type: ignore
from datetime import datetime, timezone, timedelta
import json
import os
import re

from . import ChangelogGenerator

def main():
    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)

    timestamp = now.strftime("%Y-%m-%d")
    start_date = one_week_ago.strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")

    filename = f"changelog_data/data/weekly_changelog_{start_date}_to_{end_date}.json"

    os.makedirs("data", exist_ok=True)

    token = os.getenv("GH_TOKEN") or os.getenv("REPOLINTER_AUTO_TOKEN")
    if not token:
        raise ValueError("Github token not found in environmental variables")
    
    org_name = "DSACMS"

    gen = ChangelogGenerator(token,filename=filename,log_history_start=start_date)

    gen.get_and_save_data(org_name)

if __name__ == "__main__":
    main()