from flask import Flask, render_template, request, redirect, url_for
from celery import Celery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import datetime
import os
from decouple import config
import requests

app = Flask(__name__)


app.config['CELERY_BROKER_URL'] = config('CELERY_BROKER_URL')
app.config['SENDGRID_API_KEY'] = ''



# Configure Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# In-memory mock database for tasks
tasks = []

# Celery task to send emails
@celery.task
def send_email_task(recipient, subject, content):
    # SendGrid API URL
    url = "https://api.sendgrid.com/v3/mail/send"
    
    # Headers for the request
    headers = {
        "Authorization": f"Bearer {app.config['SENDGRID_API_KEY']}",
        "Content-Type": "application/json",
    }
    
    # Email payload
    data = {
        "personalizations": [
            {"to": [{"email": recipient}]}
        ],
        "from": {"email": "joao.kasprowicz@univali.br"},  # Replace with your verified sender email
        "subject": subject,
        "content": [
            {"type": "text/plain", "value": content}
        ],
    }
    
    try:
        # Make the POST request to SendGrid API
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP status codes 4xx or 5xx
        return response.status_code, response.text, response.headers
    except requests.exceptions.RequestException as e:
        # Log full exception details
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

