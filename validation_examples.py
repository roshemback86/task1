# validation_examples.py
"""
Comprehensive validation examples and test cases for Flow Manager.

This module demonstrates various validation scenarios including valid flows,
common error cases, and edge conditions for testing the validation framework.
"""

import requests
import json
from validators import FlowValidator, ContextValidator, FlowValidationError


def test_valid_flow():
    """Test case for a properly structured flow definition."""
    print("=== Testing Valid Flow ===")

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
        print("✅ Validation passed successfully!")
        return valid_flow
    except FlowValidationError as e:
        print(f"❌ Validation error: {e}")
        return None


def test_invalid_flows():
    """Test cases for various invalid flow configurations."""
    print("\n=== Testing Invalid Flows ===")

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
            "name": "Condition references nonexistent task",
            "flow": {
                "flow": {
                    "id": "test_flow",
                    "name": "Test Flow",
                    "start_task": "task1",
                    "tasks": [
                        {"name": "task1", "description": "First task"}
                    ],
                    "conditions": [
                        {
                            "name": "condition1",
                            "description": "Test condition",
                            "source_task": "nonexistent_task",
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
                    "tasks": [
                        {"name": "task1", "description": "First task"}
                    ],
                    "conditions": [
                        {
                            "name": "condition1",
                            "description": "Test condition",
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
            "name": "Nonexistent start_task",
            "flow": {
                "flow": {
                    "id": "test_flow",
                    "name": "Test Flow",
                    "start_task": "nonexistent_start",
                    "tasks": [
                        {"name": "task1", "description": "First task"}
                    ],
                    "conditions": []
                }
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Test: {test_case['name']}")
        try:
            FlowValidator.validate_complete_flow(test_case['flow'])
            print("❌ Validation should have failed!")
        except FlowValidationError as e:
            print(f"✅ Expected error: {e}")


def test_context_validation():
    """Test cases for execution context validation."""
    print("\n=== Testing Context Validation ===")

    test_cases = [
        {
            "name": "Valid context",
            "context": {
                "user_id": "12345",
                "order_data": {
                    "items": [{"id": 1, "quantity": 2}],
                    "total": 100.50
                },
                "metadata": {
                    "source": "mobile_app",
                    "version": "1.2.3"
                }
            },
            "should_pass": True
        },
        {
            "name": "Non-dictionary context",
            "context": "this is not a dict",
            "should_pass": False
        },
        {
            "name": "Numeric keys in context",
            "context": {
                123: "numeric key",
                "valid_key": "valid value"
            },
            "should_pass": False
        },
        {
            "name": "Oversized context",
            "context": {
                "data": "x" * (1024 * 1024 + 1)
            },
            "should_pass": False
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Test: {test_case['name']}")
        try:
            ContextValidator.validate_execution_context(test_case['context'])
            if test_case['should_pass']:
                print("✅ Context is valid!")
            else:
                print("❌ Validation should have failed!")
        except FlowValidationError as e:
            if not test_case['should_pass']:
                print(f"✅ Expected error: {e}")
            else:
                print(f"❌ Unexpected error: {e}")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("\n=== Testing Edge Cases ===")

    print("\n1. Test: Flow with cycle")
    cyclic_flow = {
        "flow": {
            "id": "cyclic_flow",
            "name": "Flow with cycle",
            "start_task": "task1",
            "tasks": [
                {"name": "task1", "description": "First task"},
                {"name": "task2", "description": "Second task"}
            ],
            "conditions": [
                {
                    "name": "condition1",
                    "description": "Task1 to Task2",
                    "source_task": "task1",
                    "outcome": "success",
                    "target_task_success": "task2",
                    "target_task_failure": "end"
                },
                {
                    "name": "condition2",
                    "description": "Task2 back to Task1 (cycle!)",
                    "source_task": "task2",
                    "outcome": "success",
                    "target_task_success": "task1",
                    "target_task_failure": "end"
                }
            ]
        }
    }

    try:
        FlowValidator.validate_complete_flow(cyclic_flow)
        print("❌ Validation should have detected cycle!")
    except FlowValidationError as e:
        print(f"✅ Cycle detected: {e}")

    print("\n2. Test: Flow with unreachable tasks")
    unreachable_flow = {
        "flow": {
            "id": "unreachable_flow",
            "name": "Flow with unreachable tasks",
            "start_task": "task1",
            "tasks": [
                {"name": "task1", "description": "Reachable task"},
                {"name": "task2", "description": "Unreachable task"},
                {"name": "task3", "description": "Another unreachable task"}
            ],
            "conditions": [
                {
                    "name": "condition1",
                    "description": "Task1 ends flow",
                    "source_task": "task1",
                    "outcome": "success",
                    "target_task_success": "end",
                    "target_task_failure": "end"
                }
            ]
        }
    }

    try:
        FlowValidator.validate_complete_flow(unreachable_flow)
        print("✅ Flow created with warning about unreachable tasks")
    except FlowValidationError as e:
        print(f"⚠️  Error: {e}")


def test_api_validation():
    """Test validation through API endpoints."""
    print("\n=== Testing API Validation ===")

    base_url = "http://localhost:8000"

    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code != 200:
            print("❌ Server not running. Start with: python main.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Start with: python main.py")
        return

    print("✅ Server is accessible")

    valid_flow = test_valid_flow()
    if valid_flow:
        print("\n1. Test: Creating valid flow via API")
        try:
            response = requests.post(
                f"{base_url}/flows",
                json={"flow_data": valid_flow}
            )
            if response.status_code == 201:
                print("✅ Flow successfully created")
                result = response.json()
                print(f"   Response: {result['message']}")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Request error: {e}")

    print("\n2. Test: Creating invalid flow via API")
    invalid_flow = {
        "flow": {
            "id": "",
            "name": "Invalid Flow",
            "start_task": "task1",
            "tasks": [],
            "conditions": []
        }
    }

    try:
        response = requests.post(
            f"{base_url}/flows",
            json={"flow_data": invalid_flow}
        )
        if response.status_code == 400:
            print("✅ Validation correctly rejected invalid flow")
            error = response.json()
            print(f"   Error: {error['detail']}")
        else:
            print(f"❌ Expected status 400, got: {response.status_code}")
    except Exception as e:
        print(f"❌ Request error: {e}")

    print("\n3. Test: Execution with invalid context")
    try:
        response = requests.post(
            f"{base_url}/flows/execute",
            json={
                "flow_id": "order_processing",
                "context": "invalid context"
            }
        )
        if response.status_code == 422:
            print("✅ Pydantic correctly rejected invalid context")
            error = response.json()
            print(f"   Error: {error['detail']}")
        else:
            print(f"❌ Expected status 422, got: {response.status_code}")
    except Exception as e:
        print(f"❌ Request error: {e}")


def demo_validation_levels():
    """Demonstrate the different levels of validation."""
    print("\n=== Validation Levels Overview ===")

    print("\n🔹 Level 1: Type Validation (Pydantic)")
    print("   - Automatic type checking for API requests")
    print("   - Ensures flow_id is string, context is dictionary")
    print("   - Occurs before custom validation code")

    print("\n🔹 Level 2: Structure Validation (FlowValidator)")
    print("   - Checks presence of required fields")
    print("   - Validates task and condition references")
    print("   - Ensures name uniqueness")

    print("\n🔹 Level 3: Logic Validation")
    print("   - Detects cycles in flow execution")
    print("   - Identifies unreachable tasks")
    print("   - Validates logical consistency")

    print("\n🔹 Level 4: Runtime Validation")
    print("   - Checks task function availability")
    print("   - Validates task results")
    print("   - Handles execution exceptions")


if __name__ == "__main__":
    print("🧪 Running comprehensive validation tests")

    test_valid_flow()
    test_invalid_flows()
    test_context_validation()
    test_edge_cases()
    demo_validation_levels()

    print("\n" + "=" * 50)
    print("🚀 To test API validation:")
    print("   1. python main.py  (in one terminal)")
    print("   2. python validation_examples.py api  (in another terminal)")
    print("=" * 50)

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "api":
        test_api_validation()