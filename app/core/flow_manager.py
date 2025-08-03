from typing import Dict, Any, Optional
from datetime import datetime
from app.models.models import Flow, FlowExecution, FlowStatus, TaskStatus
from app.services.task_executor import TaskExecutor


class FlowManager:
    def __init__(self):
        self.flows: Dict[str, Flow] = {}
        self.executions: Dict[str, FlowExecution] = {}
        self.task_executor = TaskExecutor()

    def register_flow(self, flow: Flow) -> None:
        self.flows[flow.id] = flow

    async def execute_flow(self, flow_id: str, context: Dict[str, Any] = None) -> FlowExecution:
        if flow_id not in self.flows:
            raise ValueError(f"Flow '{flow_id}' not found")

        flow = self.flows[flow_id]
        context = context or {}

        execution = FlowExecution(
            flow_id=flow_id,
            context=context,
            start_time=datetime.now(),
            status=FlowStatus.RUNNING,
            current_task=flow.start_task
        )

        self.executions[execution.execution_id] = execution

        try:
            while execution.current_task and execution.current_task != "end":
                task = next((t for t in flow.tasks if t.name == execution.current_task), None)
                if not task:
                    raise ValueError(f"Task '{execution.current_task}' not found in flow")

                # Execute the current task
                result = await self.task_executor.execute_task(task, execution.context)

                # Save the result and store it in the context
                execution.task_results[task.name] = result
                execution.context[f"{task.name}_result"] = result.data

                # Find the next task based on conditions
                next_task = "end"
                for cond in flow.conditions:
                    if cond.source_task == task.name:
                        next_task = cond.evaluate(result)
                        break

                execution.current_task = next_task

                # If the task failed and there is no next step — mark flow as failed
                if result.status == TaskStatus.FAILURE and next_task == "end":
                    execution.status = FlowStatus.FAILED
                    break

            if execution.status == FlowStatus.RUNNING:
                execution.status = FlowStatus.COMPLETED

        except Exception as e:
            execution.status = FlowStatus.FAILED
            execution.context["error"] = str(e)
        finally:
            execution.end_time = datetime.now()

        return execution

    def get_execution(self, execution_id: str) -> Optional[FlowExecution]:
        return self.executions.get(execution_id)

    def get_flow(self, flow_id: str) -> Optional[Flow]:
        return self.flows.get(flow_id)