# Importing necessary libraries
import requests  # Used to make HTTP requests to the API
import json  # Used to handle JSON data
import os  # Used to manage environment variables (like API keys)

# Retrieve your Monday.com API key from environment variables
MONDAY_API_KEY = os.getenv('MONDAY_API_KEY')

# Define the URL for the Monday.com GraphQL API endpoint
MONDAY_API_URL = "https://api.monday.com/v2"

# Replace 'board_id' with your actual board ID from Monday.com
board_id = '7234762094'

# GraphQL query to retrieve specific data
query = f"""
{{
    boards(ids: {board_id}) {{
        items_page(limit: 100) {{
            items {{
                id
                name
                column_values(ids: ["name", "email__1", "long_text__1"]) {{
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
    # Parse the response JSON data
    data = response.json()
    print(json.dumps(data, indent=2))  # Pretty-print the data for debugging
else:
    # If the request failed, print the status code and the error
    print(f"Request failed with status code {response.status_code}")
    print(response.text)

# Function to process the response data and extract relevant information
def process_data(data):
    # Initialize a list to store processed items
    processed_items = []

    # Iterate over each item in the response
    for item in data['data']['boards'][0]['items_page']['items']:
        # Extract the name
        name = item['name']
        
        # Initialize email and email_content with empty strings
        email = ""
        email_content = ""
        
        # Access the first and second elements safely
        if len(item['column_values']) > 0:
            email = item['column_values'][0]['text']
        if len(item['column_values']) > 1:
            email_content = item['column_values'][1]['text']
        
        # Append the processed item to the list
        processed_items.append({
            "name": name,
            "client_email": email,
            "email_content": email_content
        })

    return processed_items

# Process the data if the request was successful
if response.status_code == 200:
    processed_items = process_data(data)
    print(json.dumps(processed_items, indent=2))  # Print the processed data for debugging
