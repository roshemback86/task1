# test_client.py
"""
Test client for Flow Manager API endpoints.

This module provides comprehensive testing functionality for the Flow Manager
API, including basic functionality tests and stress testing capabilities.
"""

import requests
import json
import time
from typing import Dict, Any

SAMPLE_FLOW_JSON = {
    "flow": {
        "id": "flow123",
        "name": "Data processing flow",
        "start_task": "task1",
        "tasks": [
            {
                "name": "task1",
                "description": "Fetch data"
            },
            {
                "name": "task2",
                "description": "Process data"
            },
            {
                "name": "task3",
                "description": "Store data"
            }
        ],
        "conditions": [
            {
                "name": "condition_task1_result",
                "description": "Evaluate the result of task1. If successful, proceed to task2; otherwise, end the flow.",
                "source_task": "task1",
                "outcome": "success",
                "target_task_success": "task2",
                "target_task_failure": "end"
            },
            {
                "name": "condition_task2_result",
                "description": "Evaluate the result of task2. If successful, proceed to task3; otherwise, end the flow.",
                "source_task": "task2",
                "outcome": "success",
                "target_task_success": "task3",
                "target_task_failure": "end"
            }
        ]
    }
}


class FlowManagerClient:
    """HTTP client for Flow Manager API testing."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client with base URL.

        Args:
            base_url: Base URL of the Flow Manager API
        """
        self.base_url = base_url

    def create_flow(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new flow via API.

        Args:
            flow_data: Flow definition dictionary

        Returns:
            API response as dictionary
        """
        response = requests.post(
            f"{self.base_url}/flows",
            json={"flow_data": flow_data}
        )
        response.raise_for_status()
        return response.json()

    def execute_flow(self, flow_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a flow via API.

        Args:
            flow_id: Identifier of the flow to execute
            context: Optional execution context

        Returns:
            Execution result as dictionary
        """
        response = requests.post(
            f"{self.base_url}/flows/execute",
            json={"flow_id": flow_id, "context": context or {}}
        )
        response.raise_for_status()
        return response.json()

    def get_flow(self, flow_id: str) -> Dict[str, Any]:
        """
        Retrieve flow information via API.

        Args:
            flow_id: Identifier of the flow

        Returns:
            Flow information as dictionary
        """
        response = requests.get(f"{self.base_url}/flows/{flow_id}")
        response.raise_for_status()
        return response.json()

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """
        Retrieve execution status via API.

        Args:
            execution_id: Identifier of the execution

        Returns:
            Execution status as dictionary
        """
        response = requests.get(f"{self.base_url}/executions/{execution_id}")
        response.raise_for_status()
        return response.json()

    def health_check(self) -> Dict[str, Any]:
        """
        Check service health via API.

        Returns:
            Health status as dictionary
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


def test_api():
    """Execute comprehensive API functionality tests."""
    print("=== Testing Flow Manager API ===")

    client = FlowManagerClient()

    try:
        print("1. Testing health check...")
        health = client.health_check()
        print("✓ Health check passed:", health)

        print("\n2. Creating flow...")
        create_result = client.create_flow(SAMPLE_FLOW_JSON)
        print("✓ Flow created:", create_result)

        print("\n3. Getting flow information...")
        flow_info = client.get_flow("flow123")
        print("✓ Flow info retrieved:")
        print(f"   Name: {flow_info['name']}")
        print(f"   Tasks: {[t['name'] for t in flow_info['tasks']]}")

        print("\n4. Executing flow...")
        execution_result = client.execute_flow("flow123", {"user_id": "test_user"})
        print("✓ Flow executed:")
        print(f"   Execution ID: {execution_result['execution_id']}")
        print(f"   Status: {execution_result['status']}")

        print("\n5. Getting execution details...")
        execution_details = client.get_execution(execution_result['execution_id'])
        print("✓ Execution details:")
        print(f"   Status: {execution_details['status']}")
        print(f"   Task Results:")
        for task_name, result in execution_details['task_results'].items():
            print(f"     {task_name}: {result['status']} ({result['execution_time']:.3f}s)")
            if result['data']:
                print(f"       Data: {result['data']}")

        print("\n✓ All tests passed!")

    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to Flow Manager API")
        print("   Make sure the server is running: python main.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")


def stress_test():
    """Execute stress test with multiple concurrent executions."""
    print("=== Stress Test ===")

    client = FlowManagerClient()

    try:
        client.create_flow(SAMPLE_FLOW_JSON)

        num_executions = 5
        execution_ids = []

        print(f"Running {num_executions} concurrent executions...")
        start_time = time.time()

        for i in range(num_executions):
            result = client.execute_flow("flow123", {"batch_id": f"batch_{i}"})
            execution_ids.append(result['execution_id'])
            print(f"  Started execution {i + 1}: {result['execution_id']}")

        end_time = time.time()

        print("\nChecking execution results...")
        success_count = 0
        for exec_id in execution_ids:
            details = client.get_execution(exec_id)
            if details['status'] == 'completed':
                success_count += 1
                print(f"  ✓ {exec_id}: {details['status']}")
            else:
                print(f"  ❌ {exec_id}: {details['status']}")

        print(f"\nStress test results:")
        print(f"  Total executions: {num_executions}")
        print(f"  Successful: {success_count}")
        print(f"  Failed: {num_executions - success_count}")
        print(f"  Total time: {end_time - start_time:.2f}s")
        print(f"  Average time per execution: {(end_time - start_time) / num_executions:.2f}s")

    except Exception as e:
        print(f"❌ Stress test failed: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "test":
            test_api()
        elif command == "stress":
            stress_test()
        else:
            print("Available commands: test, stress")
    else:
        print("Usage: python test_client.py [test|stress]")
        print("\nCommands:")
        print("  test   - Run API tests")
        print("  stress - Run stress test")