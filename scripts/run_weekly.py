import os
import sys
import subprocess
from datetime import datetime, timezone

def run_script(script_path, description):
    """Run a Python script and handle errors."""
    print(f"{description}...")
    try:
        result = subprocess.run([sys.executable, script_path],
                                capture_output=True, text=True, check=True)
        print(f"{description} completely successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{description} failed:")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"Script not found: {script_path}")
        return False
    
def check_environment():
    """Check if required environment variables are set."""
    required_vars = ["GH_TOKEN", "GITHUB_TOKEN"]
    token_found = False

    for var in required_vars:
        if os.getenv(var):
            token_found = True
            break

    if not token_found:
        print("GitHub token not found. Please set GH_TOKEN or GITHUB_TOKEN environmental variable.")
        return False
    
    return True

def main():
    """Main function to run weekly changelog workflow."""
    print("Starting weekly chngelog generation workflow")
    print(f"Started at: {datetime.now(timezone.utc).isoformat()}")
    print("-" * 60)

    if not check_environment():
        sys.exit(1)

    script_dir = "scripts"
    scripts = [
        (os.path.join(script_dir, "generate_changelog_weekly.py"),
         "Generating weekly changelog data"),
        (os.path.join(script_dir, "generate_summary.py"),
         "Generating summary and notifications"),
        (os.path.join(script_dir, "generate_summary_condensed.py"),
         "Generating condensed changelog summary"),
    ]

    all_success = True
    for script_path, description in scripts:
        if not run_script(script_path, description):
            all_success = False
            break
        print()

    if all_success:
        print("Weekly changelog generated successfully!")
        print()
        print("Genrated files:")

        data_dir = "changelog_data/data"
        summary_dir = "changelog_data/summaries"

        if os.path.exists(data_dir):
            print(f" Data files in {data_dir}/:")
            for file in sorted(os.listdir(summary_dir)):
                print(f"  - {file}")

        print()
        print("Next steps:")
        print(" 1. Review the generated summary files")
        print(" 2. Create a detailed PR: python scripts/create_pr.py")
        print(" 3. Create a condensed PR: python scripts/create_pr_condensed.py")
        print(" 4. Use the mailto link to send email notifications")

        timestamp = datetime.now(timezone.utc).strftime("%y-%m-%d")
        mailto_file = os.path.join(summary_dir, f"mailto_{timestamp}.txt")
        if os.path.exists(mailto_file):
            with open(mailto_file, 'r') as f:
                mailto_link = f.read().strip()
            print(f" Mailto link ready: {len(mailto_link)} characters")

        print()
        print("Two PR formats available:")
        print(" - Detailed: Full statistics and activity breakdown")
        print(" - Condensed: Emoji-based changelog format (Added, Fixed, Changed, etc.)")

    else:
        print("Weekly changelog generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()