# scan.py
import json
import logging
from collections import Counter
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ScanResult:
    tot_files: int
    tot_dirs: int
    tot_size: int
    sizes: list[tuple[str, int]]
    types: list[tuple[str, int]]

def scan(path: Path, hidden: bool, top: int) -> ScanResult | None:
    if not path.exists():
        logger.error('%s: No such directory', path)
        return None

    tot_files = 0
    tot_dirs = 0
    tot_size = 0
    sizes = []
    types = []

    logger.info('Starting scan: %s', path)
    logger.debug('Options: hidden=%s, top=%s', hidden, top)

    for i in path.rglob('*'):
        if not hidden and i.name.startswith('.'):
            continue
        elif i.is_file():
            tot_files += 1
            tot_size += i.stat().st_size
            sizes.append((i.name, i.stat().st_size))
            types.append(i.suffix)
        elif i.is_dir():
            tot_dirs += 1

    sizes = sorted(sizes, key=lambda x: x[1], reverse=True)[:top]
    types = Counter(types).most_common(5)

    logger.info('Scan finished: %d files, %d dirs, %s',
                tot_files, tot_dirs, format_size(tot_size))

    return ScanResult(
    tot_files=tot_files,
    tot_dirs=tot_dirs,
    tot_size=tot_size,
    sizes=sizes,
    types=types
    )


def format_size(size_bytes: int) -> str:
    if size_bytes >= 1024 ** 2:
        return f'{size_bytes / (1024 ** 2):.2f} MB'
    return f'{size_bytes / 1024:.2f} KB'


def log_text(result, path: Path) -> None:
    print(f'\nDirectory: {path}')
    print(f'Total files: {result.tot_files}')
    print(f'Total dirs:  {result.tot_dirs}')
    print(f'Total size:  {format_size(result.tot_size)}')

    print('\nLargest files:')
    for i, (name, size) in enumerate(result.sizes, start=1):
        print(f'  {i}. {name} — {format_size(size)}')

    print('\nFile types:')
    for ext, count in result.types:
        label = ext if ext else '(no ext)'
        print(f'  {label:12} — {count} files')


def log_json(result, path: Path) -> None:
    data = {
        'directory': str(path),
        'total_files': result.tot_files,
        'total_dirs': result.tot_dirs,
        'total_size': format_size(result.tot_size),
        'largest_files': [
            {'name': name, 'size': format_size(size)}
            for name, size in result.sizes
        ],
        'file_types': {
            (ext if ext else '(no ext)'): count
            for ext, count in result.types
        }
    }

    print(f'\n{json.dumps(data, indent=2, ensure_ascii=False)}')


def run(args) -> None:
    logger.info('Command: scan')
    logger.debug('Args: path=%s, hidden=%s, top=%s, format=%s',
                 args.path, args.hidden, args.top, args.format)

    result = scan(args.path, args.hidden, args.top)

    if result is None:
        return

    if args.format == 'text':
        log_text(result, args.path)
    else:
        log_json(result, args.path)