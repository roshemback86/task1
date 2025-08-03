from typing import Dict, Any, Optional
from pydantic import BaseModel


class FlowCreateRequest(BaseModel):
    # Payload when creating a new flow
    flow_data: Dict[str, Any]


class FlowExecuteRequest(BaseModel):
    # Payload for executing an existing flow
    flow_id: str
    context: Optional[Dict[str, Any]] = None


class TaskResultResponse(BaseModel):
    # Info about a single task execution result
    status: str
    data: Any = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class FlowExecutionResponse(BaseModel):
    # Full response after running a flow
    execution_id: str
    flow_id: str
    status: str
    current_task: Optional[str]
    task_results: Dict[str, TaskResultResponse]
    start_time: Optional[str]
    end_time: Optional[str]
    context: Dict[str, Any]


class TaskInfo(BaseModel):
    # Basic info about a task in a flow
    name: str
    description: str


class ConditionInfo(BaseModel):
    # How tasks connect depending on outcomes
    name: str
    description: str
    source_task: str
    outcome: str
    target_task_success: str
    target_task_failure: str


class FlowInfo(BaseModel):
    # Full metadata for a flow definition
    id: str
    name: str
    start_task: str
    tasks: list[TaskInfo]
    conditions: list[ConditionInfo]


class HealthResponse(BaseModel):
    # Response format for /health endpoint
    status: str
    service: str


class MessageResponse(BaseModel):
    # Generic message format for responses
    message: str