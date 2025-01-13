import os
from flask import Flask, render_template, request, redirect, url_for
from celery import Celery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import datetime
from decouple import config

app = Flask(__name__)

app.config['CELERY_BROKER_URL'] = config('CELERY_BROKER_URL')
app.config['SENDGRID_API_KEY'] = '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'

# Configure Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# In-memory mock database for tasks
tasks = []

# Celery task to send emails
@celery.task
def send_email_task(recipient, subject, content):
    message = Mail(
        from_email="yasmimbenevides@live.com",  # Replace with your verified sender email
        to_emails=recipient,
        subject=subject,
        html_content=content
    )
    try:
        sg = SendGridAPIClient(app.config['SENDGRID_API_KEY'])
        response = sg.send(message)
        return response.status_code, response.body, response.headers
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return 500, f"Exception occurred: {e}\nDetails:\n{error_details}", None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_name = request.form['task_name']
        deadline = request.form['deadline']
        expiration_period = int(request.form['expiration_period'])
        status = 'new'
        user_email = request.form['user_email']  # Get the email from the form

        # Add the task with the email included
        tasks.append({
            'id': len(tasks) + 1,
            'name': task_name,
            'deadline': datetime.datetime.strptime(deadline, '%Y-%m-%dT%H:%M'),
            'expiration_period': expiration_period,
            'status': status,
            'user_email': user_email  # Use the dynamic email here
        })
        return redirect(url_for('index'))

    return render_template('index.html', tasks=tasks)

# Route to update task status
@app.route('/update_status/<int:task_id>/<status>', methods=['POST'])
def update_status(task_id, status):
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = status
            user_email = task['user_email']
            print(f"Task '{task['name']}' status updated to '{status}'. Sending email to {user_email}")  # Log the email

            if status == 'pending':
                send_email_task.delay(
                    user_email,
                    f"Task '{task['name']}' is pending",
                    f"<p>The task '{task['name']}' is now pending. Please complete it by {task['deadline']}.</p>"
                )
            elif status == 'completed':
                send_email_task.delay(
                    user_email,
                    f"Task '{task['name']}' is completed",
                    f"<p>The task '{task['name']}' has been completed successfully!</p>"
                )
            break
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
