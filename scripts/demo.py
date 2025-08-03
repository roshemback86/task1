
import asyncio
from app.models.models import Flow
from app.core.flow_manager import FlowManager
from app.services.demo_tasks import TASK_FUNCTIONS

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


async def demo():
    """
    Demonstrate flow manager functionality.

    Creates a sample flow, registers it with the manager, executes it,
    and displays the results.
    """
    print("=== Flow Manager Demo ===")

    manager = FlowManager()

    flow = Flow.from_json(SAMPLE_FLOW_JSON)

    for task in flow.tasks:
        if task.name in TASK_FUNCTIONS:
            task.function = TASK_FUNCTIONS[task.name]

    manager.register_flow(flow)

    print("Executing flow...")
    execution = await manager.execute_flow("flow123")

    print(f"Execution ID: {execution.execution_id}")
    print(f"Status: {execution.status.value}")
    print(f"Task Results:")
    for task_name, result in execution.task_results.items():
        print(f"  {task_name}: {result.status.value} - {result.data}")
        if result.execution_time:
            print(f"    Execution time: {result.execution_time:.3f}s")

    print(f"Total execution time: {(execution.end_time - execution.start_time).total_seconds():.3f}s")


if __name__ == "__main__":
    asyncio.run(demo())