import asyncio
from app.models.models import Flow
from app.core.flow_manager import FlowManager
from app.services.demo_tasks import TASK_FUNCTIONS

# Sample flow definition used for demonstration
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
                "description": "If task1 succeeds, go to task2. Otherwise, end the flow.",
                "source_task": "task1",
                "outcome": "success",
                "target_task_success": "task2",
                "target_task_failure": "end"
            },
            {
                "name": "condition_task2_result",
                "description": "If task2 succeeds, go to task3. Otherwise, end the flow.",
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
    Runs a complete example of a flow execution:
    - Loads a predefined flow
    - Registers it with the manager
    - Executes the flow
    - Prints execution status and results
    """
    print("=== Flow Manager Demo ===")

    manager = FlowManager()

    # Parse the flow definition
    flow = Flow.from_json(SAMPLE_FLOW_JSON)

    # Attach actual functions to tasks
    for task in flow.tasks:
        if task.name in TASK_FUNCTIONS:
            task.function = TASK_FUNCTIONS[task.name]

    # Register the flow
    manager.register_flow(flow)

    print("Executing flow...")
    execution = await manager.execute_flow("flow123")

    # Output execution results
    print(f"\nExecution ID: {execution.execution_id}")
    print(f"Status: {execution.status.value}")
    print("Task Results:")
    for task_name, result in execution.task_results.items():
        print(f"  {task_name}: {result.status.value}")
        if result.data:
            print(f"    Output: {result.data}")
        if result.execution_time:
            print(f"    Time: {result.execution_time:.3f} sec")

    if execution.start_time and execution.end_time:
        duration = (execution.end_time - execution.start_time).total_seconds()
        print(f"\nTotal execution time: {duration:.3f} sec")


if __name__ == "__main__":
    asyncio.run(demo())