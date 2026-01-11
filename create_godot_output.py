import re

def validate_and_correct_tasks(ai_data, parent_id, child_type):
    """
    1. Extracts numeric durations using Regex.
    2. Calculates relative distance (current / max).
    3. Formats output with parent context.
    """
    raw_subtasks = ai_data.get("subtasks", [])
    if not raw_subtasks:
        return {"subtasks": [], "parent_id": parent_id, "subtasks_type": child_type} #prevents app from crashing if nay mistake happens

    # Step 1: Extract numeric durations as a list of floats
    durations = []
    for st in raw_subtasks:
        # Regex explanation: \d+ matches digits, \.? matches an optional decimal, 
        # \d* matches optional digits after decimal.
        match = re.search(r"(\d+\.?\d*)", str(st.get("duration", "1")))
        val = float(match.group(1)) if match else 1.0
        durations.append(val)

    # Step 2: Find max duration for relative calculation
    max_val = max(durations) if durations else 1.0

    # Step 3: Build the final list with calculated 'distance'
    processed_subtasks = []
    for i, st in enumerate(raw_subtasks):
        # Calculation: distance = current_duration / max_duration
        # This keeps the values relative to the largest task
        rel_distance = durations[i] / max_val if max_val > 0 else 1.0
        
        # Rounding to 2 decimal places for cleaner JSON
        processed_subtasks.append({
            "name": st.get("name", "Unnamed Task"),
            "description": st.get("description", ""),
            "distance": round(rel_distance, 2)
        })

    # Step 4: Return in the specific JSON format required
    return {
        "subtasks": processed_subtasks,
        "parent_id": parent_id,
        "subtasks_type": child_type
    }