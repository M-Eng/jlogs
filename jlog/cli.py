"""
CLI entry point for jlog
"""

import argparse
import sys
from . import __version__
from .commands import init_command, today_command, aggregate_command, push_command


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='jlog',
        description='A markdown-based CLI journaling tool',
        epilog='Use "jlog <command> --help" for more information about a command.'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'jlog {__version__}'
    )
    
    # Create subparsers
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )
    
    # jlog init
    init_parser = subparsers.add_parser(
        'init',
        help='Interactive setup of journal folder structure and git repo'
    )
    
    # jlog today
    today_parser = subparsers.add_parser(
        'today',
        help='Create today\'s log file with a predefined markdown template'
    )
    
    # jlog aggregate
    aggregate_parser = subparsers.add_parser(
        'aggregate',
        help='Extract sections from all daily logs into category-wise markdown tables'
    )
    
    # jlog push
    push_parser = subparsers.add_parser(
        'push',
        help='Run aggregation, then git add/commit/push'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle no command provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute commands
    try:
        if args.command == 'init':
            init_command()
        elif args.command == 'today':
            today_command()
        elif args.command == 'aggregate':
            aggregate_command()
        elif args.command == 'push':
            push_command()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 