# toolkit.py
import argparse
import logging
from pathlib import Path


def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    handlers = [logging.StreamHandler()]
    logging.basicConfig(
        level=level,
        format='%(asctime)s  %(levelname)-8s  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='DevOps toolkit — a CLI tool for system administration',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    subparsers = parser.add_subparsers(dest='command', metavar='COMMAND')
    subparsers.required = True

    p = subparsers.add_parser('scan', help='Scan a directory and show statistics')
    p.add_argument('path', type=Path, help='Path to the directory')
    p.add_argument('--hidden', action='store_true', help='Include hidden files')
    p.add_argument('--top', '-t', type=int, default=5, help='Show top N largest files (default: 5)')
    p.add_argument('--format', '-f', type=str,
                   default='text', help='Output format: text or json (default: text)')

    p = subparsers.add_parser('backup', help='Create a compressed archive of a directory')
    p.add_argument('source', type=Path, help='Source directory path')
    p.add_argument('dest', type=Path, help='Destination directory path')
    p.add_argument('--keep', '-k', type=int, help='Number of recent backups to keep')
    p.add_argument('--ext', '-e', choices=['gztar', 'zip', 'bztar', 'xztar', 'tar'],
                   default='gztar', help='Archive format (default: gztar)')

    p = subparsers.add_parser('monitor', help='Monitor system resources in real time')
    p.add_argument('--watch', '-w', type=int, help='Refresh interval in seconds')
    p.add_argument('--log', '-l', type=Path, help='Path to a log file to write output')

    p = subparsers.add_parser('deploy', help='Pull latest changes and restart a service')
    p.add_argument('path', type=Path, help='Path to the git repository')
    p.add_argument('branch', type=str, default='main', help='Branch to deploy (default: main)')
    p.add_argument('--restart', '-r', type=str, help='systemd service name to restart after deploy')

    p = subparsers.add_parser('serve', help='Start the Flask HTTP server')

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.command == 'scan':
        from commands.scan import run
        run(args)
    elif args.command == 'backup':
        from commands.backup import run
        run(args)
    elif args.command == 'monitor':
        from commands.monitor import run
        run(args)
    elif args.command == 'deploy':
        from commands.deploy import run
        run(args)
    elif args.command == 'serve':
        from commands.serve import run
        run(args)


if __name__ == '__main__':
    main()