# Receipt Processor API

This project provides a web service to process and score retail receipts according to specific rules. The API has two main endpoints: one for processing receipts and another for retrieving the points awarded for a specific receipt.

## Requirements

- Docker
- Python 3.9+ (if you want to use the provided testing utility)

## Installation

**Clone the repository:**

  ```bash
  git clone https://github.com/akhilesh-varanasi/receipt-processor
  cd receipt-processor
  ```

## Running the Application with Docker

1. **Build the Docker image:**

    ```bash
    docker build -t receipt-processor .
    ```

2. **Run the Docker container:**

    ```bash
    docker run -p 8080:8080 receipt-processor
    ```

    The application will start running on `http://localhost:8080`.

Make sure your project directory structure looks like this:

```plaintext
receipt-processor/
├── app.py
├── Dockerfile
├── requirements.txt
└── examples/
    ├── simple-receipt.json
    └── morning-receipt.json
```

### Testing

A testing utility (`test_receipts.py`) has been provided. It takes a file name as an argument and returns the total points for the receipt. This requires Python 3.9+ and for the test file to be in the `examples` folder. However, you can use `curl` or any other testing method if you prefer.

#### Using `test_receipts.py` Script

1. **Ensure the Flask application is running.**

2. **Run the test script:**

    ```bash
    python test_receipts.py <filename>
    ```

    Replace `<filename>` with the name of the receipt JSON file located in the `examples` directory.

##### Example Usage

```bash
python test_receipts.py simple-receipt.json
python test_receipts.py morning-receipt.json
```

#### Using `curl` Commands

1. **Ensure the Flask application is running.**

2. **Use `curl` commands to test the endpoints:**

    **Process a receipt and get points:**

    ```bash
    # Process the receipt
    response=$(curl -X POST http://localhost:8080/receipts/process -H "Content-Type: application/json" -d @examples/simple-receipt.json)
    echo $response
    id=$(echo $response | sed -n 's/.*"id":"\([^"]*\)".*/\1/p')

    # Get points for the processed receipt
    curl http://localhost:8080/receipts/$id/points
    ```

##### Example Commands

```bash
# Process the receipt
response=$(curl -X POST http://localhost:8080/receipts/process -H "Content-Type: application/json" -d @examples/simple-receipt.json)
echo $response
id=$(echo $response | sed -n 's/.*"id":"\([^"]*\)".*/\1/p')

# Get points for the processed receipt
curl http://localhost:8080/receipts/$id/points
```

