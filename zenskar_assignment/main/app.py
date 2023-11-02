import json
import boto3
from flask_lambda import FlaskLambda
from flask import request

app = FlaskLambda(__name__)
ddb = boto3.resource('dynamodb')
table = ddb.Table('user_billing')

@app.route('/sms_billing', methods=['GET', 'POST'])
def put_list_billing():
    if request.method == 'GET':
        bills = table.scan()['Items']
        return json_response(bills)
    else:
        # Assuming 'data' is the key containing the JSON data
        data = request.get_json()

        # Send data to the SQS queue
        sqs = boto3.client('sqs')
        queue_url = 'https://sqs.ap-south-1.amazonaws.com/729812678123/sms_queue'  # Replace with your SQS queue URL
        sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps({'data': data}))
        return json_response({"message": "billing entry created"})

        # table.put_item(Item=request.form.to_dict())
        # data = request.get_json()
        # table.put_item(
        #     Item={
        #         'id': data['id'],
        #         'bytes': data['bytes'],
        #         'time': data['time']
        #     }
        # )

@app.route('/sms_billing/<id>', methods=['GET'])
def get_bill_by_id(id):
    key = {'id': id}
    if request.method == 'GET':
        bills = table.get_item(Key=key).get('Item')
        if bills:
            return json_response(bills)
        else:
            return json_response({"message": "Customer or billing not found"}, 404)

def json_response(data, response_code=200):
    return json.dumps(data), response_code, {'Content-Type': 'application/json'}
