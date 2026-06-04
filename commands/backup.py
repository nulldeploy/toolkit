# backup.py
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

ARCHIVE_FORMATS = ['gztar', 'zip', 'bztar', 'xztar', 'tar']


@dataclass
class BackupResult:
    archive_name: str
    size: int


def backup(source: Path, dest: Path, ext: str) -> BackupResult | None:
    if not source.exists():
        logger.error('%s: No such file or directory', source)
        return None

    if not dest.exists():
        logger.error('%s: No such file or directory', dest)
        return None

    archive_name = f'{source.name}_{datetime.now().strftime("%Y-%m-%d__%H:%M:%S")}'
    base_name = str(dest / archive_name)

    logger.info('Starting backup: %s → %s', source, dest)
    logger.debug('Archive format: %s', ext)

    archive = shutil.make_archive(
        base_name=base_name,
        format=ext,
        root_dir=source
    )

    archive = Path(archive)
    size = archive.stat().st_size

    logger.info('Archive created: %s (%s)', archive.name, format_size(size))

    return BackupResult(archive_name=archive_name, size=size)


def cleanup(dest: Path, keep: int) -> int:
    if keep is None:
        return 0

    extensions = ['*.tar.gz', '*.zip', '*.tar.bz2', '*.tar.xz', '*.tar']
    files = []

    for ext in extensions:
        files.extend(dest.glob(ext))

    files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
    to_delete = files[keep:]

    for f in to_delete:
        logger.debug('Removing old archive: %s', f.name)
        f.unlink()

    logger.info('Cleanup: removed %d archives, kept last %d', len(to_delete), keep)

    return len(to_delete)


def format_size(size_bytes: int) -> str:
    if size_bytes >= 1024 ** 2:
        return f'{size_bytes / (1024 ** 2):.2f} MB'
    return f'{size_bytes / 1024:.2f} KB'


def log(result: BackupResult, source: Path, dest: Path,
        keep: int, removed: int) -> None:
    print(f'\nBacking up:  {source}')
    print(f'Destination: {dest}')
    print(f'Archive:     {result.archive_name}')
    print(f'Size:        {format_size(result.size)}')
    print('Done!')

    if keep is not None:
        print(f'\nCleanup: removed {removed} old archives (kept last {keep})')


def run(args) -> None:
    logger.info('Command: backup')
    logger.debug('Args: source=%s, dest=%s, ext=%s, keep=%s',
                 args.source, args.dest, args.ext, args.keep)

    result = backup(args.source, args.dest, args.ext)

    if result is None:
        return

    removed = cleanup(args.dest, args.keep)
    log(result, args.source, args.dest, args.keep, removed)