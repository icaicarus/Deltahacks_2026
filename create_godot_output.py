import json

def validate_and_correct_tasks(ai_data, parent_id, child_type):
    # 1. Convert JSON string to Python List
    # If ai_data is already a list, this step is skipped
    if isinstance(ai_data, str):
        try:
            tasks = json.loads(ai_data)
        except json.JSONDecodeError:
            print("Error: Could not parse AI JSON data.")
            return None
    else:
        tasks = ai_data

    # 2. Find Max Duration for the 0-1 Decimal Calculation
    # We assume the AI includes a 'duration' number for each task
    durations = [float(t.get('duration', 1)) for t in tasks]
    max_duration = max(durations) if durations else 1

    clean_subtasks = []

    # 3. Parse and Correct Information
    for task in tasks:
        # Calculate the duration decimal (0-1)
        raw_dur = float(task.get('duration', 1))
        duration_factor = round(raw_dur / max_duration, 4)

        # Build the cleaned task (ignoring color as requested)
        clean_task = {
            "name": task.get("name", "Unnamed Task"),
            "description": task.get("description", "No description"),
            "distance": int(task.get("distance", 1)),
            "duration_factor": duration_factor # Your 0-1 decimal
        }
        clean_subtasks.append(clean_task)

    # 4. Return the structured dictionary for the main file
    return {
        "subtasks": clean_subtasks,
        "parent_id": parent_id,
        "subtasks_type": child_type
    }