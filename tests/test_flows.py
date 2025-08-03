# tests/test_flows.py

import pytest
from flow_manager import FlowManager
from models import Flow, Task, Condition
from demo_tasks import TASK_FUNCTIONS


@pytest.fixture
def flow_ok():
    return Flow(
        id="test_flow",
        name="Simple Flow",
        start_task="task1",
        tasks=[
            Task(name="task1", description="Fetch", function=TASK_FUNCTIONS["task1"]),
            Task(name="task2", description="Process", function=TASK_FUNCTIONS["task2"]),
            Task(name="task3", description="Store", function=TASK_FUNCTIONS["task3"]),
        ],
        conditions=[
            Condition(
                name="cond1",
                description="task1 success → task2",
                source_task="task1",
                outcome="success",
                target_task_success="task2",
                target_task_failure="end"
            ),
            Condition(
                name="cond2",
                description="task2 success → task3",
                source_task="task2",
                outcome="success",
                target_task_success="task3",
                target_task_failure="end"
            )
        ]
    )


@pytest.mark.asyncio
async def test_execute_success_flow(flow_ok):
    manager = FlowManager()
    manager.register_flow(flow_ok)

    result = await manager.execute_flow("test_flow")
    assert result.status.value == "completed"
    assert list(result.task_results.keys()) == ["task1", "task2", "task3"]
    assert all(tr.status.value == "success" for tr in result.task_results.values())