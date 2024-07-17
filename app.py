from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
import uuid
import math
from datetime import datetime
import re
import traceback

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
        points += sum(c.isalnum() for c in self.retailer)
        total_float = float(self.total)
        if total_float == int(total_float):
            points += 50
        if total_float % 0.25 == 0:
            points += 25
        points += (len(self.items) // 2) * 5
        for item in self.items:
            trimmed_desc = item['shortDescription'].strip()
            if len(trimmed_desc) % 3 == 0:
                price = float(item['price'])
                points += math.ceil(price * 0.2)
        purchase_date = datetime.strptime(self.purchase_date, '%Y-%m-%d')
        if purchase_date.day % 2 != 0:
            points += 6
        purchase_time = datetime.strptime(self.purchase_time, '%H:%M')
        if 14 <= purchase_time.hour < 16:
            points += 10
        return points

def validate_receipt_data(data):
    required_keys = ['retailer', 'purchaseDate', 'purchaseTime', 'items', 'total']
    for key in required_keys:
        if key not in data:
            raise BadRequest(f"Missing key: {key}")
    if not re.match(r"^[\w\s\-&]+$", data['retailer']):
        raise BadRequest("Invalid retailer format")
    try:
        datetime.strptime(data['purchaseDate'], '%Y-%m-%d')
    except ValueError:
        raise BadRequest("Invalid purchaseDate format")
    try:
        datetime.strptime(data['purchaseTime'], '%H:%M')
    except ValueError:
        raise BadRequest("Invalid purchaseTime format")
    if not isinstance(data['items'], list) or len(data['items']) < 1:
        raise BadRequest("Items should be a non-empty array")
    for item in data['items']:
        if 'shortDescription' not in item or 'price' not in item:
            raise BadRequest("Item is missing shortDescription or price")
        if not re.match(r"^[\w\s\-]+$", item['shortDescription']):
            raise BadRequest("Invalid item shortDescription format")
        if not re.match(r"^\d+\.\d{2}$", item['price']):
            raise BadRequest("Invalid item price format")
    if not re.match(r"^\d+\.\d{2}$", data['total']):
        raise BadRequest("Invalid total format")

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
        validate_receipt_data(data)
        receipt = Receipt(
            retailer=data['retailer'],
            purchase_date=data['purchaseDate'],
            purchase_time=data['purchaseTime'],
            items=data['items'],
            total=data['total']
        )
        receipts[receipt.id] = receipt
        return jsonify({"id": receipt.id}), 200
    except BadRequest as e:
        return handle_bad_request(e)
    except NotFound as e:
        return handle_not_found(e)
    except Exception as e:
        return handle_internal_server_error(e)

@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_points(receipt_id):
    try:
        receipt = receipts.get(receipt_id)
        if receipt is None:
            raise NotFound("Receipt not found")
        return jsonify({"points": receipt.points}), 200
    except NotFound as e:
        return handle_not_found(e)
    except Exception as e:
        return handle_internal_server_error(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
