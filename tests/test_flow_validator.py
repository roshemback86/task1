import pytest
from app.validators.validators import FlowValidator, FlowValidationError


@pytest.mark.parametrize("flow_data,should_pass", [
    (
        {
            "flow": {
                "id": "valid_flow",
                "name": "Valid Flow",
                "start_task": "task1",
                "tasks": [
                    {"name": "task1", "description": "First task"},
                    {"name": "task2", "description": "Second task"}
                ],
                "conditions": [
                    {
                        "name": "condition1",
                        "description": "Go from task1 to task2",
                        "source_task": "task1",
                        "outcome": "success",
                        "target_task_success": "task2",
                        "target_task_failure": "end"
                    }
                ]
            }
        },
        True
    ),
    (
        {
            "flow": {
                "id": "missing_name",
                "start_task": "task1",
                "tasks": [{"name": "task1", "description": "Task 1"}],
                "conditions": []
            }
        },
        False  # Missing 'name'
    ),
    (
        {
            "flow": {
                "id": "duplicate_tasks",
                "name": "Has Duplicates",
                "start_task": "task1",
                "tasks": [
                    {"name": "task1", "description": "Duplicate 1"},
                    {"name": "task1", "description": "Duplicate 2"}
                ],
                "conditions": []
            }
        },
        False  # Duplicate task names
    ),
    (
        {
            "flow": {
                "id": "invalid_condition_reference",
                "name": "Invalid Reference",
                "start_task": "task1",
                "tasks": [{"name": "task1", "description": "Task 1"}],
                "conditions": [
                    {
                        "name": "bad_cond",
                        "description": "Points to missing task",
                        "source_task": "task1",
                        "outcome": "success",
                        "target_task_success": "task_missing",
                        "target_task_failure": "end"
                    }
                ]
            }
        },
        False  # Condition references nonexistent target
    ),
    (
        {
            "flow": {
                "id": "invalid_outcome",
                "name": "Bad Outcome",
                "start_task": "task1",
                "tasks": [{"name": "task1", "description": "Task 1"}],
                "conditions": [
                    {
                        "name": "bad_outcome",
                        "description": "Unknown outcome",
                        "source_task": "task1",
                        "outcome": "maybe",
                        "target_task_success": "end",
                        "target_task_failure": "end"
                    }
                ]
            }
        },
        False  # Invalid outcome value
    ),
])
def test_flow_validator(flow_data, should_pass):
    if should_pass:
        try:
            FlowValidator.validate_complete_flow(flow_data)
        except Exception:
            pytest.fail("Validation was expected to pass but failed.")
    else:
        with pytest.raises(FlowValidationError):
            FlowValidator.validate_complete_flow(flow_data)