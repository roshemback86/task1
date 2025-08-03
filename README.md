# Flow Manager System

A microservice for managing sequential task execution with conditional flow control. The system allows you to define workflows as JSON configurations and execute them with full state tracking and error handling.

## Features

- **Sequential Task Execution**: Execute tasks in a defined order with conditional branching
- **Flow Control**: Define conditions that determine task transitions based on success/failure
- **State Tracking**: Complete execution history with timing and result data
- **Validation Framework**: Multi-level validation for flow definitions and execution contexts
- **REST API**: Full HTTP API with OpenAPI documentation
- **Asynchronous Processing**: Non-blocking task execution with proper error handling
- **Extensible Architecture**: Easy to add custom task implementations

## Project Structure

```
flow-manager/
├── requirements.txt          # Python dependencies
├── models.py                # Core data models and enums
├── task_executor.py         # Task execution engine
├── flow_manager.py          # Flow orchestration logic
├── demo_tasks.py           # Sample task implementations
├── api_models.py           # Pydantic models for API
├── validators.py           # Validation framework
├── main.py                # FastAPI application entry point
├── demo.py                # Standalone demonstration
├── test_client.py         # API test client
├── validation_examples.py  # Validation test cases
├── run.sh                 # Unix startup script
├── run.bat               # Windows startup script
└── README.md             # This file
```

## Installation and Setup

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Quick Start

1. **Clone or download the project files**
   ```bash
   mkdir flow-manager
   cd flow-manager
   # Copy all project files to this directory
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the API server**
   ```bash
   python main.py
   ```
   
   The server will start on `http://localhost:8000`

4. **Access the API documentation**
   - Swagger UI: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Alternative Startup Methods

#### Using startup scripts

**Linux/macOS:**
```bash
chmod +x run.sh
./run.sh                    # Start API server
./run.sh demo              # Run standalone demo
./run.sh test              # Run API tests (server must be running)
```

**Windows:**
```cmd
run.bat                    # Start API server
run.bat demo              # Run standalone demo
run.bat test              # Run API tests (server must be running)
```

#### Direct Python execution

```bash
# API server
python main.py

# Standalone demo (no API required)
python demo.py

# API tests (requires running server)
python test_client.py test

# Validation tests
python validation_examples.py
```

## API Usage

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |
| GET | `/docs` | Interactive API documentation |
| POST | `/flows` | Create a new flow definition |
| GET | `/flows/{flow_id}` | Retrieve flow information |
| POST | `/flows/execute` | Execute a flow |
| GET | `/executions/{execution_id}` | Get execution status |

### Example API Usage

#### 1. Create a Flow

```bash
curl -X POST "http://localhost:8000/flows" \
     -H "Content-Type: application/json" \
     -d '{
       "flow_data": {
         "flow": {
           "id": "data_pipeline",
           "name": "Data Processing Pipeline",
           "start_task": "extract",
           "tasks": [
             {"name": "extract", "description": "Extract data from source"},
             {"name": "transform", "description": "Transform extracted data"},
             {"name": "load", "description": "Load data to destination"}
           ],
           "conditions": [
             {
               "name": "extract_success",
               "description": "Check extraction success",
               "source_task": "extract",
               "outcome": "success",
               "target_task_success": "transform",
               "target_task_failure": "end"
             },
             {
               "name": "transform_success", 
               "description": "Check transformation success",
               "source_task": "transform",
               "outcome": "success",
               "target_task_success": "load",
               "target_task_failure": "end"
             }
           ]
         }
       }
     }'
```

#### 2. Execute a Flow

```bash
curl -X POST "http://localhost:8000/flows/execute" \
     -H "Content-Type: application/json" \
     -d '{
       "flow_id": "data_pipeline",
       "context": {
         "source_url": "https://api.example.com/data",
         "batch_id": "batch_001"
       }
     }'
```

#### 3. Check Execution Status

```bash
curl "http://localhost:8000/executions/{execution_id}"
```

### Response Examples

**Successful Flow Execution:**
```json
{
  "execution_id": "12345678-1234-1234-1234-123456789abc",
  "flow_id": "data_pipeline",
  "status": "completed",
  "current_task": null,
  "task_results": {
    "extract": {
      "status": "success",
      "data": {"records": 1000},
      "error": null,
      "execution_time": 0.245
    },
    "transform": {
      "status": "success", 
      "data": {"processed_records": 950},
      "error": null,
      "execution_time": 1.123
    },
    "load": {
      "status": "success",
      "data": {"loaded_records": 950},
      "error": null,
      "execution_time": 0.567
    }
  },
  "start_time": "2024-01-15T10:30:00.000Z",
  "end_time": "2024-01-15T10:30:02.000Z",
  "context": {
    "source_url": "https://api.example.com/data",
    "batch_id": "batch_001",
    "extract_result": {"records": 1000},
    "transform_result": {"processed_records": 950},
    "load_result": {"loaded_records": 950}
  }
}
```

## Flow Definition Format

### Basic Structure

```json
{
  "flow": {
    "id": "unique_flow_identifier",
    "name": "Human readable flow name",
    "start_task": "first_task_name",
    "tasks": [
      {
        "name": "task_name",
        "description": "Task description"
      }
    ],
    "conditions": [
      {
        "name": "condition_name",
        "description": "Condition description", 
        "source_task": "task_that_triggers_condition",
        "outcome": "success|failure",
        "target_task_success": "next_task_on_success",
        "target_task_failure": "next_task_on_failure_or_end"
      }
    ]
  }
}
```

### Field Descriptions

**Flow Level:**
- `id`: Unique identifier for the flow
- `name`: Human-readable name
- `start_task`: Name of the first task to execute
- `tasks`: Array of task definitions
- `conditions`: Array of conditional transitions

**Task Level:**
- `name`: Unique task identifier within the flow
- `description`: Human-readable task description

**Condition Level:**
- `name`: Unique condition identifier
- `description`: Human-readable condition description
- `source_task`: Task whose result triggers this condition
- `outcome`: Expected task outcome ("success" or "failure")
- `target_task_success`: Next task if condition matches
- `target_task_failure`: Next task if condition doesn't match (use "end" to terminate)

## Testing

### Automated Tests

```bash
# Basic API functionality tests
python test_client.py test

# Stress testing with multiple concurrent executions
python test_client.py stress

# Validation framework tests
python validation_examples.py

# API validation tests (requires running server)
python validation_examples.py api
```

### Manual Testing

1. **Start the server:**
   ```bash
   python main.py
   ```

2. **Open browser to Swagger UI:**
   ```
   http://localhost:8000/docs
   ```

3. **Test using the interactive documentation or curl commands**

### Expected Test Results

**Successful API Test Output:**
```
=== Testing Flow Manager API ===
1. Testing health check...
✓ Health check passed: {'status': 'healthy', 'service': 'Flow Manager'}

2. Creating flow...
✓ Flow created: {'message': 'Flow flow123 created successfully'}

3. Getting flow information...
✓ Flow info retrieved:
   Name: Data processing flow
   Tasks: ['task1', 'task2', 'task3']

4. Executing flow...
✓ Flow executed:
   Execution ID: 12345678-1234-1234-1234-123456789abc
   Status: completed

5. Getting execution details...
✓ Execution details:
   Status: completed
   Task Results:
     task1: success (0.201s)
       Data: {'users': [{'id': 1, 'name': 'John'}, {'id': 2, 'name': 'Jane'}]}
     task2: success (0.302s)
       Data: {'processed_users': 2, 'timestamp': '2024-...'}
     task3: success (0.101s)
       Data: {'stored': True, 'record_id': '...'}

✓ All tests passed!
```

## Architecture Overview

### Core Components

1. **Models** (`models.py`): Data structures for flows, tasks, conditions, and execution tracking
2. **Task Executor** (`task_executor.py`): Engine for executing individual tasks
3. **Flow Manager** (`flow_manager.py`): Orchestration engine for complete flows
4. **Validators** (`validators.py`): Multi-level validation framework
5. **API Layer** (`main.py`): REST API with FastAPI and Pydantic validation

### Execution Flow

1. **Flow Registration**: Flow definitions are validated and registered
2. **Execution Initialization**: New execution instance created with unique ID
3. **Sequential Processing**: Tasks executed in order based on conditions
4. **Context Management**: Results passed between tasks via shared context
5. **State Tracking**: Complete execution history maintained
6. **Completion**: Final status and results returned

### Validation Levels

1. **API Validation**: Automatic type checking via Pydantic models
2. **Structure Validation**: Flow definition completeness and correctness
3. **Logic Validation**: Cycle detection and reachability analysis
4. **Runtime Validation**: Task execution and result validation

## Development

### Adding Custom Tasks

1. **Create task function:**
   ```python
   async def my_custom_task(context: Dict[str, Any]) -> Any:
       # Access previous task results
       previous_data = context.get("previous_task_result")
       
       # Perform custom logic
       result = await some_async_operation(previous_data)
       
       # Return result data
       return {"processed": True, "data": result}
   ```

2. **Register in task registry:**
   ```python
   TASK_FUNCTIONS["my_task"] = my_custom_task
   ```

3. **Use in flow definition:**
   ```json
   {
     "name": "my_task",
     "description": "My custom task implementation"
   }
   ```

### Extending Validation

Add custom validation rules in `validators.py`:

```python
@staticmethod
def validate_custom_rule(flow_data: Dict[str, Any]) -> None:
    # Custom validation logic
    if some_condition:
        raise FlowValidationError("Custom validation failed")
```

### Environment Configuration

The system uses the following defaults:
- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 8000
- **Context Size Limit**: 1MB
- **Task Timeout**: No default timeout (implement in custom tasks)

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   # Kill the process
   kill -9 <PID>
   ```

2. **Import errors:**
   - Ensure all files are in the same directory
   - Verify Python version (3.9+ required)
   - Check that all dependencies are installed

3. **Connection refused:**
   - Verify server is running on correct port
   - Check firewall settings
   - Ensure no proxy interference

4. **Validation errors:**
   - Check flow JSON structure against documentation
   - Verify all required fields are present
   - Ensure task names are unique
   - Check condition references are valid

### Debug Mode

Run with detailed logging:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

### Performance Considerations

- Task execution is sequential within a flow
- Multiple flows can execute concurrently
- Context data is kept in memory during execution
- Large context data may impact performance

## API Reference

For complete API documentation with interactive testing, visit:
`http://localhost:8000/docs` (when server is running)

The API follows REST conventions and returns standard HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `404`: Not Found
- `422`: Unprocessable Entity (type validation error)
- `500`: Internal Server Error

## License

This project is provided as-is for educational and demonstration purposes.