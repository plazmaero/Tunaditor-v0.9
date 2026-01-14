import pygame, random, math, os
from time import time
from pygame._sdl2.video import Window, Renderer, Texture, Image
from pygame.sysfont import *
from Scripts.timers import Timer
from Scripts.settings import *


class Room:
  def __init__(self, name="Room1", main=None):
    self.main = main
    self.name = name
    self.menu = {"speed": 1.0, "trigger": "", "down_s": "", "up_s": "", "down_sfx": None, "up_sfx": None, "flags": ["toggle", "reset"], "items": []} #toggle/hold, players can join
    self.menu_active = False
    self.selected_item = [0, 0]
    self.layers = []
    self.cutscenes = []
    self.track = ""
    self.first_track = ""
    self.backgrounds = []
    self.doors = []
    self.zones = []
    self.mode = "Platformer"
    self.show_player = True
    self.allow_scrolling = False
    self.spawn_hm = False
    self.spawn_vm = False
    self.hm = False
    self.vm = False
    self.scroll_mode = "No Scrolling"
    self.spawn_borders = {"right": 0, "top": 0, "left": 0, "bottom": 0}
    self.borders = {"right": 0, "top": 0, "left": 0, "bottom": 0}
    self.move_threshold = {"right": 200, "top": 200, "left": 200, "bottom": 200}
    self.gravity = 1.0
    self.show_ui = []
    self.hide_ui = []
    self.ui_modes = []
    self.shader = ""
    self.shader_prog = 0
    self.shader_vao = 0

  def render_backgrounds(self, screen, cutscene=False, dt=1, bg=True, fg=True):
    def render(background, rect):
      if (background.foreground and fg) or (not background.foreground and bg):
        if (self.main.gamestate != 10 and self.main.editor_mode) or not background.hidden:
          #if self.main.gamestate != 10 and not background.spawn_as_visible: background.image.set_alpha(100)
          #if self.main.gamestate != 10 and background.spawn_as_visible: background.image.set_alpha(255)
          background.image.set_alpha(background.alpha)
          if background.distance != 0:
            sx = self.main.camera.scroll[0]; sy = self.main.camera.scroll[1]
            if not background.x_scroll: sx = 0
            if not background.y_scroll: sy = 0
            if background.repeat_x and background.repeat_y:
              for x in range(repeat):
                for y in range(repeat): screen.blit(background.image, ((rect.x - (sx / background.distance) + ((x - math.floor(repeat / 2)) * (rect.width + background.marges[0]))), (rect.y - (sy / background.distance) + ((y - math.floor(repeat / 2)) * (rect.height + background.marges[1])))))
            elif background.repeat_x:
              for x in range(repeat): screen.blit(background.image, ((rect.x - (sx / background.distance) + ((x - math.floor(repeat / 2)) * (rect.width + background.marges[0]))), (rect.y - (sy / background.distance))))
            elif background.repeat_y:
              for y in range(repeat): screen.blit(background.image, ((rect.x - (sx / background.distance)), (rect.y - (sy / background.distance) + ((y - math.floor(repeat / 2)) * (rect.height + background.marges[1])))))
            else: screen.blit(background.image, (rect.x - (sx / background.distance), rect.y - (sy / background.distance)))
          else: #this is for when distance is set at 0, y'know when you divide by 0 and that gives an error, so we don't parallex at all and instead lock it regardless of scroll
            if background.repeat_x and background.repeat_y:
              for x in range(repeat):
                for y in range(repeat): screen.blit(background.image, (rect.x + ((x - math.floor(repeat / 2)) * (rect.width + background.marges[0])), background.rect.y + ((y - math.floor(repeat / 2)) * (rect.height + background.marges[1]))))
            elif background.repeat_x:
              for x in range(repeat): screen.blit(background.image, (rect.x + ((x - math.floor(repeat / 2)) * (rect.width + background.marges[0])), rect.y))
            elif background.repeat_y:
              for y in range(repeat): screen.blit(background.image, (rect.x, rect.y + ((y - math.floor(repeat / 2)) * (rect.height + background.marges[1]))))
            else: screen.blit(background.image, (rect.x, rect.y))
      
    repeat = 25
    for background in self.backgrounds:
      if background.is_animating: background.looped = background.timer.tally == len(background.images) - 1 and background.timer.time >= (background.anim_speed * dt) - 1
      if background.is_animating and not self.main.game_paused:
        try:
          if background.anim_speed > 0: background.image = background.images[background.timer.keep_count(background.anim_speed * dt, len(background.images), 0)]
          else: background.image = background.images[background.timer.tally]
        except IndexError: background.image = background.images[0]; background.timer.reset()

      if not cutscene: rect = background.rect; render(background, rect)

      else:
        background.last_frame_active = 0
        key_frame_rect = background.rect
        for key_object in self.main.rooms[self.main.current_room].cutscenes[self.main.selected_cutscene].animations:
          if key_object["Object"] == background and key_object["Frame"] > background.last_frame_active: background.last_frame_active = key_object["Frame"]
          if key_object["Object"] == background and key_object["Frame"] <= self.main.selected_key:
            if key_object["Rect"] != None:
              key_frame_rect = pygame.FRect(key_object["Rect"])
              if key_object["SOCR"] and self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key + 1: background.rect = background.key_frame_rect
            if self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key:
              if not key_object["Speed"]:
                background.cs_speed[0] += key_object["X Speed"] * dt
                background.cs_speed[1] += key_object["Y Speed"] * dt
                background.cs_speed[0] = round(background.cs_speed[1], 2)
                background.cs_speed[1] = round(background.cs_speed[1], 2)
              else:
                background.cs_speed_dest = key_object["Speed"]
                background.cs_dest[0] = background.rect.x + key_object["X Speed"]
                background.cs_dest[1] = background.rect.y + key_object["Y Speed"]
              background.hidden = key_object["Hidden"]
              if background.looped and key_object["B1"] and (self.main.playtest_on or self.main.playback_on): self.main.selected_key += 1
              if key_object["Action"] == "flip": background.timer.tally += 1; break
              if key_object["Action"] == "back": background.timer.tally -= 1; break
              if key_object["Action"] == "restart": background.timer.reset(); break
              if key_object["Action"] == "random": background.timer.tally = random.randrange(0, len(background.images)); break
        
        render(background, key_frame_rect)

      background.update()
      background.move(cutscene)



class Tile:
  def __init__(self, x, y, name, main):
    self.main = main
    self.type = name
    self.name = name
    self.speed = [0.0, 0.0]
    self.spawn_speed = [0.0, 0.0]
    self.spawn_location = [x, y]
    self.stood_on = False
    self.bring_player = True
    self.alive = True
    self.selected = False
    if name != "/":
      self.no_image = False
      self.offset = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["off"]
      self.ramp = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["ramp"]
      size = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["size"]
      self.rect = pygame.FRect((x + self.offset[0], y + self.offset[1]), (size[0], size[1]))
      self.type_dict = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]
      self.solid = "solid" in self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["flags"]
      self.slippery = "ice" in self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["flags"]
      self.flat = "flat" in self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["flags"]
      self.deviating_modes = []
      self.team = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["team"]
      try: self.destroy_delay = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["destr_delay"]
      except: pass
      self.anim_speed = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["anim_s"]
      if os.path.isdir(main.active_directory + f"Assets/tiles/" + name):
        self.images = []; self.is_animating = True
        if not self.main.snap_tile_image:
          for image in sorted(os.listdir(main.active_directory + f"Assets/tiles/" + name), key=extract_number): self.images.append(pygame.image.load(main.active_directory + f"Assets/tiles/" + name + "/" + image).convert_alpha())
        else:
          for image in sorted(os.listdir(main.active_directory + f"Assets/tiles/" + name), key=extract_number): self.images.append(pygame.transform.scale(pygame.image.load(main.active_directory + f"Assets/tiles/" + name + "/" + image).convert_alpha(), (self.main.tiles_size, self.main.tiles_size)))
        self.image = self.images[0]
      else:
        self.is_animating = False
        if not self.main.snap_tile_image: self.image = pygame.image.load(self.main.active_directory + f"Assets/tiles/" + name).convert_alpha()
        else: self.image = pygame.transform.scale(pygame.image.load(self.main.active_directory + f"Assets/tiles/" + name).convert_alpha(), (self.main.tiles_size, self.main.tiles_size))
        #except: self.image = pygame.Surface((self.main.tiles_size, self.main.tiles_size)); self.image.fill("Dark blue")
      self.chain_speed = 0
      self.broken_others = False
      self.only_breakable_by_chains = False
      self.destroy_if_stood_on = "diso" in self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["flags"]
      self.destroy_if_head_bump = "dihb" in self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["flags"]
      self.hp = -1
      self.spawn_hp = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["hp"]
      self.step_sound = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["step_sfx"]
      self.destroy_sound = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["destr_sfx"]
      if self.step_sound: self.step_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.step_sound)
      else: self.step_sfx = None
      if self.destroy_sound: self.destroy_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.destroy_sound)
      else: self.destroy_sfx = None
      self.destroy_anim = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["destr_anim"]
    else: self.image = pygame.transform.scale(pygame.image.load("Assets/editor/door_no_image.png").convert_alpha(), (32, 32)); self.rect = pygame.FRect((x, y), (self.main.tiles_size, self.main.tiles_size)); self.no_image = True
    self.destroyed = False
    self.instigator = False
    self.crumbs = []
    self.zones_can_move = False
    self.zones_can_rotate = False
    self.last_centerx, self.last_centery = self.rect.center
    self.image_size_manipulated = self.main.snap_tile_image
    self.rect_size_manipulated = self.main.snap_tile_rect
    self.key_frame_rect = self.rect
    self.last_frame_active = 0
    self.cs_speed = [0, 0]
    self.cs_dest = [0, 0]
    self.cs_speed_dest = 0
    self.hidden = False
    self.spawn_as_visible = True
    self.form = []
    self.layer = None
    self.timer = Timer()
    self.disperse_timer = Timer()
    self.chain_timer = Timer()

  def update(self, cutscene, dt=1):
    if not cutscene: rect = self.rect
    else: rect = self.key_frame_rect

    self.last_centerx, self.last_centery = self.rect.center

    if ((self.main.gamestate == 1 and not self.main.editor_mode) or (self.main.gamestate == 10 and self.main.editor_mode)) or (self.main.gamestate == 24 and self.main.playback_on):
      self.stood_on = False

      #self.main.rooms[self.main.current_room].layers.index(self.layer) == 0 and round(self.rect.x) - round(zone.rect.x) & round(self.main.tiles_size) == 0 and round(self.rect.y) - round(zone.rect.y) & round(self.main.tiles_size) == 0 and 
      for zone in self.main.rooms[self.main.current_room].zones:
        if self.rect.colliderect(zone.rect) and self.zones_can_move:
          if not zone.ease_motion: self.speed = zone.tile_speed
          else:
            if self.speed[0] < zone.tile_speed[0]: self.speed[0] += 0.25
            elif self.speed[0] > zone.tile_speed[0]: self.speed[0] -= 0.25
            elif self.speed[1] < zone.tile_speed[1]: self.speed[1] += 0.25
            elif self.speed[1] > zone.tile_speed[1]: self.speed[1] -= 0.25
            else: self.speed = zone.tile_speed
        if self.rect.colliderect(zone.rect) and self.zones_can_rotate: dx = (rect.centerx - zone.rect.centerx) * math.cos(math.radians((zone.tile_rotation / 10) * dt)) - (rect.centery - zone.rect.centery) * math.sin(math.radians((zone.tile_rotation / 10) * dt)); dy = (rect.centerx - zone.rect.centerx) * math.sin(math.radians((zone.tile_rotation / 10) * dt)) + (rect.centery - zone.rect.centery) * math.cos(math.radians((zone.tile_rotation / 10) * dt)); rect.center = (zone.rect.centerx + dx, zone.rect.centery + dy)
      
      rect.x += self.speed[0] * dt
      rect.y += self.speed[1] * dt
      self.speed[0] = round(self.speed[0], 2)
      self.speed[1] = round(self.speed[1], 2)

      rect.x += self.cs_speed[0] * dt
      rect.y += self.cs_speed[1] * dt
      self.cs_speed[0] = round(self.cs_speed[0], 2)
      self.cs_speed[1] = round(self.cs_speed[1], 2)

      if self.cs_speed_dest:
        if self.rect.x == self.cs_dest[0] and self.rect.y == self.cs_dest[1]: self.cs_speed_dest = 0
        else:
          if self.rect.x > self.cs_dest[0]: self.rect.x -= self.cs_speed_dest
          if self.rect.x < self.cs_dest[0]: self.rect.x += self.cs_speed_dest
          if abs(self.rect.x - self.cs_dest[0]) < self.cs_speed_dest: self.rect.x = self.cs_dest[0]
          if self.rect.y > self.cs_dest[1]: self.rect.y -= self.cs_speed_dest
          if self.rect.y < self.cs_dest[1]: self.rect.y += self.cs_speed_dest
          if abs(self.rect.y - self.cs_dest[1]) < self.cs_speed_dest: self.rect.y = self.cs_dest[1]

    if not cutscene: self.rect = rect
    self.key_frame_rect = rect

    if self.spawn_hp != -1 or not self.alive:
      if self.hp <= 0:
        if self.destroy_anim == "Disappear": self.hidden = True
        if self.destroy_anim == "Crumble" and not self.destroyed:
          self.hidden = True
          for x in range(random.randrange(2, 5)): self.crumbs.append(Crumble(self))
        if self.destroy_anim == "Poof": self.hidden = True
        if self.destroy_anim == "Disperse":
          self.image.fill("White", special_flags=pygame.BLEND_RGB_ADD)
          if self.disperse_timer.timer(3 * dt): self.hidden = True; self.image = pygame.image.load(self.main.active_directory + f"Assets/tiles/" + self.name).convert_alpha()
        if self.destroy_anim == "S Descend":
          self.rect.y += 1 * dt
          if self.rect.y > self.main.height: self.hidden = True
        if self.destroy_anim == "Descend":
          self.rect.y += 3 * dt
          if self.rect.y > self.main.height: self.hidden = True
        if self.destroy_anim == "F Descend":
          self.rect.y += 6 * dt
          if self.rect.y > self.main.height: self.hidden = True
        
        self.alive = False
        if (self.destroy_sound or self.destroy_sfx != None) and not self.destroyed:
          if type(self.destroy_sound) == list: self.destroy_sfx = pygame.mixer.Sound("Sounds/sfx/" + self.destroy_sound[random.randrange(0, len(self.destroy_sound))])
          self.destroy_sfx.play()
        self.destroyed = True
        
        if self.chain_speed and not self.broken_others:
          if self.chain_timer.timer(self.chain_speed):
            for tile in [tile for tile in self.layer.tiles if pygame.Rect((self.rect.x - 1, self.rect.y - 1), (self.rect.width + 2, self.rect.height + 2)).colliderect(tile.rect)]:
              tile.alive = False
              if not tile.destroy_sound: tile.destroy_sfx = self.destroy_sfx
              if tile.destroy_anim == "Disappear": tile.destroy_anim = self.destroy_anim
              tile.chain_speed = self.chain_speed
              self.broken_others = True
              tile.broken_others = False

  def regenerate_values(self):
    self.solid = "solid" in self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["flags"]
    self.flat = "flat" in self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["flags"]
    self.slippery = "ice" in self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["flags"]
    self.offset = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["off"]
    self.ramp = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["ramp"]
    size = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["size"]
    self.rect = pygame.FRect((self.rect.x, self.rect.y), (size[0], size[1]))
    self.anim_speed = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["anim_s"]
    self.destroy_if_stood_on = "diso" in self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["flags"]
    self.destroy_if_head_bump = "dihb" in self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["flags"]
    self.hp = -1
    self.spawn_hp = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["hp"]
    self.team = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["team"]
    self.step_sound = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["step_sfx"]
    self.destroy_sound = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["destr_sfx"]
    if self.step_sound: self.step_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.step_sound)
    else: self.step_sfx = None
    if self.destroy_sound: self.destroy_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.destroy_sound)
    else: self.destroy_sfx = None
    self.destroy_anim = self.main.tile_types[next(key for key, value in self.main.tile_types.items() if value.get("img") == self.type)]["destr_anim"]
    if "s" in self.deviating_modes: self.solid = not self.solid
    if "f" in self.deviating_modes: self.flat = not self.flat
    if "sl" in self.deviating_modes: self.slippery = not self.slippery


class Door(Tile):
  def __init__(self, x, y, name, room, main):
    super().__init__(x=x, y=y, name=name, main=main)
    self.open = True
    self.led_room = room
    self.led_pos = [x, y]
    self.requires_input = False
    self.passable = True
    self.spawn_passable = True
    self.hover_images = []
    self.unhover_images = []
    self.open_images = []
    self.close_images = []
    self.pop_images = []
    try:
      for image in sorted(os.listdir(main.active_directory + "Assets/tiles/" + name + "/hover/"), key=extract_number): self.hover_images.append(pygame.image.load(main.active_directory + f"Assets/tiles/" + name + "/" + image).convert_alpha())
    except: pass
    try:
      for image in sorted(os.listdir(main.active_directory + "Assets/tiles/" + name + "/unhover/"), key=extract_number): self.unhover_images.append(pygame.image.load(main.active_directory + f"Assets/tiles/" + name + "/" + image).convert_alpha())
    except: pass
    try:
      for image in sorted(os.listdir(main.active_directory + "Assets/tiles/" + name + "/open/"), key=extract_number): self.open_images.append(pygame.image.load(main.active_directory + f"Assets/tiles/" + name + "/" + image).convert_alpha())
    except: pass
    try:
      for image in sorted(os.listdir(main.active_directory + "Assets/tiles/" + name + "/close/"), key=extract_number): self.close_images.append(pygame.image.load(main.active_directory + f"Assets/tiles/" + name + "/" + image).convert_alpha())
    except: pass
    try:
      for image in sorted(os.listdir(main.active_directory + "Assets/tiles/" + name + "/pop/"), key=extract_number): self.pop_images.append(pygame.image.load(main.active_directory + f"Assets/tiles/" + name + "/" + image).convert_alpha())
    except: pass
    self.state = "idle"
    self.transition = []
    self.transition_speed_pre = 30
    self.transition_speed_post = 30
    self.transition_color = (0, 0, 0)
    self.transition_shape = "Circle.png"
    self.transition_override_ui = False
    self.transition_flag_1 = False
    self.transition_flag_2 = False
    self.transition_pre_immobilize_player = False
    self.transition_post_immobilize_player = False
    self.transition_play_door_and_player_animation = False
    self.t_playing = False
    self.t_over = False
    self.tfi = 0
    self.t_timer = Timer()
    self.hover_sound = ""
    self.enter_sound = ""
    self.exit_sound = ""
    if self.hover_sound: self.hover_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + self.hover_sound)
    else: self.hover_sfx = None
    if self.enter_sound: self.enter_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + self.enter_sound)
    else: self.enter_sfx = None
    if self.exit_sound: self.exit_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + self.exit_sound)
    else: self.exit_sfx = None
    self.hover_timer = Timer()
    self.open_timer = Timer()
    self.cutscene_transport = False
    
  def update(self, screen, cutscene=False, dt=1):
    if not cutscene: rect = self.rect
    else: rect = self.key_frame_rect

    screen.blit(self.image, (self.rect.x - self.main.camera.scroll[0], self.rect.y - self.main.camera.scroll[1]))
    if ((self.main.gamestate == 1 and not self.main.editor_mode) or (self.main.gamestate == 10 and self.main.editor_mode)) or (self.main.gamestate == 24 and self.main.playback_on):
      self.stood_on = False

      for zone in self.main.rooms[self.main.current_room].zones:
        if self.rect.colliderect(zone.rect) and self.zones_can_move:
          if not zone.ease_motion: self.speed = zone.tile_speed
          else:
            if self.speed[0] < zone.tile_speed[0]: self.speed[0] += 0.25
            elif self.speed[0] > zone.tile_speed[0]: self.speed[0] -= 0.25
            elif self.speed[1] < zone.tile_speed[1]: self.speed[1] += 0.25
            elif self.speed[1] > zone.tile_speed[1]: self.speed[1] -= 0.25
            else: self.speed = zone.tile_speed
        if self.rect.colliderect(zone.rect) and self.zones_can_rotate: dx = (rect.centerx - zone.rect.centerx) * math.cos(math.radians((zone.tile_rotation / 10) * dt)) - (rect.centery - zone.rect.centery) * math.sin(math.radians((zone.tile_rotation / 10) * dt)); dy = (rect.centerx - zone.rect.centerx) * math.sin(math.radians((zone.tile_rotation / 10) * dt)) + (rect.centery - zone.rect.centery) * math.cos(math.radians((zone.tile_rotation / 10) * dt)); rect.center = (zone.rect.centerx + dx, zone.rect.centery + dy)

      rect.x += self.speed[0] * dt
      rect.y += self.speed[1] * dt
      self.speed[0] = round(self.speed[0], 2)
      self.speed[1] = round(self.speed[1], 2)

      rect.x += self.cs_speed[0] * dt
      rect.y += self.cs_speed[1] * dt
      self.cs_speed[0] = round(self.cs_speed[0], 2)
      self.cs_speed[1] = round(self.cs_speed[1], 2)

      if self.cs_speed_dest:
        if self.rect.x == self.cs_dest[0] and self.rect.y == self.cs_dest[1]: self.cs_speed_dest = 0
        else:
          if self.rect.x > self.cs_dest[0]: self.rect.x -= self.cs_speed_dest
          if self.rect.x < self.cs_dest[0]: self.rect.x += self.cs_speed_dest
          if abs(self.rect.x - self.cs_dest[0]) < self.cs_speed_dest: self.rect.x = self.cs_dest[0]
          if self.rect.y > self.cs_dest[1]: self.rect.y -= self.cs_speed_dest
          if self.rect.y < self.cs_dest[1]: self.rect.y += self.cs_speed_dest
          if abs(self.rect.y - self.cs_dest[1]) < self.cs_speed_dest: self.rect.y = self.cs_dest[1]

    if cutscene:
      self.rect = rect
      for key_object in self.main.rooms[self.main.current_room].cutscenes[self.main.selected_cutscene].animations:
        if key_object["Object"] == self and key_object["Frame"] > self.last_frame_active: self.last_frame_active = key_object["Frame"]

        if key_object["Object"] == self and key_object["Frame"] <= self.main.selected_key:
          if key_object["Rect"] != None:
            self.key_frame_rect = pygame.FRect(key_object["Rect"])
            if key_object["SOCR"] and self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key - 1: self.rect = self.key_frame_rect
          if self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key:
            if not key_object["Speed"]:
              self.cs_speed[0] += key_object["X Speed"] * dt
              self.cs_speed[1] += key_object["Y Speed"] * dt
              self.cs_speed[0] = round(self.cs_speed[1], 2)
              self.cs_speed[1] = round(self.cs_speed[1], 2)
            else:
              self.cs_speed_dest = key_object["Speed"]
              self.cs_dest[0] = self.rect.x + key_object["X Speed"]
              self.cs_dest[1] = self.rect.y + key_object["Y Speed"]
            self.hidden = key_object["Hidden"]
            if self.alive: self.cutscene_transport = key_object["Action"] == "transport"
    else: self.key_frame_rect = rect

    if not self.no_image:
      if self.state == "idle":
        if self.is_animating: self.image = self.images[self.timer.keep_count(self.anim_speed, len(self.images), 0)]
      if self.state == "hover":
        if self.hover_images: self.image = self.hover_images[self.hover_timer.count(self.anim_speed, len(self.hover_images), 0)]
      if self.state == "open":
        if self.open_images: self.image = self.open_images[self.open_timer.count(self.anim_speed, len(self.open_images), 0)]
    
  def transport(self, player):
    self.main.playback_on, self.main.selected_key = False, 0; player.rect.x, player.rect.y = self.led_pos[0], self.led_pos[1]; player.key_frame_rect.x, player.key_frame_rect.y = self.led_pos[0], self.led_pos[1]; self.main.time_since_start = time()
    for button in self.main.rooms[self.led_room].menu["items"]: button["Clicked"] = False

  def transport_everyone(self):
    self.main.playback_on, self.main.selected_key = False, 0
    for player in self.main.players: player.rect.x, player.rect.y = self.led_pos[0], self.led_pos[1]; player.key_frame_rect.x, player.key_frame_rect.y = self.led_pos[0], self.led_pos[1]; self.main.time_since_start = time()
    for button in self.main.rooms[self.led_room].menu["items"]: button["Clicked"] = False

  def play_transition(self, screen, dt=1):
    if self.t_playing:
      if not self.transition: self.t_over = True; self.t_playing = False
      if self.transition:
        if self.t_over: self.tfi -= self.transition_speed_post * dt
        else: self.tfi += self.transition_speed_pre * dt
      if "Fade to Room" in self.transition:
        c = maxint(minint(self.tfi, 0), 255)
        screen.set_alpha(abs(c - 255))
        if self.tfi > 255: self.t_over = True
        if self.tfi < 0: self.tfi = 0; self.t_playing = False; self.t_over = False; screen.set_alpha(255)
      if "Fade to Color" in self.transition:
        c = maxint(minint(self.tfi, 0), 255)
        if tuple(self.transition_color) == (0, 0, 0): screen.fill((c, c, c), special_flags=pygame.BLEND_RGB_SUB)
        elif tuple(self.transition_color) == (255, 255, 255): screen.fill((c, c, c), special_flags=pygame.BLEND_RGB_ADD)
        else: screen.fill((c, c, c), special_flags=pygame.BLEND_RGB_MULT)
        if self.tfi > 255: self.t_over = True
        if self.tfi < 0: self.tfi = 0; self.t_playing = False; self.t_over = False
      if "Cut to Color" in self.transition:
        if self.tfi: screen.fill(self.transition_color)
        if self.tfi > 255: self.t_over = True
        if self.tfi < 0: self.tfi = 0; self.t_playing = False; self.t_over = False
      if "Gaussian Blur" in self.transition:
        if self.tfi: screen = pygame.transform.gaussian_blur(screen, round(self.tfi / 40), self.transition_flag_1)
        if self.tfi > 255: self.t_over = True
        if self.tfi < 0: self.tfi = 0; self.t_playing = False; self.t_over = False
      if "Box Blur" in self.transition:
        if self.tfi: screen = pygame.transform.box_blur(screen, minint(round(self.tfi), 0), self.transition_flag_1)
        if self.tfi > 255: self.t_over = True
        if self.tfi < 0: self.tfi = 0; self.t_playing = False; self.t_over = False
      if "Pixelate" in self.transition:
        if self.tfi:
          if not self.transition_flag_1: screen = pygame.transform.scale(screen, (abs(round(self.tfi) - 255), abs(round(self.tfi) - 255)))
          else: screen = pygame.transform.smoothscale(screen, (abs(round(self.tfi) - 255), abs(round(self.tfi) - 255)))
        if self.tfi > 255: self.t_over = True
        if self.tfi < 0: self.tfi = 0; self.t_playing = False; self.t_over = False
      if "Rotate" in self.transition:
        if self.tfi:
          if self.transition_flag_1: screen = pygame.transform.rotate(screen, round(self.tfi / 255) * 360)
          else: screen = pygame.transform.rotate(screen, round(self.tfi / 255) * (180))
        if self.tfi > 255: self.t_over = True
        if self.tfi < 0: self.tfi = 0; self.t_playing = False; self.t_over = False
      if "Shrink to Shape" in self.transition:
        if self.tfi:
          shape = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(f"Assets/editor/shapes/{self.transition_shape}").convert_alpha(), (abs(((self.tfi / 255) * (self.main.width * 2)) - (self.main.width * 2)), abs(((self.tfi / 255) * (self.main.height * 2)) - (self.main.height * 2)))), self.tfi * int(self.transition_flag_2))
          if not self.transition_flag_1:
            shape.blit(screen, (-((WIDTH / 2) - shape.get_width() / 2), -((HEIGHT / 2) - shape.get_height() / 2)), special_flags=pygame.BLEND_RGB_ADD)
            screen.fill(self.transition_color)
            screen.blit(shape, ((WIDTH / 2) - shape.get_width() / 2, (HEIGHT / 2) - shape.get_height() / 2))
          else:
            shape.blit(screen, (-((self.main.players[0].rect.x + (self.main.players[0].rect.width / 2)) - shape.get_width() / 2), -((self.main.players[0].rect.y + (self.main.players[0].rect.height / 2)) - shape.get_height() / 2)), special_flags=pygame.BLEND_RGB_ADD)
            screen.fill(self.transition_color)
            screen.blit(shape, ((self.main.players[0].rect.x + (self.main.players[0].rect.width / 2)) - shape.get_width() / 2, (self.main.players[0].rect.y + (self.main.players[0].rect.height / 2)) - shape.get_height() / 2))
        if self.tfi > 255: self.t_over = True
        if self.tfi < 0: self.tfi = 0; self.t_playing = False; self.t_over = False
    return screen


class Crumble:
  def __init__(self, tile):
    try: self.rect = pygame.Rect((random.randrange(tile.rect.x, tile.rect.right), random.randrange(tile.rect.y, tile.rect.bottom)), (tile.rect.width / random.randrange(4, 8), tile.rect.height / random.randrange(4, 8)))
    except: self.rect = pygame.Rect((tile.rect.x, tile.rect.y), (4, 4))
    slices = chop_surface(tile.image, self.rect.width, self.rect.height)
    self.image = slices[random.randrange(0, len(slices))]
    self.x_vel, self.y_vel = random.randrange(-6, 7), random.randrange(-7, 1)
    self.alive_for = 0
    self.lifetime = 30

  def update(self, dt):
    if self.x_vel < 0: self.x_vel += 1 * dt
    if self.x_vel > 0: self.x_vel -= 1 * dt
    self.y_vel += 1 * dt
    self.rect.x += self.x_vel * dt
    self.rect.y += self.y_vel * dt
    self.alive_for += 1


class Background:
  def __init__(self, x, y, image_path, speed, distance, main):
    self.main = main
    self.timer = Timer()
    self.anim_speed = 1
    self.loop = True
    self.load_bg(x, y, main.active_directory + image_path)
    self.image_file_without_dir = image_path
    self.distance = distance
    self.speed = speed
    self.repeat_x = False
    self.repeat_y = False
    self.x_scroll = True
    self.y_scroll = True
    self.hm_for_move = True
    self.vm_for_move = True
    self.marges = [0, 0]
    self.foreground = False
    self.shader = ""
    self.spawn_location = [x, y]
    self.alpha = 255
    self.key_frame_rect = self.rect
    self.last_frame_active = 0
    self.cs_speed = [0, 0]
    self.cs_dest = [0, 0]
    self.cs_speed_dest = 0
    self.hidden = False
    self.looped = False
    self.spawn_as_visible = True
    self.alive = True
    self.take_variable = False
    self.character_string = ["", ""]
    self.take_index = 0
    self.player_or_team = False

  def load_bg(self, x, y, image_path):
    self.images = []
    if os.path.isdir(image_path):
      self.is_animating = True
      for image in sorted(os.listdir(image_path), key=extract_number): self.images.append(pygame.image.load(image_path + "/" + image).convert_alpha())
      self.image = self.images[0]
    else: self.image = pygame.image.load(image_path).convert_alpha(); self.is_animating = False
    self.rect = pygame.FRect((x, y), (self.image.get_width(), self.image.get_height()))
    self.image_file = image_path
    self.name = image_path

  def update(self):
    if self.take_variable:
      if self.player_or_team:
        if self.take_index < len(self.main.teams):
          if self.name != self.main.active_directory + "Assets/backgrounds/" + self.character_string[0] + self.main.teams[self.take_index].name + self.character_string[1]:
            try: self.load_bg(self.rect.x, self.rect.y, self.main.active_directory + "Assets/backgrounds/" + self.character_string[0] + self.main.teams[self.take_index].name + self.character_string[1])
            except FileNotFoundError: pass
      else:
        if self.take_index < len(self.main.players):
          if self.name != self.main.active_directory + "Assets/backgrounds/" + self.character_string[0] + self.main.players[self.take_index].name + self.character_string[1]:
            try: self.load_bg(self.rect.x, self.rect.y, self.main.active_directory + "Assets/backgrounds/" + self.character_string[0] + self.main.players[self.take_index].name + self.character_string[1])
            except FileNotFoundError: pass
      

  def move(self, cutscene=False, dt=1):
    if not cutscene: rect = self.rect
    else: rect = self.key_frame_rect
    if ((self.main.gamestate == 1 and not self.main.editor_mode) or (self.main.gamestate == 10 and self.main.editor_mode)) or (self.main.gamestate == 24 and self.main.playback_on):
      self.rect.x += self.speed[0] * dt
      self.rect.y += self.speed[1] * dt
      self.rect.x += self.cs_speed[0] * dt
      self.rect.y += self.cs_speed[1] * dt
      if self.cs_speed_dest:
        if self.rect.x == self.cs_dest[0] and self.rect.y == self.cs_dest[1]: self.cs_speed_dest = 0
        else:
          if self.rect.x > self.cs_dest[0]: self.rect.x -= self.cs_speed_dest
          if self.rect.x < self.cs_dest[0]: self.rect.x += self.cs_speed_dest
          if abs(self.rect.x - self.cs_dest[0]) < self.cs_speed_dest: self.rect.x = self.cs_dest[0]
          if self.rect.y > self.cs_dest[1]: self.rect.y -= self.cs_speed_dest
          if self.rect.y < self.cs_dest[1]: self.rect.y += self.cs_speed_dest
          if abs(self.rect.y - self.cs_dest[1]) < self.cs_speed_dest: self.rect.y = self.cs_dest[1]
    if ((self.main.gamestate == 1 and not self.main.editor_mode) or (self.main.gamestate == 10 and self.main.editor_mode)): width, height = self.main.width, self.main.height
    else: width, height = WIDTH, HEIGHT
    if self.hm_for_move:
      if self.speed[0]:
        if self.distance != 0:
          if rect.x + rect.width < self.main.camera.scroll[0] / self.distance: rect.x = (self.main.camera.scroll[0] / self.distance) + width
        else:
          if rect.x + rect.width < 0: rect.x = width
        if self.distance != 0:
          if rect.x > (self.main.camera.scroll[0] / self.distance) + width: rect.x = (self.main.camera.scroll[0] / self.distance) - rect.width
        else:
          if rect.x > width: rect.x = 0 - rect.width
    if self.vm_for_move:
      if self.speed[1]:
        if self.distance != 0:
          if rect.y > (self.main.camera.scroll[1] / self.distance) + height: rect.y = (self.main.camera.scroll[1] / self.distance) - rect.height
        else:
          if rect.y > height: rect.y = 0 - rect.height
        if self.distance != 0:
          if rect.y + rect.height < self.main.camera.scroll[1] / self.distance: rect.y = (self.main.camera.scroll[1] / self.distance) + height
        else:
          if rect.y + rect.height < 0: rect.y = height


class Collectible_Type:
  def __init__(self, name, stat, value, sfx, main):
    self.frames = os.listdir(main.active_directory + "Assets/collectibles/" + name)
    self.name = name; self.type = name
    self.stat = stat
    self.value = value
    self.sound = sfx
    try: self.sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + sfx)
      #if type(sfx) == list: self.sfx = pygame.mixer.Sound("Sounds/sfx/" + sfx[0])
      #else: self.sfx = pygame.mixer.Sound("Sounds/sfx/" + sfx)
    except: self.sfx = None
    self.images = []
    for image in self.frames: self.images.append(pygame.image.load(main.active_directory + "Assets/collectibles/" + name + "/" + image).convert_alpha())


class Collectible:
  def __init__(self, x, y, ctype, main):
    self.main = main
    self.type = ctype
    self.name = ctype
    self.index_type = next((key for key, value in main.collectible_types.items() if value.get("img") == self.type), None)
    self.offset = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["off"]
    self.size = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["size"]
    self.rect = pygame.FRect((x, y), (self.size[0], self.size[1]))
    self.speed = [0.0, 0.0]
    self.spawn_speed = [0.0, 0.0]
    self.frames = os.listdir(main.active_directory + "Assets/collectibles/" + self.type)
    self.stat = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["stat"]
    self.value = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["value"]
    self.sound = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["sfx"]
    try: self.sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + self.sound)
    except: self.sfx = None
    self.images = []
    self.frame = 0
    self.timer = Timer()
    for image in self.frames: self.images.append(pygame.image.load(main.active_directory + "Assets/collectibles/" + self.type + "/" + image).convert_alpha())
    self.anim_speed = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["anim_s"]
    self.solid = True
    self.spawn_location = [x, y]
    self.key_frame_rect = self.rect
    self.last_frame_active = 0
    self.cs_speed = [0, 0]
    self.cs_dest = [0, 0]
    self.cs_speed_dest = 0
    self.hidden = "hidden" in self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["flags"]
    self.spawn_as_visible = True
    self.zones_can_move = False
    self.zones_can_rotate = False
    self.price_stat = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["ps"]
    self.price_value = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["pv"]
    self.price_text_position = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["ptp"]#everything is veery different İ know İ know
    self.price_text_mode = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["ptm"]
    self.price_exchange = "pe" in self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["flags"]
    self.price_decrement = "pd" in self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["flags"]
    self.debt_drop_sound = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["debt_sfx"]
    self.grabbable = True
    self.trigger_cutscene = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["cs"]
    self.trigger_cutscene2 = ""
    self.font = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["font"]
    self.font_size = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["font_size"]
    if self.debt_drop_sound != "":
      if type(self.debt_drop_sound) == list: self.debt_drop_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.debt_drop_sound[0])
      else: self.debt_drop_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.debt_drop_sound)
    else: self.debt_drop_sfx = None
    self.active_debt = False
    if type(self.font) == pygame.Font: self.font_str = None; self.font = self.font
    elif self.font != "None" and self.font: self.font_str = self.font; self.font = pygame.Font(self.font_str, self.font_size)
    else: self.font_str = ""; self.font = pygame.Font(None, self.font_size)
    self.alive = True

  def regenerate_values(self):
    self.index_type = next((key for key, value in self.main.collectible_types.items() if value.get("img") == self.type), None)
    self.anim_speed = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["anim_s"]
    self.offset = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["off"]
    self.size = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["size"]
    self.stat = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["stat"]
    self.value = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["value"]
    self.sound = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["sfx"]
    self.hidden = "hidden" in self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["flags"]
    self.price_stat = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["ps"]
    self.price_value = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["pv"]
    self.price_text_position = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["ptp"]#everything is veery different İ know İ know
    self.price_text_mode = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["ptm"]
    self.price_exchange = "pe" in self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["flags"]
    self.price_decrement = "pd" in self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["flags"]
    self.debt_drop_sound = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["debt_sfx"]
    self.trigger_cutscene = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["cs"]
    self.font = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["font"]
    self.font_size = self.main.collectible_types[next(key for key, value in self.main.collectible_types.items() if value.get("img") == self.type)]["font_size"]
    if self.sound != "":
      if type(self.sound) == list: self.sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.debt_drop_sound[0])
      else: self.sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.sound)
    else: self.sfx = None
    if self.debt_drop_sound != "":
      if type(self.debt_drop_sound) == list: self.debt_drop_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.debt_drop_sound[0])
      else: self.debt_drop_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.debt_drop_sound)
    else: self.debt_drop_sfx = None
    self.active_debt = False
    if type(self.font) == pygame.Font: self.font_str = None; self.font = self.font
    elif self.font != "None" and self.font: self.font_str = self.font; self.font = pygame.Font(self.font_str, self.font_size)
    else: self.font_str = ""; self.font = pygame.Font(None, self.font_size)
    self.alive = True

  def update(self, cutscene, dt=1):
    if not cutscene: rect = self.rect
    else: rect = self.key_frame_rect

    if ((self.main.gamestate == 1 and not self.main.editor_mode) or (self.main.gamestate == 10 and self.main.editor_mode)) or (self.main.gamestate == 24 and self.main.playback_on):
      for zone in self.main.rooms[self.main.current_room].zones:
        if self.rect.colliderect(zone.rect) and self.zones_can_move:
          if not zone.ease_motion: self.speed = zone.tile_speed
          else:
            if self.speed[0] < zone.tile_speed[0]: self.speed[0] += 0.25
            elif self.speed[0] > zone.tile_speed[0]: self.speed[0] -= 0.25
            elif self.speed[1] < zone.tile_speed[1]: self.speed[1] += 0.25
            elif self.speed[1] > zone.tile_speed[1]: self.speed[1] -= 0.25
            else: self.speed = zone.tile_speed
        if self.rect.colliderect(zone.rect) and self.zones_can_rotate: dx = (rect.centerx - zone.rect.centerx) * math.cos(math.radians((zone.tile_rotation / 10) * dt)) - (rect.centery - zone.rect.centery) * math.sin(math.radians((zone.tile_rotation / 10) * dt)); dy = (rect.centerx - zone.rect.centerx) * math.sin(math.radians((zone.tile_rotation / 10) * dt)) + (rect.centery - zone.rect.centery) * math.cos(math.radians((zone.tile_rotation / 10) * dt)); rect.center = (zone.rect.centerx + dx, zone.rect.centery + dy)
      
      rect.x += self.speed[0] * dt
      rect.y += self.speed[1] * dt
      self.speed[0] = round(self.speed[0], 2)
      self.speed[1] = round(self.speed[1], 2)

      rect.x += self.cs_speed[0] * dt
      rect.y += self.cs_speed[1] * dt
      self.cs_speed[0] = round(self.cs_speed[0], 2)
      self.cs_speed[1] = round(self.cs_speed[1], 2)

      if self.cs_speed_dest:
        if self.rect.x == self.cs_dest[0] and self.rect.y == self.cs_dest[1]: self.cs_speed_dest = 0
        else:
          if self.rect.x > self.cs_dest[0]: self.rect.x -= self.cs_speed_dest
          if self.rect.x < self.cs_dest[0]: self.rect.x += self.cs_speed_dest
          if abs(self.rect.x - self.cs_dest[0]) < self.cs_speed_dest: self.rect.x = self.cs_dest[0]
          if self.rect.y > self.cs_dest[1]: self.rect.y -= self.cs_speed_dest
          if self.rect.y < self.cs_dest[1]: self.rect.y += self.cs_speed_dest
          if abs(self.rect.y - self.cs_dest[1]) < self.cs_speed_dest: self.rect.y = self.cs_dest[1]

  def display_price_tag(self, screen, x, y):
    try:
      offset = 4
      for coin_type in self.main.collectible_types:
        if coin_type.stat == self.price_stat and "Image" in self.price_text_mode: image = coin_type.images[0]; break
      if self.price_text_mode == "Value Stat": text = self.font.render(f"{self.price_value} {self.price_stat}", True, "White")
      if self.price_text_mode == "Stat Value": text = self.font.render(f"{self.price_stat} {self.price_value}", True, "White")
      if self.price_text_mode == "Value Image": text = self.font.render(f"{self.price_value} {self.price_stat}", True, "White"); screen.blit(image, (x, y))
      if self.price_text_mode == "Image Value": text = self.font.render(f"{self.price_stat} {self.price_value}", True, "White"); screen.blit(image, (x, y))
      if self.price_text_position == "Below": screen.blit(text, (x + ((self.rect.width / 2) - (text.get_width() / 2)), y + self.rect.height + offset))
      if self.price_text_position == "Above": screen.blit(text, (x + ((self.rect.width / 2) - (text.get_width() / 2)), y - (text.get_height() + offset)))
      if self.price_text_position == "Left": screen.blit(text, (x - (text.get_width() + offset), y + ((self.rect.height / 2) - (text.get_height() / 2))))
      if self.price_text_position == "Right": screen.blit(text, (x + self.rect.width + offset, y + ((self.rect.height / 2) - (text.get_height() / 2))))
    except: pass

class Entity_Type:
  def __init__(self, character, hp, stat, value, behaviors, range, drops, defeat_anim, main):
    self.character = character
    self.hp = hp
    self.stat = stat
    self.value = value
    self.behaviors = behaviors
    self.range = range
    self.drops = drops
    self.defeat_anim = defeat_anim
    self.image = pygame.image.load(main.active_directory + f"Assets/characters/{self.character.character}/idle/1.png").convert_alpha()


class Zone:
  def __init__(self, x, y, main):
    self.main = main
    self.rect = pygame.Rect((x, y), (self.main.tiles_size, self.main.tiles_size))
    self.key_frame_rect = pygame.Rect((0, 0), (0, 0))
    self.surface = pygame.Surface((self.rect.width, self.rect.height))
    self.texture = pygame.image.load("Assets/editor/zone texture.png").convert_alpha()
    self.trigger_event = []
    self.trigger_cutscene = ""
    self.passed = False
    self.left = False
    self.multi_active = False
    self.entity_active = False
    self.void = False
    self.ease_motion = False
    self.enter_sound = ""
    self.exit_sound = ""
    self.track_volume = 1.0
    self.gravity = 1.0
    self.color = (255, 0, 0)
    self.tile_speed = [0.0, 0.0]
    self.tile_rotation = 0
    self.texture.fill(self.color, special_flags=pygame.BLEND_RGB_MIN)
    if self.enter_sound: self.enter_sfx = pygame.mixer.Sound("Sounds/sfx/" + self.enter_sound)
    if self.exit_sound: self.exit_sfx = pygame.mixer.Sound("Sounds/sfx/" + self.exit_sound)
    self.timer = Timer()

  def draw(self, screen):
    dim_color = []
    for color in self.color: dim_color.append(color / 2)
    self.surface.fill((50, 0, 0))
    for x in range(self.rect.left, self.rect.right, self.texture.get_width()):
      for y in range(self.rect.top, self.rect.bottom, self.texture.get_height()):
        self.surface.blit(self.texture, (x - self.rect.left, y - self.rect.top))
    pygame.draw.rect(screen, dim_color, ((self.rect.x - self.main.camera.scroll[0] - 1, self.rect.y - self.main.camera.scroll[1] - 1), (self.rect.width + 2, self.rect.height + 2)), 1)
    self.surface.set_alpha(self.timer.oscillate(FPS / 20, 85, 50) + int(self.main.selected_object == self) * 30)
    screen.blit(self.surface, (self.rect.x - self.main.camera.scroll[0], self.rect.y - self.main.camera.scroll[1]))
    if self.tile_rotation: pygame.draw.circle(screen, "White", (self.rect.centerx - self.main.camera.scroll[0], self.rect.centery - self.main.camera.scroll[1]), 5, 1)


class Text:
  def __init__(self, x, y, font, font_size, main):
    self.main = main
    try:
      try:
        if type(font) == pygame.Font: self.font_str = None; self.font = font
        elif font != None: self.font_str = font; self.font = pygame.Font(self.font_str, font_size)
        else: self.font_str = ""; self.font = pygame.Font(None, font_size)
      except: self.font = pygame.Font(main.active_directory + "Fonts/" + font, font_size); self.font_str = main.active_directory + "Fonts/" + font
    except: self.font = pygame.font.SysFont(font, font_size); self.font_str = font
    self.size = font_size
    self.behaviors = []
    self.text = "A B C"
    self.color = (255, 255, 255)
    self.bg_color = "Transparent"
    self.outline_color = (0, 0, 0)
    self.bold = False
    self.italic = False
    self.underline = False
    self.strikethrough = False
    self.anti_aliasing = False
    self.align = "Left"
    self.margin = 0
    self.direction = "LTR"
    self.rotation = 0
    self.scale = [0, 0]
    self.opacity = 255
    self.outline_thickness = 0
    self.flip = [False, False]
    self.capitalization_mode = "Default"
    self.take_variable = False
    self.character_string = ["", ""]
    self.take_index = 0
    self.player_or_team = False
    self.image = self.font.render(self.text, self.anti_aliasing, self.color, wraplength=self.margin)
    self.rect = pygame.Rect((x, y), (self.image.get_width(), self.image.get_height()))
    self.layer = 1
    self.font.set_script("Arab")
    self.ui_mode = False
    self.hidden = False
    self.spawn_as_visible = True
    self.cs_speed = [0, 0]
    self.cs_dest = [0, 0]
    self.cs_speed_dest = 0
    self.key_frame_rect = self.rect
    self.name = self.text
    self.spawn_location = [self.rect.x, self.rect.y]
    self.timer = Timer()
    self.deceives = [0, 0]

  def regenerate(self):
    try: self.font = pygame.Font(self.font_str, self.size)
    except: self.font = pygame.font.SysFont(self.font_str, self.size)
    self.font.set_script("Arab")
    self.font.set_bold(self.bold)
    self.font.set_italic(self.italic)
    self.font.set_underline(self.underline)
    self.font.set_strikethrough(self.strikethrough)
    if self.align == "Left": self.font.align = pygame.FONT_LEFT
    if self.align == "Center": self.font.align = pygame.FONT_CENTER
    if self.align == "Right": self.font.align = pygame.FONT_RIGHT
    if self.direction == "LTR": self.font.set_direction(pygame.DIRECTION_LTR)
    if self.direction == "RTL": self.font.set_direction(pygame.DIRECTION_RTL)
    if self.direction == "TTB": self.font.set_direction(pygame.DIRECTION_TTB)
    if self.direction == "BTT": self.font.set_direction(pygame.DIRECTION_BTT)
    text = self.text
    if self.capitalization_mode == "All decapitalize": text = self.text.lower()
    elif self.capitalization_mode == "All capitalize": text = self.text.upper()
    elif self.capitalization_mode == "First capitalize": text = self.text.capitalize()
    else: text = self.text
    if self.bg_color == "Transparent": self.image = self.font.render(text, self.anti_aliasing, self.color, wraplength=self.margin).convert_alpha()
    else: self.image = self.font.render(text, self.anti_aliasing, self.color, self.bg_color, self.margin).convert_alpha()
    if self.scale[0] > 0 and self.scale[1] > 0: self.image = pygame.transform.scale(self.image, (self.scale[0], self.scale[1]))
    elif self.scale[0] > 0: self.image = pygame.transform.scale(self.image, (self.scale[0], self.image.get_height()))
    elif self.scale[1] > 0: self.image = pygame.transform.scale(self.image, (self.image.get_width(), self.scale[1]))
    self.image = pygame.transform.rotate(self.image, self.rotation)
    self.image = pygame.transform.flip(self.image, self.flip[0], self.flip[1])
    if self.outline_thickness:
      ol_image = self.image
      self.image = pygame.mask.from_surface(self.image).convolve(pygame.mask.Mask((self.outline_thickness, self.outline_thickness), fill=True)).to_surface(setcolor=self.outline_color, unsetcolor=self.image.get_colorkey()).convert_alpha()
      self.image.blit(ol_image, (self.outline_thickness / 2, self.outline_thickness / 2))
    self.image.set_alpha(self.opacity)
    self.rect.width, self.rect.height = self.image.get_width(), self.image.get_height()
    self.name = self.text

  def update(self, dt=1):
    if self.take_variable:
      if self.character_string[0].endswith("<PLAYEREXISTS>") and len(self.main.players) <= self.take_index: self.text = self.character_string[0][:-len("<PLAYEREXISTS>")]; self.regenerate()
      elif self.character_string[1].endswith("<PLAYEREXISTS>"): self.text = self.character_string[1][:-len("<PLAYEREXISTS>")]; self.regenerate()
      if self.character_string[0].endswith("<PLAYERIN>") and len([player for player in self.main.players if player.in_]) <= self.take_index: self.text = self.character_string[0][:-len("<PLAYERIN>")]; self.regenerate()
      elif self.character_string[1].endswith("<PLAYERIN>"): self.text = self.character_string[1][:-len("<PLAYERIN>")]; self.regenerate()
      #elif self.character_string[0].endswith("<PLAYERIN>") and self.main.players[self.take_index].in_: self.text = self.character_string[0][:-len("<PLAYERIN>")]; self.regenerate()
      #elif self.character_string[1].endswith("<PLAYERIN>"): self.text = self.character_string[1][:-len("<PLAYERIN>")]; self.regenerate()
      elif self.character_string[0].endswith("<BUTTONTEXT>"): self.text = self.main.current_button_text; self.regenerate()
      elif self.character_string[1].endswith("<BUTTONTEXT>"): self.text = self.main.current_button_text; self.regenerate()
      elif self.character_string[0].endswith("<BUTTONTEXTHASIMAGE>"):
        self.text = self.main.current_button_text if self.main.current_button_has_image else "           "; self.regenerate()
      elif self.character_string[1].endswith("<BUTTONTEXTHASIMAGE>"):
        self.text = self.main.current_button_text if self.main.current_button_has_image else "           "; self.regenerate()
      else:
        if self.player_or_team:
          if self.take_index < len(self.main.teams):
            if self.text != self.character_string[0] + self.main.teams[self.take_index].name + self.character_string[1]:
              self.text = self.character_string[0] + self.main.teams[self.take_index].name + self.character_string[1]
              self.regenerate()
          else: self.text = "Take Index Exceeds Teams Amount"
        else:
          if self.take_index < len(self.main.players):
            if self.text != self.character_string[0] + self.main.players[self.take_index].name + self.character_string[1]:
              self.text = self.character_string[0] + self.main.players[self.take_index].name + self.character_string[1]
              self.regenerate()
          else: self.text = "Take Index Exceeds Players Amount"

    self.behave(dt)

  def behave(self, dt=1):
    t = pygame.time.get_ticks() / 1000
    if "shake h" in self.behaviors: self.deceives[0] = random.randint(-2, 2)
    if "shake v" in self.behaviors: self.deceives[1] = random.randint(-2, 2)
    if "freak out" in self.behaviors: self.deceives = [random.randint(-10, 10), random.randint(-10, 10)]
    if "float h" in self.behaviors: self.deceives[0] = math.sin(t * 5) * 5
    if "float v" in self.behaviors: self.deceives[1] = math.sin(t * 5) * 5
    if "float h slow" in self.behaviors: self.deceives[0] = math.sin((t / 2) * 5) * 5 
    if "float v slow" in self.behaviors: self.deceives[1] = math.sin((t / 2) * 5) * 5
    if "float h fast" in self.behaviors: self.deceives[0] = math.sin((t * 2) * 5) * 5
    if "float v fast" in self.behaviors: self.deceives[1] = math.sin((t * 2) * 5) * 5
    if "hover h" in self.behaviors: self.deceives[0] = math.sin(t * 5) * 10
    if "hover v" in self.behaviors: self.deceives[1] = math.sin(t * 5) * 10
    if "hover h slow" in self.behaviors: self.deceives[0] = math.sin((t / 2) * 5) * 10
    if "hover v slow" in self.behaviors: self.deceives[1] = math.sin((t / 2) * 5) * 10
    if "hover h fast" in self.behaviors: self.deceives[0] = math.sin((t * 2) * 5) * 10
    if "hover v fast" in self.behaviors: self.deceives[1] = math.sin((t * 2) * 5) * 10
    if "oscillate h" in self.behaviors: self.deceives[0] = (2 * abs(2 * ((t * 1) % 1) - 1) - 1) * 10
    if "oscillate v" in self.behaviors: self.deceives[1] = (2 * abs(2 * ((t * 1) % 1) - 1) - 1) * 10
    if "oscillate h slow" in self.behaviors: self.deceives[0] = (2 * abs(2 * ((t * 0.5) % 1) - 1) - 1) * 8
    if "oscillate v slow" in self.behaviors: self.deceives[1] = (2 * abs(2 * ((t * 0.5) % 1) - 1) - 1) * 8
    if "oscillate h fast" in self.behaviors: self.deceives[0] = (2 * abs(2 * ((t * 2) % 1) - 1) - 1) * 10
    if "oscillate v fast" in self.behaviors: self.deceives[1] = (2 * abs(2 * ((t * 2) % 1) - 1) - 1) * 10
    if "get h" in self.behaviors: self.deceives[0] = 2 * (2 * ((t * 1) % 1) - 1) - 1
    if "get v" in self.behaviors: self.deceives[1] = 2 * (2 * ((t * 1) % 1) - 1) - 1
    if "get h fast" in self.behaviors: self.deceives[0] = 2 * (2 * ((t * 2) % 1) - 1) - 1
    if "get v fast" in self.behaviors: self.deceives[1] = 2 * (2 * ((t * 2) % 1) - 1) - 1
    if "hop up slow" in self.behaviors: self.deceives[1] = -abs(math.sin((t / 2) * 5) * 15)
    if "hop right slow" in self.behaviors: self.deceives[0] = abs(math.sin((t / 2) * 5) * 15)
    if "hop left slow" in self.behaviors: self.deceives[0] = -abs(math.sin((t / 2) * 5) * 15)
    if "hop down slow" in self.behaviors: self.deceives[1] = abs(math.sin((t / 2) * 5) * 15)
    if "hop up fast" in self.behaviors: self.deceives[1] = -abs(math.sin((t * 2) * 5) * 15)
    if "hop right fast" in self.behaviors: self.deceives[0] = abs(math.sin((t * 2) * 5) * 15)
    if "hop left fast" in self.behaviors: self.deceives[0] = -abs(math.sin((t * 2) * 5) * 15)
    if "hop down fast" in self.behaviors: self.deceives[1] = abs(math.sin((t * 2) * 5) * 15)

    #self.deceives = [((self.main.width / 2) - (self.rect.width / 2)) + self.main.camera.scroll[0], ((self.main.height / 2) - (self.rect.height / 2)) + self.main.camera.scroll[1]]

    if "central far up" in self.behaviors: self.deceives = [((self.main.width / 2) - (self.rect.width / 2)) + self.main.camera.scroll[0], ((self.main.height / 2) - (self.rect.height / 2) / 5) + self.main.camera.scroll[1]]
    if "central up" in self.behaviors: self.deceives = [((self.main.width / 2) - (self.rect.width / 2)) + self.main.camera.scroll[0], ((self.main.height / 2) - (self.rect.height / 2) / 2.5) + self.main.camera.scroll[1]]
    if "central" in self.behaviors: self.deceives = [((self.main.width / 2) - (self.rect.width / 2)), ((self.main.height / 2) - (self.rect.height / 2))]
    if "central down" in self.behaviors: self.deceives = [((self.main.width / 2) - (self.rect.width / 2)) + self.main.camera.scroll[0], ((self.main.height / 2) - (self.rect.height / 2) * 1.5) + self.main.camera.scroll[1]]
    if "central far down" in self.behaviors: self.deceives = [((self.main.width / 2) - (self.rect.width / 2)) + self.main.camera.scroll[0], ((self.main.height / 2) - (self.rect.height / 2) * 3) + self.main.camera.scroll[1]]

    if "tremble" in self.behaviors: self.deceives = [self.deceives[0] + random.randint(-1, 1), self.deceives[1] + random.randint(-1, 1)]



class Layer:
  def __init__(self, label="Layer1", main=None):
    self.main = main
    self.room = None # in which room the layer inhibits. This should be the room object
    self.tiles = [] #the tiles that the layer has, it's a list of Tile objects
    self.collectibles = [] #the collectibles that the layer has, it's a list of collectible objects
    self.actors = [] #the collectibles that the layer has, it's a list of actor objects
    self.texts = [] #the text objects that the layer has, it's a list of text objects
    self.distance = 1 #this is for parallexing
    self.shade = 250 #this is for shading
    self.label = label #a short label to remember which layer you are looking for, you can set them in the editor self
    self.name = "" #Name of the layer (this is always layer 1, layer 2, this is not customizable)
    self.flash = Timer()

  def render_texts(self, screen, cutscene=False, dt=1, front=False):
    if not cutscene:
      if self.distance != 0:
        for text in [text for text in self.texts if ("front" in text.behaviors) == front]:
          text.update(dt)
          text.rect.x += text.cs_speed[0] * dt
          text.rect.y += text.cs_speed[1] * dt
          if self.distance != 0: xpos = text.rect.x - (self.main.camera.scroll[0] / self.distance)
          else: xpos = text.rect.x
          if self.distance != 0: ypos = text.rect.y - (self.main.camera.scroll[1] / self.distance)
          else: ypos = text.rect.y
          if (xpos < WIDTH or xpos < self.main.width) and (ypos < HEIGHT or ypos < self.main.height) and (ypos + text.rect.height) and self.distance > 0 and ((self.main.gamestate != 10 and self.main.editor_mode) or not text.hidden): text.image.fill((self.shade, self.shade, self.shade), special_flags=pygame.BLEND_RGB_MIN); screen.blit(text.image, (text.rect.x - (self.main.camera.scroll[0] / self.distance) + text.deceives[0], text.rect.y - (self.main.camera.scroll[1] / self.distance) + text.deceives[1]))
      else: #this is for when distance is set at 0, y'know when you divide by 0 and that gives an error, so we don't parallex at all and instead lock it regardless of scroll
        for text in [text for text in self.texts if ("front" in text.behaviors) == front]:
          if (text.rect.x < WIDTH + self.main.camera.scroll[0] or text.rect.x < self.main.width + self.main.camera.scroll[0]) and (text.rect.right > self.main.camera.scroll[0]) and (text.rect.y < HEIGHT + self.main.camera.scroll[1] or text.rect.y < self.main.height + self.main.camera.scroll[1]) and (text.rect.bottom > self.main.camera.scroll[1]) and self.distance > 0 and ((self.main.gamestate != 10 and self.main.editor_mode) or not text.hidden): text.image.fill((self.shade, self.shade, self.shade), special_flags=pygame.BLEND_RGB_MIN); screen.blit(text.image, (text.rect.x + text.deceives[0], text.rect.y + text.deceives[1])); text.update(dt)
    else:
      for text in [text for text in self.texts if ("front" in text.behaviors) == front]:
        text.update(dt)
        if ((self.main.gamestate == 1 and not self.main.editor_mode) or (self.main.gamestate == 10 and self.main.editor_mode)) or (self.main.gamestate == 24 and self.main.playback_on):
          text.rect.x += text.cs_speed[0] * dt
          text.rect.y += text.cs_speed[1] * dt
          if text.cs_speed_dest:
            if text.rect.x == text.cs_dest[0] and text.rect.y == text.cs_dest[1]: text.cs_speed_dest = 0
            else:
              if text.rect.x > text.cs_dest[0]: text.rect.x -= text.cs_speed_dest
              if text.rect.x < text.cs_dest[0]: text.rect.x += text.cs_speed_dest
              if abs(text.rect.x - text.cs_dest[0]) < text.cs_speed_dest: text.rect.x = text.cs_dest[0]
              if text.rect.y > text.cs_dest[1]: text.rect.y -= text.cs_speed_dest
              if text.rect.y < text.cs_dest[1]: text.rect.y += text.cs_speed_dest
              if abs(text.rect.y - text.cs_dest[1]) < text.cs_speed_dest: text.rect.y = text.cs_dest[1]
        text.last_frame_active = 0
        key_frame_rect = text.rect
        for key_object in self.main.rooms[self.main.current_room].cutscenes[self.main.selected_cutscene].animations:
          if key_object["Object"] == text and key_object["Frame"] > text.last_frame_active: text.last_frame_active = key_object["Frame"]

          if key_object["Object"] == text and key_object["Frame"] <= self.main.selected_key:
            if key_object["Rect"] != None:
              key_frame_rect = pygame.FRect(key_object["Rect"])
              if key_object["SOCR"] and self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key - 1: text.rect = text.key_frame_rect
            if self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key:
              if not key_object["Speed"]:
                text.cs_speed[0] += key_object["X Speed"] * dt
                text.cs_speed[1] += key_object["Y Speed"] * dt
                text.cs_speed[0] = round(text.cs_speed[1], 2)
                text.cs_speed[1] = round(text.cs_speed[1], 2)
              else:
                text.cs_speed_dest = key_object["Speed"]
                text.cs_dest[0] = text.rect.x + key_object["X Speed"]
                text.cs_dest[1] = text.rect.y + key_object["Y Speed"]
            if key_object["Frame"] == self.main.selected_key:
              text.hidden = key_object["Hidden"]

        text.key_frame_rect = key_frame_rect
        if self.distance != 0: xpos = text.rect.x / self.distance
        else: xpos = text.rect.x
        if self.distance != 0: ypos = text.rect.y / self.distance
        else: ypos = text.rect.y
        if (xpos < WIDTH + self.main.camera.scroll[0] or xpos < self.main.width + self.main.camera.scroll[0]) and (ypos < HEIGHT + self.main.camera.scroll[1] or ypos < self.main.height + self.main.camera.scroll[1]) and (ypos + text.rect.height + self.main.camera.scroll[1]) and self.distance > 0 and (((self.main.gamestate != 10 and self.main.editor_mode) and self.main.editor_mode) or not text.hidden):
          if self.distance != 0: text.image.fill((self.shade, self.shade, self.shade), special_flags=pygame.BLEND_RGB_MIN); screen.blit(text.image, (key_frame_rect.x - (self.main.camera.scroll[0] / self.distance) + text.deceives[0], key_frame_rect.y - (self.main.camera.scroll[1] / self.distance) + text.deceives[1]))
          else: text.image.fill((self.shade, self.shade, self.shade), special_flags=pygame.BLEND_RGB_MIN); screen.blit(text.image, (key_frame_rect.x + text.deceives[0], key_frame_rect.y + text.deceives[1]))

  def render_tiles(self, screen, cutscene=False, dt=1):
    for tile in [tile for tile in self.tiles if tile.layer == None]: tile.layer = self
    for tile in [tile for tile in self.tiles if tile.is_animating and not self.main.game_paused]:
      if tile.anim_speed > 0: tile.image = tile.images[tile.timer.keep_count(tile.anim_speed * dt, len(tile.images), 0)]
      else: tile.image = tile.images[tile.timer.tally]
    flash = self.flash.wait(FPS / 2)
    if self.main.gamestate != 7:
      if not cutscene:
        if self.distance != 0:
          for tile in self.tiles:
            xpos = tile.rect.x - (self.main.camera.scroll[0] / self.distance); ypos = tile.rect.y - (self.main.camera.scroll[1] / self.distance)
            if (xpos < WIDTH or xpos < self.main.width) and (ypos < HEIGHT or ypos < self.main.height) and (((self.main.gamestate != 10 and self.main.editor_mode) and self.main.editor_mode) or not tile.hidden): tile.image.fill((self.shade, self.shade, self.shade), special_flags=pygame.BLEND_RGB_MIN); screen.blit(tile.image, ((tile.rect.x - tile.offset[0]) - (self.main.camera.scroll[0] / self.distance), (tile.rect.y - tile.offset[1]) - (self.main.camera.scroll[1] / self.distance)))
            for crumb in tile.crumbs:
              crumb.update(dt)
              crumb.image.fill((self.shade, self.shade, self.shade), special_flags=pygame.BLEND_RGB_MIN); screen.blit(crumb.image, (crumb.rect.x - (self.main.camera.scroll[0] / self.distance), crumb.rect.y - (self.main.camera.scroll[1] / self.distance)))
              xpos = crumb.rect.x - (self.main.camera.scroll[0] / self.distance); ypos = crumb.rect.y - (self.main.camera.scroll[1] / self.distance)
              if (xpos > WIDTH or xpos > self.main.width) or (ypos > HEIGHT or ypos > self.main.height): tile.crumbs.remove(crumb)
        else: #this is for when distance is set at 0, y'know when you divide by 0 and that gives an error, so we don't parallex at all and instead lock it regardless of scroll
          for tile in self.tiles:
            if (tile.rect.x < WIDTH + self.main.camera.scroll[0] or tile.rect.x < self.main.width + self.main.camera.scroll[0]) and (tile.rect.right > self.main.camera.scroll[0]) and (tile.rect.y < HEIGHT + self.main.camera.scroll[1] or tile.rect.y < self.main.height + self.main.camera.scroll[1]) and (tile.rect.bottom > self.main.camera.scroll[1]) and ((self.main.gamestate != 10 and self.main.editor_mode) or not tile.hidden): tile.image.fill((self.shade, self.shade, self.shade), special_flags=pygame.BLEND_RGB_MIN); screen.blit(tile.image, (tile.rect.x - tile.offset[0], tile.rect.y - tile.offset[1]))
            for crumb in tile.crumbs:
              crumb.update(dt)
              crumb.image.fill((self.shade, self.shade, self.shade), special_flags=pygame.BLEND_RGB_MIN); screen.blit(crumb.image, crumb.rect)
              if crumb.rect.x > self.main.width or crumb.rect.y > self.main.height or crumb.rect.right < self.main.camera.scroll[0] or crumb.alive_for > crumb.lifetime: tile.crumbs.remove(crumb)
      else:
        for tile in self.tiles:
          tile.last_frame_active = 0
          key_frame_rect = tile.rect
          for key_object in self.main.rooms[self.main.current_room].cutscenes[self.main.selected_cutscene].animations:
            if key_object["Object"] == tile and key_object["Frame"] > tile.last_frame_active: tile.last_frame_active = key_object["Frame"]

            if key_object["Object"] == tile and key_object["Frame"] <= self.main.selected_key:
              if key_object["Rect"] != None:
                key_frame_rect = pygame.FRect(key_object["Rect"])
                if key_object["SOCR"] and self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key - 1: tile.rect = tile.key_frame_rect
              if self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key:
                if not key_object["Speed"]:
                  tile.cs_speed[0] += key_object["X Speed"] * dt
                  tile.cs_speed[1] += key_object["Y Speed"] * dt
                  tile.cs_speed[0] = round(tile.cs_speed[1], 2)
                  tile.cs_speed[1] = round(tile.cs_speed[1], 2)
                else:
                  tile.cs_speed_dest = key_object["Speed"]
                  tile.cs_dest[0] = tile.rect.x + key_object["X Speed"]
                  tile.cs_dest[1] = tile.rect.y + key_object["Y Speed"]
                tile.hidden = key_object["Hidden"]
                if tile.alive: tile.alive = not key_object["Action"] == "destroy"

          tile.key_frame_rect = key_frame_rect
          if self.distance != 0: xpos = tile.rect.x / self.distance
          else: xpos = tile.rect.x
          if self.distance != 0: ypos = tile.rect.y / self.distance
          else: ypos = tile.rect.y
          if (xpos < WIDTH + self.main.camera.scroll[0] or xpos < self.main.width + self.main.camera.scroll[0]) and (ypos < HEIGHT + self.main.camera.scroll[1] or ypos < self.main.height + self.main.camera.scroll[1]) and (ypos + tile.rect.height + self.main.camera.scroll[1]) and self.distance > 0 and (self.main.gamestate != 10 or not tile.hidden):
            if self.distance != 0: tile.image.fill((self.shade, self.shade, self.shade), special_flags=pygame.BLEND_RGB_MIN); screen.blit(tile.image, ((key_frame_rect.x - tile.offset[0]) - (self.main.camera.scroll[0] / self.distance), (key_frame_rect.y - tile.offset[1]) - (self.main.camera.scroll[1] / self.distance)))
            else: tile.image.fill((self.shade, self.shade, self.shade), special_flags=pygame.BLEND_RGB_MIN); screen.blit(tile.image, (key_frame_rect.x - tile.offset[0], key_frame_rect.y - tile.offset[1]))
          for crumb in tile.crumbs:
            crumb.update(dt)
            if self.distance != 0:
              crumb.image.fill((self.shade, self.shade, self.shade), special_flags=pygame.BLEND_RGB_MIN); screen.blit(crumb.image, (crumb.rect.x - (self.main.camera.scroll[0] / self.distance), crumb.rect.y - (self.main.camera.scroll[1] / self.distance)))
              xpos = crumb.rect.x - (self.main.camera.scroll[0] / self.distance); ypos = crumb.rect.y - (self.main.camera.scroll[1] / self.distance)
              if xpos > self.main.width or ypos > self.main.height or crumb.alive_for > crumb.lifetime: tile.crumbs.remove(crumb)
            else:
              crumb.update(dt)
              crumb.image.fill((self.shade, self.shade, self.shade), special_flags=pygame.BLEND_RGB_MIN); screen.blit(crumb.image, crumb.rect)
              if crumb.rect.x > self.main.width or crumb.rect.y > self.main.height or crumb.alive_for > crumb.lifetime: tile.crumbs.remove(crumb)
    else:
      for tile in self.tiles:
        if not (tile.solid or flash): tile.image.set_alpha(150)
        screen.blit(tile.image, (tile.rect.x - self.main.camera.scroll[0] - tile.offset[0], tile.rect.y - self.main.camera.scroll[1] - tile.offset[1]))
        if not (not tile.slippery or flash): pygame.draw.rect(screen, "Cyan", ((tile.rect.x - self.main.camera.scroll[0], tile.rect.y - self.main.camera.scroll[1]), (tile.rect.width, tile.rect.height)), 2, 1)
        if not (not tile.flat or flash): pygame.draw.line(screen, "Yellow", (tile.rect.x - self.main.camera.scroll[0], tile.rect.y - self.main.camera.scroll[1]), ((tile.rect.x + tile.rect.width) - self.main.camera.scroll[0], tile.rect.y - self.main.camera.scroll[1]), 2)
        tile.image.set_alpha(255)
        if tile.selected: pygame.draw.rect(screen, "Green", ((tile.rect.x - self.main.camera.scroll[0], tile.rect.y - self.main.camera.scroll[1]), (tile.rect.width, tile.rect.height)), 1)
  
  def render_collectibles(self, screen, cutscene=False, dt=1):
    for coin in self.collectibles:
      if coin.alive and (coin.rect.x < WIDTH + self.main.camera.scroll[0] or coin.rect.x < self.main.width + self.main.camera.scroll[0]) and (coin.rect.right > self.main.camera.scroll[0]) and (coin.rect.y < HEIGHT + self.main.camera.scroll[1] or coin.rect.y < self.main.height + self.main.camera.scroll[1]) and (coin.rect.bottom > self.main.camera.scroll[1]) and ((self.main.gamestate != 10 and self.main.editor_mode) or not coin.hidden):
        if not cutscene:
          if ((self.main.gamestate != 10 and self.main.editor_mode) or not coin.hidden):
            screen.blit(coin.images[coin.frame], (coin.rect.x - self.main.camera.scroll[0], coin.rect.y - self.main.camera.scroll[1]))
            if coin.anim_speed > 0 and len(coin.images) > 1: coin.frame = coin.timer.keep_count(coin.anim_speed, len(coin.images), 0)
            else: coin.frame = 0
            if coin.price_value != 0: coin.display_price_tag(screen, coin.rect.x - self.main.camera.scroll[0], coin.rect.y - self.main.camera.scroll[1])
        else:
          coin.last_frame_active = 0
          key_frame_rect = coin.rect
          for key_object in self.main.rooms[self.main.current_room].cutscenes[self.main.selected_cutscene].animations:
            if key_object["Object"] == coin and key_object["Frame"] > coin.last_frame_active: coin.last_frame_active = key_object["Frame"]

            if key_object["Object"] == coin and key_object["Frame"] <= self.main.selected_key:
              if key_object["Rect"] != None:
                key_frame_rect = pygame.FRect(key_object["Rect"])
                if key_object["SOCR"] and self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key: coin.rect = coin.key_frame_rect
              if self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key:
                if not key_object["Speed"]:
                  coin.cs_speed[0] += key_object["X Speed"] * dt
                  coin.cs_speed[1] += key_object["Y Speed"] * dt
                  coin.cs_speed[0] = round(coin.cs_speed[1], 2)
                  coin.cs_speed[1] = round(coin.cs_speed[1], 2)
                else:
                  coin.cs_speed_dest = key_object["Speed"]
                  coin.cs_dest[0] = coin.rect.x + key_object["X Speed"]
                  coin.cs_dest[1] = coin.rect.y + key_object["Y Speed"]
                coin.hidden = key_object["Hidden"]

          coin.key_frame_rect = key_frame_rect
          if not coin.hidden:
            screen.blit(coin.images[coin.frame], (key_frame_rect.x - self.main.camera.scroll[0], key_frame_rect.y - self.main.camera.scroll[1]))
            if coin.anim_speed > 0: coin.frame = coin.timer.keep_count(coin.anim_speed, len(coin.images), 0)
            else: coin.frame = 0
            # if coin.frame <= len(coin.images): coin.frame += 0.1 * dt
            # else: coin.frame = 0
            # screen.blit(coin.images[math.floor(coin.frame)], (key_frame_rect.x - self.main.camera.scroll[0], key_frame_rect.y - self.main.camera.scroll[1]))
            
  def update_tiles(self, screen, cutscene=False, dt=1):
    for tile in self.tiles: tile.update(cutscene, dt)
  
  def update_collectibles(self, screen, cutscene=False, dt=1):
    for coin in self.collectibles: coin.update(cutscene, dt)

  def render_entities(self, screen, cutscene=False, dt=1):
    for actor in self.actors:
      if self.main.editor_mode and self.main.gamestate != 10:
        seen = True
        if actor.rect.x > self.main.camera.scroll[0] + WIDTH: seen = False
        if actor.rect.right < self.main.camera.scroll[0]: seen = False
        if actor.rect.y > self.main.camera.scroll[1] + HEIGHT: seen = False
        if actor.rect.bottom < self.main.camera.scroll[1]: seen = False
        if seen: actor.display(screen=screen, cutscene=cutscene, dt=dt)
      else:
        seen = True
        if actor.rect.x > self.main.camera.scroll[0] + self.main.width: seen = False
        if actor.rect.right < self.main.camera.scroll[0]: seen = False
        if actor.rect.y > self.main.camera.scroll[1] + self.main.height: seen = False
        if actor.rect.bottom < self.main.camera.scroll[1]: seen = False
        if seen: actor.display(screen=screen, cutscene=cutscene, dt=dt)

  def update_entities(self, screen, dt=1):
    for actor in self.actors: actor.update(screen, actor.font, dt)
    



class Camera:
  def __init__(self, main):
    self.main = main
    self.scroll = [0, 0]
    self.shake = [0, 0]
    self.cs_speed = [0, 0]
    self.cs_dest = [0, 0]
    self.cs_speed_dest = 0
    self.name = "Camera"
    self.rect = pygame.FRect((0, 0), (main.width, main.height))
    self.key_frame_rect = self.rect
    self.last_frame_active = 0
    self.follow_player = True
    self.spawn_follow_player = True
    self.image = pygame.transform.scale(pygame.image.load("Assets/editor/camera.png").convert_alpha(), (64, 64))

  def render_preview(self, screen):
    screen.blit(self.image, (self.rect.x - self.main.camera.scroll[0], self.rect.y - self.main.camera.scroll[1]))
    pygame.draw.rect(screen, "Red", ((self.rect.x - self.main.camera.scroll[0], self.rect.y - self.main.camera.scroll[1]), (self.rect.width, self.rect.height)), 1)

  def camera_scene(self, dt=1):
    self.last_frame_active = 0
    key_frame_rect = self.rect
    #try:
    for key_object in self.main.rooms[self.main.current_room].cutscenes[self.main.selected_cutscene].animations:
      if key_object["Object"] == self and key_object["Frame"] > self.last_frame_active: self.last_frame_active = key_object["Frame"]

      if key_object["Object"] == self and key_object["Frame"] <= self.main.selected_key:
        if key_object["Rect"] != None:
          key_frame_rect = pygame.FRect(key_object["Rect"])
          if key_object["SOCR"] and self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key: self.rect = self.key_frame_rect
        if self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key:
          if not key_object["Speed"]:
            self.cs_speed[0] += key_object["X Speed"] * dt
            self.cs_speed[1] += key_object["Y Speed"] * dt
            self.cs_speed[0] = round(self.cs_speed[1], 2)
            self.cs_speed[1] = round(self.cs_speed[1], 2)
          else:
            self.cs_speed_dest = key_object["Speed"]
            self.cs_dest[0] = self.rect.x + key_object["X Speed"]
            self.cs_dest[1] = self.rect.y + key_object["Y Speed"]
        self.follow_player = key_object["Hidden"]
    #except IndexError: pass

    self.key_frame_rect = key_frame_rect
    if not self.follow_player:
      self.rect = key_frame_rect
      self.rect.x += self.cs_speed[0]
      self.rect.y += self.cs_speed[1]
      if ((self.main.gamestate == 1 and not self.main.editor_mode) or (self.main.gamestate == 10 and self.main.editor_mode)):
        self.scroll[0], self.scroll[1] = self.key_frame_rect.x, self.key_frame_rect.y
        self.scroll[0] += self.cs_speed[0]
        self.scroll[1] += self.cs_speed[1]
        self.scroll[0] = round(self.scroll[1], 2)
        self.scroll[1] = round(self.scroll[1], 2)
      if self.cs_speed_dest:
        if self.rect.x == self.cs_dest[0] and self.rect.y == self.cs_dest[1]: self.cs_speed_dest = 0
        else:
          if self.rect.x > self.cs_dest[0]: self.rect.x -= self.cs_speed_dest
          if self.rect.x < self.cs_dest[0]: self.rect.x += self.cs_speed_dest
          if abs(self.rect.x - self.cs_dest[0]) < self.cs_speed_dest: self.rect.x = self.cs_dest[0]
          if self.rect.y > self.cs_dest[1]: self.rect.y -= self.cs_speed_dest
          if self.rect.y < self.cs_dest[1]: self.rect.y += self.cs_speed_dest
          if abs(self.rect.y - self.cs_dest[1]) < self.cs_speed_dest: self.rect.y = self.cs_dest[1]
    else: self.cs_speed = [0, 0]; self.cs_speed_dest = 0; self.cs_dest = [0, 0]


class Cutscene:
  def __init__(self, name="Cutscene1", index=1):
    self.name = name #name of the cutscene (for example intro, ending, bossfight appearance, etc...)
    self.keys = [] #keyframes
    self.passed = False #it's a condition that when it is true, the cutscene has finished already
    self.buttons = [] #the buttons of the small cutscene windows
    self.state = "stop" #states such as "playing", "beginning" etc
    self.animations = []
    self.index = index #these are the buttons of that cutscene window
    self.condition_gate = "or"
    self.conditions = ["Zone", "Collectible"]
    self.condition_stat_gate = "and"
    self.stat_required = []
    for i in range(5000): self.keys.append(Key(i, self))


class Key:
  def __init__(self, frame, cutscene):
    self.cutscene = cutscene
    self.frame = frame
    self.lag = 1
    self.no_input = True