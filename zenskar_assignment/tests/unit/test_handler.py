import requests
import time
import uuid

# Define the endpoint URL and payload
endpoint_url = "https://mqpyh6hoi3.execute-api.ap-south-1.amazonaws.com/Prod/sms_billing"

# Define the headers with the authorization token
headers = {
    "auth-token": "zenskar123"
}

# Define the duration of the test in seconds
test_duration = 60  # 1 minute

# Start time for measuring test duration
start_time = time.time()

# Main loop for sending POST requests
while time.time() - start_time < test_duration:
    try:
        # Generate a random customer ID
        customer_id = str(uuid.uuid4())

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

    # Wait for 1 second before sending the next request
    time.sleep(1)

print("Test completed.")
