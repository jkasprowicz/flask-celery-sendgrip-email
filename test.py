from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

sg = SendGridAPIClient('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')
message = Mail(
    from_email='joao.kasprowicz@univali.br',
    to_emails='yasmimbenevides@live.com',
    subject='Test Email',
    plain_text_content='This is a test email.'
)
try:
    response = sg.send(message)
    print(f"Email sent, status code: {response.status_code}")
except Exception as e:
    print(f"Failed to send email: {e}")
