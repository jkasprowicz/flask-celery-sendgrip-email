# Flask Celery Email Automation

This project is a Flask application integrated with Celery to simulate task management and send email notifications automatically. Tasks are monitored, and emails are triggered based on their status.

## Features
- Flask application to handle routes and logic.
- Celery for asynchronous task management.
- SendGrid integration to send email notifications.
- Example use case: Notify users about pending tasks or completed tasks.

## Setup Instructions

### Prerequisites
- Python 3.8 or above
- SendGrid API Key
- Redis (for Celery backend and broker)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/<repository-name>.git
   cd <repository-name>
  
2. ```bash
   python3 -m venv venv
   source venv/bin/activate

3. ```bash
   pip install -r requirements.txt

4. ```bash
   redis-server
   celery -A app.celery worker --loglevel=info
   python app.py


Usage
Access the Flask app at http://127.0.0.1:5000/send-notification to trigger an email notification.
Define tasks in Celery and let the app monitor their statuses to send emails automatically.
