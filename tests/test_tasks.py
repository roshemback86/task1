import pytest
from app.services.demo_tasks import TASK_FUNCTIONS


@pytest.mark.asyncio
async def test_task1():
    result = await TASK_FUNCTIONS["task1"]({})
    assert result is not None
    assert "users" in result
    assert isinstance(result["users"], list)


@pytest.mark.asyncio
async def test_task2():
    context = {
        "task1_result": {
            "users": [{"id": 1}, {"id": 2}]
        }
    }
    result = await TASK_FUNCTIONS["task2"](context)
    assert "processed_users" in result
    assert result["processed_users"] == 2


@pytest.mark.asyncio
async def test_task3():
    context = {
        "task2_result": {
            "processed_users": 2
        }
    }
    result = await TASK_FUNCTIONS["task3"](context)
    assert result["stored"] is True
    assert "record_id" in result