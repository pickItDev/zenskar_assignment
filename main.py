from flask import Flask, request, jsonify
from collections import defaultdict
from flask_jwt_extended import JWTManager, jwt_required, create_access_token


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'zenskar'  # Change this to a secure secret key.
jwt = JWTManager(app)

# Dummy user database for authentication
users = {
    "user1": "password1",
    "user2": "password2"
}

# In-memory storage for demo purpose. Ideally, this should be a DB instance initiation
monthly_usage = defaultdict(lambda: defaultdict(int))

# JWT Authentication
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username] == password:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# Routing requests to /usage
@app.route('/usage', methods=['POST'])
@jwt_required()
def record_usage():
    data = request.get_json()

    # Input validation of the customer & bytes fields from the JSON object
    if 'customer' not in data or 'bytes' not in data:
        return jsonify({"error": "Invalid data format"}), 400

    customer_id = data['customer']
    bytes_sent = data['bytes']

    # Get the current month and year for grouping.
    current_month = data.get('month', 1)
    current_year = data.get('year', 2023)

    # Update the usage data for the customer in the corresponding month.
    monthly_usage[customer_id][f"{current_year}-{current_month:02}"] += bytes_sent

    print(f"Customer {customer_id}: Total bytes sent = {bytes_sent} bytes")
    return jsonify({"message": "Usage recorded"}), 201

# Get user month wise details using customer ID
@app.route('/getUsageByCustomer', methods=['GET'])
@jwt_required()
def get_usage_by_customer():
    customer_id = request.args.get('customer')

    if customer_id in monthly_usage:
        return jsonify({"customer": customer_id, "usage_data": monthly_usage[customer_id]})
    else:
        return jsonify({"error": "Data not found for the specified customer"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
