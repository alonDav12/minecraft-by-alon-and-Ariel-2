from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.sky import Sky
import random
import time

app = Ursina()

# ---------------- Textures ----------------
textures = {
    "grass": load_texture("assets/grass.png"),
    "stone": load_texture("assets/stone.png"),
    "brick": load_texture("assets/brick.png"),
    "wood": load_texture("assets/wood.png"),
    "tnt": load_texture("assets/tnt.png"),
    "fire": load_texture("assets/fire.png"),
    "DiamondBlock": load_texture("assets/DiamondBlock.png"),
    "PumpkinHead": load_texture("assets/PumpkinHead.png"),
    "IronBlock": load_texture("assets/IronBlock.png"),
}

# ---------------- Player ----------------
player = FirstPersonController()
player.collider = 'box'
player_health = 10

Sky()

# ---------------- Block Class ----------------
class Block(Button):
    def __init__(self, position=(0,0,0), block_type="wood"):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=textures.get(block_type, textures["grass"]),
            color=color.color(0, 0, random.uniform(0.9, 1)),
            highlight_color=color.white,
            collider='box'
        )
        self.block_type = block_type

    def explode(self):
        radius = 2.5
        for e in scene.entities:
            if isinstance(e, Block) and distance_xz(self.position, e.position) <= radius and e != self:
                destroy(e)

        for i in range(10):
            FireEffect(position=self.position + Vec3(random.uniform(-2, 2), 0.5, random.uniform(-2, 2)))

        destroy(self)

def distance_xz(a, b):
    return ((a[0]-b[0])**2 + (a[2]-b[2])**2) ** 0.5

# ---------------- Fire Effect ----------------
class FireEffect(Entity):
    def __init__(self, position=(0,0,0)):
        super().__init__(
            parent=scene,
            position=position,
            model='quad',
            texture=textures["fire"],
            scale=1,
            double_sided=True,
            color=color.rgb(255, random.randint(100,150), 0),
            rotation_y=random.randint(0, 360),
        )
        self.life = 1.5

    def update(self):
        self.life -= time.dt
        self.scale *= 1.03
        self.color = color.color(0, 0, max(self.life,0))
        if self.life <= 0:
            destroy(self)

# ---------------- Zombie Class ----------------
zombies = []

class Zombie(Entity):
    def __init__(self, position=(10,0,10)):
        super().__init__(
            parent=scene,
            position=position,
            model='assets/zombie.glb',
            scale=0.05,
            collider='box',
        )
        self.speed = 2

    def update(self):
        global player_health
        direction = player.position - self.position
        direction.y = 0
        distance = direction.length()
        if distance > 0.5:
            new_position = self.position + direction.normalized() * time.dt * self.speed
            hit_info = raycast(self.position + (0,0.5,0), direction.normalized(), distance=distance, ignore=(self,))
            if not hit_info.hit:
                self.position = new_position
            self.look_at(player.position)
            self.rotation_y += 180
        else:
            player_health -= 1
            print(f"Zombie hit you! Health: {player_health}")
            if player_health <= 0:
                print("Game Over!")
                application.quit()
            destroy(self)
            if self in zombies:
                zombies.remove(self)

    def hit(self):
        destroy(self)
        if self in zombies:
            zombies.remove(self)
        print("Zombie killed!")

def spawn_zombies(number=3):
    for _ in range(number):
        x, z = random.randint(0,24), random.randint(0,24)
        zmb = Zombie(position=(x,0,z))
        zombies.append(zmb)

def spawn_wave():
    spawn_zombies(number=3)
    invoke(spawn_wave, delay=30)

spawn_wave()

# ---------------- Ground ----------------
for z in range(25):
    for y in range(4):
        for x in range(25):
            Block(position=(x,-1.2,z), block_type="grass")

# ---------------- Block Selection ----------------
block_type = ["grass","stone","brick","wood","tnt","DiamondBlock","PumpkinHead","IronBlock"]
current_block = 3

selected_preview = Entity(
    parent=camera.ui,
    model='quad',
    texture=textures[block_type[current_block]],
    scale=(0.15,0.15),
    position=(0,-0.4)
)

def update_selected_preview():
    selected_preview.texture = textures[block_type[current_block]]

# ---------------- Input Handling ----------------
def input(key):
    global current_block

    if key in [str(i) for i in range(1,len(block_type)+1)]:
        current_block = int(key)-1
        update_selected_preview()

    if key == 'scroll up':
        current_block = (current_block + 1) % len(block_type)
        update_selected_preview()

    if key == 'scroll down':
        current_block = (current_block - 1) % len(block_type)
        update_selected_preview()

    if key == 'left mouse down' and mouse.hovered_entity:
        if isinstance(mouse.hovered_entity, Zombie):
            mouse.hovered_entity.hit()
        else:
            Block(position=mouse.hovered_entity.position + mouse.normal, block_type=block_type[current_block])

    if key == 'right mouse down' and mouse.hovered_entity:
        if hasattr(mouse.hovered_entity, "block_type") and mouse.hovered_entity.block_type == "tnt":
            mouse.hovered_entity.explode()
        else:
            destroy(mouse.hovered_entity)

app.run()
