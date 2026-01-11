extends Node2D

# The address where your Python server is running
const URL = "http://127.0.0.1:8000/generate"

@onready var http_request = $HTTPRequest

func _ready():
	# Connect the signal so we know when the response arrives
	http_request.request_completed.connect(_on_request_completed)
	
	# Wait 1 second before testing to make sure everything is initialized
	await get_tree().create_timer(1.0).timeout
	send_test_request()

func send_test_request():
	print("--- Starting Connection Test ---")
	
	# This matches the 'GodotTaskRequest' model in your Python script
	var test_data = {
		"task_description": "generate project about anime",
		"parent_type": "star",
		"parent_id": 999
	}
	
	# Convert dictionary to JSON string
	var json_body = JSON.stringify(test_data)
	
	# Headers are required so Python knows we are sending JSON
	var headers = ["Content-Type: application/json"]
	
	print("Sending request to: ", URL)
	var error = http_request.request(URL, headers, HTTPClient.METHOD_POST, json_body)
	
	if error != OK:
		print("An error occurred while making the HTTP request.")

# This function runs when the Python server replies
func _on_request_completed(result, response_code, _headers, body):
	print("--- Response Received ---")
	print("HTTP Response Code: ", response_code)
	
	if response_code == 200:
		var json = JSON.parse_string(body.get_string_from_utf8())
		print("Successfully connected! Data received:")
		print(JSON.stringify(json, "\t"))
	else:
		print("Failed to connect. Make sure your Python script (main.py) is running!")
		print("Error body: ", body.get_string_from_utf8())
