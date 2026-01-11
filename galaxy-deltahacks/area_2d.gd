extends Area2D



@export var radius := 120.0
@export var speed := 1.0

var angle := 0.0
var center := Vector2.ZERO

func _ready():
	center = global_position
	$AnimatedSprite2D.play()
	

func _process(delta):
	angle += speed * delta
	global_position = center + Vector2(
		cos(angle),
		sin(angle)
	) * radius
