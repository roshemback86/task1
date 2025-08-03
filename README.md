# Flow Manager

Flow Manager is a lightweight orchestration system that allows defining and executing workflows composed of tasks with conditional logic.

## Features

- Define workflows with custom tasks and branching logic
- Validate flows structurally and logically
- Execute flows asynchronously with shared context
- Run unit and integration tests
- Validate definitions via script or API
- Run demo flows without API server
- Dockerized for containerized deployment

---

## Project Structure

```
flow-manager/
├── app/
│   ├── api/                    # FastAPI route handlers
│   ├── core/                   # Core business logic (executors, flow engine)
│   ├── models/                 # Pydantic models and enums
│   ├── services/               # Service registry and utility logic
│   ├── validators/             # Flow and context validation logic
│   └── main.py                 # Application entry point
├── scripts/
│   ├── validation_examples.py  # Flow validation scenarios and API tests
│   ├── test_client.py          # Functional and stress tests against running API
│   └── demo.py                 # Standalone flow demo (no server required)
├── tests/                      # Unit tests
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── pytest.ini
```

---

## Installation (Local Python)

```bash
git clone https://github.com/your-username/flow-manager.git
cd flow-manager
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Running the Server

```bash
python app/main.py
```

By default, the API will be available at:  
http://localhost:8000

Swagger documentation is available at:  
http://localhost:8000/docs

---

## Running via Docker

1. Build and start the container:

```bash
docker-compose up --build
```

This will:

- Build the image using the provided Dockerfile
- Start the FastAPI server on port 8000

2. Open in browser:

- http://localhost:8000/docs – Swagger UI
- http://localhost:8000/health – Health check

3. Stop container:

```bash
docker-compose down
```

---

## Running Tests

Run all unit tests using `pytest`:

```bash
python -m pytest
```

Make sure you have `pytest`, `pytest-asyncio`, and `anyio` installed.

---

## Validation Testing

You can validate sample flows using the provided script.

### 1. Run local validation logic

```bash
python -m scripts.validation_examples
```

This performs:

- structural validation
- invalid cases
- edge cases (cycles, unreachable tasks)
- context validation

### 2. Run validation via API

Make sure the server is running in another terminal:

```bash
python app/main.py
# or
docker-compose up
```

Then run:

```bash
python -m scripts.validation_examples api
```

This will:

- POST valid/invalid flows to the API
- Test execution with invalid context
- Verify server responses and validation behavior

---

## API Testing (Functional & Stress)

You can test API endpoints with:

```bash
python -m scripts.test_client test
```

To run a simple stress test with multiple flow executions:

```bash
python -m scripts.test_client stress
```

---

## CLI Demo (No API Required)

You can run a local flow directly via `scripts/demo.py`:

```bash
python -m scripts.demo
```

This will:

- Load a predefined flow
- Assign example task functions
- Execute the flow directly in memory
- Display execution results and timings

---

## Example Flow Definition

```json
{
  "flow": {
    "id": "order_processing",
    "name": "Order Processing Flow",
    "start_task": "validate_order",
    "tasks": [
      { "name": "validate_order", "description": "Validate customer order" },
      { "name": "check_inventory", "description": "Check product availability" },
      { "name": "process_payment", "description": "Process payment" },
      { "name": "ship_order", "description": "Ship the order" }
    ],
    "conditions": [
      {
        "name": "validation_passed",
        "source_task": "validate_order",
        "outcome": "success",
        "target_task_success": "check_inventory",
        "target_task_failure": "end"
      }
    ]
  }
}
```

---

## Validation Levels

1. **Pydantic Validation**: Ensures input types (e.g. dict, str)
2. **Structure Validation**: Checks required fields and reference integrity
3. **Logic Validation**: Detects cycles and unreachable tasks
4. **Runtime Validation**: Ensures task function availability and safe execution