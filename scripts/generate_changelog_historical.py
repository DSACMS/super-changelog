"""
Historical Changelog Data Generation Script
"""

import os
import sys
import subprocess
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from util import ChangelogGenerator # type: ignore


def parse_dates(value: str, label: str) -> str:
    """Validate an ISO date string."""
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"Invalid {label} date format: '{value}'. Expected format: YYYY-MM-DD"
        )
    return value


def main() -> None:
    """Main function to generate historical changelog data."""
    start_raw = os.getenv("START_DATE") or (sys.argv[1] if len(sys.argv) > 1 else None)
    end_raw = os.getenv("END_DATE") or (sys.argv[2] if len(sys.argv) > 2 else None)

    if not start_raw or not start_raw.strip():
        print(
            "Error: START_DATE is required. \n"
            "Provide it as an environment variable or pass it as the first input argument:\n"
            "python scripts/generate_changelog_historical.py <start_date> [end_date]"
        )
        sys.exit(1)

    try:
        start_date = parse_dates(start_raw.strip(), "START_DATE")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if end_raw and end_raw.strip():
        try:
            end_date = parse_dates(end_raw.strip(), "END_DATE")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        print(f"END_DATE not provided. Defaulting to current date: {end_date}")

    if start_date >= end_date:
        print("Error: START_DATE ({start_date}) must be earlier than END_DATE ({end_date}).")
        sys.exit(1)

    token = os.getenv("GH_TOKEN") or os.getenv("REPOLINTER_AUTO_TOKEN")
    if not token:
        print("Error: GitHub token not found. Please set GH_TOKEN or REPOLINTER_AUTO_TOKEN environment variable.")
        sys.exit(1)

    org_name = os.getenv("ORG_NAME", "DSACMS")

    output_dir = "changelog_data/data"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"historical_changelog_{start_date}_to_{end_date}.json")

    print(f"Generating historical changelog data for {org_name} from {start_date} to {end_date}...")
    print(f"Organization: {org_name}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Output file: {filename}")
    print("-" * 60)

    gen = ChangelogGenerator(token, filename=filename, log_history_start=start_date)
    saved = gen.get_and_save_data(org_name=org_name)

    if saved:
        print("-" * 60)
        print(f"Historical changelog data generated and saved to {filename}")
    else:
        print("Failed to generate historical changelog data.")
        sys.exit(1)


if __name__ == "__main__":
    main()
