# flow_manager.py
"""
Core flow management and orchestration engine.

This module provides the FlowManager class which handles flow registration,
execution orchestration, and state management for workflow instances.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from models import Flow, FlowExecution, FlowStatus, TaskStatus
from task_executor import TaskExecutor


class FlowManager:
    """
    Central orchestrator for workflow execution and state management.

    The FlowManager maintains a registry of available flows and manages
    their execution lifecycle, including task sequencing and condition evaluation.
    """

    def __init__(self):
        """Initialize the flow manager with empty registries."""
        self.flows: Dict[str, Flow] = {}
        self.executions: Dict[str, FlowExecution] = {}
        self.task_executor = TaskExecutor()

    def register_flow(self, flow: Flow) -> None:
        """
        Register a flow definition for execution.

        Args:
            flow: The flow definition to register
        """
        self.flows[flow.id] = flow

    async def execute_flow(self, flow_id: str, initial_context: Dict[str, Any] = None) -> FlowExecution:
        """
        Execute a registered flow with optional initial context.

        Args:
            flow_id: Identifier of the flow to execute
            initial_context: Optional initial data for the execution context

        Returns:
            FlowExecution instance tracking the execution state

        Raises:
            ValueError: If the specified flow is not found
        """
        if flow_id not in self.flows:
            raise ValueError(f"Flow {flow_id} not found")

        flow = self.flows[flow_id]
        execution = FlowExecution(
            flow_id=flow_id,
            context=initial_context or {},
            start_time=datetime.now()
        )

        self.executions[execution.execution_id] = execution
        execution.status = FlowStatus.RUNNING
        execution.current_task = flow.start_task

        try:
            while execution.current_task and execution.current_task != "end":
                current_task = None
                for task in flow.tasks:
                    if task.name == execution.current_task:
                        current_task = task
                        break

                if not current_task:
                    raise ValueError(f"Task {execution.current_task} not found")

                task_result = await self.task_executor.execute_task(current_task, execution.context)
                execution.task_results[current_task.name] = task_result

                execution.context[f"{current_task.name}_result"] = task_result.data

                next_task = "end"
                for condition in flow.conditions:
                    if condition.source_task == current_task.name:
                        next_task = condition.evaluate(task_result)
                        break

                execution.current_task = next_task

                if task_result.status == TaskStatus.FAILURE and next_task == "end":
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
        """
        Retrieve an execution instance by its identifier.

        Args:
            execution_id: Unique identifier of the execution

        Returns:
            FlowExecution instance or None if not found
        """
        return self.executions.get(execution_id)

    def get_flow(self, flow_id: str) -> Optional[Flow]:
        """
        Retrieve a flow definition by its identifier.

        Args:
            flow_id: Unique identifier of the flow

        Returns:
            Flow instance or None if not found
        """
        return self.flows.get(flow_id)