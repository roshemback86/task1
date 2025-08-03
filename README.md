# Flow Manager API

Flow Manager is an asynchronous task orchestration engine built with FastAPI.  
It enables users to define, validate, and execute flows of tasks with conditional transitions and context-aware logic.

---

## Features

- Declarative JSON-based flow definitions
- Sequential and conditional task execution
- Execution context propagation between tasks
- Strict flow and condition validation
- Fully asynchronous execution using Python's asyncio
- REST API for flow registration, execution, and inspection
- Test coverage using pytest and asyncio plugins

---

## Technology Stack

- Python 3.9
- FastAPI
- Uvicorn
- Pydantic
- Pytest
- pytest-asyncio

---

## Project Structure

```
.
├── main.py                 # FastAPI entry point
├── models/                 # Data models for Flow, Task, Condition
├── flow_manager/           # Core logic for executing flows
├── demo_tasks.py           # Example asynchronous task functions
├── validators.py           # Flow and context validation
├── tests/                  # Test suite
│   ├── test_flows.py
│   ├── test_tasks.py
│   └── test_validators.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Setup Instructions

```bash
git clone https://github.com/roshemback86/task1
cd task1
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Running the API

```bash
uvicorn main:app --reload
```

The interactive documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Running Tests

```bash
python -m pytest tests/
```

---

## API Endpoints

| Method | Path                    | Description                       |
|--------|-------------------------|-----------------------------------|
| GET    | `/health`               | Check service health              |
| POST   | `/flows`                | Register a new flow definition    |
| GET    | `/flows/{flow_id}`      | Retrieve a specific flow          |
| POST   | `/flows/execute`        | Execute a registered flow         |
| GET    | `/executions/{exec_id}` | Check execution status            |

---

## Example Flow Payload

```json
{
  "flow": {
    "id": "flow123",
    "name": "Data Processing Flow",
    "start_task": "task1",
    "tasks": [
      {"name": "task1", "description": "Fetch data"},
      {"name": "task2", "description": "Process data"},
      {"name": "task3", "description": "Store data"}
    ],
    "conditions": [
      {
        "name": "condition_1",
        "source_task": "task1",
        "outcome": "success",
        "target_task_success": "task2",
        "target_task_failure": "end"
      },
      {
        "name": "condition_2",
        "source_task": "task2",
        "outcome": "success",
        "target_task_success": "task3",
        "target_task_failure": "end"
      }
    ]
  }
}
```

---

## Author

Developed by [@roshemback86](https://github.com/roshemback86)
