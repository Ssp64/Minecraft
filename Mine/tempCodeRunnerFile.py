from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math

# ---------- Config ----------
WORLD_SIZE = 24          # X/Z size (creates WORLD_SIZE x WORLD_SIZE surface)
MAX_STACK = 4            # how many blocks tall the simple terrain goes
MOUSE_SENS = Vec2(40, 40)

# Block "palette" (press 1-4 to switch)
BLOCKS = {
    1: ('white_cube', color.lime),     # grass
    2: ('white_cube', color.rgb(139, 69, 19)),  # dirt/brown
    3: ('white_cube', color.gray),     # stone
    4: ('white_cube', color.azure),    # planks-ish
}

current_block = 1  # start with grass-like

app = Ursina(borderless=False)

# Tweak window
window.title = 'MiniCraft - Ursina'
window.fps_counter.enabled = True
window.exit_button.visible = False
mouse.locked = True
camera.fov = 90


def nice_h(x, z):
    """A tiny height function to make the world a bit bumpy (no external noise libs)."""
    # combine a couple of gentle waves and clamp to [0, MAX_STACK)
    h = (math.sin(x * 0.35) + math.cos(z * 0.35) + math.sin((x + z) * 0.25)) * 0.5
    h = int(max(0, min(MAX_STACK - 1, round(h + (MAX_STACK - 1) / 2))))
    return h


class Voxel(Button):
    def __init__(self, position=(0, 0, 0), block_id=1):
        tex, col = BLOCKS.get(block_id, BLOCKS[1])
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=tex,
            color=col,
            scale=1,
            collider='box'
        )
        self.block_id = block_id

    def input(self, key):
        global current_block
        if self.hovered:
            if key == 'left mouse down':
                # Place a block onto the face we’re pointing at
                Voxel(self.position + mouse.normal, current_block)
                punch()
            if key == 'right mouse down':
                # Remove this block
                destroy(self)
                punch()


def punch():
    # a tiny feedback animation + sound
    if hasattr(player, 'hand'):
        player.hand.rotation_z = -30
        player.hand.animate_rotation_z(0, duration=0.15, curve=curve.out_quad)
    if hasattr(punch, 'snd'):
        punch.snd.play()


# Load a short click sound (Ursina has a built-in 'shore' etc., but this is optional)
try:
    punch.snd = Audio('mouse_click', autoplay=False)
except Exception:
    pass

# Light & sky
ambient_light = AmbientLight()
ambient_light.color = color.rgba(255, 255, 255, 0.35)
DirectionalLight(y=2, z=3, shadows=True, color=color.rgba(255, 255, 255, 0.85))
Sky()

# Create a small world
for x in range(-WORLD_SIZE // 2, WORLD_SIZE // 2):
    for z in range(-WORLD_SIZE // 2, WORLD_SIZE // 2):
        h = nice_h(x, z)
        # Build a little stack (stone at bottom, dirt in middle, grass on top)
        for y in range(h + 1):
            if y == h:
                bid = 1  # top layer = grass-like
            elif y <= 1:
                bid = 3  # bottom layers = stone-like
            else:
                bid = 2  # middle = dirt-like
            Voxel((x, y, z), bid)

# Player
player = FirstPersonController(y=MAX_STACK + 3, speed=6, origin_y=0.5)
player.mouse_sensitivity = MOUSE_SENS

# Simple hand/crosshair UI
player.hand = Entity(
    parent=camera.ui,
    model='quad',
    texture='circle',
    scale=0.09,
    color=color.rgba(255, 255, 255, 180),
    position=(0, 0)
)

block_label = Text(
    text='Block: 1 (Grass)',
    origin=(.5, -.5),
    position=(-.01, .45),
    scale=1,
    background=True
)

help_txt = Text(
    text='WASD to move • Space jump • Shift sprint\nLeft-click place • Right-click break • 1–4 change block • Esc unlock mouse',
    origin=(.5, -.5),
    position=(-.01, .4),
    scale=.8,
    background=True
)

# Hotbar names for label
BLOCK_NAMES = {
    1: 'Grass',
    2: 'Dirt',
    3: 'Stone',
    4: 'Wood',
}


def set_block(n: int):
    global current_block
    current_block = max(1, min(4, n))
    block_label.text = f'Block: {current_block} ({BLOCK_NAMES[current_block]})'


def input(key):
    # Switch block types
    if key in ('1', '2', '3', '4'):
        set_block(int(key))

    # Escape to unlock/lock mouse
    if key == 'escape':
        mouse.locked = not mouse.locked
        if mouse.locked:
            help_txt.text = 'WASD to move • Space jump • Shift sprint\nLeft-click place • Right-click break • 1–4 change block • Esc unlock mouse'
        else:
            help_txt.text = 'Mouse unlocked (press Esc to lock again)'

    # Quick quit
    if key == 'q' and not mouse.locked:
        application.quit()


def update():
    # Optional: simple “bob” on hand when moving
    if held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']:
        player.hand.y = math.sin(time.time() * 12) * 0.01
    else:
        player.hand.y = 0


if __name__ == '__main__':
    app.run()
