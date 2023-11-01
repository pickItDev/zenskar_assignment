import json
import boto3
from flask_lambda import FlaskLambda
from flask import request

app = FlaskLambda(__name__)
ddb = boto3.resource('dynamodb')
table = ddb.Table('user_billing')

@app.route('/sms_billing', methods=['GET', 'POST'])
def put_list_students():
    if request.method == 'GET':
        bills = table.scan()['Items']
        return json_response(bills)
    else:
        table.put_item(Item=request.form.to_dict())
        return json_response({"message": "billing entry created"})

@app.route('/sms_billing/<id>', methods=['GET'])
def get_patch_delete_student(id):
    key = {'id': id}
    if request.method == 'GET':
        bills = table.get_item(Key=key).get('Item')
        if bills:
            return json_response(bills)
        else:
            return json_response({"message": "Customer or billing not found"}, 404)

def json_response(data, response_code=200):
    return json.dumps(data), response_code, {'Content-Type': 'application/json'}
