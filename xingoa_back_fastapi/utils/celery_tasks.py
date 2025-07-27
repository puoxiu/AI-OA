# AI-OA/xingoa_back_fastapi/utils/celery_tasks.py
from .mailer import send_email
from .celery_app import celery_app

@celery_app.task(name='send_email_task')
def send_email_task(subject: str, recipient_list: list[str], message: str):
    send_email(subject, recipient_list, message)