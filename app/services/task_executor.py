import asyncio
from typing import Dict, Any
from datetime import datetime
from app.models.models import Task, TaskResult, TaskStatus


class TaskExecutor:
    # Responsible for running tasks and reporting their results

    @staticmethod
    async def execute_task(task: Task, context: Dict[str, Any]) -> TaskResult:
        """
        Runs a task and returns the outcome in a TaskResult.

        Args:
            task: Task to be executed
            context: Shared flow context (passed into the task function)

        Returns:
            TaskResult with status, result data, and timing
        """
        start_time = datetime.now()

        try:
            if task.function:
                # Run the actual task function (async)
                result_data = await task.function(context)
                execution_time = (datetime.now() - start_time).total_seconds()

                return TaskResult(
                    status=TaskStatus.SUCCESS,
                    data=result_data,
                    execution_time=execution_time
                )
            else:
                # Fallback for tasks without a function – simulate with delay
                await asyncio.sleep(0.1)
                execution_time = (datetime.now() - start_time).total_seconds()

                return TaskResult(
                    status=TaskStatus.SUCCESS,
                    data=f"Result from {task.name}",
                    execution_time=execution_time
                )

        except Exception as e:
            # Task threw an exception – mark as failed
            execution_time = (datetime.now() - start_time).total_seconds()

            return TaskResult(
                status=TaskStatus.FAILURE,
                error=str(e),
                execution_time=execution_time
            )