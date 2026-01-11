import re
import json

def validate_and_correct_tasks(ai_data, parent_id, child_type):
    # Ensure ai_data is a dictionary (if it's a raw string, parse it)
    if isinstance(ai_data, str):
        ai_data = json.loads(ai_data)
    
    raw_subtasks = ai_data.get("subtasks", [])
    processed_subtasks = []
    
    # 1. First pass: Extract duration as numbers for calculation
    durations = []
    for st in raw_subtasks:
        # Regex to find numbers in strings like "3 days" or "Duration: 5"
        match = re.search(r"(\d+)", str(st.get("duration", "1")))
        val = float(match.group(1)) if match else 1.0
        durations.append(val)
    
    # 2. Find max duration to calculate ratio (distance)
    max_dur = max(durations) if durations else 1.0
    
    # 3. Second pass: Build the final objects
    for i, st in enumerate(raw_subtasks):
        # Calculate distance (0 to 1 scale)
        # distance = current_duration / max_duration
        distance_ratio = durations[i] / max_dur
        
        processed_subtasks.append({
            "name": st.get("name", "Unnamed Task"),
            "description": st.get("description", "No description provided."),
            "distance": distance_ratio  # This will be used for orbit radius in Godot
        })
        
    return {
        "subtasks": processed_subtasks,
        "parent_id": parent_id,
        "subtasks_type": child_type
    }