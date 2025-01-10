from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

#@celery.task
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
