import pytest
from app.core.flow_manager import FlowManager
from app.models.models import Flow, Task, Condition
from app.services.demo_tasks import TASK_FUNCTIONS

@pytest.mark.asyncio
async def test_generic_flow_mapping():
    flow = Flow(
        id="generic_flow",
        name="Generic Flow",
        start_task="task1",
        tasks=[
            Task(name="task1", description="Fetch data from API", function_name="fetch_data"),
            Task(name="task2", description="Process data"),
            Task(name="task3", description="Store in DB")
        ],
        conditions=[
            Condition(
                name="c1", source_task="task1", outcome="success",
                target_task_success="task2", target_task_failure="end",
                description="t1→t2"
            ),
            Condition(
                name="c2", source_task="task2", outcome="success",
                target_task_success="task3", target_task_failure="end",
                description="t2→t3"
            )
        ]
    )

    manager = FlowManager()
    manager.register_flow(flow)

    result = await manager.execute_flow("generic_flow")
    assert result.status.value == "completed"
    assert list(result.task_results.keys()) == ["task1", "task2", "task3"]