# demo_tasks.py
"""
Sample task implementations for demonstration purposes.

This module provides example task functions that can be used to test
the Flow Manager system functionality.
"""

import asyncio
import uuid
from typing import Dict, Any
from datetime import datetime


async def fetch_data_task(context: Dict[str, Any]) -> Any:
    """
    Demo task that simulates data fetching operation.

    Args:
        context: Execution context from previous tasks

    Returns:
        Dictionary containing simulated user data
    """
    await asyncio.sleep(0.2)
    data = {"users": [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]}
    return data


async def process_data_task(context: Dict[str, Any]) -> Any:
    """
    Demo task that processes data from the previous task.

    Args:
        context: Execution context containing task1_result

    Returns:
        Dictionary containing processed data summary

    Raises:
        ValueError: If no data is available to process
    """
    fetch_result = context.get("task1_result")
    if not fetch_result:
        raise ValueError("No data to process")

    await asyncio.sleep(0.3)
    processed_data = {
        "processed_users": len(fetch_result.get("users", [])),
        "timestamp": datetime.now().isoformat()
    }
    return processed_data


async def store_data_task(context: Dict[str, Any]) -> Any:
    """
    Demo task that simulates data storage operation.

    Args:
        context: Execution context containing task2_result

    Returns:
        Dictionary containing storage confirmation

    Raises:
        ValueError: If no processed data is available to store
    """
    process_result = context.get("task2_result")
    if not process_result:
        raise ValueError("No processed data to store")

    await asyncio.sleep(0.1)
    return {"stored": True, "record_id": str(uuid.uuid4())}


TASK_FUNCTIONS = {
    """Registry mapping task names to their implementation functions."""
    "task1": fetch_data_task,
    "task2": process_data_task,
    "task3": store_data_task
}