# monitor.py
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import psutil

logger = logging.getLogger(__name__)


@dataclass
class MonitorResult:
    cpu: float
    mem: float
    disk: float
    top: list


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def progress_bar(percent: float, width: int = 20) -> str:
    filled = int(width * percent / 100)
    empty = width - filled
    return f"[{'#' * filled}{'-' * empty}]"


def monitor() -> MonitorResult | None:
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    procs = []

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            procs.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    top = sorted(procs, key=lambda p: p['cpu_percent'], reverse=True)[:5]

    return MonitorResult(cpu=cpu, mem=mem, disk=disk, top=top)


def display(result: MonitorResult, output=None) -> None:
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ram_used = result.mem.used / (1024 ** 3)
    ram_total = result.mem.total / (1024 ** 3)
    disk_free = result.disk.free / (1024 ** 3)

    p = lambda *args, **kwargs: print(*args, **kwargs, file=output)

    p(f'\n{"=" * 15} System Monitor {"=" * 15} {now}')
    p()
    p(f'  CPU      {result.cpu:5.1f}%  {progress_bar(result.cpu)}')
    p(f'  RAM      {result.mem.percent:5.1f}%  {progress_bar(result.mem.percent)}'
      f'  {ram_used:.1f} GB / {ram_total:.1f} GB')
    p(f'  Disk /   {result.disk.percent:5.1f}%  {progress_bar(result.disk.percent)}'
      f'  free: {disk_free:.1f} GB')
    p()
    p('  Top processes (by CPU):')
    p(f'  {"#":>3}  {"NAME":<22}  {"CPU":>6}  {"MEM":>6}')
    p(f'  {"-" * 45}')

    for i, proc in enumerate(result.top, start=1):
        name = proc['name'][:22]
        cpu = proc['cpu_percent']
        mem = proc['memory_percent']
        p(f'  {i:>3}. {name:<22}  {cpu:>5.1f}%  {mem:>5.1f}%')


def run(args) -> None:
    logger.info('Command: monitor')
    logger.debug('Args: watch=%s, log=%s', args.watch, args.log)

    logger.debug('Warming up psutil...')
    psutil.cpu_percent(interval=None)
    for proc in psutil.process_iter(['cpu_percent']):
        proc.info
    time.sleep(1)
    logger.debug('Warmup done')

    output = None
    if args.log:
        output = open(args.log, 'a', encoding='utf-8')
        size_bytes = args.log.stat().st_size
        size_mb = f'{size_bytes / (1024 ** 2):.2f}'
        size_kb = f'{size_bytes / 1024:.2f}'
        logger.info('Logging to file: %s', args.log)
        logger.info('Logging to file successful')
        if size_bytes > 1024 * 1024:
            print(f'%s size: %s MB', args.log, size_mb)
        else:
            logger.info('%s size: %s KB', args.log, size_kb)


    try:
        if args.watch:
            logger.info('Watch mode: every %d sec', args.watch)
            while True:
                result = monitor()
                clear()
                display(result, output)
                time.sleep(args.watch)
        else:
            result = monitor()
            display(result, output)

    except KeyboardInterrupt:
        print('\nMonitor stopped.')
        logger.info('Monitor stopped by user')

    finally:
        if output:
            output.close()