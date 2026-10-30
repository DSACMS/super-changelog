from github import Github, Auth
from datetime import datetime, timezone, timedelta
import json
import os
from util import ChangelogGenerator

ORG_CONFIGS = [
    {"name": "DSACMS", "use_app": True},
    {"name": "GSA-SHARE-IT", "use_app": False},
    {"name": "CMS-Enterprise", "use_app": False},
]


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

    fallback_pat = os.getenv("GH_FALLBACK_PAT")
    if not fallback_pat:
        raise ValueError(
            "GH_FALLBACK_PAT not found in environment. This is required for "
            "orgs without the GitHub App installed (see ORG_CONFIGS)."
        )

    print(f"App ID present: {bool(app_id)}")
    print(f"Private key present: {bool(private_key)}")
    print(f"Installation ID present: {bool(installation_id)} (value: {installation_id})")
    print(f"Fallback PAT present: {bool(fallback_pat)}")

    combined_data = {}
    for org in ORG_CONFIGS:
        org_name = org["name"]
        print(f"Fetching data for {org_name}...")

        if org["use_app"]:
            if not (app_id and private_key and installation_id):
                raise ValueError(
                    f"Org '{org_name}' is configured to use the GitHub App, "
                    f"but App credentials are missing from the environment."
                )
            gen = ChangelogGenerator(
                filename=None,
                log_history_start=start_date,
                log_history_end=end_date,
                app_id=app_id,
                private_key=private_key,
                installation_id=installation_id,
            )
        else:
            gen = ChangelogGenerator(
                token=fallback_pat,
                filename=None,
                log_history_start=start_date,
                log_history_end=end_date,
            )

        combined_data[org_name] = gen.get_data(org_name)

    with open(filename, "w") as f:
        json.dump(combined_data, f, indent=2)
    print(f"Saved combined changelog for {len(ORG_CONFIGS)} orgs to {filename}")


if __name__ == "__main__":
    main()