import os
from flask import Flask, render_template, request, redirect, url_for
from celery import Celery
from flask_mail import Mail, Message
import datetime
from decouple import config

app = Flask(__name__)

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = config('MAILTRAP_USERNAME')  # Use your Mailtrap username
app.config['MAIL_PASSWORD'] = config('MAILTRAP_PASSWORD')  # Use your Mailtrap password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# Configure Celery
app.config['CELERY_BROKER_URL'] = config('CELERY_BROKER_URL')
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# In-memory mock database for tasks
tasks = []

# Initialize Flask-Mail
mail = Mail(app)

# Celery task to send emails
@celery.task
def send_email_task(recipient, subject, content):
    try:
        msg = Message(
            subject=subject,
            sender="your-email@example.com",  # Replace with your verified sender email
            recipients=[recipient],
            html=content
        )
        mail.send(msg)
        return 202, "Email sent successfully"
    except Exception as e:
        return 500, f"Exception occurred: {e}"

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
