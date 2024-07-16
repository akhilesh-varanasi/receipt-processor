import os
import sys
import subprocess
import json

# Define the directory where the example files are stored
EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'examples')

# Define the URL of the running Flask application
FLASK_URL = "http://localhost:8080"

def run_test(filename):
    filepath = os.path.join(EXAMPLES_DIR, filename)
    if not os.path.isfile(filepath):
        print(f"Error: File '{filename}' not found in the examples directory.")
        return

    # Process the receipt
    process_response = subprocess.run(
        ['curl', '-s', '-X', 'POST', f"{FLASK_URL}/receipts/process", '-H', 'Content-Type: application/json', '-d', f"@{filepath}"],
        capture_output=True,
        text=True
    )
    process_output = process_response.stdout
    try:
        process_data = json.loads(process_output)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode response: {process_output}")
        return

    receipt_id = process_data.get("id")
    if not receipt_id:
        print(f"Error: Failed to process receipt. Response: {process_output}")
        return

    # Get points for the processed receipt
    points_response = subprocess.run(
        ['curl', '-s', f"{FLASK_URL}/receipts/{receipt_id}/points"],
        capture_output=True,
        text=True
    )
    points_output = points_response.stdout
    try:
        points_data = json.loads(points_output)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode points response: {points_output}")
        return

    points = points_data.get("points")
    print(f"File: {filename}, Points: {points}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_receipts.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    run_test(filename)
