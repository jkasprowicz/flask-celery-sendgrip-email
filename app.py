from flask import Flask, render_template, request, redirect, url_for
from celery import Celery
from tasks import send_email_task
import datetime
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

# Flask Configurations
app.config['SECRET_KEY'] = ''

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)



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
        "from": {"email": "joaokasprowicz@hotmail.com"},  # Replace with your verified sender email
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



# Mock database for tasks
tasks = []

# Route to display tasks and add new ones
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_name = request.form['task_name']
        deadline = request.form['deadline']
        expiration_period = int(request.form['expiration_period'])
        status = 'new'

        # Corrected datetime format to handle 'T' in the datetime string
        tasks.append({
            'id': len(tasks) + 1,
            'name': task_name,
            'deadline': datetime.datetime.strptime(deadline, '%Y-%m-%dT%H:%M'),  # Adjusted format
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
