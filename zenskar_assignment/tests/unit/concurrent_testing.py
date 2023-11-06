import requests
import time
import uuid
import concurrent.futures

# Define the endpoint URL and payload
endpoint_url = "https://mqpyh6hoi3.execute-api.ap-south-1.amazonaws.com/Prod/sms_billing"

# Define the headers with the authorization token
headers = {
    "auth-token": "zenskar123"
}

# Function to send a POST request with a random customer ID
def send_post_request(customer_id):
    try:
        # Create a payload with the random customer ID
        payload = {
            "id": customer_id,
            "bytes": 34
        }

        response = requests.post(endpoint_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx, 5xx)
        print(f"Request for customer ID {customer_id} successful.")
    except requests.exceptions.RequestException as e:
        print(f"Request failed with an exception: {str(e)}")

# Main loop for sending POST requests with 12 concurrent invocations
while True:
    customer_ids = [str(uuid.uuid4()) for _ in range(12)]  # Generate 12 random customer IDs
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        executor.map(send_post_request, customer_ids)
    time.sleep(1)  # Wait for 1 second before sending the next batch of requests
