"""
Command implementations for jlog CLI
"""

import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Optional

from .parser import parse_journal_entries
from .templates import get_daily_template, get_aggregated_table_template, get_readme_template


def get_config_file() -> Path:
    """Get the path to the jlog configuration file."""
    return Path.home() / ".jlog_config"


def get_journal_root() -> Optional[Path]:
    """Get the journal root directory from config."""
    config_file = get_config_file()
    if config_file.exists():
        try:
            root_path = config_file.read_text().strip()
            return Path(root_path)
        except Exception:
            pass
    return None


def save_journal_root(root_path: Path) -> None:
    """Save the journal root directory to config."""
    config_file = get_config_file()
    config_file.write_text(str(root_path))


def run_git_command(command: list, cwd: Path) -> tuple[bool, str]:
    """
    Run a git command and return success status and output.
    
    Args:
        command: List of command arguments
        cwd: Working directory
        
    Returns:
        Tuple of (success, output)
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except Exception as e:
        return False, str(e)


def init_command() -> None:
    """Initialize journal folder structure and git repo."""
    print("🚀 Initializing jlog journal...")
    
    # Get journal root folder name
    default_name = "journal"
    journal_name = input(f"📁 Journal root folder name (default: {default_name}): ").strip()
    if not journal_name:
        journal_name = default_name
    
    # Create journal root directory
    journal_root = Path.cwd() / journal_name
    if journal_root.exists():
        print(f"❌ Directory '{journal_name}' already exists!")
        return
    
    # Create directory structure
    journal_root.mkdir()
    entries_dir = journal_root / "entries"
    aggregated_dir = journal_root / "aggregated"
    entries_dir.mkdir()
    aggregated_dir.mkdir()
    
    # Create initial aggregated files
    for filename in ["accomplished.md", "blockers.md", "learned.md", "improve.md"]:
        section_title = {
            "accomplished.md": "What I accomplished",
            "blockers.md": "What didn't go well / blockers",
            "learned.md": "What I learned",
            "improve.md": "What to improve"
        }[filename]
        
        content = get_aggregated_table_template(section_title, [])
        (aggregated_dir / filename).write_text(content)
    
    print(f"✅ Created journal structure in '{journal_name}/'")
    
    # Save journal root to config
    save_journal_root(journal_root)
    
    # Git initialization
    git_init = input("🗃️ Initialize Git repository? (y/n): ").strip().lower()
    if git_init in ('y', 'yes'):
        success, output = run_git_command(['git', 'init'], journal_root)
        if success:
            print("✅ Git repository initialized")
            
            # Add remote
            remote_url = input("🌍 Remote URL (optional): ").strip()
            if remote_url:
                success, output = run_git_command(['git', 'remote', 'add', 'origin', remote_url], journal_root)
                if success:
                    print(f"✅ Remote 'origin' added: {remote_url}")
                else:
                    print(f"❌ Failed to add remote: {output}")
        else:
            print(f"❌ Failed to initialize Git: {output}")
    
    print(f"🎉 Journal initialized! You can now use 'jlog today' to create your first entry.")


def today_command() -> None:
    """Create today's log file with predefined template."""
    journal_root = get_journal_root()
    if not journal_root:
        print("❌ No journal found. Run 'jlog init' first.")
        return
    
    if not journal_root.exists():
        print(f"❌ Journal directory '{journal_root}' does not exist. Run 'jlog init' first.")
        return
    
    # Get today's date
    today_date = date.today().strftime("%Y-%m-%d")
    entries_dir = journal_root / "entries"
    today_file = entries_dir / f"{today_date}.md"
    
    # Check if file already exists
    if today_file.exists():
        print(f"📝 Today's entry already exists: {today_file}")
        return
    
    # Create today's entry
    template = get_daily_template(today_date)
    today_file.write_text(template)
    
    print(f"✅ Created today's entry: {today_file}")


def aggregate_command() -> None:
    """Extract sections from all daily logs into category-wise markdown tables."""
    journal_root = get_journal_root()
    if not journal_root:
        print("❌ No journal found. Run 'jlog init' first.")
        return
    
    if not journal_root.exists():
        print(f"❌ Journal directory '{journal_root}' does not exist. Run 'jlog init' first.")
        return
    
    entries_dir = journal_root / "entries"
    aggregated_dir = journal_root / "aggregated"
    
    if not entries_dir.exists():
        print(f"❌ Entries directory '{entries_dir}' does not exist.")
        return
    
    print("📊 Aggregating journal entries...")
    
    # Parse all entries
    aggregated_data = parse_journal_entries(entries_dir)
    
    # Write aggregated files
    file_mappings = {
        "accomplished": ("accomplished.md", "What I accomplished"),
        "blockers": ("blockers.md", "What didn't go well / blockers"),
        "learned": ("learned.md", "What I learned"),
        "improve": ("improve.md", "What to improve")
    }
    
    for section_key, (filename, title) in file_mappings.items():
        entries = aggregated_data[section_key]
        content = get_aggregated_table_template(title, entries)
        
        output_file = aggregated_dir / filename
        output_file.write_text(content)
        
        print(f"✅ Updated {filename} with {len(entries)} entries")
    
    # Create/update main README.md at journal root
    readme_content = get_readme_template(aggregated_data)
    readme_file = journal_root / "README.md"
    readme_file.write_text(readme_content)
    
    total_entries = sum(len(entries) for entries in aggregated_data.values())
    print(f"✅ Updated README.md with {total_entries} total entries")
    
    print("🎉 Aggregation complete!")


def push_command() -> None:
    """Run aggregation, then git add/commit/push."""
    journal_root = get_journal_root()
    if not journal_root:
        print("❌ No journal found. Run 'jlog init' first.")
        return
    
    if not journal_root.exists():
        print(f"❌ Journal directory '{journal_root}' does not exist. Run 'jlog init' first.")
        return
    
    # Check if it's a git repository
    if not (journal_root / ".git").exists():
        print("❌ Not a Git repository. Initialize Git first during 'jlog init'.")
        return
    
    # Run aggregation first
    print("📊 Running aggregation...")
    aggregate_command()
    
    # Get today's date for commit message
    today_date = date.today().strftime("%Y-%m-%d")
    
    # Git add
    print("📝 Adding files to Git...")
    success, output = run_git_command(['git', 'add', '.'], journal_root)
    if not success:
        print(f"❌ Failed to add files: {output}")
        return
    
    # Git commit
    commit_message = f"Update journal logs on {today_date}"
    print(f"💾 Committing changes: {commit_message}")
    success, output = run_git_command(['git', 'commit', '-m', commit_message], journal_root)
    if not success:
        if "nothing to commit" in output:
            print("✅ Nothing to commit, working tree clean")
        else:
            print(f"❌ Failed to commit: {output}")
            return
    
    # Git push
    print("🚀 Pushing to remote...")
    success, output = run_git_command(['git', 'push'], journal_root)
    if success:
        print("✅ Successfully pushed to remote!")
        if output.strip():
            print(output)
    else:
        # Check if the error is about missing upstream branch
        if "has no upstream branch" in output or "set-upstream" in output:
            print("⚠️  No upstream branch set. Setting up upstream...")
            
            # Get current branch name
            branch_success, branch_output = run_git_command(['git', 'branch', '--show-current'], journal_root)
            if branch_success:
                current_branch = branch_output.strip()
            else:
                current_branch = "main"  # fallback
            
            # Try to push with upstream
            success, output = run_git_command(['git', 'push', '-u', 'origin', current_branch], journal_root)
            if success:
                print("✅ Successfully pushed with upstream!")
                if output.strip():
                    print(output)
            else:
                print(f"❌ Failed to push with upstream: {output}")
        else:
            print(f"❌ Failed to push: {output}")
            # Try to push with upstream as fallback
            branch_success, branch_output = run_git_command(['git', 'branch', '--show-current'], journal_root)
            if branch_success:
                current_branch = branch_output.strip()
            else:
                current_branch = "main"  # fallback
                
            success, output = run_git_command(['git', 'push', '-u', 'origin', current_branch], journal_root)
            if success:
                print("✅ Successfully pushed with upstream!")
                if output.strip():
                    print(output)
            else:
                print(f"❌ Failed to push with upstream: {output}") 