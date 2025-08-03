import requests
from app.validators.validators import FlowValidator, ContextValidator, FlowValidationError


def test_valid_flow():
    """Run validation on a well-formed flow definition."""
    print("=== Valid Flow Test ===")

    valid_flow = {
        "flow": {
            "id": "order_processing",
            "name": "Order Processing Flow",
            "start_task": "validate_order",
            "tasks": [
                {"name": "validate_order", "description": "Validate customer order"},
                {"name": "check_inventory", "description": "Check product availability"},
                {"name": "process_payment", "description": "Process payment"},
                {"name": "ship_order", "description": "Ship the order"}
            ],
            "conditions": [
                {
                    "name": "order_validation_check",
                    "description": "Check if order is valid",
                    "source_task": "validate_order",
                    "outcome": "success",
                    "target_task_success": "check_inventory",
                    "target_task_failure": "end"
                },
                {
                    "name": "inventory_check",
                    "description": "Check if items are in stock",
                    "source_task": "check_inventory",
                    "outcome": "success",
                    "target_task_success": "process_payment",
                    "target_task_failure": "end"
                },
                {
                    "name": "payment_check",
                    "description": "Check if payment was successful",
                    "source_task": "process_payment",
                    "outcome": "success",
                    "target_task_success": "ship_order",
                    "target_task_failure": "end"
                }
            ]
        }
    }

    try:
        FlowValidator.validate_complete_flow(valid_flow)
        print("Validation passed.")
        return valid_flow
    except FlowValidationError as e:
        print("Validation failed:", e)
        return None


def test_invalid_flows():
    """Run validation tests for invalid flow structures."""
    print("\n=== Invalid Flow Tests ===")

    test_cases = [
        {
            "name": "Missing required field 'name'",
            "flow": {
                "flow": {
                    "id": "test_flow",
                    "start_task": "task1",
                    "tasks": [{"name": "task1", "description": "Task 1"}],
                    "conditions": []
                }
            }
        },
        {
            "name": "Duplicate task names",
            "flow": {
                "flow": {
                    "id": "test_flow",
                    "name": "Test Flow",
                    "start_task": "task1",
                    "tasks": [
                        {"name": "task1", "description": "First task"},
                        {"name": "task1", "description": "Duplicate task"}
                    ],
                    "conditions": []
                }
            }
        },
        {
            "name": "Condition with unknown source task",
            "flow": {
                "flow": {
                    "id": "test_flow",
                    "name": "Test Flow",
                    "start_task": "task1",
                    "tasks": [{"name": "task1", "description": "Task"}],
                    "conditions": [
                        {
                            "name": "cond",
                            "description": "Invalid condition",
                            "source_task": "nonexistent",
                            "outcome": "success",
                            "target_task_success": "task1",
                            "target_task_failure": "end"
                        }
                    ]
                }
            }
        },
        {
            "name": "Invalid outcome value",
            "flow": {
                "flow": {
                    "id": "test_flow",
                    "name": "Test Flow",
                    "start_task": "task1",
                    "tasks": [{"name": "task1", "description": "Task"}],
                    "conditions": [
                        {
                            "name": "cond",
                            "description": "Invalid outcome",
                            "source_task": "task1",
                            "outcome": "maybe",
                            "target_task_success": "end",
                            "target_task_failure": "end"
                        }
                    ]
                }
            }
        },
        {
            "name": "Unknown start_task",
            "flow": {
                "flow": {
                    "id": "test_flow",
                    "name": "Test Flow",
                    "start_task": "nonexistent_task",
                    "tasks": [{"name": "task1", "description": "Task"}],
                    "conditions": []
                }
            }
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['name']}")
        try:
            FlowValidator.validate_complete_flow(case['flow'])
            print("Expected validation error, but passed.")
        except FlowValidationError as e:
            print("Validation correctly failed:", e)


def test_context_validation():
    """Validate different execution context structures."""
    print("\n=== Context Validation Tests ===")

    test_cases = [
        {"name": "Valid context", "context": {"a": 1}, "should_pass": True},
        {"name": "Not a dict", "context": "not a dict", "should_pass": False},
        {"name": "Numeric key", "context": {1: "invalid"}, "should_pass": False},
        {"name": "Too large", "context": {"x": "x" * (1024 * 1024 + 1)}, "should_pass": False}
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['name']}")
        try:
            ContextValidator.validate_execution_context(case['context'])
            if case['should_pass']:
                print("Context is valid.")
            else:
                print("Expected failure, but passed.")
        except FlowValidationError as e:
            if case['should_pass']:
                print("Unexpected error:", e)
            else:
                print("Validation failed as expected:", e)


def test_edge_cases():
    """Test edge conditions like cycles and unreachable tasks."""
    print("\n=== Edge Case Tests ===")

    # Cycle test
    print("\n1. Flow with cycle")
    flow = {
        "flow": {
            "id": "cyclic",
            "name": "Cycle",
            "start_task": "task1",
            "tasks": [{"name": "task1", "description": "t1"}, {"name": "task2", "description": "t2"}],
            "conditions": [
                {"name": "c1", "description": "", "source_task": "task1", "outcome": "success", "target_task_success": "task2", "target_task_failure": "end"},
                {"name": "c2", "description": "", "source_task": "task2", "outcome": "success", "target_task_success": "task1", "target_task_failure": "end"}
            ]
        }
    }
    try:
        FlowValidator.validate_complete_flow(flow)
        print("Expected cycle detection, but passed.")
    except FlowValidationError as e:
        print("Cycle correctly detected:", e)

    # Unreachable task test
    print("\n2. Flow with unreachable tasks")
    flow = {
        "flow": {
            "id": "unreachable",
            "name": "Unreachable",
            "start_task": "task1",
            "tasks": [
                {"name": "task1", "description": "reachable"},
                {"name": "task2", "description": "unreachable"},
                {"name": "task3", "description": "also unreachable"}
            ],
            "conditions": [
                {"name": "c", "description": "", "source_task": "task1", "outcome": "success", "target_task_success": "end", "target_task_failure": "end"}
            ]
        }
    }
    try:
        FlowValidator.validate_complete_flow(flow)
        print("Validation passed with unreachable task warning.")
    except FlowValidationError as e:
        print("Validation error:", e)


def test_api_validation():
    """Test flow validation via running API server."""
    print("\n=== API Validation Tests ===")

    base_url = "http://localhost:8000"

    try:
        res = requests.get(f"{base_url}/health")
        if res.status_code != 200:
            print("Server is running but returned an unexpected status.")
            return
    except requests.ConnectionError:
        print("Cannot connect to server. Make sure it is running.")
        return

    print("Server is reachable.")

    valid_flow = test_valid_flow()
    if valid_flow:
        print("\nSubmitting valid flow to API...")
        res = requests.post(f"{base_url}/flows", json={"flow_data": valid_flow})
        if res.status_code == 201:
            print("Flow created successfully:", res.json().get("message"))
        else:
            print("Unexpected response:", res.status_code, res.text)

    print("\nSubmitting invalid flow to API...")
    bad_flow = {
        "flow": {
            "id": "",
            "name": "Bad Flow",
            "start_task": "task1",
            "tasks": [],
            "conditions": []
        }
    }
    res = requests.post(f"{base_url}/flows", json={"flow_data": bad_flow})
    if res.status_code == 400:
        print("Validation failed as expected:", res.json())
    else:
        print("Unexpected response:", res.status_code)

    print("\nSubmitting invalid context to API...")
    res = requests.post(f"{base_url}/flows/execute", json={"flow_id": "order_processing", "context": "not a dict"})
    if res.status_code == 422:
        print("Context validation failed as expected.")
    else:
        print("Unexpected response:", res.status_code)


def demo_validation_levels():
    """Explain internal validation stages."""
    print("\n=== Validation Levels ===")

    print("\nLevel 1: Pydantic Type Validation")
    print(" - Validates request structure on API input")

    print("\nLevel 2: Flow Structure Validation")
    print(" - Checks required fields, types, uniqueness")

    print("\nLevel 3: Flow Logic Validation")
    print(" - Detects cycles and unreachable tasks")

    print("\nLevel 4: Runtime Validation")
    print(" - Verifies task behavior and context data")


if __name__ == "__main__":
    print("Starting flow validation tests...")

    test_valid_flow()
    test_invalid_flows()
    test_context_validation()
    test_edge_cases()
    demo_validation_levels()

    print("\nTo test validation through the API, run:")
    print("   python main.py     (in a separate terminal)")
    print("   python validation_examples.py api")

    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        test_api_validation()