from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
job_id = 'mantis_sync_job'

def start_scheduler(job_func, interval_minutes=60):
    scheduler.add_job(job_func, 'interval', minutes=interval_minutes, id=job_id)
    scheduler.start()

def update_scheduler_interval(new_interval):
    existing_job = scheduler.get_job(job_id)
    if existing_job:
        existing_job.reschedule(trigger='interval', minutes=new_interval)
