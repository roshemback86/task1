# main.py
"""
FastAPI application entry point for the Flow Manager service.

This module provides the REST API interface for flow management operations,
including flow creation, execution, and status monitoring.
"""

from fastapi import FastAPI, HTTPException
from models import Flow
from flow_manager import FlowManager
from demo_tasks import TASK_FUNCTIONS
from api_models import (
    FlowCreateRequest, FlowExecuteRequest, FlowExecutionResponse,
    FlowInfo, TaskInfo, ConditionInfo, HealthResponse, MessageResponse,
    TaskResultResponse
)

app = FastAPI(title="Flow Manager API", version="1.0.0")
flow_manager = FlowManager()


@app.post("/flows", status_code=201, response_model=MessageResponse)
async def create_flow(request: FlowCreateRequest):
    """
    Create and register a new flow definition.

    Args:
        request: Flow creation request containing flow definition

    Returns:
        Success message with flow ID

    Raises:
        HTTPException: 400 for validation errors, 500 for internal errors
    """
    try:
        from validators import FlowValidator, FlowValidationError

        flow = Flow.from_json(request.flow_data)

        for task in flow.tasks:
            if task.name in TASK_FUNCTIONS:
                task.function = TASK_FUNCTIONS[task.name]

        flow_manager.register_flow(flow)
        return MessageResponse(message=f"Flow {flow.id} created successfully")

    except FlowValidationError as e:
        raise HTTPException(status_code=400, detail=f"Flow validation error: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid flow data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/flows/execute", response_model=FlowExecutionResponse)
async def execute_flow(request: FlowExecuteRequest):
    """
    Execute a registered flow with optional context.

    Args:
        request: Flow execution request with flow ID and context

    Returns:
        Complete execution status and results

    Raises:
        HTTPException: 400 for validation errors, 404 for missing flow, 500 for internal errors
    """
    try:
        if request.context:
            from validators import ContextValidator, FlowValidationError
            ContextValidator.validate_execution_context(request.context)

        execution = await flow_manager.execute_flow(request.flow_id, request.context)

        task_results = {}
        for k, v in execution.task_results.items():
            task_results[k] = TaskResultResponse(
                status=v.status.value,
                data=v.data,
                error=v.error,
                execution_time=v.execution_time
            )

        return FlowExecutionResponse(
            execution_id=execution.execution_id,
            flow_id=execution.flow_id,
            status=execution.status.value,
            current_task=execution.current_task,
            task_results=task_results,
            start_time=execution.start_time.isoformat() if execution.start_time else None,
            end_time=execution.end_time.isoformat() if execution.end_time else None,
            context=execution.context
        )

    except FlowValidationError as e:
        raise HTTPException(status_code=400, detail=f"Context validation error: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/flows/{flow_id}", response_model=FlowInfo)
async def get_flow(flow_id: str):
    """
    Retrieve flow definition by ID.

    Args:
        flow_id: Unique identifier of the flow

    Returns:
        Complete flow definition including tasks and conditions

    Raises:
        HTTPException: 404 if flow not found
    """
    flow = flow_manager.get_flow(flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")

    tasks = [TaskInfo(name=t.name, description=t.description) for t in flow.tasks]
    conditions = [
        ConditionInfo(
            name=c.name,
            description=c.description,
            source_task=c.source_task,
            outcome=c.outcome,
            target_task_success=c.target_task_success,
            target_task_failure=c.target_task_failure
        ) for c in flow.conditions
    ]

    return FlowInfo(
        id=flow.id,
        name=flow.name,
        start_task=flow.start_task,
        tasks=tasks,
        conditions=conditions
    )


@app.get("/executions/{execution_id}", response_model=FlowExecutionResponse)
async def get_execution(execution_id: str):
    """
    Retrieve execution status and results by ID.

    Args:
        execution_id: Unique identifier of the execution

    Returns:
        Complete execution status including task results and timing

    Raises:
        HTTPException: 404 if execution not found
    """
    execution = flow_manager.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    task_results = {}
    for k, v in execution.task_results.items():
        task_results[k] = TaskResultResponse(
            status=v.status.value,
            data=v.data,
            error=v.error,
            execution_time=v.execution_time
        )

    return FlowExecutionResponse(
        execution_id=execution.execution_id,
        flow_id=execution.flow_id,
        status=execution.status.value,
        current_task=execution.current_task,
        task_results=task_results,
        start_time=execution.start_time.isoformat() if execution.start_time else None,
        end_time=execution.end_time.isoformat() if execution.end_time else None,
        context=execution.context
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for service monitoring.

    Returns:
        Service health status
    """
    return HealthResponse(status="healthy", service="Flow Manager")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)