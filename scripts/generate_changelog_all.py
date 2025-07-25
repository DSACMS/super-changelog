from github import Github # type: ignore
from datetime import datetime, timezone, timedelta
import json
import os
import re
from . import ChangelogGenerator

def main():
    timestamp = datetime.now(timezone.utc).strftime("%y-%m-%d")
    filename = f"changelog_data/data/changelog{timestamp}.json"
    # since = datetime.now(timezone.utc) - timedelta(days=7)

    os.makedirs("data", exist_ok=True)

    token = os.getenv("GH_TOKEN") or os.getenv("REPOLINTER_AUTO_TOKEN")
    if not token:
        raise ValueError("Github token not found in environmental variables")
    
    org_name = "DSACMS"


    gen = ChangelogGenerator(token,filename=filename)

    gen.get_and_save_data(org_name)

if __name__ == "__main__":
    main()