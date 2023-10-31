from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)

# In-memory storage for demo purpose. Ideally, this should be a DB instance initiation
monthly_usage = defaultdict(lambda: defaultdict(int))

# Routing requests to /usage
@app.route('/usage', methods=['POST'])

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

    return jsonify({"message": "Usage recorded"}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
