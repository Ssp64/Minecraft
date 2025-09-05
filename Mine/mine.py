from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import time as pytime

app = Ursina()

player = FirstPersonController()
player.jump_height = 1
player.gravity = 0.5
player.speed = 5

custom_sky = Entity(parent=scene, model='sphere', texture='sky.png', scale=500, double_sided=True)
custom_sky.rotation_x = 90

block_types = [
    'grass.jpg',
    'stone.jpg',
    'wood.jpg',
    'plank.png',
    'dirt.jpg',
    'glass.png',
    'brick.jpg',
    'dia.png',
    'leaf.jpg',
]

selected_block = 0

boxes = []
for i in range(30):
    for j in range(30):
        box = Button(color=color.white, model='cube', position=(j, 0, i), texture='grass.jpg', parent=scene, origin_y=0.5)
        boxes.append(box)

hotbar_bg = Entity(parent=camera.ui, model='quad', texture='image.png', scale=(0.8, 0.1), position=(0, -0.45), z=1)

inventory = []
slot_spacing = 0.08 + 0.010
start_x = -((slot_spacing * 9) / 2) + (slot_spacing / 2)

for i in range(9):
    slot = Button(
        parent=camera.ui,
        model='quad',
        texture=block_types[i],
        color=color.white,
        position=Vec2(start_x + i * slot_spacing, -0.45),
        scale=0.08,
        z=0
    )
    inventory.append(slot)

highlight = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(255, 255, 255, 0.5),
    scale=(0.085, 0.085),
    position=inventory[selected_block].position,
    z=-0.01
)

highlight_border = Entity(
    parent=highlight,
    model=Mesh(mode='line_loop'),
    color=color.white,
    scale=(1.05, 1.05),
    z=-0.02
)

crosshair = Text(text='+', origin=(0, 0), scale=2, color=color.black)

flying = False
last_space_press_time = 0
double_press_threshold = 0.35

def input(key):
    global selected_block, flying, last_space_press_time

    if key == 'control':
        player.speed = 7
    if key == 'control up':
        player.speed = 5

    if key.isdigit():
        index = int(key) - 1
        if 0 <= index < len(inventory):
            selected_block = index
            highlight.position = inventory[selected_block].position

    if key == 'left mouse down':
        for box in boxes:
            if box.hovered:
                boxes.remove(box)
                destroy(box)
                return

    if key == 'right mouse down':
        for box in boxes:
            if box.hovered:
                pos = box.position + mouse.normal
                if not any(e.position == pos for e in boxes):
                    new_block_texture = inventory[selected_block].texture
                    new = Button(
                        color=color.white,
                        model='cube',
                        position=pos,
                        texture=new_block_texture,
                        parent=scene,
                        origin_y=0.5
                    )
                    boxes.append(new)
                return

    if key == 'space':
        current_time = pytime.time()
        if current_time - last_space_press_time < double_press_threshold:
            flying = not flying
            if flying:
                player.gravity = 0
            else:
                player.gravity = 0.5
        last_space_press_time = current_time
def update():
    if flying:
        player.speed = 7
        if held_keys['space']:
            player.position += Vec3(0, time.dt * 5, 0)
        if held_keys['left shift']:
            player.position -= Vec3(0, time.dt * 5, 0)
        player.gravity = 0
    else:
        player.speed = 5
        player.gravity = 0.5
        if not player.grounded:
            player.y += held_keys['space'] * time.dt * 3

app.run()