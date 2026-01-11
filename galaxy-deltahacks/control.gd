extends Control

const URL = "http://127.0.0.1:8000/generate"

var increment = 0 

@onready var open_button: Button = $button
@onready var submit_button: Button = $SubmitButton
@onready var input: LineEdit = $TaskButton
@onready var http_request: HTTPRequest = $HTTPRequest

func _ready():
	# Start hidden
	input.visible = false
	submit_button.visible = false

	open_button.pressed.connect(_on_open_pressed)
	submit_button.pressed.connect(_on_submit_pressed)
	http_request.request_completed.connect(_on_request_completed)

# 1️⃣ Open the text box
func _on_open_pressed():
	input.visible = true
	submit_button.visible = true
	
	increment += 1

	input.grab_focus()

# 2️⃣ Send user input to Python
func _on_submit_pressed():
	var text := input.text.strip_edges()
	if text.is_empty():
		print("Input is empty")
		return

	send_request(text)
# 3️⃣ HTTP request
func send_request(task_description: String):
	var data = {
		"task_description": task_description,
		"parent_type": "star",
		"parent_id": increment
	}

	var json_body = JSON.stringify(data)
	var headers = ["Content-Type: application/json"]

	print("Sending:", task_description)

	var err = http_request.request(
		URL,
		headers,
		HTTPClient.METHOD_POST,
		json_body
	)

	if err != OK:
		print("HTTP request error:", err)

# 4️⃣ Response handler
func _on_request_completed(result, response_code, _headers, body):
	print("HTTP:", response_code)

	if response_code == 200:
		var json = JSON.parse_string(body.get_string_from_utf8())
		if json == null:
			print("Invalid JSON")
			return

		print("Response:")
		print(JSON.stringify(json, "\t"))
	else:
		print("Error:")
		print(body.get_string_from_utf8())
