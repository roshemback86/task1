from fastapi import FastAPI, HTTPException
from app.models.models import Flow
from app.models.api_models import *
from app.services.demo_tasks import TASK_FUNCTIONS
from app.validators.validators import FlowValidator, ContextValidator, FlowValidationError
from app.core.flow_manager import FlowManager


def register_routes(app: FastAPI, flow_manager: FlowManager):
    @app.post("/flows", status_code=201, response_model=MessageResponse)
    async def create_flow(request: FlowCreateRequest):
        try:
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
        try:
            if request.context:
                ContextValidator.validate_execution_context(request.context)
            execution = await flow_manager.execute_flow(request.flow_id, request.context)
            task_results = {
                k: TaskResultResponse(
                    status=v.status.value,
                    data=v.data,
                    error=v.error,
                    execution_time=v.execution_time
                )
                for k, v in execution.task_results.items()
            }
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
        flow = flow_manager.get_flow(flow_id)
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        tasks = [TaskInfo(name=t.name, description=t.description) for t in flow.tasks]
        conditions = [ConditionInfo(
            name=c.name,
            description=c.description,
            source_task=c.source_task,
            outcome=c.outcome,
            target_task_success=c.target_task_success,
            target_task_failure=c.target_task_failure
        ) for c in flow.conditions]
        return FlowInfo(
            id=flow.id,
            name=flow.name,
            start_task=flow.start_task,
            tasks=tasks,
            conditions=conditions
        )

    @app.get("/executions/{execution_id}", response_model=FlowExecutionResponse)
    async def get_execution(execution_id: str):
        execution = flow_manager.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        task_results = {
            k: TaskResultResponse(
                status=v.status.value,
                data=v.data,
                error=v.error,
                execution_time=v.execution_time
            )
            for k, v in execution.task_results.items()
        }
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
        return HealthResponse(status="healthy", service="Flow Manager")
