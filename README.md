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
  
