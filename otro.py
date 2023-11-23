from ursina import *
from ursina.prefabs.health_bar import HealthBar
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

from ursina import Button

app = Ursina()
window.fps_counter.enabled=False
window.exit_button.enabled=True
random.seed(0)


casa4 = Entity(model='scene.gltf', collider  ='mash', scale =1, rotation_y= 180)
casa4.position = (40, -1.25, -40)  
casa4.scale = (1, 1, 1) 

casa5 = Entity(model='scene.gltf', collider  ='mash', scale =1, rotation_y= 180)
casa5.position = (40, -1.25, 0)  
casa5.scale = (1, 1, 1)  

casa6 = Entity(model='scene.gltf', collider  ='mash', scale =1, rotation_y= 180)
casa6.position = (40, -1.25, 40)  
casa6.scale = (1, 1, 1)  


wall1 = Entity(model = 'cube', scale=(20,12,1), collider = 'box', x =32,z=-2, texture='orc1' ,  double_sided=True)
wall3 = Entity(model = 'cube', scale=(24,12,1), collider = 'box', x =-10,z=32, rotation_y = 90, texture = 'orc1',  double_sided=True)
wall4 = Entity(model = 'cube', scale=(24,12,1), collider = 'box', x =-32,z=2, rotation_y = 90, texture = 'orc1')
wall5 = Entity(model = 'cube', scale=(20,12,1), collider = 'box', x =20,z=41, texture ='orc1' ,rotation_y = 90)
wall6 = Entity(model = 'cube', scale=(20,12,1), collider = 'box', x =12,z=-32, texture ='orc1')
wall7 = Entity(model = 'cube', scale=(20,12,1), collider = 'box', x =15,z=2, texture ='orc1' , rotation_y = 90)
wall8 = Entity(model = 'cube', scale=(20,12,1), collider = 'box', x =18,z=32, texture ='orc1')
wall9 = Entity(model = 'cube', scale=(20,12,1), collider = 'box', x =30,z=-22, texture ='orc1', rotation_y = 90)

lable = Text(text='Pause / Map', scale=3, x=-0.85,
             y=0.45,visible=False ,color=rgb(255, 48, 33))

Entity.default_shader = lit_with_shadows_shader
button = Button(button='Restart / Map', scale= 8, x=-100)
ground = Entity(model='plane', collider='box', scale=128,
                texture='orc2', texture_scale=(4,4))
editor_camera = EditorCamera(enabled=False, ignore_paused=True)

vida_barra = Entity(model='quad', color=color.red, scale_x=3, scale_y=0.2)
vida_barra.position = window.bottom_right - (vida_barra.scale_x / 2, vida_barra.scale_y / 2)
vida_actual = 100


        
player = FirstPersonController(origin_y=-.5, speed=10, origin_x = 6)
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))
player.cursor.color = color.white
player.cursor.texture='assets\\scope'
player.cursor.scale=(0.1)
player.cursor.rotation_z = (90)
gun = Entity(model='assets/M1', parent=camera, posassets=(.5,-.25,.45),
             scale=(0.07),rotation_y=190, origin_z=2.5, texture='assets/M1.png',
             on_cooldown=False,collider='mesh')
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad',
                          color=color.yellow, enabled=False)
shootables_parent = Entity()
mouse.traverse_target = shootables_parent

def update():
    if held_keys['left mouse']:
        shoot()

def shoot():
    if not gun.on_cooldown:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled = True
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)



class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=shootables_parent,  
            model='assets\man\man.fbx',
            scale=0.2,
            double_sided=True,
            origin_y=-0.5,
            texture='assets\man\orc2',
            collider='mesh',
            **kwargs
        )
        self.randomize_position()

    def randomize_position(self):
        x = random.uniform(-10, 20)  
        y = random.uniform(0, 0)  
        z = random.uniform(-10, 20)  
        self.position = (x, y, z)
        self.health_bar = Entity(parent=self, y=18, model='cube', color=color.red,
                                 world_scale=(1.5, 0.1, 0.1))
        self.max_hp = 100
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return
        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 19

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            player.cursor.color = color.white
            player.cursor.shake(duration=0.8)
            return
        if value <= 10:
            player.cursor.color = color.red
            return
        else:
            player.cursor.color = color.white
        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

    def get_random_position(self):
        return Vec3(random.uniform(-16, 16), 0, random.uniform(-32, 32) + 8 )

enemies = [Enemy(x=x*12) for x in range(16)]

def pause_input(key):
    if key == 'escape':    
        editor_camera.enabled = not editor_camera.enabled
        lable.visible = not lable.visible
        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position
        application.paused = editor_camera.enabled
    if key == 'right mouse down':
        gun.position=(.5,-.24,.40)
        player.cursor.shake(duration=0.3)
    else:
        gun.position = (.5, -.25, .45)

def si(self): 
    if self.input.ket_down('shift'): 
        self.speed = 20 
    else: 
        self.speed = 10 

def reiniciar_zombies():
    for zombie in enemies:
        zombie.position = zombie.get_random_position()
        zombie.hp = zombie.max_hp
pause_handler = Entity(ignore_paused=True, input=pause_input)
sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))


Sky(texture='assets\skybox')
app.run()