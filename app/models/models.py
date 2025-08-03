# models.py
"""
Core data models for the Flow Manager system.

This module defines the primary data structures used throughout the application,
including Flow, Task, Condition, and execution tracking models.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime


class TaskStatus(Enum):
    """Enumeration of possible task execution states."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"


class FlowStatus(Enum):
    """Enumeration of possible flow execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskResult:
    """
    Container for task execution results.

    Attributes:
        status: Current execution status of the task
        data: Result data returned by the task function
        error: Error message if task failed
        execution_time: Time taken to execute the task in seconds
    """
    status: TaskStatus
    data: Any = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


@dataclass
class Task:
    """
    Represents a single executable task within a flow.

    Attributes:
        name: Unique identifier for the task
        description: Human-readable description of the task
        function: Optional async function to execute for this task
    """
    name: str
    description: str
    function: Optional[Callable] = None


@dataclass
class Condition:
    """
    Defines conditional logic for flow control between tasks.

    Attributes:
        name: Unique identifier for the condition
        description: Human-readable description of the condition
        source_task: Name of the task this condition evaluates
        outcome: Expected task outcome ('success' or 'failure')
        target_task_success: Next task to execute if condition matches
        target_task_failure: Next task to execute if condition doesn't match
    """
    name: str
    description: str
    source_task: str
    outcome: str
    target_task_success: str
    target_task_failure: str

    def evaluate(self, task_result: TaskResult) -> str:
        """
        Evaluate the condition against a task result.

        Args:
            task_result: The result of the source task execution

        Returns:
            Name of the next task to execute or 'end' to terminate flow
        """
        if self.outcome == "success" and task_result.status == TaskStatus.SUCCESS:
            return self.target_task_success
        elif self.outcome == "failure" and task_result.status == TaskStatus.FAILURE:
            return self.target_task_success
        else:
            return self.target_task_failure


@dataclass
class FlowExecution:
    """
    Tracks the state and progress of a flow execution instance.

    Attributes:
        flow_id: Identifier of the flow being executed
        execution_id: Unique identifier for this execution instance
        status: Current execution status
        current_task: Name of the currently executing task
        task_results: Dictionary of completed task results
        start_time: Timestamp when execution began
        end_time: Timestamp when execution completed
        context: Shared data context for task communication
    """
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
    """
    Defines a complete workflow with tasks and conditional logic.

    Attributes:
        id: Unique identifier for the flow
        name: Human-readable name for the flow
        start_task: Name of the first task to execute
        tasks: List of all tasks in the flow
        conditions: List of conditional transitions between tasks
    """
    id: str
    name: str
    start_task: str
    tasks: List[Task]
    conditions: List[Condition]

    @classmethod
    def from_json(cls, flow_data: Dict[str, Any]) -> 'Flow':
        """
        Create a Flow instance from JSON data with validation.

        Args:
            flow_data: Dictionary containing flow definition

        Returns:
            Validated Flow instance

        Raises:
            ValueError: If flow data is invalid or validation fails
        """
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
        """
        Create a Flow instance from a dictionary (e.g. parsed JSON).
    
        Args:
            data: Dictionary containing flow structure
    
        Returns:
            Flow instance
        """
        tasks = [Task(**task_data) for task_data in data.get("tasks", [])]
        conditions = [Condition(**cond_data) for cond_data in data.get("conditions", [])]
    
        return cls(
            id=data["id"],
            name=data["name"],
            start_task=data["start_task"],
            tasks=tasks,
            conditions=conditions
        )