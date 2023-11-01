import boto3
import json
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import logging

# Initialize Flask app & configure JWT
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'zenskar'  # Change this to a secure secret key.
jwt = JWTManager(app)

# Initialize a Boto3 session
session = boto3.Session(
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY',
    region_name='ap-south-1'
)

# Initialize a DynamoDB client & table
dynamodb = session.client('dynamodb')
table_name = 'Usage_events'

# Dummy user database for authentication
users = {
    "user1": "password1",
    "user2": "password2"
}


# Lambda handler
def lambda_handler(event, context):
    # Set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    try:
        if event['httpMethod'] == 'POST':
            data = event['body']
            data = json.loads(data)

            if 'customer' not in data or 'bytes' not in data:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid data format"})
                }

            customer_id = data['customer']
            bytes_sent = data['bytes']

            # Get the current month and year for grouping.
            current_month = data.get('month', 1)
            current_year = data.get('year', 2023)

            # Store the usage data in DynamoDB
            dynamodb.put_item(
                TableName=table_name,
                Item={
                    'CustomerID': {'S': customer_id},
                    'Timestamp-EventID': {'S': f"{current_year}-{current_month:02}"},
                    'BytesSent': {'N': str(bytes_sent)}
                }
            )

            logger.info(f"Customer {customer_id}: Total bytes sent = {bytes_sent} bytes")
            return {
                "statusCode": 201,
                "body": json.dumps({"message": "Usage recorded"})
            }

        elif event['httpMethod'] == 'GET':
            customer_id = event['queryStringParameters']['customer']

            # Use the Query operation to retrieve all records for the specified customer
            response = dynamodb.query(
                TableName=table_name,
                KeyConditionExpression='CustomerID = :customer_id',
                ExpressionAttributeValues={
                    ':customer_id': {'S': customer_id}
                }
            )

            items = response.get('Items', [])

            # Parse and format the retrieved items
            formatted_data = {
                'customer': customer_id,
                'usage_data': {}
            }

            for item in items:
                event_id = item['Timestamp-EventID']['S']
                bytes_sent = int(item['BytesSent']['N'])
                formatted_data['usage_data'][event_id] = bytes_sent

            if formatted_data['usage_data']:
                return {
                    "statusCode": 200,
                    "body": json.dumps(formatted_data)
                }
            else:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Data not found for the specified customer"})
                }
    except Exception as e:
        # Handle the exception and log the error
        logger.error(f"An error occurred: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }
