# api_models.py
"""
Pydantic models for API request and response validation.

This module defines the data structures used for API communication,
providing automatic validation and serialization for HTTP endpoints.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class FlowCreateRequest(BaseModel):
    """Request model for flow creation endpoint."""
    flow_data: Dict[str, Any]


class FlowExecuteRequest(BaseModel):
    """Request model for flow execution endpoint."""
    flow_id: str
    context: Optional[Dict[str, Any]] = None


class TaskResultResponse(BaseModel):
    """Response model for individual task execution results."""
    status: str
    data: Any = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class FlowExecutionResponse(BaseModel):
    """Response model for flow execution status and results."""
    execution_id: str
    flow_id: str
    status: str
    current_task: Optional[str]
    task_results: Dict[str, TaskResultResponse]
    start_time: Optional[str]
    end_time: Optional[str]
    context: Dict[str, Any]


class TaskInfo(BaseModel):
    """Response model for task information."""
    name: str
    description: str


class ConditionInfo(BaseModel):
    """Response model for condition information."""
    name: str
    description: str
    source_task: str
    outcome: str
    target_task_success: str
    target_task_failure: str


class FlowInfo(BaseModel):
    """Response model for complete flow information."""
    id: str
    name: str
    start_task: str
    tasks: list[TaskInfo]
    conditions: list[ConditionInfo]


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    service: str


class MessageResponse(BaseModel):
    """Generic response model for simple message responses."""
    message: str