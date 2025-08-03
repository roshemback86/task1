from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime


class TaskStatus(Enum):
    # Current state of a task during execution
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"


class FlowStatus(Enum):
    # Overall state of a flow execution
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskResult:
    # Result of a single task run
    status: TaskStatus
    data: Any = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


@dataclass
class Task:
    # Defines a task that can be executed in a flow
    name: str
    description: str
    function: Optional[Callable] = None


@dataclass
class Condition:
    # Controls flow between tasks depending on result
    name: str
    description: str
    source_task: str
    outcome: str
    target_task_success: str
    target_task_failure: str

    def evaluate(self, task_result: TaskResult) -> str:
        # Decide next task based on task result
        if self.outcome == "success" and task_result.status == TaskStatus.SUCCESS:
            return self.target_task_success
        elif self.outcome == "failure" and task_result.status == TaskStatus.FAILURE:
            return self.target_task_success
        return self.target_task_failure


@dataclass
class FlowExecution:
    # Tracks the progress of a running flow
    flow_id: str
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: FlowStatus = FlowStatus.PENDING
    current_task: Optional[str] = None
    task_results: Dict[str, TaskResult] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Flow:
    # Defines a full workflow with tasks and conditions
    id: str
    name: str
    start_task: str
    tasks: List[Task]
    conditions: List[Condition]

    @classmethod
    def from_json(cls, flow_data: Dict[str, Any]) -> 'Flow':
        # Parse and validate flow definition from JSON-like dict
        try:
            from app.validators.validators import FlowValidator
            FlowValidator.validate_complete_flow(flow_data)
        except ImportError:
            if "flow" not in flow_data:
                raise ValueError("Missing 'flow' key in flow_data")

        flow_info = flow_data["flow"]

        tasks = []
        for task in flow_info["tasks"]:
            if "name" not in task or "description" not in task:
                raise ValueError("Task must have 'name' and 'description'")
            tasks.append(Task(name=task["name"], description=task["description"]))

        conditions = []
        for cond in flow_info["conditions"]:
            required_fields = ["name", "description", "source_task", "outcome",
                               "target_task_success", "target_task_failure"]
            for field in required_fields:
                if field not in cond:
                    raise ValueError(f"Condition missing required field: {field}")

            conditions.append(Condition(
                name=cond["name"],
                description=cond["description"],
                source_task=cond["source_task"],
                outcome=cond["outcome"],
                target_task_success=cond["target_task_success"],
                target_task_failure=cond["target_task_failure"]
            ))

        return cls(
            id=flow_info["id"],
            name=flow_info["name"],
            start_task=flow_info["start_task"],
            tasks=tasks,
            conditions=conditions
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Flow":
        # Simpler version for creating flow from already parsed dict
        tasks = [Task(**task_data) for task_data in data.get("tasks", [])]
        conditions = [Condition(**cond_data) for cond_data in data.get("conditions", [])]

        return cls(
            id=data["id"],
            name=data["name"],
            start_task=data["start_task"],
            tasks=tasks,
            conditions=conditions
        )