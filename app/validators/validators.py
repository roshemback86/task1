from typing import Dict, Any, List, Set
from app.models.models import Flow


class FlowValidationError(Exception):
    """Custom error raised when flow validation fails."""
    pass


class FlowValidator:
    """Performs validation of flow structure, content, and logic."""

    @staticmethod
    def validate_flow_structure(flow_data: Dict[str, Any]) -> None:
        """Check that the flow has all required top-level fields."""
        if "flow" not in flow_data:
            raise FlowValidationError("Missing 'flow' key in flow_data")

        flow_info = flow_data["flow"]
        required_fields = ["id", "name", "start_task", "tasks", "conditions"]

        for field in required_fields:
            if field not in flow_info:
                raise FlowValidationError(f"Missing required field: '{field}'")

        if not isinstance(flow_info["id"], str) or not flow_info["id"].strip():
            raise FlowValidationError("Field 'id' must be a non-empty string")

        if not isinstance(flow_info["name"], str) or not flow_info["name"].strip():
            raise FlowValidationError("Field 'name' must be a non-empty string")

        if not isinstance(flow_info["start_task"], str) or not flow_info["start_task"].strip():
            raise FlowValidationError("Field 'start_task' must be a non-empty string")

        if not isinstance(flow_info["tasks"], list) or len(flow_info["tasks"]) == 0:
            raise FlowValidationError("Field 'tasks' must be a non-empty list")

        if not isinstance(flow_info["conditions"], list):
            raise FlowValidationError("Field 'conditions' must be a list")

    @staticmethod
    def validate_tasks(tasks_data: List[Dict[str, Any]]) -> None:
        """Ensure tasks are valid and unique."""
        task_names = set()

        for i, task in enumerate(tasks_data):
            if not isinstance(task, dict):
                raise FlowValidationError(f"Task {i} must be a dictionary")

            if "name" not in task or "description" not in task:
                raise FlowValidationError(f"Task {i} must have 'name' and 'description' fields")

            if not isinstance(task["name"], str) or not task["name"].strip():
                raise FlowValidationError(f"Task {i} 'name' must be a non-empty string")

            if not isinstance(task["description"], str):
                raise FlowValidationError(f"Task {i} 'description' must be a string")

            if task["name"] in task_names:
                raise FlowValidationError(f"Duplicate task name: '{task['name']}'")

            task_names.add(task["name"])

    @staticmethod
    def validate_conditions(conditions_data: List[Dict[str, Any]], task_names: Set[str], start_task: str) -> None:
        """Ensure conditions reference valid tasks and are structurally correct."""
        for i, condition in enumerate(conditions_data):
            if not isinstance(condition, dict):
                raise FlowValidationError(f"Condition {i} must be a dictionary")

            required_fields = ["name", "source_task", "outcome", "target_task_success", "target_task_failure"]
            for field in required_fields:
                if field not in condition:
                    raise FlowValidationError(f"Condition {i} missing field: '{field}'")

            for field in required_fields:
                if not isinstance(condition[field], str) or not condition[field].strip():
                    raise FlowValidationError(f"Condition {i} field '{field}' must be a non-empty string")

            if condition["source_task"] not in task_names:
                raise FlowValidationError(f"Condition {i} uses unknown source_task: '{condition['source_task']}'")

            if condition["outcome"] not in ["success", "failure"]:
                raise FlowValidationError(
                    f"Condition {i} has invalid outcome: '{condition['outcome']}' "
                    f"(expected 'success' or 'failure')"
                )

            for target_field in ["target_task_success", "target_task_failure"]:
                target_task = condition[target_field]
                if target_task != "end" and target_task not in task_names:
                    raise FlowValidationError(f"Condition {i} uses unknown {target_field}: '{target_task}'")

    @staticmethod
    def validate_flow_logic(flow: Flow) -> None:
        """Check for cycles and unreachable tasks."""
        task_names = {task.name for task in flow.tasks}

        if flow.start_task not in task_names:
            raise FlowValidationError(f"start_task '{flow.start_task}' not found in tasks")

        FlowValidator._check_for_cycles(flow)
        FlowValidator._check_task_reachability(flow)

    @staticmethod
    def _check_for_cycles(flow: Flow) -> None:
        """Detect cycles using DFS."""
        transitions = {}
        for condition in flow.conditions:
            src = condition.source_task
            transitions.setdefault(src, [])

            if condition.target_task_success != "end":
                transitions[src].append(condition.target_task_success)
            if condition.target_task_failure != "end":
                transitions[src].append(condition.target_task_failure)

        visited = set()
        rec_stack = set()

        def visit(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            for next_task in transitions.get(node, []):
                if visit(next_task):
                    return True

            rec_stack.remove(node)
            return False

        if visit(flow.start_task):
            raise FlowValidationError("Flow contains a cycle in task transitions")

    @staticmethod
    def _check_task_reachability(flow: Flow) -> None:
        """Ensure that all tasks can be reached from the start."""
        transitions = {}
        for condition in flow.conditions:
            src = condition.source_task
            transitions.setdefault(src, [])
            if condition.target_task_success != "end":
                transitions[src].append(condition.target_task_success)
            if condition.target_task_failure != "end":
                transitions[src].append(condition.target_task_failure)

        reachable = set()
        stack = [flow.start_task]

        while stack:
            current = stack.pop()
            if current in reachable:
                continue

            reachable.add(current)
            stack.extend(transitions.get(current, []))

        all_tasks = {task.name for task in flow.tasks}
        unreachable = all_tasks - reachable

        if unreachable:
            print(f"Warning: unreachable tasks: {unreachable}")

    @classmethod
    def validate_complete_flow(cls, flow_data: Dict[str, Any]) -> None:
        """Run full validation: structure, task/condition integrity, and logic."""
        cls.validate_flow_structure(flow_data)

        flow_info = flow_data["flow"]
        cls.validate_tasks(flow_info["tasks"])

        task_names = {task["name"] for task in flow_info["tasks"]}
        cls.validate_conditions(flow_info["conditions"], task_names, flow_info["start_task"])

        try:
            flow = Flow.from_dict(flow_info)
        except Exception as e:
            raise FlowValidationError(f"Failed to build Flow model: {e}")

        cls.validate_flow_logic(flow)


class ContextValidator:
    """Basic validation for execution context."""

    @staticmethod
    def validate_execution_context(context: Dict[str, Any]) -> None:
        """Make sure context is a flat dict with string keys and reasonable size."""
        if not isinstance(context, dict):
            raise FlowValidationError("Context must be a dictionary")

        for key in context:
            if not isinstance(key, str):
                raise FlowValidationError(f"Context key must be a string. Got: {type(key)}")

        import json
        size = len(json.dumps(context, default=str))
        if size > 1024 * 1024:
            raise FlowValidationError(f"Context too large: {size} bytes (max 1MB)")


if __name__ == "__main__":
    valid_flow = {
        "flow": {
            "id": "test_flow",
            "name": "Test Flow",
            "start_task": "task1",
            "tasks": [
                {"name": "task1", "description": "First task"},
                {"name": "task2", "description": "Second task"}
            ],
            "conditions": [
                {
                    "name": "condition1",
                    "description": "Test condition",
                    "source_task": "task1",
                    "outcome": "success",
                    "target_task_success": "task2",
                    "target_task_failure": "end"
                }
            ]
        }
    }

    try:
        FlowValidator.validate_complete_flow(valid_flow)
        print("Flow validation passed")
    except FlowValidationError as e:
        print(f"Flow validation failed: {e}")

    invalid_flow = {
        "flow": {
            "id": "test_flow",
            "name": "Test Flow",
            "start_task": "task1",
            "tasks": [
                {"name": "task1", "description": "First task"},
                {"name": "task1", "description": "Duplicate task"}
            ],
            "conditions": []
        }
    }

    try:
        FlowValidator.validate_complete_flow(invalid_flow)
        print("Flow validation passed")
    except FlowValidationError as e:
        print(f"Flow validation failed: {e}")