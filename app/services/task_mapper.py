from app.services.demo_tasks import TASK_FUNCTIONS

DESCRIPTION_MAP = {
    "fetch": "fetch_data",
    "process": "process_data",
    "store": "store_data"
}

def match_function_by_description(description: str):
    desc_lower = description.lower()
    for key, func_name in DESCRIPTION_MAP.items():
        if key in desc_lower:
            return TASK_FUNCTIONS.get(func_name)
    return None