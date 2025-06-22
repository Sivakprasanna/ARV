from apscheduler.schedulers.background import BackgroundScheduler
from app.scheduler.notification import get_pending_dose_reminders
from app.scheduler.sms_sender import send_sms
import datetime

def job_send_sms_reminders():
    reminders = get_pending_dose_reminders()
    today = datetime.date.today()

    for r in reminders:
        if r['scheduled_date'] == today or r['scheduled_date'] == today + datetime.timedelta(days=1):
            message = f"Reminder: Dear {r['patient_name']}, your rabies dose #{r['dose_number']} is scheduled for {r['scheduled_date']}."
            send_sms(r['mobile'], message)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_send_sms_reminders, 'cron', hour=8, minute=18)
    scheduler.start()
