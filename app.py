from flask import Flask
from celery_app import make_celery
from tasks import check_task_status_and_notify

app = Flask(__name__)

# Flask Configurations
app.config['SECRET_KEY'] = 'your_secret_key'

# Celery Configurations
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = make_celery(app)


tasks = [
    {'id': 1, 'title': 'Review PR #42', 'status': 'pending', 'user_email': 'user1@example.com'},
    {'id': 2, 'title': 'Submit Report', 'status': 'performed', 'user_email': 'user2@example.com'},
]

@app.route('/simulate-tasks', methods=['GET'])
def simulate_tasks():
    check_task_status_and_notify.delay(tasks)
    return "Task statuses are being processed!"
