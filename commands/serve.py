# serve.py
from flask import Flask, jsonify
import os
import logging
from commands.monitor import monitor

logger = logging.getLogger(__name__)


app = Flask(__name__)

@app.route('/health')
def health():
    result = monitor()
    return jsonify(
        {
        "cpu_percent": result.cpu,
        "ram_percent": result.mem.percent,
        "ram_used_gb": round(result.mem.used / (1024**3), 2),
        "disk_percent": result.disk.percent,
        "disk_free_gb": round(result.disk.free / (1024**3), 2),
        }
    )

def run(args) -> None:
    logger.info('Starting Flask server...')
    port = int(os.environ.get('APP_PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    logger.info('Flask server stopped')