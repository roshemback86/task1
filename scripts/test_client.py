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
            {"name": "task1", "description": "Fetch data"},
            {"name": "task2", "description": "Process data"},
            {"name": "task3", "description": "Store data"}
        ],
        "conditions": [
            {
                "name": "condition_task1_result",
                "description": "If task1 is successful, go to task2. Otherwise, end.",
                "source_task": "task1",
                "outcome": "success",
                "target_task_success": "task2",
                "target_task_failure": "end"
            },
            {
                "name": "condition_task2_result",
                "description": "If task2 is successful, go to task3. Otherwise, end.",
                "source_task": "task2",
                "outcome": "success",
                "target_task_success": "task3",
                "target_task_failure": "end"
            }
        ]
    }
}


class FlowManagerClient:
    """Basic HTTP client for interacting with the Flow Manager API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def create_flow(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a new flow definition to the API."""
        response = requests.post(f"{self.base_url}/flows", json={"flow_data": flow_data})
        response.raise_for_status()
        return response.json()

    def execute_flow(self, flow_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Trigger a registered flow to execute."""
        response = requests.post(
            f"{self.base_url}/flows/execute",
            json={"flow_id": flow_id, "context": context or {}}
        )
        response.raise_for_status()
        return response.json()

    def get_flow(self, flow_id: str) -> Dict[str, Any]:
        """Fetch flow metadata by ID."""
        response = requests.get(f"{self.base_url}/flows/{flow_id}")
        response.raise_for_status()
        return response.json()

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """Get details of a specific flow execution."""
        response = requests.get(f"{self.base_url}/executions/{execution_id}")
        response.raise_for_status()
        return response.json()

    def health_check(self) -> Dict[str, Any]:
        """Check if the API service is running."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


def test_api():
    """Run basic checks against the Flow Manager API."""
    print("=== Testing Flow Manager API ===")

    client = FlowManagerClient()

    try:
        print("1. Health check")
        print("   Service:", client.health_check())

        print("2. Creating flow")
        print("   Response:", client.create_flow(SAMPLE_FLOW_JSON))

        print("3. Fetching flow details")
        flow = client.get_flow("flow123")
        print("   Name:", flow['name'])
        print("   Tasks:", [t['name'] for t in flow['tasks']])

        print("4. Executing flow")
        exec_result = client.execute_flow("flow123", {"user_id": "tester"})
        print("   Execution ID:", exec_result["execution_id"])
        print("   Status:", exec_result["status"])

        print("5. Fetching execution results")
        result = client.get_execution(exec_result["execution_id"])
        print("   Status:", result["status"])
        for task_name, task in result["task_results"].items():
            print(f"   {task_name}: {task['status']} ({task['execution_time']:.3f}s)")
            if task["data"]:
                print(f"     Data: {task['data']}")

        print("Test run finished.")

    except requests.exceptions.ConnectionError:
        print("Connection failed. Make sure the server is running.")
    except Exception as e:
        print("Test failed:", e)


def stress_test():
    """Run multiple executions in sequence to test API under load."""
    print("=== Stress Test ===")

    client = FlowManagerClient()

    try:
        client.create_flow(SAMPLE_FLOW_JSON)

        count = 5
        ids = []

        print(f"Running {count} executions...")
        start = time.time()

        for i in range(count):
            result = client.execute_flow("flow123", {"run_id": f"run_{i}"})
            ids.append(result["execution_id"])
            print(f"  Started: {result['execution_id']}")

        end = time.time()

        print("\nChecking results...")
        ok = 0
        for exec_id in ids:
            res = client.get_execution(exec_id)
            status = res["status"]
            print(f"  {exec_id}: {status}")
            if status == "completed":
                ok += 1

        duration = end - start
        print(f"\nFinished {count} runs in {duration:.2f} sec")
        print(f"Successful: {ok}, Failed: {count - ok}")

    except Exception as e:
        print("Stress test failed:", e)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_api()
        elif sys.argv[1] == "stress":
            stress_test()
        else:
            print("Unknown command. Use: test | stress")
    else:
        print("Usage:")
        print("  python test_client.py test    # Run API tests")
        print("  python test_client.py stress  # Run stress test")