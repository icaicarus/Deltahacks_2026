import json
# Replace 'your_logic_filename' with the actual name of your .py file
from create_godot_output import validate_and_correct_tasks

# 1. Create mock data that mimics Gemini's output
mock_ai_data = {
    "subtasks": [
        { "name": "Check fuel injection system", "description": "Check Fuel", "duration": "1 day" },
        { "name": "Replace worn spark plugs", "description": "Replace Plugs", "duration": "3 days" },
        { "name": "Tighten timing belt", "description": "Tighten Belt", "duration": "2 days" }
    ]
}

# 2. Run the function
final_output = validate_and_correct_tasks(
    ai_data=mock_ai_data,
    parent_id=102,
    child_type="planet"
)

# 3. Print the result as formatted JSON
print(json.dumps(final_output, indent=2))