import pygame, random, os
from pygame._sdl2.video import Window, Renderer, Texture, Image
from Scripts.timers import Timer
from Scripts.settings import *
import math

class Actor:
  def __init__(self, x, y, character, main):
    self.main = main
    self.character = character
    self.name = character.character
    self.character_spawn = character
    self.name_spawn = character.character
    #self.character = Character(character=character.character, main=main)
    #self.character.state_controls = character.state_controls.copy()
    #self.character_object = character
    try: width, height = pygame.image.load(main.active_directory + f"Assets/characters/{character.character}/idle/1.png").get_width(), pygame.image.load(main.active_directory + f"Assets/characters/{character.character}/idle/1.png").get_height()
    except FileNotFoundError: width, height = pygame.image.load(main.active_directory + f"Assets/characters/{character.character}/down/idle/1.png").get_width(), pygame.image.load(main.active_directory + f"Assets/characters/{character.character}/down/idle/1.png").get_height()
    self.rect = pygame.FRect((x, y), (width, height))
    self.movement = [0.0, 0.0] #the movement of actor vector speed
    self.airtimer = 0 #sees how much time spent in air (for jumping purposes)
    self.jump_force = character.jump_force
    self.jumps_left = character.jumps
    self.speed = character.speed
    self.state = "idle"
    self.frame = 1 #the frame for the animation state
    self.y_vel = 0 #speed verticle
    self.y_vel_kb = 0.0
    self.x_vel = 0.0
    self.x_vel_kb = 0.0
    self.terminal_x_vel = 8.0
    self.on_ice = False
    self.collision = {"top": False, "bottom": False, "right": False, "left": False}
    self.gravity_enabled = True #Enable gravity
    self.immobilize = False
    self.flipped = False
    self.started_walking = False
    self.offset = [0, 0]
    self.dir = "down"
    self.timer = Timer()
    self.hit_timer = Timer()
    self.protection_timer = Timer()
    self.smashdown_timer = Timer()
    self.combo_activation_count = 0
    self.cannot_be_attacked = False
    self.accelerated_travel = False
    self.x_accel = 0
    self.friction = 0.2
    self.weight = 0.75
    self.bump_cancel_momentum = True
    self.bump_head = False
    self.jumps_spawn = 1
    self.jumps = 1
    self.drop_down_flat_tile = False
    self.change_trajectory_midair = True
    self.midair_jump_dash = False
    self.wall_sliding = False
    self.projectiles = []
    self.hp = 5
    self.start_hp = 5
    self.stagger = 0
    self.start_stagger = 0
    self.team = 0
    self.spawn_location = [0, 0]
    self.alive = True
    self.turn_rate = 0
    self.stats = {}
    self.key_frame_rect = self.rect
    self.last_frame_active = 0
    self.cs_speed = [0, 0]
    self.cs_dest = [0, 0]
    self.cs_speed_dest = 0
    self.hidden = False
    self.spawn_as_visible = True
    self.debt = 0
    self.attacked = False
    self.stat = ""
    self.value = 0
    self.respawn_location = [0, 0]
    self.image = self.character.image
    self.wait_timer = Timer()
    self.alive_in_room_for_frames = 0
    
    #Animation variables
    self.frame = 0
    self.time_accumulator = 0
    self.finished = False

  def clear(self):
    #self.character = Character(character=self.character.character, main=self.main)
    #self.character.state_controls = self.character_object.state_controls.copy()
    self.character = self.character_spawn
    self.name = self.name_spawn
    self.rect.x, self.rect.y = self.spawn_location[0], self.spawn_location[1]
    self.jump_force = self.character.jump_force
    self.speed = self.character.speed
    self.movement = [0.0, 0.0]
    self.airtimer = 0
    self.y_vel = 0.0
    self.y_vel_kb = 0.0
    self.x_vel = 0.0
    self.x_vel_kb = 0.0
    self.on_ice = False
    self.state = "idle"
    self.frame = 1
    self.turn_rate = 0
    self.collision = {"top": False, "bottom": False, "right": False, "left": False}
    self.immobilize = False
    self.flipped = False
    self.started_walking = False
    self.offset = [0, 0]
    self.dir = "down"
    self.projectiles.clear()
    self.stats = {}
    self.key_frame_rect = self.rect
    self.last_frame_active = 0
    self.cs_speed = [0, 0]
    self.cs_dest = [0, 0]
    self.cs_speed_dest = 0
    self.hidden = False
    self.alive = True
    self.debt = 0
    self.timer = Timer()
    self.protection_timer = Timer()
    self.hit_timer = Timer()
    self.wait_timer = Timer()
    self.alive_in_room_for_frames = 0
    self.respawn_location = [0, 0]
    self.hit_protection = 15
    self.spawn_protection = 30
    self.frame = 0
    self.time_accumulator = 0
    self.finished = False
    if self.character.mode == "platformer":
      for action in self.character.actions:
        for frant in self.character.actions[action].frants: frant.loops = frant.loops_spawn
    elif self.character.mode == "topdown":
      for dir in ["down", "up", "right", "left"]:
        for action in self.character.actions[dir]:
          for frant in self.character.actions[dir][action].frants: frant.loops = frant.loops_spawn
    for stat in self.main.game_stats: self.stats[stat] = self.main.game_stats_initpoint[stat]
    for stat in (stat for stat in self.main.game_stats if self.main.game_stats_effect[stat] == "hp"): self.start_hp = self.main.game_stats_initpoint[stat]
    for stat in (stat for stat in self.main.game_stats if self.main.game_stats_effect[stat] == "stagger"): self.start_stagger = self.main.game_stats_initpoint[stat]
    self.hp, self.stagger = self.start_hp, self.start_stagger
    if isinstance(self, Player):
      self.state_controls = self.character.state_controls.copy()
      self.port = self.main.ports[self.player_index]
      self.in_ = self.in_spawn

    if isinstance(self, Entity): 
      self.ai = AI(self)
      self.current_dialogue = 0
      self.dl_timer.reset()
      self.add_letter_to_dialogue_timer.reset()
      self.dialogue_text = ""
      
      self.hp = self.type["hp"]
      self.stat = self.type["stat"]
      self.value = self.type["value"]
      self.behaviors = self.type["behaviors"]
      self.range = self.type["range"]
      self.drops = self.type["drops"]
    #if self.clone: self.rect.x, self.rect.y = -99, -5; self.spawn_location = [-99, -5]
  
  # def load_images(self, path):
  #   images_dict = {}
  #   states = []
  #   states = os.listdir(path)#list of all the states
  #   in_images = []
    
  #   for state in states:
  #     try:
  #       order = [int(file[0 : len(file) - 4]) for file in os.listdir(path + "/" + state)]
  #       order.sort()
  #       images = os.listdir(path + "/" + state)#the list of images
  #       path.split("/")[-1]
  #       in_images = []
  #       #for img in images:
  #       #  load = pygame.image.load(path + "/" + state + "/" + img)
  #       #  in_images.append(load)
  #       in_images = [pygame.image.load(path + "/" + state + "/" + str(file) + ".png").convert_alpha() for file in order]
  #       images_dict[state] = in_images
  #       self.mode = "platformer"
  #     except: pass
  #   return images_dict, states
  
  def display(self, screen, cutscene=False, dt=1): #renders the entity
    
    #if self.state in self.actions and self.frame < len(self.actions[self.state].frants):
    #  frame_rect = self.actions[self.state].frants[self.frame].rect
    #  frame_rect.x = self.rect.x + ((self.rect.width / 2) - (frame_rect.width / 2))
    #  frame_rect.y = self.rect.y + ((self.rect.height / 2) - (frame_rect.height / 2))
    
    if cutscene:
      self.last_frame_active = 0
      key_frame_rect = self.rect
      for key_object in self.main.rooms[self.main.current_room].cutscenes[self.main.selected_cutscene].animations:
        if key_object["Object"] == self and key_object["Frame"] > self.last_frame_active: self.last_frame_active = key_object["Frame"]

        if key_object["Object"] == self and key_object["Frame"] <= self.main.selected_key:
          if key_object["Rect"] != None:
            key_frame_rect = pygame.FRect(key_object["Rect"])
            if key_object["SOCR"] and self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key - 1: self.rect = self.key_frame_rect
          if self.main.frame_timer.time == 0 and key_object["Frame"] == self.main.selected_key:
            if key_object["SFX"]: self.character = key_object["SFX"]; self.name = self.character.character; self.state_controls = self.character.state_controls.copy()
              #for character in self.main.characters:
              #  if character.character == key_object["SFX"]:
              #    self.character = character; self.name = key_object["SFX"]
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
            if key_object["Action"]:
              if key_object["Action"] != "BOSSFIGHT":
                if key_object["Action"] in self.character.actions: self.state = key_object["Action"]; self.frame = 0
              elif type(self) == Entity: self.bossfight = True
            if self.character.mode == "platformer":
              if key_object["Dir"] == "right": self.flipped = False
              if key_object["Dir"] == "left": self.flipped = True
            if self.character.mode == "top-down": self.dir = key_object["Dir"]

        self.key_frame_rect = key_frame_rect
    
    if self.image != None:
      # if self.character.mode == "platformer":
      #   if self.state in self.character.actions: self.frame = self.character.actions[self.state].frame
      # elif self.character.mode == "topdown":
      #   if self.state in self.character.actions[self.dir]: self.frame = self.character.actions[self.dir][self.state].frame
      
      if self.alive or not self.character.defeat_anim == "Nothing":
        if self.state in self.character.actions and not self.main.game_paused: reset = self.flip(dt=0.001 * dt, screen=screen)
        else: reset = True

        if self.hit_timer.time:
          self.image.fill("White", special_flags=pygame.BLEND_RGB_MAX)
          self.hit_timer.wait(FPS / 8)

        if self.main.rooms[self.main.current_room].show_player and (self.rect.x < WIDTH + self.main.camera.scroll[0] or self.rect.x < self.main.width + self.main.camera.scroll[0]) and (self.rect.y < HEIGHT + self.main.camera.scroll[1] or self.rect.y < self.main.height + self.main.camera.scroll[1]) and (self.rect.y + self.rect.height + self.main.camera.scroll[1]):
          if (not (self.main.gamestate == 1 and not self.main.editor_mode) and not (self.main.gamestate == 10 and self.main.editor_mode)) or not self.hidden:
            if self.state in self.character.actions and self.frame < len(self.character.actions[self.state].frants) and not reset:
              frant_rect = self.character.actions[self.state].frants[self.frame].rect
              if not self.flipped: self.offset[0] = frant_rect.x
              else: self.offset[0] = self.image.get_width() - frant_rect.width - frant_rect.x
              self.offset[1] = frant_rect.y
            if (not (self.main.gamestate == 1 and not self.main.editor_mode) and not (self.main.gamestate == 10 and self.main.editor_mode)) and not self.spawn_as_visible: self.image.set_alpha(100)
            if not cutscene: screen.blit(self.image, ((self.rect.x - self.offset[0]) - self.main.camera.scroll[0], (self.rect.y - self.offset[1]) - self.main.camera.scroll[1]))
            else: screen.blit(self.image, ((self.key_frame_rect.x - self.offset[0]) - self.main.camera.scroll[0], (self.key_frame_rect.y - self.offset[1]) - self.main.camera.scroll[1]))

    else: pygame.draw.rect(screen, "Red", (self.rect.x - self.main.camera.scroll[0], self.rect.y - self.main.camera.scroll[1], self.rect.width, self.rect.height), 2)
    
    if ((self.main.gamestate == 1 and not self.main.editor_mode) or (self.main.gamestate == 10 and self.main.editor_mode)) or (self.main.gamestate == 24 and self.main.playback_on): self.alive_in_room_for_frames += 1; self.rect.x += self.cs_speed[0]; self.rect.y += self.cs_speed[1]
    if self.cs_speed_dest:
      if self.rect.x == self.cs_dest[0] and self.rect.y == self.cs_dest[1]: self.cs_speed_dest = 0
      else:
        if self.rect.x > self.cs_dest[0]: self.rect.x -= self.cs_speed_dest
        if self.rect.x < self.cs_dest[0]: self.rect.x += self.cs_speed_dest
        if abs(self.rect.x - self.cs_dest[0]) < self.cs_speed_dest: self.rect.x = self.cs_dest[0]
        if self.rect.y > self.cs_dest[1]: self.rect.y -= self.cs_speed_dest
        if self.rect.y < self.cs_dest[1]: self.rect.y += self.cs_speed_dest
        if abs(self.rect.y - self.cs_dest[1]) < self.cs_speed_dest: self.rect.y = self.cs_dest[1]

  def display_projectiles(self, screen, dt):
    for proj in self.projectiles:
      if proj.alive: proj.update(screen, dt)
      else: self.projectiles.remove(proj)

  def flip(self, dt, screen):
    self.time_accumulator += dt
    self.finished = False

    if self.character.mode == "platformer": action = self.character.actions[self.state]
    elif self.character.mode == "topdown": action = self.character.actions[self.dir][self.state]

    if self.time_accumulator >= 1.0 / action.rate if action.rate else 1.0:
      self.time_accumulator = 0
      if self.frame < len(action.frames) - 1: self.frame += 1; self.finished = True
      elif action.loop: self.frame = 0

    if self.time_accumulator == 0 and self.frame < len(action.frames):
      if not action.allow_travel: self.movement[0] = 0
      if (not self.flipped) or not action.directional_relative: self.movement[0] += action.frants[self.frame - 1].move_x
      elif self.flipped: self.movement[0] -= action.frants[self.frame - 1].move_x
      if action.apply_gravity: self.movement[1] += action.frants[self.frame - 1].move_y
      else: self.movement[1] = action.frants[self.frame - 1].move_y
      self.x_vel += action.frants[self.frame - 1].gain_x
      if action.frants[self.frame - 1].gain_y < 0 and not self.collision["top"]: self.rect.y -= 1
      self.y_vel_kb += action.frants[self.frame - 1].gain_y
      if action.frants[self.frame - 1].sound:
        if type(action.frants[self.frame - 1].sound) == list: action.frants[self.frame - 1].sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + action.frants[self.frame - 1].sound[random.randrange(0, len(action.frants[self.frame - 1].sound))])
        action.frants[self.frame - 1].sfx.play()
      if action.frants[self.frame - 1].loop_to < 0 and (action.frants[self.frame - 1].loops != action.frants[self.frame - 1].loops_spawn or not action.frants[self.frame - 1].loops): action.frants[self.frame - 1].loops = action.frants[self.frame - 1].loops_spawn
      if isinstance(self, Player):
        self.combo_activation_count -= 1
        if self.state_button:
          if self.button_dict[self.state_button]: self.combo_activation_count = 3
        if action.frants[self.frame - 1].combo_unit != action.frants[self.frame].combo_unit and self.combo_activation_count < 0:
          for frame in [frame for frame in action.frants if frame.frame > self.frame and frame.combo_unit == 0]: self.frame = frame.frame; break
          else:
            if "idle" in self.character.actions: self.offset[0] = self.character.actions["idle"].frants[0].rect.x; self.offset[1] = self.character.actions["idle"].frants[0].rect.y; self.state, self.frame = "idle", 0
      if action.frants[self.frame - 1].loops: action.frants[self.frame - 1].loops -= 1; self.frame = action.frants[self.frame - 1].loop_to - 1
        
      for proj in action.frants[self.frame - 1].projectiles:
        try: self.projectiles.append(Projectile(self, self.main.projectiles[proj - 1]))
        except IndexError: pass

    try:
      rtn = action.frames[self.frame]; reset = False; #pygame.draw.circle(screen, "Green", (50, 50), 25)
    except IndexError:
      rtn = action.frames[0]; reset = True; #pygame.draw.circle(screen, "Red", (50, 50), 25)
      if "idle" in self.character.actions: self.offset[0] = self.character.actions["idle"].frants[0].rect.x; self.offset[1] = self.character.actions["idle"].frants[0].rect.y; self.state, self.frame = "idle", 0
    self.image = rtn

    if self.character.mode == "platformer": self.image = pygame.transform.flip(self.image, self.flipped, False)

    return reset


  def move(self, tiles, rect, dt):
    collision = {"top": False, "bottom": False, "right": False, "left": False}

    damage = 0
    if self.state in self.character.actions and self.frame < len(self.character.actions[self.state].frants):
      if self.frame > len(self.character.actions[self.state].frants): damage = self.character.actions[self.state].frants[self.frame].damage

    #if self.state in self.character.actions and self.frame < len(self.character.actions[self.state].frants):
    #  hb_rect = self.character.actions[self.state].frants[self.frame].rect
    #else: hb_rect = self.rect

    if self.x_vel: self.movement[0] += self.x_vel
    
    if self.on_ice:
      if collision["right"] or collision["left"]: self.x_vel = 0.0
      if self.x_vel < 1 and self.x_vel > -1 and not collision["bottom"]: self.movement[0] = self.on_ice = False
      if self.x_vel > self.terminal_x_vel: self.x_vel = self.terminal_x_vel
      if self.x_vel < -self.terminal_x_vel: self.x_vel = -self.terminal_x_vel

    if self.x_vel < 1.0 and self.x_vel > -1.0 and self.x_vel != 0: self.x_vel = 0.0
    
    rect.x += float(self.movement[0]) * dt
    hit_list = []
    if self.alive or not "Tumble" in self.character.defeat_anim or not "Fall" in self.character.defeat_anim: hit_list = collision_test(rect, tiles)
    for tile in hit_list:
      if self.movement[0] > 0 and not tile.flat:
        rect.right = tile.rect.left
        collision["right"] = True
        self.x_vel = 0.0
        if tile.team != self.team: tile.hp -= damage
      elif self.movement[0] < 0 and not tile.flat:
        rect.left = tile.rect.right
        collision["left"] = True
        self.x_vel = 0.0
        if tile.team != self.team: tile.hp -= damage
    
    rect.y += float(self.movement[1]) * dt

    hit_list = []
    if self.alive or not "Tumble" in self.character.defeat_anim or not "Fall" in self.character.defeat_anim: hit_list = collision_test(rect, tiles)
    stand_on_flat = True
    for tile in hit_list:
      if tile.solid and not tile.flat: stand_on_flat = False

    if isinstance(self, Player): press_down = self.port.buttons["Press"]["down"]
    else: press_down = False
    
    self.bump_head = False

    for tile in hit_list:
      if self.movement[1] > 0 and not (press_down and tile.flat and stand_on_flat):
        if self.state == "jump" and self.y_vel != 0 and self.character.land_sound:
          if type(self.character.land_sound) == list: self.character.land_sfx = pygame.mixer.Sound("Sounds/sfx/" + self.character.land_sound[random.randrange(0, len(self.character.land_sound))])
          self.character.land_sfx.play()
        rect.bottom = tile.rect.top
        collision["bottom"] = True
        tile.stood_on = True
        if tile.destroy_if_stood_on and not tile.only_breakable_by_chains: tile.alive = False
        if tile.step_sound and self.state == "walk" and (self.frame == 1 or self.frame == 5 or self.frame == 9) and self.time_accumulator == 0:
          if type(tile.step_sound) == list: tile.step_sfx = pygame.mixer.Sound("Sounds/sfx/" + tile.step_sound[random.randrange(0, len(tile.step_sound))])
          tile.step_sfx.play()
        if tile.slippery:
          if not self.on_ice: self.x_vel = self.movement[0]
          self.on_ice = True
        elif self.collision["bottom"]: self.on_ice = False; self.x_vel = 0.0
        
        if tile.bring_player:
          if tile.speed[0]: rect.x += tile.speed[0] * dt
          if tile.speed[1]: rect.y += tile.speed[1] * dt

        if tile.zones_can_rotate:
          dx = tile.rect.centerx - tile.last_centerx
          dy = tile.rect.centery - tile.last_centery
          rect.x += dx; rect.y += dy
            
        hit_list = collision_test(rect, tiles)
        for new_tile in hit_list:
          if tile.speed[0] > 0 and not new_tile.flat:
            rect.right = new_tile.rect.left
            collision["right"] = True
          elif tile.speed[0] < 0 and not new_tile.flat:
            rect.left = new_tile.rect.right
            collision["left"] = True

      elif self.movement[1] < 0 and not tile.flat:
        rect.top = tile.rect.bottom
        collision["top"] = True
        self.bump_head = True
        if self.bump_cancel_momentum: self.y_vel = 0
        if tile.destroy_if_head_bump and not tile.only_breakable_by_chains: tile.alive = False
  
    return collision, rect
  
  def combat(self, actors, tiles, rect):
    collision = {'top': False, 'bottom': False, 'right': False, 'left': False}

    self.protection_timer.nonstopcount(1, 0)

    if self.state in self.character.actions and self.frame < len(self.character.actions[self.state].frants):
      if not self.flipped: attack_rect = pygame.FRect((self.character.actions[self.state].frants[self.frame].attack_rect.x + self.rect.x - self.offset[0], self.character.actions[self.state].frants[self.frame].attack_rect.y + self.rect.y - self.offset[1]), (self.character.actions[self.state].frants[self.frame].attack_rect.width, self.character.actions[self.state].frants[self.frame].attack_rect.height))
      else: attack_rect = pygame.FRect((self.rect.right - self.character.actions[self.state].frants[self.frame].attack_rect.x - self.character.actions[self.state].frants[self.frame].attack_rect.width + self.offset[0], self.character.actions[self.state].frants[self.frame].attack_rect.y + self.rect.y - self.offset[1]), (self.character.actions[self.state].frants[self.frame].attack_rect.width, self.character.actions[self.state].frants[self.frame].attack_rect.height))
    else: attack_rect = pygame.FRect((0, 0), (0, 0))

    #if self.state in self.character.actions and self.frame < len(self.character.actions[self.state].frants):
    #  hb_rect = self.character.actions[self.state].frants[self.frame].rect
    #else: hb_rect = self.rect
    hit_list = [enemy for enemy in collision_test(attack_rect, actors) if enemy.alive and enemy != self and enemy.team != self.team and not enemy.cannot_be_attacked]

    if self.state in self.character.actions and self.frame < len(self.character.actions[self.state].frants):
      damage = self.character.actions[self.state].frants[self.frame].damage
      knockback_x = self.character.actions[self.state].frants[self.frame].knockback_x
      knockback_y = self.character.actions[self.state].frants[self.frame].knockback_y
    else: damage, knockback_x, knockback_y = 0, 0, 0

    for enemy in hit_list:
      self.attacked = False
      # if enemy.state in enemy.character.actions and enemy.frame < len(enemy.character.actions[enemy.state].frants):
      #   e_damage = enemy.character.actions[enemy.state].frants[enemy.frame].damage
      #   e_knockback_x = enemy.character.actions[enemy.state].frants[enemy.frame].knockback_x
      #   e_knockback_y = enemy.character.actions[enemy.state].frants[enemy.frame].knockback_y
      # else: e_damage, e_knockback_x, e_knockback_y = 0, 0, 0
      #if self.movement[1] > 0 and not collision["left"] and not collision["right"] and rect.bottom >= enemy.rect.top:
      if (self.rect.y < enemy.rect.y) and "stompable_head" in enemy.behaviors: #(self.rect.y < enemy.rect.y)
        if self.y_vel != 0 and self.character.beat_sound:
          if type(self.character.beat_sound) == list: self.beat_sfx = pygame.mixer.Sound("Sounds/sfx/" + self.character.beat_sound[random.randrange(0, len(self.character.beat_sound))])
          self.character.beat_sfx.play()
        rect.bottom = enemy.rect.top
        if self.movement[1] > 0 and self.state != "fly": self.state = "jump"; self.frame = 1; self.y_vel = self.jump_force
        collision['bottom'] = True
        enemy.change_hp(-1, self)
      # elif self.protection_timer.tally >= self.hit_protection: #and damage == 0
      #   self.hp -= e_damage; self.protection_timer.reset()
      #   self.state = "hurt"
      #   self.frame = 1
      #   if "hurt" in self.character.actions: self.frame = 1
      #   if not self.attacked and self.character.hurt_sound:
      #     if type(self.character.hurt_sound) == list: self.character.hurt_sfx = pygame.mixer.Sound("Sounds/sfx/" + self.character.hurt_sound[random.randrange(0, len(self.character.hurt_sound))])
      #     self.character.hurt_sfx.play()
      #   self.attacked = True
      elif damage and enemy.protection_timer.tally >= enemy.hit_protection and not self.attacked:
        enemy.change_hp(-damage, self)
        if not enemy.stagger: stagger = 1
        else: stagger = enemy.stagger
        if self.rect.x < enemy.rect.x: enemy.x_vel_kb += knockback_x * (stagger / 13); enemy.flipped = True
        if self.rect.x > enemy.rect.x: enemy.x_vel_kb += -knockback_x * (stagger / 13); enemy.flipped = False
        enemy.y_vel_kb += knockback_y * (stagger / 18)
        enemy.wait_timer.reset()
        if "hurt" in enemy.character.actions: enemy.state = "hurt"; enemy.frame = 1
        elif enemy.state == "away": enemy.state = "idle"; enemy.frame = 0
        if self.character.beat_sound:
          if type(self.character.beat_sound) == list: self.character.beat_sfx = pygame.mixer.Sound("Sounds/sfx/" + self.character.beat_sound[random.randrange(0, len(self.character.beat_sound))])
          self.character.beat_sfx.play()
        if enemy.character.hurt_sound:
          if type(enemy.character.hurt_sound) == list: enemy.character.hurt_sfx = pygame.mixer.Sound("Sounds/sfx/" + enemy.character.hurt_sound[random.randrange(0, len(enemy.character.hurt_sound))])
          enemy.character.hurt_sfx.play()
        self.attacked = True
        enemy.protection_timer.reset()
      #elif self.movement[1] < 0: collision['top'] = True

    hit_list = [tile for tile in collision_test(attack_rect, tiles) if tile.alive and tile != self and tile.team != self.team and tile.spawn_hp > 0]
    for tile in hit_list:
      self.attacked = False
      tile.hp -= damage
    
    return collision, rect
    
  def gravity(self, gravity=1.0, dt=1):
    self.y_vel += self.weight * gravity * dt
    if self.y_vel > 10: self.y_vel = 10
    self.movement[1] = self.y_vel
    self.movement[1] += self.y_vel_kb
    if self.collision["bottom"]: self.y_vel = 0; self.airtimer = 0
    else: self.airtimer += 1 * dt
    
    if self.y_vel_kb > 0: self.y_vel_kb -= 0.5
    if self.y_vel_kb < 0: self.y_vel_kb += 0.5
    if self.y_vel_kb < 1 and self.y_vel_kb > -1: self.y_vel_kb = 0

  def jump(self):
    if self.state in self.character.actions: allow_hop = self.character.actions[self.state].allow_jump
    else: allow_hop = True
    if self.state in self.character.actions: hold = self.character.actions[self.state].trigger_mode == "Hold"
    else: hold = True

    if hold:
      if allow_hop:
        if self.y_vel == 0 and self.collision['bottom'] and self.state != "fly": self.state = "jump"
        
        if self.airtimer < 10:
          self.y_vel = self.jump_force
          if self.collision['bottom'] and self.state != "fly":
            if self.character.jump_sound:
              if type(self.character.jump_sound) == list: self.character.jump_sfx = pygame.mixer.Sound("Sounds/sfx/" + self.character.jump_sound[random.randrange(0, len(self.character.jump_sound))])
              self.character.jump_sfx.play()
            self.character.actions["jump"].reset()

        #if self.airtimer > 3: self.state = "jump"
        #if self.state == "jump" and self.collision['bottom'] and self.character.land_sound:
        #  if type(self.character.land_sound) == list: self.character.land_sfx = pygame.mixer.Sound("Sounds/sfx/" + self.character.land_sound[random.randrange(0, len(self.character.land_sound))])
        #  self.character.land_sfx.play()
    else:
      if allow_hop:
        pass

  def wall_slide(self):
    if self.collision["left"] and self.movement[0] < 0:
      if "slide" in self.character.actions and not self.wall_sliding: self.state = "slide"; self.frame = 1; self.timer.reset()
      self.wall_sliding = True; self.air_timer = 0
      self.x_vel = 0
      self.x_vel_kb = 0
      self.x_accel = 0
      self.climbing = False
      self.flipped = True
    elif self.collision["right"] and self.movement[0] > 0:
      if "slide" in self.character.actions and not self.wall_sliding: self.state = "slide"; self.frame = 1; self.timer.reset()
      self.wall_sliding = True; self.air_timer = 0
      self.x_vel = 0
      self.x_vel_kb = 0
      self.x_accel = 0
      self.climbing = False
      self.flipped = False
    else: self.wall_sliding = False
        
    if self.wall_sliding: self.movement[1] *= self.friction

  def set_hp(self, hp, opponent=None):
    for stat in (stat for stat in self.main.game_stats if self.main.game_stats_effect[stat] == "hp"): self.stats[stat] = hp; self.hp = hp; break
    for stat in (stat for stat in self.main.game_stats if self.main.game_stats_effect[stat] == "stagger"): self.stats[stat] = hp; self.stagger = hp; break
    if self.hp <= 0 and self.start_hp > 0: self.defeat(opponent)
  
  def change_hp(self, hp, opponent=None):
    for stat in (stat for stat in self.main.game_stats if self.main.game_stats_effect[stat] == "hp"): self.stats[stat] += hp; self.hp += hp; break
    for stat in (stat for stat in self.main.game_stats if self.main.game_stats_effect[stat] == "stagger"): self.stats[stat] -= hp; self.stagger -= hp; break
    if self.hp <= 0 and self.start_hp > 0: self.defeat(opponent)

  def defeat(self, opponent):
    if opponent != None:
      if self.stat: opponent.stats[self.stat] += self.value
      else: pass
    self.alive = False
    if "defeat" in self.character.actions: self.state = "defeat"
    self.frame = 1
    if self.character.defeat_anim == "Tumble": self.y_vel = self.jump_force
    if self.character.defeat_anim == "Hide": self.hidden = True
    if self.character.defeat_sound:
      if type(self.character.defeat_sound) == list: self.character.defeat_sfx = pygame.mixer.Sound("Sounds/sfx/" + self.character.defeat_sound[random.randrange(0, len(self.character.defeat_sound))])
      self.character.defeat_sfx.play()

  def render_ui(self, screen, font):
    screen.blit(font.render(str(self.hp), True, "White"), (2, 50))
    for index, key in enumerate(self.stats):
      text = font.render(key + " " + str(self.stats[key]), True, "White").convert_alpha()
      screen.blit(text, (2, 50 + ((index + 1) * text.get_height())))
    #screen.blit(font.render(str(self.main.rooms[0].doors[0].tfi), True, "White").convert_alpha(), (2, 200))
      

class Player(Actor): #we use su
  def __init__(self, x, y, character=None, main=None, controller=None, index=0):#I'M FREE!!!1
    super().__init__(x=x, y=y, character=character, main=main)
    self.deceives = [0, 0]
    self.state_controls = self.character.state_controls.copy()
    self.port = controller
    self.button_dict = {"A Button": False, "B Button": False, "Y Button": False, "X Button": False, "D-Pad Right": False, "D-Pad Left": False, "D-Pad Up": False, "D-Pad Down": False, "R Shoulder": False, "L Shoulder": False, "Select": False, "Start": False}
    self.state_button = ""
    self.player_index = index
    self.behaviors = []
    self.in_spawn = True
    self.in_ = True
    self.hide_if_out = False
    for stat in (stat for stat in self.main.game_stats if self.main.game_stats_effect[stat] == "hp"): self.hp = self.main.game_stats_initpoint[stat]
    for stat in (stat for stat in self.main.game_stats if self.main.game_stats_effect[stat] == "speed" and self.main.game_stats[stat] == int): self.speed = self.main.game_stats_initpoint[stat]
    for stat in (stat for stat in self.main.game_stats if self.main.game_stats_effect[stat] == "leap" and self.main.game_stats[stat] == int): self.jump_force = -int(self.main.game_stats_initpoint[stat])

  def update(self, screen, cutscene=False, dt=1):
    if self.state in self.character.actions and self.frame < len(self.character.actions[self.state].frants): rect = pygame.FRect((self.rect.x, self.rect.y), (self.character.actions[self.state].frants[self.frame].rect.width, self.character.actions[self.state].frants[self.frame].rect.height))
    else: rect = self.rect
    
    self.display(screen=screen, cutscene=cutscene)

    for stat in (stat for stat in self.main.game_stats if self.main.game_stats_effect[stat] == "speed" and self.main.game_stats[stat] == int): self.speed = self.stats[stat]
    for stat in (stat for stat in self.main.game_stats if self.main.game_stats_effect[stat] == "leap" and self.main.game_stats[stat] == int): self.jump_force = -int(self.stats[stat])

    css = []
    for cs in self.main.rooms[self.main.current_room].cutscenes: css.append(cs.name)

    # if self.state in self.character.actions and self.frame < len(self.character.actions[self.state].frants):
    #   rect = pygame.FRect((self.rect.x + self.character.actions[self.state].frants[self.frame].rect.x, self.rect.y + self.character.actions[self.state].frants[self.frame].rect.y), (self.character.actions[self.state].frants[self.frame].rect.width, self.character.actions[self.state].frants[self.frame].rect.height))
    #   x_offset = self.character.actions[self.state].frants[self.frame].rect.x
    #   y_offset = self.character.actions[self.state].frants[self.frame].rect.x
    # else: rect = self.rect; x_offset, y_offset = 0, 0

    cs_conditions_met = []

    gravity = self.main.rooms[self.main.current_room].gravity
    for zone in self.main.rooms[self.main.current_room].zones:
      if rect.colliderect(zone.rect):
        gravity = zone.gravity
        if not zone.passed:
          zone.passed = True; zone.left = True
          if zone.enter_sound:
            if type(zone.enter_sound) == list: zone.enter_sfx = pygame.mixer.Sound("Sounds/sfx/" + zone.enter_sound[random.randrange(0, len(zone.enter_sound))])
            zone.enter_sfx.play()
          if zone.trigger_cutscene in css:
            if "Zone" in self.main.get_cutscene_from_name(zone.trigger_cutscene).conditions:
              cs_conditions_met.append("Zone")
              #self.main.play_cutscene(zone.trigger_cutscene)
          if zone.track_volume != 1.0: pygame.mixer_music.set_volume(zone.track_volume)
          if zone.void: self.set_hp(0)
      if zone.left and not rect.colliderect(zone.rect):
        zone.left = False
        if zone.exit_sound:
          if type(zone.exit_sound) == list: zone.exit_sfx = pygame.mixer.Sound("Sounds/sfx/" + zone.exit_sound[random.randrange(0, len(zone.exit_sound))])
          zone.exit_sfx.play()
        if zone.multi_active: zone.passed = False
        if zone.track_volume != 1.0: pygame.mixer_music.set_volume(1.0)

    tiles = []; coins = []; actors = []
    for layer in self.main.rooms[self.main.current_room].layers:
      for tile in (tile for tile in layer.tiles if tile.alive and tile.solid): tiles.append(tile)
      for actor in (actor for actor in layer.actors if actor.alive and ((not "spawn_often" in actor.behaviors and not "spawn_rarely" in actor.behaviors) or actor.clone)): actors.append(actor)
      for actor in (actor for actor in layer.actors if "solid" in actor.behaviors): tiles.append(actor)

    for room in self.main.rooms:
      for layer in room.layers:
        for coin in [coin for coin in layer.collectibles if (self.main.current_room == self.main.rooms.index(room) or coin.active_debt) and coin.grabbable]: coins.append(coin)
        
    for coin in coins:
      if coin.price_stat: grabbable = coin.price_value <= self.stats[coin.price_stat]
      else: grabbable = True
      if rect.colliderect(coin.rect) and coin.alive and grabbable:
        coin.alive = False
        if coin.sound:
          if type(coin.sound) == list: coin.sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + coin.sound[random.randrange(0, len(coin.sound))])
          coin.sfx.play()
        if coin.trigger_cutscene in css:
          if "Collectible" in self.main.get_cutscene_from_name(zone.trigger_cutscene).conditions:
            cs_conditions_met.append("Collectible")
            #self.main.play_cutscene(coin.trigger_cutscene)
        if coin.stat in self.main.game_stats:
          if self.main.game_stats[coin.stat] == int or self.main.game_stats[coin.stat] == float:
            self.stats[coin.stat] += coin.value
          if self.main.game_stats[coin.stat] == bool:
            if coin.value == "True": self.stats[coin.stat] = True
            if coin.value == "False": self.stats[coin.stat] = False
            if coin.value == "Negate": self.stats[coin.stat] = not self.stats[coin.stat]
            for stat in self.stats:
              if stat in self.character.actions:
                if stat != coin.stat: self.stats[stat] = False
                else:
                  if self.main.game_stats_effect[stat] == "ability a": self.state_controls["A Button"].append(stat)
                  if self.main.game_stats_effect[stat] == "ability b": self.state_controls["B Button"].append(stat)
                  if self.main.game_stats_effect[stat] == "ability x": self.state_controls["X Button"].append(stat)
                  if self.main.game_stats_effect[stat] == "ability y": self.state_controls["Y Button"].append(stat)
                  #if self.main.game_stats_effect[stat] == "ability a click": self.state_controls["A Button"].append(stat); self.main.input_hold["A"] = False
                  #if self.main.game_stats_effect[stat] == "ability b click": self.state_controls["B Button"].append(stat); self.main.input_hold["B"] = False
                  #if self.main.game_stats_effect[stat] == "ability x click": self.state_controls["X Button"].append(stat); self.main.input_hold["X"] = False
                  #if self.main.game_stats_effect[stat] == "ability y click": self.state_controls["Y Button"].append(stat); self.main.input_hold["Y"] = False
                  #if self.main.game_stats_effect[stat] == "ability a hold": self.state_controls["A Button"].append(stat); self.main.input_hold["A"] = True
                  #if self.main.game_stats_effect[stat] == "ability b hold": self.state_controls["B Button"].append(stat); self.main.input_hold["B"] = True
                  #if self.main.game_stats_effect[stat] == "ability x hold": self.state_controls["X Button"].append(stat); self.main.input_hold["X"] = True
                  #if self.main.game_stats_effect[stat] == "ability y hold": self.state_controls["Y Button"].append(stat); self.main.input_hold["Y"] = True
          if self.main.game_stats[coin.stat] == str: self.stats[coin.stat] = coin.value
          if coin.price_value != 0 and coin.price_exchange:
            if not coin.price_decrement: self.stats[coin.price_stat] -= coin.price_value
            else: self.debt = coin.price_value; coin.active_debt = True
      if coin.active_debt:
        self.stats[coin.price_stat] -= 1
        self.debt -= 1
        if coin.debt_drop_sound:
          if type(coin.debt_drop_sound) == list: coin.debt_drop_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + coin.debt_drop_sound[random.randrange(0, len(coin.debt_drop_sound))])
          coin.debt_drop_sfx.play()
        if self.debt == 0: coin.active_debt = False

    #STAT RANGE
    for stat in [stat for stat in self.stats if self.main.game_stats[stat] == int or self.main.game_stats[stat] == float]:
      if self.main.game_stats_range[stat][0] < self.main.game_stats_range[stat][1]:
        if self.stats[stat] > self.main.game_stats_range[stat][1]: self.stats[stat] = self.main.game_stats_range[stat][1]
        if self.stats[stat] < self.main.game_stats_range[stat][0]: self.stats[stat] = self.main.game_stats_range[stat][0]
      if self.main.game_stats_effect[stat] == "hp": self.stats[stat] = self.hp
    
    required_stats_met = []
    for stat in [stat for stat in self.stats if self.main.game_stats[stat] == bool]:
      if self.stats[stat]: required_stats_met.append(stat)

    self.movement[0] += self.x_vel_kb
    if self.x_vel_kb > self.terminal_x_vel: self.x_vel_kb = self.terminal_x_vel
    if self.x_vel_kb < -self.terminal_x_vel: self.x_vel_kb = -self.terminal_x_vel
    if self.x_vel_kb > 0: self.x_vel_kb -= 0.2
    if self.x_vel_kb < 0: self.x_vel_kb += 0.2
    if self.x_vel_kb > -1 and self.x_vel_kb < 1: self.x_vel_kb = 0

    self.collision, self.rect = self.combat(actors + self.main.players, tiles, rect)
    self.collision, self.rect = self.move(tiles, rect, dt)

    if self.alive_in_room_for_frames < 2:
      for cs in self.main.rooms[self.main.current_room].cutscenes:
        if "Start of Room" in cs.conditions:
          #if cs.condition_gate == "or": self.main.play_cutscene(cs)
          cs_conditions_met.append("Start of Room"); break


    for door in self.main.rooms[self.main.current_room].doors:
      if (((self.state == "door" and door.requires_input) or not door.requires_input) and (door.rect.colliderect(rect) and door.passable and not door.t_playing)) or door.cutscene_transport:
        door.t_playing = True; self.main.playback_on = False; self.main.frame_timer.reset(); self.main.selected_key = 0; door.cutscene_transport = False
        if door.enter_sound:
          if type(door.enter_sound) == list: door.enter_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + door.enter_sound[random.randrange(0, len(door.enter_sound))])
          door.enter_sfx.play()
        if "Fade to Room" in door.transition: door.tfi = 150
        else: door.tfi = 0
      if door.t_over and door.t_playing:
        if self.main.rooms[self.main.current_room].track != self.main.rooms[door.led_room].track:
          if self.main.rooms[door.led_room].track and not self.main.rooms[door.led_room].first_track: pygame.mixer.music.load(self.main.active_directory + f"Sounds/tracks/{self.main.rooms[door.led_room].track}"); pygame.mixer.music.play(-1, 0.0); self.main.track = self.main.rooms[door.led_room].track
          if self.main.rooms[door.led_room].first_track: pygame.mixer.music.load(self.main.active_directory + f"Sounds/tracks/{self.main.rooms[door.led_room].first_track}"); pygame.mixer.music.play(1, 0.0); self.main.track = self.main.rooms[door.led_room].track
          if (not self.main.rooms[door.led_room].first_track) and (not self.main.rooms[door.led_room].track): pygame.mixer.music.stop()
        self.y_vel = 0.0; self.x_vel = 0.0; self.x_accel = 0.0; self.x_vel_kb; self.airtimer = 0; self.main.current_room = door.led_room; self.main.camera.scroll[0] = (door.led_pos[0] - (self.main.width / 2)) * int(self.main.rooms[self.main.current_room].borders["left"] != 0 or self.main.rooms[self.main.current_room].borders["right"] != 0); self.main.camera.scroll[1] = (door.led_pos[1] - (self.main.height / 2)) * int(self.main.rooms[self.main.current_room].borders["top"] != 0 or self.main.rooms[self.main.current_room].borders["bottom"] != 0)
        for cs in self.main.rooms[self.main.current_room].cutscenes:
          if "Start of Room" in cs.conditions:
            if cs.condition_gate == "or": self.main.play_cutscene(cs)
            cs_conditions_met.append("Start of Room"); break
        if self.main.camera.scroll[0] < self.main.rooms[self.main.current_room].borders["left"]: self.main.camera.scroll[0] = self.main.rooms[self.main.current_room].borders["left"]
        if self.main.camera.scroll[0] > self.main.rooms[self.main.current_room].borders["right"]: self.main.camera.scroll[0] = self.main.rooms[self.main.current_room].borders["right"]
        if self.main.camera.scroll[1] < self.main.rooms[self.main.current_room].borders["top"]: self.main.camera.scroll[1] = self.main.rooms[self.main.current_room].borders["top"]
        if self.main.camera.scroll[1] > self.main.rooms[self.main.current_room].borders["bottom"]: self.main.camera.scroll[1] = self.main.rooms[self.main.current_room].borders["bottom"]
        for ui in self.main.ui.instances:
          if self.main.ui.instances[ui]["SM"] in self.main.rooms[self.main.current_room].show_ui: self.main.ui.instances[ui]["Hidden"] = False
          if self.main.ui.instances[ui]["SM"] in self.main.rooms[self.main.current_room].hide_ui: self.main.ui.instances[ui]["Hidden"] = True
        self.rect.x, self.rect.y = door.led_pos[0], door.led_pos[1]; self.key_frame_rect.x, self.key_frame_rect.y = door.led_pos[0], door.led_pos[1]
        door.transport_everyone()
        if "reset" in self.main.rooms[self.main.current_room].menu["flags"]: self.main.rooms[self.main.current_room].selected_item = [0, 0]

    #Play cutscene with met conditions because the cutscene has an AND gate
    for cs in self.main.rooms[self.main.current_room].cutscenes:
      if contains_all(cs_conditions_met, cs.conditions) and cs.condition_gate == "and":
        self.main.play_cutscene(cs); break
      if any(x in cs.conditions for x in cs_conditions_met) and cs.condition_gate == "or":
        self.main.play_cutscene(cs); break
    
    if self.gravity_enabled and self.main.rooms[self.main.current_room].mode == "Platformer": self.gravity(gravity, dt)

    if self.state in self.character.actions: self.gravity_enabled = self.character.actions[self.state].apply_gravity
    else: self.gravity_enabled = False

    #self.port.update(self.main)

    for stat in [stat for stat in self.stats if self.main.game_stats_effect[stat] == "hp"]: self.stats[stat] = self.hp

    if self.main.game_paused: self.port.disable()
    if not self.immobilize:
      if self.in_:
        if self.alive: self.controls(dt)
        else:
          if not self.accelerated_travel: self.movement[0] = 0
          elif self.x_accel > 0: self.x_accel -= 0.2
      else: self.decision_move(dt)

    if self.character.wall_slider: self.wall_slide()#Scrolling

    if self.main.camera.follow_player:
      self.deceives = [self.rect.x - self.main.camera.scroll[0], self.rect.y - self.main.camera.scroll[1]]
      if self.main.rooms[self.main.current_room].scroll_mode != "No Scroll":
        if self.main.rooms[self.main.current_room].scroll_mode == "Default Scroll":
          if self.deceives[0] > self.main.width - self.main.rooms[self.main.current_room].move_threshold["right"] and self.main.camera.scroll[0] < self.main.rooms[self.main.current_room].borders["right"]: self.main.camera.scroll[0] += self.speed * dt
          if self.deceives[0] < self.main.rooms[self.main.current_room].move_threshold["left"] and self.main.camera.scroll[0] > self.main.rooms[self.main.current_room].borders["left"]: self.main.camera.scroll[0] -= self.speed * dt
          if self.deceives[1] > self.main.width - self.main.rooms[self.main.current_room].move_threshold["bottom"] and self.main.camera.scroll[1] < self.main.rooms[self.main.current_room].borders["bottom"]: self.main.camera.scroll[1] += 5 * dt
          if self.deceives[1] < self.main.rooms[self.main.current_room].move_threshold["top"] and self.main.camera.scroll[1] > self.main.rooms[self.main.current_room].borders["top"]: self.main.camera.scroll[1] -= 5 * dt
        elif self.main.rooms[self.main.current_room].scroll_mode == "Snapped Scroll":
          if self.deceives[0] >= self.main.width and self.main.camera.scroll[0] < self.main.rooms[self.main.current_room].borders["right"]: self.main.camera.scroll[0] += self.main.width
          if self.deceives[0] < 0 and self.main.camera.scroll[0] > self.main.rooms[self.main.current_room].borders["left"]: self.main.camera.scroll[0] -= self.main.width
          if self.deceives[1] >= self.main.width and self.main.camera.scroll[1] < self.main.rooms[self.main.current_room].borders["bottom"]: self.main.camera.scroll[1] += self.main.height
          if self.deceives[1] < 0 and self.main.camera.scroll[1] > self.main.rooms[self.main.current_room].borders["top"]: self.main.camera.scroll[1] -= self.main.height
        elif self.main.rooms[self.main.current_room].scroll_mode == "Central Focus" and self.player_index == 0:
          self.main.camera.scroll[0] = (self.rect.x + (self.rect.width / 2)) - (self.main.width / 2)
          self.main.camera.scroll[1] = (self.rect.y + (self.rect.height / 2)) - (self.main.height / 2)
        if self.main.rooms[self.main.current_room].scroll_mode != "Snapped Scroll":
          if self.main.camera.scroll[0] < self.main.rooms[self.main.current_room].borders["left"]: self.main.camera.scroll[0] = self.main.rooms[self.main.current_room].borders["left"]
          if self.main.camera.scroll[0] > self.main.rooms[self.main.current_room].borders["right"]: self.main.camera.scroll[0] = self.main.rooms[self.main.current_room].borders["right"]
          if self.main.camera.scroll[1] < self.main.rooms[self.main.current_room].borders["top"]: self.main.camera.scroll[1] = self.main.rooms[self.main.current_room].borders["top"]
          if self.main.camera.scroll[1] > self.main.rooms[self.main.current_room].borders["bottom"]: self.main.camera.scroll[1] = self.main.rooms[self.main.current_room].borders["bottom"]
    if self.main.rooms[self.main.current_room].hm:
      if self.rect.x > self.main.width + self.main.camera.scroll[0] - 4: self.rect.x = self.main.camera.scroll[0] + 4
      if self.rect.x + 4 < self.main.camera.scroll[0]: self.rect.x = self.main.width + self.main.camera.scroll[0] - 4
    if self.main.rooms[self.main.current_room].vm:
      if self.rect.y > self.main.height + self.main.camera.scroll[1] - 4: self.rect.y = self.main.camera.scroll[1] + 4
      if self.rect.y + 4 < self.main.camera.scroll[1]: self.rect.y = self.main.height + self.main.camera.scroll[1] - 4

  def controls(self, dt=1):
    if not self.main.game_paused: self.wait_timer.nonstopcount(1 * dt)

    if "turn" in self.character.actions:
      if self.state == "turn":
        if not self.flipped:
          self.frame += 1; self.timer.reset(); self.turn_rate += 1
          if self.turn_rate > 2: self.flipped = True; self.turn_rate = 0; self.state = "walk"
        elif self.flipped:
          self.frame += 1; self.timer.reset(); self.turn_rate += 1
          if self.turn_rate > 2: self.flipped = False; self.turn_rate = 0; self.state = "walk"

    if self.state in self.character.actions: prior = self.character.actions[self.state].prioritize_action
    else: prior = False
    if self.state in self.character.actions: allow_walk = self.character.actions[self.state].allow_travel
    else: allow_walk = True
    if self.state in self.character.actions: allow_hop = self.character.actions[self.state].allow_jump
    else: allow_hop = True
    if self.state in self.character.actions: allow_flip = self.character.actions[self.state].allow_flip
    else: allow_flip = True

    self.state = self.state.lower()

    remember_state = self.state

    if self.state in self.character.actions: ca = self.character.actions[self.state]
    else: ca = self.character.actions["idle"]
      
    idled = False

    walking = False

    if self.character.mode == "platformer":
      if self.state != "walk" and self.state != "walkstart": self.started_walking = False
      if self.state == "walkstart" and not self.movement[0]: self.state = "idle"; self.frame = 0
      
      if self.port.buttons[self.character.actions["walk"].trigger_mode]["right"] and ("walk" in self.state_controls["D-Pad Right"]):
        if not prior:
          if "walkstart" in self.character.actions and not self.started_walking:
            if self.state != "walkstart": self.frame = 0
            self.state = "walkstart"
          if self.state == "walkstart" and self.frame + 1 >= len(self.character.actions["walkstart"].frames) and self.time_accumulator >= 0.9 / self.character.actions[self.state].rate if self.character.actions[self.state].rate else 1.0: self.started_walking = True; self.state = "walk"; self.frame = 0
          if self.started_walking or not "walkstart" in self.character.actions: self.state = "walk"
        if allow_flip:
          if self.flipped:
            if "turn" in self.character.actions and not prior: self.state = "turn"
            if not "turn" in self.character.actions: self.flipped = False
        if allow_walk:
          if not self.accelerated_travel:
            if not self.flipped: self.movement[0] = self.speed
            if self.collision["bottom"]: self.x_vel += 0.1 * dt
          else: self.x_accel += 0.2 * dt
        walking = True
        self.wait_timer.reset()
        idled = True
        if self.collision["right"] and self.wall_sliding and self.flipped: self.movement[0] = 0

      if self.port.buttons[self.character.actions["walk"].trigger_mode]["left"] and ("walk" in self.state_controls["D-Pad Left"]):
        if not prior:
          if "walkstart" in self.character.actions and not self.started_walking:
            if self.state != "walkstart": self.frame = 0
            self.state = "walkstart"
          if self.state == "walkstart" and self.frame + 1 >= len(self.character.actions["walkstart"].frames) and self.time_accumulator >= 0.9 / self.character.actions[self.state].rate if self.character.actions[self.state].rate else 1.0: self.started_walking = True; self.state = "walk"; self.frame = 0
          if self.started_walking or not "walkstart" in self.character.actions: self.state = "walk"
        if allow_flip:
          if not self.flipped:
            if "turn" in self.character.actions and not prior: self.state = "turn"
            if not "turn" in self.character.actions: self.flipped = True
        if allow_walk:
          if not self.accelerated_travel:
            if self.flipped: self.movement[0] = -self.speed
            if self.collision["bottom"]: self.x_vel -= 0.1 * dt
          else: self.x_accel += 0.2 * dt
        walking = True
        self.wait_timer.reset()
        idled = True
        if self.collision["left"] and self.wall_sliding and not self.flipped: self.movement[0] = 0



    elif self.character.mode == "topdown":
      if self.port.buttons[self.character.actions["walk"].trigger_mode]["right"] and ("walk" in self.state_controls["D-Pad Right"]):
        if not prior: self.state = "walk"; self.direction = "right"
        if allow_flip:
          if self.flipped:
            if not prior: self.state = "turn"
            self.frame = 1; self.timer.reset(); self.turn_rate += 1
            if self.turn_rate > 2: self.flipped = False; self.turn_rate = 0
        if allow_walk:
          if not self.accelerated_travel:
            if not self.flipped: self.movement[0] = self.speed * dt
          else: self.x_accel += 0.2 * dt
        walking = True
        self.wait_timer.reset()
        idled = True

      if self.port.buttons[self.character.actions["walk"].trigger_mode]["left"] and ("walk" in self.state_controls["D-Pad Left"]):
        if not prior: self.state = "walk"; self.direction = "left"
        if allow_flip:
          if not self.flipped:
            if not prior: self.state = "turn"
            self.frame = 1; self.timer.reset(); self.turn_rate += 1
            if self.turn_rate > 2: self.flipped = True; self.turn_rate = 0
        if allow_walk:
          if not self.accelerated_travel:
            if self.flipped: self.movement[0] = -self.speed * dt
          else: self.x_accel += 0.2 * dt
        walking = True
        self.wait_timer.reset()
        idled = True

      if self.port.buttons[self.character.actions["walk"].trigger_mode]["up"] and ("walk" in self.state_controls["D-Pad Up"]):
        if not prior: self.state = "walk"; self.direction = "up"
        if allow_flip:
          if self.flipped:
            if not prior: self.state = "turn"
            self.frame = 1; self.timer.reset(); self.turn_rate += 1
            if self.turn_rate > 2: self.flipped = False; self.turn_rate = 0
        if allow_walk:
          if not self.accelerated_travel:
            if not self.flipped: self.movement[0] = self.speed * dt
          else: self.x_accel += 0.2 * dt
        walking = True
        self.wait_timer.reset()
        idled = True

      if self.port.buttons[self.character.actions["walk"].trigger_mode]["down"] and ("walk" in self.state_controls["D-Pad Down"]):
        if not prior: self.state = "walk"; self.direction = "down"
        if allow_flip:
          if not self.flipped:
            if not prior: self.state = "turn"
            self.frame = 1; self.timer.reset(); self.turn_rate += 1
            if self.turn_rate > 2: self.flipped = True; self.turn_rate = 0
        if allow_walk:
          if not self.accelerated_travel:
            if self.flipped: self.movement[0] = -self.speed * dt
          else: self.x_accel += 0.2 * dt
        walking = True
        self.wait_timer.reset()
        idled = True

    if self.collision["bottom"] or self.wall_sliding: self.jumps_left = self.character.jumps
    if self.character.jumps == 0: self.jumps_left = -1

    if idled: pass
    elif self.state != "hurt":
      if not self.accelerated_travel: self.movement[0] = 0
      elif self.x_accel > 0: self.x_accel -= 0.2
      if abs(self.x_accel < 0.15): self.x_accel = 0.0
      if (self.state == "walk" or self.state == "jump") and self.collision["bottom"]:
        if not prior: self.state = "idle"
    if allow_hop:
      if self.character.actions["jump"].trigger_mode == "Release": mode = "Release"
      else: mode = "Hold"
      if (self.port.buttons[mode]["up"] and ("jump" in self.state_controls["D-Pad Up"])) or (self.port.buttons[mode]["down"] and ("jump" in self.state_controls["D-Pad Down"])) or (self.port.buttons[mode]["right"] and ("jump" in self.state_controls["D-Pad Right"])) or (self.port.buttons[mode]["left"] and ("jump" in self.state_controls["D-Pad Left"])) or (self.port.buttons[mode]["a"] and ("jump" in self.state_controls["A Button"])) or (self.port.buttons[mode]["b"] and ("jump" in self.state_controls["B Button"])) or (self.port.buttons[mode]["x"] and ("jump" in self.state_controls["X Button"])) or (self.port.buttons[mode]["y"] and ("jump" in self.state_controls["Y Button"])) or (self.port.buttons[mode]["l"] and ("jump" in self.state_controls["L Shoulder"])) or (self.port.buttons[mode]["r"] and ("jump" in self.state_controls["R Shoulder"])) or (self.port.buttons[mode]["select"] and ("jump" in self.state_controls["Select"])) or (self.port.buttons[mode]["start"] and ("jump" in self.state_controls["Start"])):
        self.wait_timer.reset()
        if self.state != "jump" and self.character.jump_sound and self.collision["bottom"]:
          if type(self.character.jump_sound) == list: self.character.jump_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.character.jump_sound[random.randrange(0, len(self.character.jump_sound))])
          self.character.jump_sfx.play(); self.frame = 1
        # if self.y_vel == 0 and self.collision['bottom'] and self.state != "fly":
        #   if not prior: self.state = "jump"
        if self.wall_sliding:
          if self.collision["left"]: self.movement[0] = self.jump_force; self.x_vel = self.jump_force
          elif self.collision["right"]: self.movement[0] = -self.jump_force; self.x_vel = -self.jump_force
          self.wall_sliding = False
        if self.character.actions["jump"].trigger_mode == "Hold":
          if "jump" in self.character.actions and self.airtimer < self.character.jumps * 10:
            self.y_vel = self.jump_force; self.frame = 1
        else:
          if "jump" in self.character.actions and self.jumps_left:
            self.y_vel = self.jump_force * 1.5; self.frame = 1; self.jumps_left -= 1
    if not self.collision["bottom"] and (not prior) and not self.wall_sliding: self.state = "jump"
    elif self.wall_sliding and "slide" in self.character.actions and not prior: self.state = "slide"

    self.button_dict = {"A Button": self.port.buttons[ca.trigger_mode]["a"], "B Button": self.port.buttons[ca.trigger_mode]["b"], "Y Button": self.port.buttons[ca.trigger_mode]["y"], "X Button": self.port.buttons[ca.trigger_mode]["x"], "D-Pad Right": self.port.buttons[ca.trigger_mode]["right"], "D-Pad Left": self.port.buttons[ca.trigger_mode]["left"], "D-Pad Up": self.port.buttons[ca.trigger_mode]["up"], "D-Pad Down": self.port.buttons[ca.trigger_mode]["down"], "R Shoulder": self.port.buttons[ca.trigger_mode]["r"], "L Shoulder": self.port.buttons[ca.trigger_mode]["l"], "Select": self.port.buttons[ca.trigger_mode]["select"], "Start": self.port.buttons[ca.trigger_mode]["start"]}
    
    for button, states in self.state_controls.items():
      if self.state in self.character.actions:
        if self.character.actions[self.state].condition_stat in self.stats: cond1 = self.stats[self.character.actions[self.state].condition_stat]
        else: cond1 = True
      else: cond1 = True
      for state in sorted(states, key=lambda s: (self.character.actions[s].combo == "none", self.character.actions[s].combo)):
        if self.button_dict.get(button, False) and cond1 and state in self.character.states and state != "idle" and state != "walk" and state != "jump" and self.state != state and self.frame != 1 and (not self.character.actions[state].aerial or not self.collision["bottom"]) and (not prior) and (not self.character.actions[state].terrestial or self.collision["bottom"]):
          self.combo_activation_count = -1
          if self.character.actions[state].combo == "none" or (self.port.buttons["Hold"]["right"] and self.character.actions[state].combo == "right") or (self.port.buttons["Hold"]["left"] and self.character.actions[state].combo == "left") or (self.port.buttons["Hold"]["up"] and self.character.actions[state].combo == "up") or (self.port.buttons["Hold"]["down"] and self.character.actions[state].combo == "down") or ((self.port.buttons["Hold"]["right"] or self.port.buttons["Hold"]["left"]) and self.character.actions[state].combo == "side") or ((self.port.buttons["Hold"]["up"] or self.port.buttons["Hold"]["down"]) and self.character.actions[state].combo == "updown") or ((self.port.buttons["Hold"]["right"] or self.port.buttons["Hold"]["left"] or self.port.buttons["Hold"]["up"] or self.port.buttons["Hold"]["down"]) and self.character.actions[state].combo == "all around"):
            self.state = state; self.frame = 0; self.state_button = button; self.wait_timer.reset()
            if self.character.actions[self.state].frants[self.frame - 1].sound:
              if type(self.character.actions[self.state].frants[self.frame - 1].sound) == list: self.character.actions[self.state].frants[self.frame - 1].sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.character.actions[self.state].frants[self.frame - 1].sound[random.randrange(0, len(self.character.actions[self.state].frants[self.frame - 1].sound))])
              self.character.actions[self.state].frants[self.frame - 1].sfx.play()
            break # if button is pressed #self.state_controls[get_key_from_value(self.state_controls, self.state)]

    if self.state in self.character.actions:
      if self.state != "idle" and self.state != "walk" and self.state != "walkstart" and self.state != "jump" and self.state != "turn" and self.state != "fly" and self.state != "slide" and self.state != "climb" and self.state != "hurt":
        #if self.character.actions[self.state].frame == 0:
        #  if get_key_from_value(self.button_dict, True) in {"A Button": "A", "B Button": "B", "Y Button": "Y", "X Button": "X", "D-Pad Right": "Right", "D-Pad Left": "Left", "D-Pad Up": "Up", "D-Pad Down": "Down", "R Shoulder": "R", "L Shoulder": "L", "Z Button": "Z", "Select": "SELECT", "Start": "START"}:
        #    if not self.main.input_hold[{"A Button": "A", "B Button": "B", "Y Button": "Y", "X Button": "X", "D-Pad Right": "Right", "D-Pad Left": "Left", "D-Pad Up": "Up", "D-Pad Down": "Down", "R Shoulder": "R", "L Shoulder": "L", "Z Button": "Z", "Select": "SELECT", "Start": "START"}[get_key_from_value(button_dict, True)]] and not self.actions[self.state].continue_until_cancel: self.state = "idle"
        #  else: pass
        if self.frame >= len(self.character.actions[self.state].frames) - 1 and self.finished:
          if not self.character.actions[self.state].continue_until_cancel: self.state = "idle"; self.offset = [0, 0]
          else:
            if self.character.actions[self.state].loop: self.frame = 0
            else: self.frame = len(self.character.actions[self.state].frames) - 1
      elif self.state == "hurt" and self.frame == 0: self.state = "idle"; self.offset = [0, 0]
    else: self.state = "idle"; self.offset = [0, 0]

    if self.x_accel > self.speed: self.x_accel = self.speed
    if self.accelerated_travel:
      if not self.flipped and not self.collision["right"]: self.movement[0] = self.x_accel
      elif self.flipped and not self.collision["left"]: self.movement[0] = -self.x_accel

    if self.character.mode == "platformer":
      if self.state in self.character.actions:
        if self.state.lower():
          if self.character.actions[self.state.lower()].condition_stat:
            if not self.stats[self.character.actions[self.state].condition_stat]: self.state = "idle"; self.offset = [0, 0]
      
      if (self.character.actions[self.state.lower()].cancel_on_walk and walking): self.state = "idle"; self.offset = [0, 0]
      if (self.character.actions[self.state.lower()].cancel_on_ground and self.collision["bottom"]): self.state = "idle"; self.offset = [0, 0]
      if (self.character.actions[self.state.lower()].cancel_on_jump and self.y_vel > 0.0): self.state = "idle"; self.offset = [0, 0]

    elif self.character.mode == "topdown":
      if self.state in self.character.actions:
        if self.state.lower():
          if self.character.actions[self.dir][self.state.lower()].condition_stat:
            if not self.stats[self.dir][self.character.actions[self.state].condition_stat]: self.state = "idle"; self.offset = [0, 0]
      
      if (self.character.actions[self.dir][self.state.lower()].cancel_on_ground and self.y_vel == 0): self.state = "idle"; self.offset = [0, 0]
      if (self.character.actions[self.dir][self.state.lower()].cancel_on_walk and walking): self.state = "idle"; self.offset = [0, 0]
      if (self.character.actions[self.dir][self.state.lower()].cancel_on_jump and self.y_vel > 0.0): self.state = "idle"; self.offset = [0, 0]
                       
    if self.main.playback_on and self.immobilize: self.state = remember_state

    if self.state == "idle" or self.state == "walk" or self.state == "jump": self.state_button = ""

    if "away" in self.character.actions and not self.immobilize and not self.main.game_paused:
      if self.state == "idle":
        if self.wait_timer.tally > self.character.away_delay and self.character.away_delay: self.state = "away"
        if self.wait_timer.tally > self.character.away_delay + self.character.wake_up_delay and self.character.wake_up_delay: self.wait_timer.reset()
        if self.y_vel != 0: self.wait_timer.reset()
      if self.state == "away" and self.frame >= len(self.character.actions["away"].frames) - 1:
        if self.character.mode == "platformer":
          if not self.character.actions[self.state.lower()].loop: self.state = "idle"; self.offset = [0, 0]; self.wait_timer.reset(); self.frame = 0
        elif self.character.mode == "topdown":
          if not self.character.actions[self.dir][self.state.lower()].loop: self.state = "idle"; self.offset = [0, 0]; self.wait_timer.reset(); self.frame = 0

  def decision_move(self, dt):
    pass


def collision_test(rect, tiles): hit_list = [tile for tile in tiles if tile.alive and rect.colliderect(tile)]; return hit_list



class Entity(Actor):
  def __init__(self, x, y, etype, main, font, font_size, clone=False):
    super().__init__(x=x, y=y, character=main.character_types[next(key for key, value in main.character_types.items() if value.get("type") == etype["character"])]["object"], main=main)
    self.type = etype
    self.type_index = etype["index"]
    #self.type_index = etype.index
    #self.character = etype.character
    self.name = self.character.character
    self.speed = self.character.speed
    self.jump_force = self.character.jump_force
    self.hp = etype["hp"]
    self.stat = etype["stat"]
    self.value = etype["value"]
    self.behaviors = etype["behaviors"]
    self.range = etype["range"]
    self.drops = etype["drops"]
    self.initial_direction = "right"
    if type(font) == pygame.Font: self.font_str = None; self.font = font
    elif type(font) == str and font: self.font_str = font; self.font = pygame.Font(self.main.active_directory + self.font_str, font_size)
    else: self.font_str = ""; self.font = pygame.Font(None, font_size)
    self.font_size = 20
    self.font_color = "White"
    self.dialogue = []
    #self.dialogue = ["Hello", "This is your dialogue test"]
    self.current_dialogue = 0
    self.dl_timer = Timer()
    self.dialogue_text = ""
    self.add_letter_to_dialogue_timer = Timer()
    self.letter_delay = []
    self.start_hp = self.hp
    self.ai = AI(self)
    self.spawn_location = [x, y]
    self.player_switch = None
    self.player_partner = None
    self.bossfight = False
    self.bossfight = {
      "bossfight": False,
      "active": False,
      "waves": 4,
      "wave_1": {
        "start_hp": self.start_hp,
        "wait": 1,
        "attacks": []
      },
      "wave_2": {
        "start_hp": self.start_hp // 2,
        "wait": 0.5,
        "attacks": []
      },
      "wave_3": {
        "start_hp": (self.start_hp // 2) // 2,
        "wait": 0.25,
        "attacks": []
      },
      "wave_4": {
        "start_hp": ((self.start_hp // 2) // 2) // 2,
        "wait": 0.1,
        "attacks": []
      },
    }

  def update(self, screen, font, dt=1):
    if self.state in self.character.actions and self.frame < len(self.character.actions[self.state].frants): rect = pygame.FRect((self.rect.x, self.rect.y), (self.character.actions[self.state].frants[self.frame].rect.width - self.character.actions[self.state].frants[self.frame].rect.x, self.character.actions[self.state].frants[self.frame].rect.height - self.character.actions[self.state].frants[self.frame].rect.y))
    else: rect = self.rect

    gravity = self.main.rooms[self.main.current_room].gravity
    for zone in [zone for zone in self.main.rooms[self.main.current_room].zones if zone.entity_active]:
      if rect.colliderect(zone.rect):
        gravity = zone.gravity
        if not zone.passed:
          zone.passed = True; zone.left = True
          if zone.enter_sound:
            if type(zone.enter_sound) == list: zone.enter_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + zone.enter_sound[random.randrange(0, len(zone.enter_sound))])
            zone.enter_sfx.play()
          css = []
          for cs in self.main.rooms[self.main.current_room].cutscenes: css.append(cs.name)
          if zone.trigger_cutscene in css: self.main.play_cutscene(zone.trigger_cutscene)
          if zone.track_volume != 1.0: pygame.mixer_music.set_volume(zone.track_volume)
          if zone.void: self.set_hp(0)
      if zone.left and not rect.colliderect(zone.rect):
        zone.left = False
        if zone.exit_sound:
          if type(zone.exit_sound) == list: zone.exit_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + zone.exit_sound[random.randrange(0, len(zone.exit_sound))])
          zone.exit_sfx.play()
        if zone.multi_active: zone.passed = False
        if zone.track_volume != 1.0: pygame.mixer_music.set_volume(1.0)

    if (not "spawn_often" in self.behaviors and not "spawn_rarely" in self.behaviors) or self.clone:
      move = True
      if self.rect.x - 1 > self.main.camera.scroll[0] + (self.main.width + self.rect.width): move = False
      if self.rect.right + 1 < self.main.camera.scroll[0]: move = False
      if self.rect.y - 1 > self.main.camera.scroll[1] + (self.main.height + self.rect.height): move = False
      if self.rect.bottom + 1 < self.main.camera.scroll[1]: move = False
      if (move and "in_frame_motion" in self.behaviors) or not "in_frame_motion" in self.behaviors: 
        tiles = [] #oh
        for layer in self.main.rooms[self.main.current_room].layers:
          for tile in (tile for tile in layer.tiles if tile.alive and tile.solid): tiles.append(tile)

        self.movement[0] = self.x_vel_kb
        if self.x_vel_kb > self.terminal_x_vel: self.x_vel_kb = self.terminal_x_vel
        if self.x_vel_kb < -self.terminal_x_vel: self.x_vel_kb = -self.terminal_x_vel
        if self.x_vel_kb > 0: self.x_vel_kb -= 1
        if self.x_vel_kb < 0: self.x_vel_kb += 1
        if self.x_vel_kb > -1 and self.x_vel_kb < 1: self.x_vel_kb = 0

        self.collision, self.rect = self.move(tiles, self.rect, dt)

        if not self.alive or not "fly" in self.behaviors:
          if self.main.rooms[self.main.current_room].mode == "Platformer": self.gravity(gravity, dt)
        if self.alive:
          if not self.immobilize: self.behave()
        else: self.movement[0] = 0

    if len(self.dialogue) and self.alive:
      if self.dl_timer.tally < len(self.dialogue[self.current_dialogue]):
        if self.add_letter_to_dialogue_timer.timer(self.main.fps / self.letter_delay[self.current_dialogue]):
          self.dialogue_text += self.dialogue[self.current_dialogue][self.dl_timer.tally]
          if self.character.speech_sound:
            if type(self.character.speech_sound) == list: self.character.speech_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.character.speech_sound[random.randrange(0, len(self.character.speech_sound))])
            self.character.speech_sfx.play()
      if self.add_letter_to_dialogue_timer.timer(self.main.fps / self.letter_delay[self.current_dialogue]): self.dl_timer.count(1, len(self.dialogue[self.current_dialogue]), 0)
      text = font.render(replace_letter(self.dialogue_text, "_", " "), True, "White")
      screen.blit(text, ((self.main.width / 2) - (text.get_width() / 2), self.main.height / 2))
    
    #pygame.draw.rect(screen, "Red", pygame.Rect((self.rect.right, self.rect.bottom), (self.rect.width, self.rect.height)), 1)
    #pygame.draw.rect(screen, "Blue", pygame.Rect((self.rect.left - self.rect.width, self.rect.bottom), (self.rect.width, self.rect.height)), 1)

  def behave(self): self.ai.decision_move()

class AI(Entity):
  def __init__(self, puppet):
    self.subject = puppet
    self.direction = self.subject.initial_direction
    if self.direction == "static": self.direction = ""
    #if "oscillate1" in self.subject.behaviors or "oscillate2" in self.subject.behaviors: self.direction = "right"
    self.range = puppet.range
    self.provoked = False
    self.on_ledge = False
  
  def decision_move(self): #Ooo
    if self.direction == "left": self.subject.flipped = True
    if self.direction == "right": self.subject.flipped = False
    if self.direction == "": self.subject.state = "idle"; self.subject.movement[0] = 0
    for player in self.subject.main.players: 
      if self.get_distance_to_player(player) < self.range:
        if self.subject.notice_sound and not self.provoked:
          if type(self.subject.notice_sound) == list: self.subject.character.notice_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.subject.character.notice_sound[random.randrange(0, len(self.subject.character.notice_sound))])
          self.subject.character.notice_sfx.play()
        self.provoked = True
    space_to_move = True

    if "walk" in self.subject.behaviors:
      if self.direction == "right": self.subject.movement[0] = self.subject.speed; self.subject.state = "walk"
      if self.direction == "left": self.subject.movement[0] = -self.subject.speed; self.subject.state = "walk"
      if self.direction == "up": self.subject.movement[1] = self.subject.speed; self.subject.state = "walk"
      if self.direction == "down": self.subject.movement[1] = -self.subject.speed; self.subject.state = "walk"
      if self.direction == "": self.subject.movement[0] = 0; self.subject.state = "idle"

    if "oscillate1" in self.subject.behaviors:
      if self.subject.collision["right"]: self.direction = "left"; self.subject.state = "turn"; space_to_move = False
      if self.subject.collision["left"]: self.direction = "right"; self.subject.state = "turn"; space_to_move = False
      if self.subject.character.mode == "topdown":
        if self.subject.collision["top"]: self.direction = "down"; self.subject.state = "turn"; space_to_move = False
        if self.subject.collision["bottom"]: self.direction = "up"; self.subject.state = "turn"; space_to_move = False
    
    tiles_checked = 0
    if "oscillate2" in self.subject.behaviors:
      if self.direction == "right":
        for layer in self.subject.main.rooms[self.subject.main.current_room].layers:
          for tile in [tile for tile in layer.tiles if tile.solid and tile.alive]:
            if tile.rect.colliderect(pygame.Rect((self.subject.rect.right + 1, self.subject.rect.bottom), (self.subject.rect.width, self.subject.rect.height))):
              tiles_checked += 1; self.on_ledge = False
        if not "chase" in self.subject.behaviors and tiles_checked == 0: self.direction = "left"; self.subject.state = "turn"; space_to_move = False
        elif "chase" in self.subject.behaviors and tiles_checked == 0: self.on_ledge = True; self.direction = ""; self.subject.movement[0] = 0

      if self.direction == "left":
        for layer in self.subject.main.rooms[self.subject.main.current_room].layers:
          for tile in [tile for tile in layer.tiles if tile.solid and tile.alive]:
            if tile.rect.colliderect(pygame.Rect((self.subject.rect.left - 1 - self.subject.rect.width, self.subject.rect.bottom), (self.subject.rect.width, self.subject.rect.height))):
              tiles_checked += 1; self.on_ledge = False
        if not "chase" in self.subject.behaviors and tiles_checked == 0: self.direction = "right"; self.subject.state = "turn"; space_to_move = False
        elif "chase" in self.subject.behaviors and tiles_checked == 0: self.on_ledge = True; self.direction = ""; self.subject.movement[0] = 0

    if "ledge_jump" in self.subject.behaviors:
      if self.direction == "right":
        tiles_checked = 0
        for tile in self.subject.main.rooms[self.subject.main.current_room].layers[0].tiles:
          if tile.solid and tile.rect.colliderect(pygame.Rect((self.subject.rect.right, self.subject.rect.bottom), (self.subject.rect.width, self.subject.rect.height))):
            if not tiles_checked: tiles_checked += 1
        if not tiles_checked: self.subject.jump()
      if self.direction == "left":
        tiles_checked = 0
        for tile in self.subject.main.rooms[self.subject.main.current_room].layers[0].tiles:
          if tile.solid and tile.rect.colliderect(pygame.Rect((self.subject.rect.left - self.subject.rect.width, self.subject.rect.bottom), (self.subject.rect.width, self.subject.rect.height))):
            if not tiles_checked: tiles_checked += 1
        if not tiles_checked: self.subject.jump()

    if "chase" in self.subject.behaviors:
      if self.provoked:
        for player in self.subject.main.players:
          distance = self.get_distance_to_player(player)
          if distance <= self.range and not self.on_ledge:
            if player.rect.x > self.subject.rect.x: self.direction = "right"; self.subject.movement[0] = self.subject.speed; self.subject.state = "walk"
            if player.rect.x < self.subject.rect.x: self.direction = "left"; self.subject.movement[0] = -self.subject.speed; self.subject.state = "walk"
            if self.subject.main.rooms[self.subject.main.current_room].mode == "Topdown":
              if player.rect.y > self.subject.rect.y: self.direction = "down"; self.subject.movement[1] = self.subject.speed; self.subject.state = "walk"
              if player.rect.y < self.subject.rect.y: self.direction = "up"; self.subject.movement[1] = -self.subject.speed; self.subject.state = "walk"
          elif self.on_ledge:
            self.direction = ""
            if not self.subject.flipped and player.rect.x < self.subject.rect.x: self.on_ledge = False
            if self.subject.flipped and player.rect.x > self.subject.rect.x: self.on_ledge = False

    if "hop" in self.subject.behaviors: #hops all the time non-stop
      self.subject.jump()

    if "pbtc" in self.subject.behaviors:
      spc = 0
      if space_to_move:
        for player in self.subject.main.players:
          if player.rect.x > self.subject.rect.x and player.flipped: spc += 1; self.direction = ""
          elif player.rect.x > self.subject.rect.x and not player.flipped and spc == 0: self.direction = "right"
          if player.rect.x < self.subject.rect.x and not player.flipped: spc += 1; self.direction = ""
          elif player.rect.x < self.subject.rect.x and player.flipped and spc == 0: self.direction = "left"
          if self.subject.main.rooms[self.subject.main.current_room].mode == "Topdown":
            if player.rect.y > self.subject.rect.y: spc += 1; self.direction = ""
            elif player.rect.y > self.subject.rect.y and spc == 0: self.direction = "down"
            if player.rect.y < self.subject.rect.y: spc += 1; self.direction = ""
            elif player.rect.y < self.subject.rect.y and spc == 0: self.direction = "up"
      else: self.direction = ""; self.subject.state = "idle"; self.subject.movement[0] = 0
      if spc == len(self.subject.main.players): self.direction = ""

    if "controlled" in self.subject.behaviors:
      if space_to_move:
        for player in self.subject.main.players:
          if player.rect.x > self.subject.rect.x and not player.flipped: self.direction = "right"
          if player.rect.x < self.subject.rect.x and player.flipped: self.direction = "left"
          if self.subject.main.rooms[self.subject.main.current_room].mode == "Topdown":
            if player.rect.y > self.subject.rect.y: self.direction = "down"
            if player.rect.y < self.subject.rect.y: self.direction = "up"
      else: self.direction = ""; self.subject.state = "idle"; self.subject.movement[0] = 0

    if self.subject.main.rooms[self.subject.main.current_room].mode == "Topdown": self.subjrect.dir = self.direction
      
    
  def get_distance_to_player(self, player):
    return math.sqrt(abs(((round(player.rect.x) - round(self.subject.rect.x)) ^ 2) + ((round(player.rect.y) - round(self.subject.rect.y)) ^ 2)))
  


class Action:
  def __init__(self, flip_rate, does_loop, frames, character):
    #self.frame = 0
    self.rate = flip_rate
    self.loop = does_loop
    self.frames = frames
    #self.time_accumulator = 0
    #self.finished = False
    self.character = character
    self.frants = []
    self.condition_stat = ""
    self.button_activator = [""]
    self.prioritize_action = False
    self.allow_travel = True
    self.allow_jump = True
    self.allow_flip = True
    self.apply_gravity = True
    self.aerial = False
    self.terrestial = False
    self.subaqueous = False
    self.cancel_on_ground = False
    self.cancel_on_walk = False
    self.cancel_on_jump = False
    self.cancel_on_hit = True
    self.directional_relative = True
    self.continue_until_cancel = False
    self.trigger_mode = "Press"
    self.combo = "none"
    self.cutscene_trigger = ""
    for frame in range(len(self.frames)): self.frants.append(Frant(frame + 1, self, self.frames[frame].get_width(), self.frames[frame].get_height()))

  # def flip(self, actor, delta_time:float=1.0)->pygame.Surface:
  #   self.time_accumulator += delta_time
  #   self.finished = False

  #   if self.time_accumulator >= 1.0 / self.rate if self.rate != 0 else 1.0:
  #     self.time_accumulator = 0
  #     if self.frame < len(self.frames) - 1: self.frame += 1; self.finished = True
  #     elif self.loop: self.frame = 0

  #   if self.time_accumulator == 0:
  #     if not self.allow_travel: actor.movement[0] = 0
  #     if (not actor.flipped) or not self.directional_relative: actor.movement[0] += self.frants[self.frame - 1].move_x
  #     elif actor.flipped: actor.movement[0] -= self.frants[self.frame - 1].move_x
  #     if self.apply_gravity: actor.movement[1] += self.frants[self.frame - 1].move_y
  #     else: actor.movement[1] = self.frants[self.frame - 1].move_y
  #     actor.x_vel += self.frants[self.frame - 1].gain_x
  #     if self.frants[self.frame - 1].gain_y < 0 and not actor.collision["top"]: actor.rect.y -= 1
  #     actor.y_vel += self.frants[self.frame - 1].gain_y
  #     if self.frants[self.frame - 1].sound:
  #       if type(self.frants[self.frame - 1].sound) == list: self.frants[self.frame - 1].sfx = pygame.mixer.Sound(actor.main.active_directory + "Sounds/sfx/" + self.frants[self.frame - 1].sound[random.randrange(0, len(self.frants[self.frame - 1].sound))])
  #       self.frants[self.frame - 1].sfx.play()
  #     if self.frants[self.frame - 1].loops: self.frants[self.frame - 1].loops -= 1; self.frame = self.frants[self.frame - 1].loop_to - 1
  #     if self.frants[self.frame - 1].loop_to != -1 and (self.frants[self.frame - 1].loops != self.frants[self.frame - 1].loops_spawn or not self.frants[self.frame - 1].loops): self.frants[self.frame - 1].loops = self.frants[self.frame - 1].loops_spawn
      
  #     for proj in self.frants[self.frame - 1].projectiles:
  #       try: actor.projectiles.append(Projectile(actor, actor.main.projectiles[proj - 1]))
  #       except IndexError: pass

  #   try: rtn = self.frames[self.frame]
  #   except: rtn = self.frames[0]
  #   return rtn
  
  # def reset(self): self.frame = 0


class Frant:
  def __init__(self, frame, action, width=32, height=32):
    self.frame = frame
    self.action = action
    self.move_x = 0
    self.move_y = 0
    self.gain_x = 0
    self.gain_y = 0
    self.damage = 0
    self.knockback_x = 0.0
    self.knockback_y = 0.0
    self.self_destruct = 0
    self.projectiles = []
    self.loop_to = -1
    self.loops = 0
    self.loops_spawn = 0
    self.combo_unit = 0
    self.sound = ""
    self.sfx = None
    self.rect = pygame.Rect((0, 0), (width, height))
    self.attack_rect = pygame.Rect((0, 0), (0, 0))
    self.x_bearing = 0
    self.y_bearing = 0


class Character:
  def __init__(self, character="", main=None):
    self.character = character
    self.main = main
    self.speed = 3
    self.jump_force = -5
    self.accelerated_travel = False
    self.bump_cancel_momentum = True
    self.jumps = 1
    self.wall_slider = False
    self.change_trajectory_midair = True
    self.midair_jump_dash = False
    self.hp = 0
    self.stat = ""
    self.value = 0
    self.behaviors = []
    self.range = 0
    self.drops = []
    self.actions = {}
    self.states = []
    self.state_controls = {"A Button": [], "B Button": [], "X Button": [], "Y Button": [], "D-Pad Right": [], "D-Pad Left": [], "D-Pad Up": [], "D-Pad Down": [], "R Shoulder": [], "L Shoulder": [], "Z Button": [], "Select": [], "Start": []}
    self.away_delay = 300
    self.wake_up_delay = 600
    self.defeat_anim = "Stay"
    # try: self.images_dict, self.states = self.load_images(main.active_directory + "Assets/characters/" + self.character)
    # except: self.image = None

    if os.listdir(main.active_directory + "Assets/characters/" + character) == ["down", "left", "right", "up"]: self.mode = "topdown"
    else: self.mode = "platformer"
    try:
      if self.mode == "platformer": self.image = pygame.image.load(main.active_directory + f"Assets/characters/{character}/idle/1.png").convert_alpha()
      elif self.mode == "topdown": self.image = pygame.image.load(main.active_directory + f"Assets/characters/{character}/down/idle/1.png").convert_alpha()
    except: self.image = None

    if self.mode == "platformer": self.images_dict, self.states = self.load_images(main.active_directory + "Assets/characters/" + character)
    elif self.mode == "topdown":
      self.images_dict = {"down": {}, "left": {}, "right": {}, "up": {}}
      for dir in ["down", "left", "right", "up"]: self.images_dict[dir], self.states = self.load_images(main.active_directory + "Assets/characters/" + character + "/" + dir)
    
    self.state_anims = {"idle": (50, True), "walk": (200, True), "jump": (120, False)}
    self.actions = {}
    if self.image != None:
      if self.mode == "platformer":
        for state in self.states:
          try: self.actions[state.lower()] = Action(self.state_anims[state.lower()][0], self.state_anims[state.lower()][1], self.images_dict[state.lower()], self)
          except:
            try: self.actions[state.lower()] = Action(100, True, self.images_dict[state.lower()], self)
            except: pass
      elif self.mode == "topdown":
        self.actions = {"down": {}, "left": {}, "right": {}, "up": {}}
        for dir in ["down", "left", "right", "up"]:
          for state in self.states:
            try: self.actions[dir][state.lower()] = Action(self.state_anims[state.lower()][0], self.state_anims[state.lower()][1], self.images_dict[state.lower()], self)
            except:
              try: self.actions[dir][state.lower()] = Action(100, True, self.images_dict[state.lower()], self)
              except: pass
    else: self.animation = None

    self.jump_sound = ""
    self.land_sound = ""
    self.beat_sound = ""
    self.hurt_sound = ""
    self.defeat_sound = ""
    self.trap_sound = ""
    self.notice_sound = ""
    self.speech_sound = ""
    if self.jump_sound: self.jump_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + self.jump_sound)
    if self.land_sound: self.land_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + self.land_sound)
    if self.beat_sound: self.beat_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + self.beat_sound)
    if self.hurt_sound: self.hurt_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + self.hurt_sound)
    if self.defeat_sound: self.defeat_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + self.defeat_sound)
    if self.trap_sound: self.trap_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.trap_sound)
    if self.notice_sound: self.notice_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.notice_sound)
    if self.speech_sound: self.speech_sfx = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + self.speech_sound)
    # for stat in main.game_stats:
    #   if main.game_stats[stat] == int: self.stats[stat] = 0
    #   if main.game_stats[stat] == bool: self.stats[stat] = False
    #   if main.game_stats[stat] == str: self.stats[stat] = ""
    #   if main.game_stats[stat] == float: self.stats[stat] = 0.0
    

  def load_images(self, path):
    images_dict = {}
    states = []
    states = os.listdir(path)#list of all the states
    in_images = []
    
    for state in states:
      try:
        order = [int(file[0 : len(file) - 4]) for file in os.listdir(path + "/" + state)]
        order.sort()
        images = os.listdir(path + "/" + state)#the list of images
        path.split("/")[-1]
        in_images = []
        #for img in images:
        #  load = pygame.image.load(path + "/" + state + "/" + img)
        #  in_images.append(load)
        in_images = [pygame.image.load(path + "/" + state + "/" + str(file) + ".png").convert_alpha() for file in order]
        images_dict[state] = in_images
      except: pass
    return images_dict, states




class ProjectileType:
  def __init__(self, name, main):
    self.main = main
    self.name = name
    self.images = []
    if os.path.isdir(f"Assets/projectiles/" + name):
      self.is_animating = True
      for image in sorted(os.listdir(f"Assets/projectiles/" + name), key=extract_number): self.images.append(pygame.image.load(f"Assets/projectiles/" + name + "/" + image).convert_alpha())
      self.image = self.images[0]
    else: self.is_animating = False; self.image = pygame.image.load(f"Assets/projectiles/" + name).convert_alpha()
    self.speed = [0.0, 0.0]
    self.lifespan = 1
    self.anim_speed = 1
    self.set_pos_min_range = [0, 0]
    self.set_pos_max_range = [0, 0]
    self.deal_again = False
    self.pierce = False
    self.stoppable = True
    self.returnable = False
    self.oscil_speed = 0
    self.frequency = 0
    self.vibrate = 0
    self.oscil_ease = True
    self.weight = [0, 0]
    self.stop_at_collision = False
    self.die_at_collision = False
    self.pos_mode = "Player Relative" #Player Relative, Camera Relative, Raw Position
    self.apply_weight_after = 0
    self.stop_motion_after = [0, 0]
    self.stop_motion_for = [0, 0]
    self.guided = False
    self.beam = False
    self.directional_relative = True
    self.bounce = True
    self.around_platform = False

  def __str__(self): return self.name

class Projectile:
  def __init__(self, user, proj):
    self.user = user
    self.proj = proj
    self.flipped = user.flipped
    if self.flipped: x = user.rect.x - random.randrange(proj.set_pos_min_range[0], proj.set_pos_max_range[0] + 1)
    else: x = user.rect.right + random.randrange(proj.set_pos_min_range[0], proj.set_pos_max_range[0] + 1)
    if proj.pos_mode == "Player Relative": self.rect = pygame.FRect((x, user.rect.y + random.randrange(proj.set_pos_min_range[1], proj.set_pos_max_range[1] + 1)), (proj.image.get_width(), proj.image.get_height()))
    if proj.pos_mode == "Camera Relative": self.rect = pygame.FRect((user.main.camera.scroll[0] + random.randrange(proj.set_pos_min_range[0], proj.set_pos_max_range[0] + 1), user.main.camera.scroll[1] + random.randrange(proj.set_pos_min_range[1], proj.set_pos_max_range[1] + 1)), (proj.image.get_width(), proj.image.get_height()))
    if proj.pos_mode == "Raw Position": self.rect = pygame.FRect((random.randrange(proj.set_pos_min_range[0], proj.set_pos_max_range[0] + 1), random.randrange(proj.set_pos_min_range[1], proj.set_pos_max_range[1] + 1)), (proj.image.get_width(), proj.image.get_height()))
    self.x_speed = proj.speed[0]
    self.y_speed = proj.speed[1]
    self.timer = Timer()
    self.frame_timer = Timer()
    self.weight_timer = Timer()
    self.image = proj.image
    if proj.is_animating: self.images = self.proj.images
    if proj.is_animating and self.flipped:
      for image in self.images: image = pygame.transform.flip(image, True, False)
    if self.flipped: self.image = pygame.transform.flip(self.image, True, False)
    self.movement = [0, 0]
    if not self.flipped: self.movement[0] = self.proj.speed[0]
    elif self.proj.directional_relative: self.movement[0] = -self.proj.speed[0]
    else: self.movement[0] += self.proj.speed[0]
    self.movement[1] = self.proj.speed[1]
    self.alive = True
    self.damage = user.character.actions[user.state].frants[user.frame].damage
    self.knockback_x = user.character.actions[user.state].frants[user.frame].knockback_x
    self.knockback_y = user.character.actions[user.state].frants[user.frame].knockback_y
    self.x_vel = 0
    self.y_vel = 0
    self.oscil_x = 0
    self.oscil_y = 0
    self.oscil_reverse = False

  def update(self, screen, dt=1):
    if self.proj.is_animating: self.image = self.images[self.frame_timer.keep_count(self.proj.anim_speed * dt, len(self.images), 0)]
    screen.blit(self.image, ((self.rect.x - self.proj.main.camera.scroll[0]) + self.oscil_x, (self.rect.y - self.proj.main.camera.scroll[1]) + self.oscil_y))
    if self.proj.lifespan != 0:
      if self.timer.timer((self.proj.lifespan * FPS) * dt): self.alive = False

    self.rect.x += float(self.movement[0] / 10) * dt
    self.rect.y += float(self.movement[1] / 10) * dt

    if self.proj.stop_at_collision:
      for layer in self.user.main.rooms[self.user.main.current_room].layers:
        for tile in [tile for tile in layer.tiles if self.rect.colliderect(tile.rect)]:
          if self.movement[0] > 0: self.rect.right = tile.rect.left
          elif self.movement[0] < 0: self.rect.left = tile.rect.right
          
        for tile in [tile for tile in layer.tiles if self.rect.colliderect(tile.rect)]:
          if self.movement[1] > 0: self.rect.bottom = tile.rect.top
          elif self.movement[1] < 0: self.rect.top = tile.rect.bottom

    if self.proj.die_at_collision:
      for layer in self.user.main.rooms[self.user.main.current_room].layers:
        for tile in layer.tiles:
          if tile.solid and self.rect.colliderect(tile.rect): self.alive = False

    #Projectile weight
    if self.proj.apply_weight_after < (self.weight_timer.nonstopcount(1, 1) * dt) or self.proj.apply_weight_after == 0:
      if (not self.proj.directional_relative) or (not self.flipped):
        self.rect.x += self.x_vel * dt
        self.x_vel += (self.proj.weight[0] / 50) * dt
      else:
        self.rect.x -= self.x_vel * dt
        self.x_vel += (self.proj.weight[0] / 50) * dt

      self.rect.y += self.y_vel * dt
      self.y_vel += (self.proj.weight[1] / 50) * dt

    #Projectile wave/oscillation
    if self.proj.oscil_ease:
      if abs(self.proj.speed[0]) >= abs(self.proj.speed[1]):
        # Moving mostly horizontally → wave on Y axis
        self.oscil_y = math.sin(self.proj.oscil_speed * self.timer.time) * self.proj.frequency
        if self.oscil_reverse: self.oscil_y *= -1
        self.oscil_x = 0
      elif abs(self.proj.speed[0]) < abs(self.proj.speed[1]):
        # Moving mostly vertically → wave on X axis
        self.oscil_x = math.sin(self.proj.oscil_speed * self.timer.time) * self.proj.frequency
        if self.oscil_reverse: self.oscil_x *= -1
        self.oscil_y = 0
    else:
      wave = (self.timer.time * self.proj.frequency) % 2
      wave = wave if wave < 1 else 2 - wave
      offset = (wave - 0.5) * 2 * self.proj.oscil_speed

      if abs(self.proj.speed[0]) >= abs(self.proj.speed[1]):
        self.oscil_y = -offset if self.oscil_reverse else offset
        self.oscil_x = 0
      elif abs(self.proj.speed[0]) < abs(self.proj.speed[1]):
        self.oscil_x = -offset if self.oscil_reverse else offset
        self.oscil_y = 0


    if self.proj.vibrate:
      self.oscil_x = random.randrange(-self.proj.vibrate, self.proj.vibrate)
      self.oscil_y = random.randrange(-self.proj.vibrate, self.proj.vibrate)



#class Animation():
#  def __init__(self, animation_frames, action, frame):
#    self.animation_frames = animation_frames
#    self.action = action
#    self.frame = frame
#    self.animation_database = {}
#        
#  def load_animation(self, path, frame_duration):
#    animation_name = path.split('/')[-1]
#    animation_frame_data = []
#    for n, duration in enumerate(frame_duration):
#      animation_frame_id = f'{animation_name}_{str(n)}'
#      img_loc = f'{path}/{animation_frame_id}.png'
#      animation_image = pygame.image.load(img_loc).convert()
#      animation_image.set_colorkey((255,255,255))
#      self.animation_frames[animation_frame_id] = animation_image.copy()
#      animation_frame_data.extend(animation_frame_id for _ in range(duration))
#    return animation_frame_data
#
#  def change_action(self, action_var, frame, new_value):
#    if action_var != new_value: action_var = new_value; frame = 0
#    return action_var, frame
#
#  def handle_image(self, dt):
#    self.frame += 1 * dt
#    if self.frame >= len(self.animation_database[self.action]): self.frame = 0 * dt
#        
#    image_id = self.animation_database[self.action][int(self.frame)]
#    image = self.animation_frames[image_id]
#    
#    return image
#