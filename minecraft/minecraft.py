from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# --- Load textures ---
textures = {
    "grass": load_texture("assets/grass.png"),
    "stone": load_texture("assets/stone.png"),
    "brick": load_texture("assets/brick.png"),
    "wood": load_texture("assets/wood.png"),
    "tnt": load_texture("assets/tnt.png"),
    "DiamondBlock": load_texture("assets/DiamondBlock.png"),
    "PumpkinHead": load_texture("assets/PumpkinHead.png"),
    "IronBlock": load_texture("assets/IronBlock.png"),
}

# --- Block class ---
class Block(Button):
    def __init__(self, position=(0,0,0), block_type="wood"):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=textures[block_type],
            color=color.color(0, 0, random.uniform(0.9, 1)),
            highlight_color=color.lime,
        )
        self.block_type = block_type

# --- Build the ground ---
for z in range(20):
    for y in range(2):
        for x in range(20):
            Block(position=(x,-y,z), block_type="grass")

block_type = ["grass", "stone", "brick", "wood", "tnt", "DiamondBlock", "PumpkinHead", "IronBlock"]
current_block = 0

player = FirstPersonController()

# --- Preview UI: shows block texture at bottom center ---
selected_preview = Entity(
    parent=camera.ui,
    model='quad',
    texture=textures[block_type[current_block]],
    scale=(0.15,0.15),
    position=(0,-0.4)  # bottom center
)

def update_selected_preview():
    selected_preview.texture = textures[block_type[current_block]]

# --- Handle input ---
def input(key):
    global current_block

    if key in ["1","2","3","4","5","6","7","8"]:
        current_block = int(key) - 1
        update_selected_preview()

    if key == 'scroll up':
        current_block = (current_block + 1) % len(block_type)
        update_selected_preview()

    if key == 'scroll down':
        current_block = (current_block - 1) % len(block_type)
        update_selected_preview()

    if key == 'left mouse down':
        hit_info = mouse.hovered_entity
        if hit_info:
            Block(position=hit_info.position + mouse.normal, block_type=block_type[current_block])

    if key == 'right mouse down' and mouse.hovered_entity:
        destroy(mouse.hovered_entity)

app.run()
