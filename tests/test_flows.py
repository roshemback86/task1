
import pytest
from app.core.flow_manager import FlowManager
from app.models.models import Flow, Task, Condition, TaskStatus
from app.services.demo_tasks import TASK_FUNCTIONS


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
    
@pytest.mark.asyncio
async def test_flow_stops_on_task_failure():
    async def failing_task(context):
        raise Exception("Simulated failure")

    flow = Flow(
        id="fail_flow",
        name="Flow with failure",
        start_task="task1",
        tasks=[
            Task(name="task1", description="Failing", function=failing_task),
            Task(name="task2", description="Should not run", function=TASK_FUNCTIONS["task2"]),
        ],
        conditions=[
            Condition(
                name="cond_fail",
                description="task1 failure → end",
                source_task="task1",
                outcome="failure",
                target_task_success="task2",
                target_task_failure="end"
            )
        ]
    )

    manager = FlowManager()
    manager.register_flow(flow)
    result = await manager.execute_flow("fail_flow")

    assert result.status.value in ("completed", "failed")
    assert "task1" in result.task_results
    assert result.task_results["task1"].status.value == "failure"
    assert "task2" not in result.task_results
 
 
@pytest.mark.asyncio
async def test_flow_stops_on_task_failure():
    async def failing_task(_context):
        raise Exception("Simulated failure")

    flow = Flow(
        id="fail_flow",
        name="Flow with failure",
        start_task="task1",
        tasks=[
            Task(name="task1", description="Will fail", function=failing_task),
            Task(name="task2", description="Should not run", function=TASK_FUNCTIONS["task2"]),
        ],
        conditions=[
            Condition(
                name="cond_fail",
                description="Stop on failure",
                source_task="task1",
                outcome="success",
                target_task_success="task2",
                target_task_failure="end"  # critical: stop flow on failure
            )
        ]
    )

    manager = FlowManager()
    manager.register_flow(flow)

    result = await manager.execute_flow("fail_flow")

    # Assertions
    assert result.status == TaskStatus.FAILURE or result.status.value == "failed"
    assert "task1" in result.task_results
    assert result.task_results["task1"].status == TaskStatus.FAILURE
    assert "task2" not in result.task_results  # critical: task2 must not run
    
    
@pytest.mark.asyncio
async def test_flow_handles_failure_and_continues():
    async def failing_task(_context):
        raise Exception("Simulated failure")

    async def fallback_task(_context):
        return {"recovered": True}

    flow = Flow(
        id="fail_recover_flow",
        name="Failure with recovery",
        start_task="task1",
        tasks=[
            Task(name="task1", description="Fails", function=failing_task),
            Task(name="task2", description="Recovery path", function=fallback_task),
        ],
        conditions=[
            Condition(
                name="cond_handle_failure",
                description="Go to recovery if task1 fails",
                source_task="task1",
                outcome="success",
                target_task_success="end",
                target_task_failure="task2"
            )
        ]
    )

    manager = FlowManager()
    manager.register_flow(flow)

    result = await manager.execute_flow("fail_recover_flow")

    # Assertions
    assert result.status.value == "completed"
    assert "task1" in result.task_results
    assert result.task_results["task1"].status == TaskStatus.FAILURE
    assert "task2" in result.task_results
    assert result.task_results["task2"].status == TaskStatus.SUCCESS
    
    
@pytest.mark.asyncio
async def test_flow_with_task_without_function():
    async def processing_task(context):
        # Проверяем, что предыдущий результат передался
        assert "task1_result" in context
        return {"processed": True}

    flow = Flow(
        id="no_function_flow",
        name="Task with no function",
        start_task="task1",
        tasks=[
            Task(name="task1", description="No-op task (no function)"),
            Task(name="task2", description="Processing", function=processing_task),
        ],
        conditions=[
            Condition(
                name="cond_noop_to_process",
                description="task1 to task2 always",
                source_task="task1",
                outcome="success",
                target_task_success="task2",
                target_task_failure="end"
            )
        ]
    )

    manager = FlowManager()
    manager.register_flow(flow)

    result = await manager.execute_flow("no_function_flow")

    # Проверяем статус
    assert result.status.value == "completed"
    assert result.task_results["task1"].status == TaskStatus.SUCCESS
    assert result.task_results["task2"].status == TaskStatus.SUCCESS
    assert result.task_results["task2"].data["processed"] is True