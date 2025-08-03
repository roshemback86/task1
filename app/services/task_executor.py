# task_executor.py
"""
Task execution engine for the Flow Manager system.

This module handles the actual execution of individual tasks within a flow,
including error handling and result processing.
"""

import asyncio
from typing import Dict, Any
from datetime import datetime
from app.models.models import Task, TaskResult, TaskStatus


class TaskExecutor:
    """
    Handles task execution logic and result processing.

    This class is responsible for executing individual tasks and converting
    their results into standardized TaskResult objects.
    """

    @staticmethod
    async def execute_task(task: Task, context: Dict[str, Any]) -> TaskResult:
        """
        Execute a single task and return its result.

        Args:
            task: The task to execute
            context: Shared execution context containing data from previous tasks

        Returns:
            TaskResult containing execution status, data, and timing information
        """
        start_time = datetime.now()

        try:
            if task.function:
                result_data = await task.function(context)
                execution_time = (datetime.now() - start_time).total_seconds()
                return TaskResult(
                    status=TaskStatus.SUCCESS,
                    data=result_data,
                    execution_time=execution_time
                )
            else:
                await asyncio.sleep(0.1)
                execution_time = (datetime.now() - start_time).total_seconds()
                return TaskResult(
                    status=TaskStatus.SUCCESS,
                    data=f"Result from {task.name}",
                    execution_time=execution_time
                )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return TaskResult(
                status=TaskStatus.FAILURE,
                error=str(e),
                execution_time=execution_time
            )