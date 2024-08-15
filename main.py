import os
import ssl
import certifi
import requests
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Use certifi to set the SSL certificate file
os.environ['SSL_CERT_FILE'] = certifi.where()

# Retrieve your Monday.com API key and SendGrid API key from environment variables
MONDAY_API_KEY = os.getenv('MONDAY_API_KEY')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# Define the URL for the Monday.com GraphQL API endpoint
MONDAY_API_URL = "https://api.monday.com/v2"

# Your actual board ID from Monday.com
board_id = os.getenv('MONDAY_BOARD_ID')  # Change this to your actual board ID if different

# GraphQL query to retrieve specific data from the Monday.com board
query = f"""
{{
    boards(ids: {board_id}) {{
        items_page {{
            items {{
                name
                column_values {{
                    id
                    text
                }}
            }}
        }}
    }}
}}
"""

# Define the headers for the API request, including your API key
headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

# Make the request to the Monday.com API
response = requests.post(MONDAY_API_URL, headers=headers, json={'query': query})

# Check if the request was successful (status code 200)
if response.status_code == 200:
    data = response.json()
else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)

def process_data(data):
    processed_items = []
    for item in data['data']['boards'][0]['items_page']['items']:
        name = item['name']
        email = ""
        email_content = ""
        for column in item['column_values']:
            if column['id'] == 'email__1':
                email = column['text']
            elif column['id'] == 'long_text__1':
                email_content = column['text']
        if email:
            processed_items.append({
                "name": name,
                "client_email": email,
                "email_content": email_content
            })
    return processed_items

processed_items = process_data(data)

def send_email(to_email, subject, content):
    message = Mail(
        from_email='apitesting91@gmail.com',
        to_emails=[to_email, 'apitesting91@gmail.com'],  # Send to the client and also to yourself for testing. can change emails after
        subject=subject,
        html_content=content
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent to {to_email}: {response.status_code}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")

for item in processed_items:
    send_email(
        to_email=item['client_email'],
        subject=f"Update from {item['name']}",
        content=item['email_content']
    )
