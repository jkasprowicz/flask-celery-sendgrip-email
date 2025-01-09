from celery_app import celery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

@celery.task
def send_email_task(recipient, subject, content):
    sg = SendGridAPIClient('your_sendgrid_api_key')
    message = Mail(
        from_email='your_verified_email@example.com',
        to_emails=recipient,
        subject=subject,
        plain_text_content=content
    )
    try:
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        return f"Failed to send email: {e}"

@celery.task
def check_task_status_and_notify(tasks):
    for task in tasks:
        if task['status'] == 'pending':
            send_email_task.delay(
                recipient=task['user_email'],
                subject=f"Task '{task['title']}' is still pending!",
                content=f"Your task '{task['title']}' has been pending for more than 24 hours. Please review it."
            )
        elif task['status'] == 'performed':
            send_email_task.delay(
                recipient=task['user_email'],
                subject=f"Task '{task['title']}' has been completed",
                content=f"Great job! The task '{task['title']}' has been completed successfully."
            )
