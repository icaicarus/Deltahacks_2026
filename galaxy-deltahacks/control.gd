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
var moons := []
var last_ai_data: Dictionary = {}

# ==============================
# STAR MOTION
# ==============================
var star_time := 0.0
var star_rotation_speed := 0.5
var star_pulse_speed := 2.0

# ==============================
# NODES
# ==============================
@onready var create_button: Button = $button
@onready var submit_button: Button = $SubmitButton
@onready var input: LineEdit = $TaskButton
@onready var http_request: HTTPRequest = $HTTPRequest
@onready var world: CanvasLayer = get_parent()
@onready var fixed_collision: Node2D = $CollisionShape2D  # adjust path
@onready var button_container: MarginContainer = $MarginContainer # container for new buttons

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
# UI - CREATE BUTTON
# ==============================
func _on_create_pressed():
	input.visible = true
	submit_button.visible = true
	input.text = ""
	input.grab_focus()

	# ▶ Safely generate a new button inside the MarginContainer
	if button_container:
		var new_button = Button.new()
		new_button.text = "Planet Button " + str(button_container.get_child_count() + 1)
		button_container.add_child(new_button)

		# Optional: connect pressed signal for the new button
		new_button.pressed.connect(func():
			print("Pressed button: ", new_button.text))
	else:
		print("Warning: button_container is null. Please check the path.")

# ==============================
# UI - SUBMIT BUTTON
# ==============================
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
# HTTP REQUEST
# ==============================
func send_request(task_description: String, parent_type: String):
	parent_id += 1
	var data = {
		"task_description": task_description,
		"parent_type": parent_type,
		"parent_id": parent_id
	}
	http_request.request(
		URL,
		["Content-Type: application/json"],
		HTTPClient.METHOD_POST,
		JSON.stringify(data)
	)

# ==============================
# RESPONSE
# ==============================
func _on_request_completed(result, response_code, _headers, body):
	submit_button.disabled = false

	if response_code != 200:
		print("Request failed, using default distance")
		last_ai_data = {"distance": 120.0}
	else:
		var parser := JSON.new()
		last_ai_data = parser.parse_string(body.get_string_from_utf8())
		if typeof(last_ai_data) != TYPE_DICTIONARY:
			print("Invalid JSON, using default distance")
			last_ai_data = {"distance": 120.0}

	if current_context == Context.OUTER:
		spawn_star()
		current_context = Context.STAR
	else:
		spawn_moon()

# ==============================
# SPAWN STAR
# ==============================
func spawn_star():
	current_star = STAR_SCENE.instantiate()
	world.add_child(current_star)

	# Hard-coded offset from fixed collision
	var min_distance := 300.0
	if fixed_collision:
		var direction := (get_viewport_rect().size / 2 - fixed_collision.position).normalized()
		current_star.position = fixed_collision.position + direction * min_distance
	else:
		current_star.position = get_viewport_rect().size / 2

	moons.clear()

	# Play animation if root is AnimatedSprite2D
	var anim := current_star as AnimatedSprite2D
	if anim:
		anim.play()

	print("Star spawned at", current_star.position)

# ==============================
# STAR COLLISION RADIUS
# ==============================
func get_star_collision_radius() -> float:
	if current_star == null:
		return 0.0

	var collision := current_star.find_child("CollisionShape2D", true, false)
	if collision == null:
		return 0.0

	if collision.shape is CircleShape2D:
		var shape := collision.shape as CircleShape2D
		return shape.radius * current_star.scale.x

	return 0.0

# ==============================
# SPAWN MOON
# ==============================
func spawn_moon():
	if current_star == null:
		return

	var moon = MOON_SCENE.instantiate()
	current_star.add_child(moon)

	var ai_distance := 120.0
	if last_ai_data.has("distance"):
		ai_distance = float(last_ai_data["distance"])

	var star_radius := get_star_collision_radius()
	var safety_padding := 20.0
	var orbit_radius := star_radius + ai_distance + safety_padding
	var angle := randf() * TAU

	moon.position = Vector2(cos(angle), sin(angle)) * orbit_radius

	moons.append({
		"node": moon,
		"angle": angle,
		"radius": orbit_radius,
		"speed": 1.0 + randf() * 2.0
	})

	var anim := moon as AnimatedSprite2D
	if anim:
		anim.play()

	print("Moon orbit radius:", orbit_radius)

# ==============================
# PROCESS
# ==============================
func _process(delta):
	for moon_data in moons:
		moon_data.angle += moon_data.speed * delta
		moon_data.node.position = Vector2(
			cos(moon_data.angle),
			sin(moon_data.angle)
		) * moon_data.radius

	if current_star:
		current_star.rotation += star_rotation_speed * delta
		star_time += delta
		var scale := 1.0 + 0.1 * sin(star_time * star_pulse_speed)
		current_star.scale = Vector2(scale, scale)
