from flask import Flask, render_template, request, redirect, url_for
from celery import Celery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import datetime
import os


app = Flask(__name__)

# Flask Configurations
app.config['SECRET_KEY'] = ''  # Use this for Flask session management
app.config['SENDGRID_API_KEY'] = os.getenv('SENDGRID_API_KEY')  # Fetch from environment variables
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'

# Configure Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# In-memory mock database for tasks
tasks = []

# Celery task to send emails
@celery.task
def send_email_task(recipient, subject, content):

    sg = SendGridAPIClient(app.config['SENDGRID_API_KEY'])
    message = Mail(
        from_email='joaokasprowicz@hotmail.com',  # Replace with your verified SendGrid sender email
        to_emails=recipient,
        subject=subject,
        plain_text_content=content
    )
    try:
        response = sg.send(message)
        print(f"Email sent, status code: {response.status_code}")  # Add logging
        return response.status_code
    except Exception as e:
        print(f"Failed to send email: {e}")  # Add logging
        return f"Failed to send email: {e}"

# Route to display tasks and add new ones
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_name = request.form['task_name']
        deadline = request.form['deadline']
        expiration_period = int(request.form['expiration_period'])
        status = 'new'

        # Correct datetime format to handle 'T' in the datetime string
        tasks.append({
            'id': len(tasks) + 1,
            'name': task_name,
            'deadline': datetime.datetime.strptime(deadline, '%Y-%m-%dT%H:%M'),
            'expiration_period': expiration_period,
            'status': status,
            'user_email': 'yasmimbenevides@live.com'  # Replace with user email input or default
        })
        return redirect(url_for('index'))

    return render_template('index.html', tasks=tasks)

# Route to update task status
@app.route('/update_status/<int:task_id>/<status>', methods=['POST'])
def update_status(task_id, status):
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = status
            if status == 'pending':
                send_email_task.delay(
                    task['user_email'],
                    f"Task '{task['name']}' is pending",
                    f"The task '{task['name']}' is now pending. Please complete it by {task['deadline']}."
                )
            elif status == 'completed':
                send_email_task.delay(
                    task['user_email'],
                    f"Task '{task['name']}' is completed",
                    f"The task '{task['name']}' has been completed successfully!"
                )
            break
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
