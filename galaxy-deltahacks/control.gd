extends Control

# ==============================
# CONFIG
# ==============================
const URL = "http://127.0.0.1:8000/generate"

const STAR_SCENE = preload("res://sun.tscn")
const MOON_SCENE = preload("res://moon.tscn")

# ==============================
# STATE
# ==============================
enum Context { OUTER, STAR }
var current_context := Context.OUTER
var current_star: Node2D = null
var parent_id := 0

# Moons orbiting stars
var moons := []

# ==============================
# STAR ANIMATION PARAMETERS
# ==============================
var star_angle := 0.0
var star_pulse_scale := 1.0
var star_pulse_speed := 2.0      # Pulse frequency
var star_rotation_speed := 0.5   # Rotation speed in radians/sec
var star_time := 0.0             # Time accumulator for pulsing

# ==============================
# NODES
# ==============================
@onready var create_button: Button = $button
@onready var submit_button: Button = $SubmitButton
@onready var input: LineEdit = $TaskButton
@onready var http_request: HTTPRequest = $HTTPRequest

# World = parent Node2D
@onready var world: CanvasLayer = get_parent()

# ==============================
# READY
# ==============================
func _ready():
	input.visible = false
	submit_button.visible = false

	create_button.pressed.connect(_on_create_pressed)
	submit_button.pressed.connect(_on_submit_pressed)
	http_request.request_completed.connect(_on_request_completed)

# ==============================
# UI
# ==============================
func _on_create_pressed():
	input.visible = true
	submit_button.visible = true
	input.text = ""
	input.grab_focus()

func _on_submit_pressed():
	var text := input.text.strip_edges()
	if text.is_empty():
		return

	match current_context:
		Context.OUTER:
			send_request(text, "star")
		Context.STAR:
			send_request(text, "moon")

	submit_button.disabled = true

# ==============================
# HTTP
# ==============================
func send_request(task_description: String, parent_type: String):
	parent_id += 1

	var data = {
		"task_description": task_description,
		"parent_type": parent_type,
		"parent_id": parent_id
	}

	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify(data)

	http_request.request(
		URL,
		headers,
		HTTPClient.METHOD_POST,
		body
	)

# ==============================
# RESPONSE → SPAWN OBJECT
# ==============================
func _on_request_completed(result, response_code, _headers, body):
	submit_button.disabled = false

	if response_code != 200:
		print("Request failed")
		return

	# Godot 4 JSON parsing
	var json_parser = JSON.new()
	var json_data = json_parser.parse_string(body.get_string_from_utf8())

	if typeof(json_data) != TYPE_DICTIONARY:
		print("Invalid JSON")
		return

	print("AI Response:")
	print(JSON.stringify(json_data, "\t"))

	if current_context == Context.OUTER:
		spawn_star()
		current_context = Context.STAR
	else:
		spawn_moon()

# ==============================
# SPAWNING WITH ANIMATION
# ==============================
func spawn_star():
	current_star = STAR_SCENE.instantiate()
	world.add_child(current_star)
	current_star.position = get_viewport_rect().size / 2
	moons.clear()
	
	# Play AnimatedSprite2D if it exists
	var anim_sprite := current_star as AnimatedSprite2D
	if anim_sprite:
		anim_sprite.play()
	
	print("Star spawned")

func spawn_moon():
	if current_star == null:
		return

	var moon = MOON_SCENE.instantiate()
	current_star.add_child(moon)

	# Store rotation info in a dictionary
	var moon_data = {
		"node": moon,
		"angle": randf() * TAU,
		"radius": 120,
		"speed": 1.0 + randf() * 2.0
	}

	# Set initial position
	moon.position = Vector2(cos(moon_data.angle), sin(moon_data.angle)) * moon_data.radius
	moons.append(moon_data)

	print("Moon spawned")

# ==============================
# PROCESS → Animate star and moons
# ==============================
func _process(delta):
	# Animate moons orbiting
	for moon_data in moons:
		moon_data.angle += moon_data.speed * delta
		moon_data.node.position = Vector2(
			cos(moon_data.angle),
			sin(moon_data.angle)
		) * moon_data.radius

	# Animate star rotation and pulse
	if current_star:
		# rotate
		current_star.rotation += star_rotation_speed * delta

		# pulse using delta-based time accumulator
		star_time += delta
		star_pulse_scale = 1.0 + 0.1 * sin(star_time * star_pulse_speed)
		current_star.scale = Vector2(star_pulse_scale, star_pulse_scale)
