from flask import Flask, render_template, request, jsonify, send_from_directory
from processors.regression_progress_updater import RegressionProgressUpdater
from loggers.logging_config import LoggerSetup
from config.config_manager import ConfigurationManager
from scheduler import start_scheduler, update_scheduler_interval, scheduler, job_id
from datetime import timezone
import threading
import os

app = Flask(__name__)

logger = LoggerSetup.setup_logger("flask", "logs/flask")
status = {
    'running': False,
    'progress': 0,
    'last_run': None,
    'last_status': 'Idle'
}

# Load your config instance
config_manager = ConfigurationManager()

# Job execution function (threaded)
def run_job():
    status['running'] = True
    status['progress'] = 0
    status['last_status'] = 'Running'

    try:
        updater = RegressionProgressUpdater()
        updater.update_progress()
        status['last_status'] = 'Completed Successfully'
    except Exception as e:
        logger.error(f"Job failed: {e}")
        status['last_status'] = f'Failed: {e}'
    finally:
        status['running'] = False
        status['progress'] = 100

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trigger', methods=['POST'])
def trigger():
    if not status['running']:
        thread = threading.Thread(target=run_job)
        thread.start()
        return jsonify({'message': 'Job triggered successfully.'})
    else:
        return jsonify({'message': 'Job is already running.'}), 409

@app.route('/status', methods=['GET'])
def job_status():
    return jsonify(status)

@app.route('/logs', methods=['GET'])
def get_logs():
    date = request.args.get('date')  # expects YYYY-MM-DD
    log_dir = 'logs'
    log_file = f"regression_progress_{date}.log"

    try:
        return send_from_directory(log_dir, log_file, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'message': 'Log file not found.'}), 404


@app.route('/config', methods=['GET'])
def config_page():
    return render_template('config.html')

@app.route('/config/data', methods=['GET'])
def config_data():
    keys_to_expose = [
        'REGRESSION_SHEET_KEY',
        'MANTIS_TICKETS_NEXUS_E6',
        'REGRESSION_FILTER_ID',
        'JOB_INTERVAL_MINUTES'  # Optional, for the scheduler interval
    ]
    
    config_data = {key: config_manager.get(key, '') for key in keys_to_expose}
    return jsonify(config_data)

@app.route('/config/update', methods=['POST'])
def config_update():
    data = request.json
    for key, value in data.items():
        config_manager.set(key, value)
    
    return jsonify({'message': 'Configuration updated successfully.'})

@app.route('/config/update_interval', methods=['POST'])
def update_interval():
    new_interval = int(request.json.get('interval'))
    
    config_manager.set('JOB_INTERVAL_MINUTES', new_interval)
    update_scheduler_interval(new_interval)
    
    return jsonify({'message': f'Scheduler interval updated to {new_interval} minutes.'})

@app.route('/schedule/status', methods=['GET'])
def schedule_status():
    job = scheduler.get_job(job_id)
    if not job:
        return jsonify({'next_run': None, 'message': 'No job found'}), 404
    
    next_run_time = job.next_run_time
    if next_run_time:
        # Convert to UTC ISO format or any readable format
        next_run_time_str = next_run_time.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    else:
        next_run_time_str = None

    return jsonify({
        'next_run': next_run_time_str
    })


if __name__ == '__main__':
    start_scheduler(run_job)  # Runs APScheduler for periodic jobs
    app.run(host='0.0.0.0', port=5001)
