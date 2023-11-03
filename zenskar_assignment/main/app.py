import json
import boto3
from flask_lambda import FlaskLambda
from flask import request, jsonify, Response
from decimal import Decimal

# Custom JSON encoder to handle decimal values from Dynamo DB
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)

# Initialise flask
# Initialise boto3 agent for Dynamo & SQS
app = FlaskLambda(__name__)
ddb = boto3.resource('dynamodb')
table = ddb.Table('sms_events')

# Creating two endpoints (GET & POST) at /sms_billing
# GET scans the complete DB (Not advisable! Using it only for test purposes)
# POST Redirects our request to an SQS queue
@app.route('/sms_billing', methods=['GET', 'POST'])
def put_list_billing():
    try:
        if request.method == 'GET':
            bills = table.scan()['Items']
            return json_response(bills)
        elif request.method == 'POST':
            # Get data from the request
            data = request.get_json()

            # Check if 'id' and 'bytes' are present in the data
            if 'id' not in data or 'bytes' not in data:
                return json_response({"error": "Invalid data format. 'id' and 'bytes' are required."}, 400)

            # Send data to the SQS queue
            sqs = boto3.client('sqs')
            queue_url = 'https://sqs.ap-south-1.amazonaws.com/729812678123/sms_queue'  # Replace with your SQS queue URL
            sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps({'data': data}))

            return json_response({"message": "billing entry passed to SQS"}, 201)
        else:
            return json_response({"error": "Invalid HTTP method"}, 405)
    except Exception as e:
        return json_response({"error": str(e)}, 500)

# Endpoint to get customer records by cust_id
@app.route('/sms_billing/<id>', methods=['GET'])
def get_bill_by_id(id):
    try:
        key = {'id': id}
        if request.method == 'GET':
            response = table.get_item(Key=key)
            item = response.get('Item', {})
            return json_response(item)
        else:
            return json_response({"error": "Invalid HTTP method"}, 405)
    except Exception as e:
        return json_response({"error": str(e)}, 500)


def json_response(data, response_code=200):
    return json.dumps(data, cls=DecimalEncoder), response_code, {'Content-Type': 'application/json'}