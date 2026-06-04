# deploy.py
import subprocess, logging
from pathlib import Path


logger = logging.getLogger(__name__)



def deploy(path: Path, branch: str, restart: str) -> True:
    if not path.exists():
        logger.error('%s: Not found file or directory', path)
        return None
    
    git_dir = path / '.git'

    if not git_dir.exists():
        logger.error('%s: Not found git directory', path)
        return None

    try:
        logger.info("[1/3] Pulling branch '%s'", branch)
        git_pull = subprocess.run(
            ['git', 'pull', 'origin', branch],
            capture_output=True,
            text=True,
            timeout=10,
            check=True
        )
        print(git_pull.stdout.strip())
    except subprocess.CalledProcessError as e:
        logger.error('git pull failed: %s', e.stderr)
        return None
    except subprocess.TimeoutExpired:
        logger.error('git pull timed out')
        return None

    if restart:
        try:
            logger.info("[2/3] Restarting service '%s'...", restart)
            command_restart = subprocess.run(
                ['systemctl', 'restart', restart],
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )
            logger.info('   %s restarted successfully', restart)
        except subprocess.CalledProcessError as e:
            logger.error('restarting %s failed: %s', restart, e.stderr)
            return None
        except subprocess.TimeoutExpired:
            logger.error('restarting %s timed out', restart)
            return None
    
    logger.info('[3/3] Deploy finished.')
    return True

def run(args) -> None:
    result = deploy(args.path, args.branch, args.restart)

    if result is None:
        return