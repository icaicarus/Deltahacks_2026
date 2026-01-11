import requests
import json

# The address of your FastAPI server
URL = "http://127.0.0.1:8000/generate"

def run_test():
    # 1. Create the data exactly like Godot will
    payload = {
        "task_description": "Make a strawberry milkshake",
        "parent_type": "star",  # This should result in 'planets'
        "parent_id": 102
    }

    print(f"Connecting to {URL}...")
    
    try:
        # 2. Send the POST request
        response = requests.post(URL, json=payload)

        # 3. Check the status code
        if response.status_code == 200:
            print("✅ SUCCESS: Server connected and returned data!")
            
            # Print the formatted JSON result
            result = response.json()
            print("\n--- AI Response ---")
            print(json.dumps(result, indent=4))
            
            # Simple validation checks
            if "subtasks" in result:
                print(f"\nCreated {len(result['subtasks'])} subtasks.")
                print(f"Parent ID: {result['parent_id']}")
                print(f"Child Type: {result['subtasks_type']}")
        else:
            print(f"❌ FAILED: Server returned status code {response.status_code}")
            print("Error Details:", response.text)

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to the server.")
        print("Make sure your main.py is running in another terminal!")

if __name__ == "__main__":
    run_test()