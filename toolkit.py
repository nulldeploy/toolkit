# toolkit.py
import argparse, logging
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
        description='DevOps toolkit script',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose option')

    subparsers = parser.add_subparsers(dest='command', metavar='COMMAND')
    subparsers.required = True

    p = subparsers.add_parser('scan', help='Scan directory')
    p.add_argument('path', type=Path, help='Path to directory')
    p.add_argument('--hidden', action='store_true', help='Scan hidden files too')
    p.add_argument('--top', '-t', type=int, default=5, help='Top N biggest files, default=5')
    p.add_argument('--format', '-f', type=str, 
                  default='text', help='Format output (json, text), default=text')

    p = subparsers.add_parser('backup', help='Backup directory')
    p.add_argument('source', type=Path, help='Source path')
    p.add_argument('dest', type=Path, help='Destination path')
    p.add_argument('--keep', '-k', type=int, help='Keep')
    p.add_argument('--ext', '-e', choices=['gztar', 'zip', 'bztar', 'xztar', 'tar'], default='gztar', help='Extension')

    p = subparsers.add_parser('monitor', help='Monitor system')
    p.add_argument('--watch', '-w', type=int, help='Watch in seconds')
    p.add_argument('--log', '-l', type=Path, help='Log into exist file')

    p = subparsers.add_parser('deploy', help='Deploy project')
    p.add_argument('path', type=Path, help='Path to git repository')
    p.add_argument('branch', type=str, default='main', help='Branch name')
    p.add_argument('--restart', '-r', type=str, 
                    help='Service name to restart')

    p = subparsers.add_parser('serve', help='Flask start')

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

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