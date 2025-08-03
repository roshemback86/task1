import pytest
from app.validators.validators import FlowValidator, FlowValidationError

def test_cycle_detection():
    """Test that a flow with a cycle raises a FlowValidationError."""
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

    with pytest.raises(FlowValidationError, match="cycle in task transitions"):
        FlowValidator.validate_complete_flow(cyclic_flow)


def test_unreachable_tasks_warning(capfd):
    """Test that unreachable tasks trigger a printed warning."""
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

    FlowValidator.validate_complete_flow(unreachable_flow)

    captured = capfd.readouterr()
    assert "unreachable tasks" in captured.out.lower()