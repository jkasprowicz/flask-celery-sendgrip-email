from flask import Flask
import requests

app = Flask(__name__)

# Configure your SendGrid API Key
app.config['SENDGRID_API_KEY'] = ''

def send_email(recipient, subject, content):
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

# Define the notification route
@app.route('/send-notification', methods=['GET'])
def send_notification():
    recipient = 'yasmimbenevides@live.com'  # Replace with the recipient's email
    subject = 'Pending Task Alert'
    content = 'One of your tasks has been pending for over a day!'
    
    # Call send_email function
    status, body, headers = send_email(recipient, subject, content)
    
    # Return a meaningful response
    if status == 202:  # SendGrid status for "Accepted"
        return f"Email sent! Status: {status}"
    else:
        return f"Failed to send email. Status: {status}, Error: {body}"

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
