from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
import uuid
import math
from datetime import datetime

app = Flask(__name__)
receipts = {}

class Receipt:
    def __init__(self, retailer, purchase_date, purchase_time, items, total):
        self.id = str(uuid.uuid4())
        self.retailer = retailer
        self.purchase_date = purchase_date
        self.purchase_time = purchase_time
        self.items = items
        self.total = total
        self.points = self.calculate_points()

    def calculate_points(self):
        points = 0
        # Rule 1: One point for every alphanumeric character in the retailer name.
        points += sum(c.isalnum() for c in self.retailer)

        # Rule 2: 50 points if the total is a round dollar amount with no cents.
        total_float = float(self.total)
        if total_float == int(total_float):
            points += 50

        # Rule 3: 25 points if the total is a multiple of 0.25.
        if total_float % 0.25 == 0:
            points += 25

        # Rule 4: 5 points for every two items on the receipt.
        points += (len(self.items) // 2) * 5

        # Rule 5: If the trimmed length of the item description is a multiple of 3,
        # multiply the price by 0.2 and round up to the nearest integer.
        for item in self.items:
            trimmed_desc = item['shortDescription'].strip()
            if len(trimmed_desc) % 3 == 0:
                price = float(item['price'])
                points += math.ceil(price * 0.2)

        # Rule 6: 6 points if the day in the purchase date is odd.
        purchase_date = datetime.strptime(self.purchase_date, '%Y-%m-%d')
        if purchase_date.day % 2 != 0:
            points += 6

        # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm.
        purchase_time = datetime.strptime(self.purchase_time, '%H:%M')
        if 14 <= purchase_time.hour < 16:
            points += 10

        return points

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({"error": "Bad Request", "message": str(e)}), 400

@app.errorhandler(NotFound)
def handle_not_found(e):
    return jsonify({"error": "Not Found", "message": str(e)}), 404

@app.errorhandler(InternalServerError)
def handle_internal_server_error(e):
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("Invalid JSON format")
        
        required_keys = ['retailer', 'purchaseDate', 'purchaseTime', 'items', 'total']
        for key in required_keys:
            if key not in data:
                raise BadRequest(f"Missing key: {key}")

        receipt = Receipt(
            retailer=data['retailer'],
            purchase_date=data['purchaseDate'],
            purchase_time=data['purchaseTime'],
            items=data['items'],
            total=data['total']
        )
        receipts[receipt.id] = receipt
        return jsonify({"id": receipt.id})
    except KeyError as e:
        raise BadRequest(f"Missing key: {e.args[0]}")
    except Exception as e:
        raise InternalServerError(str(e))

@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_points(receipt_id):
    try:
        receipt = receipts.get(receipt_id)
        if receipt is None:
            raise NotFound("Receipt not found")
        return jsonify({"points": receipt.points})
    except Exception as e:
        raise InternalServerError(str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
