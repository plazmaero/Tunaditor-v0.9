import pygame, json
from Scripts.settings import get_key_from_value
from Scripts.controller import Controller
from Scripts.room import Room, Tile, Door, Background, Collectible_Type, Collectible, Entity_Type, Zone, Text, Layer, Camera, Cutscene
from Scripts.actor import *
from Scripts.timers import Timer

save = {}

def get_empty_save(main, include_start_room=False):
  if include_start_room: return {"Title": main.game_name, "Publisher": main.publisher, "Display": {"Width": main.width, "Height": main.height, "FPS": main.fps, "DT": main.use_dt, "Tiles Size": main.tiles_size, "Snap Tile Image": main.snap_tile_image, "Snap Tile Rect": main.snap_tile_rect}, "Stats": {"data_types": {}, "starting_points": main.game_stats_initpoint, "effects": main.game_stats_effect, "ranges": main.game_stats_range}, "Rooms": [{"Name": "Room1", "Layers": [], "Doors": [], "Backgrounds": [], "Zones": [], "Cutscenes": [], "Track": "", "Track1": "", "Borders": {"right": 0, "top": 0, "left": 0, "bottom": 0}, "Threshold": {"right": 200, "top": 200, "left": 200, "bottom": 200}, "SUI": [], "HUI": [], "UIM": [], "Scroll_Mode": "No Scrolling", "Flags": [], "Gravity": 1.0, "Shader": "", "Menu": {"speed": 1.0, "trigger": "", "flags": ["toggle"], "items": []}}], "Players": [], "Tile_Types": {}, "Collectible_Types": {}, "Entity_Types": {}, "Projectiles": [], "Characters": {}, "UI": {}}
  else: return {"Title": main.game_name, "Publisher": main.publisher, "Display": {"Width": main.width, "Height": main.height, "FPS": main.fps, "DT": main.use_dt, "Tiles Size": main.tiles_size, "Snap Tile Image": main.snap_tile_image, "Snap Tile Rect": main.snap_tile_rect}, "Stats": {"data_types": {}, "starting_points": main.game_stats_initpoint, "effects": main.game_stats_effect, "ranges": main.game_stats_range}, "Rooms": [], "Players": [], "Tile_Types": {}, "Collectible_Types": {}, "Entity_Types": {}, "Projectiles": [], "Characters": {}, "UI": {}} #"Input Press or Hold": main.input_hold, 

def save_game(name, main):
  save = get_empty_save(main)
  
  # tile_tex_list = os.listdir(main.active_directory + "Assets/tiles/")
  # tile_tex = {}
  # for index, tex in enumerate(tile_tex_list): tile_tex[index] = {"image": tex, "rect": pygame.Rect((), ()), "solid": True, "slip": False, "soft": False}
  
  rooms = []
  for room in main.rooms:
    layers = []#lemme make a file
    for layer in room.layers: #did you import the module or * if you import the module you're in of course it's gonna circle
      tiles = []
      collectibles = []
      actors = []
      texts = []

      for tile in layer.tiles:
        flags = []
        # if tile.solid: flags.append("solid")
        # if tile.slippery: flags.append("slip")
        # if tile.flat: flags.append("flat")
        if tile.destroy_if_stood_on: flags.append("diso")
        if tile.destroy_if_head_bump: flags.append("dihb")
        if tile.instigator: flags.append("inst")
        if not tile.spawn_as_visible: flags.append("hidden")
        destroy_anim = tile.destroy_anim
        if destroy_anim == "Disappear": destroy_anim = "-"
        if tile.only_breakable_by_chains: flags.append("obc")
        if "s" in tile.deviating_modes: flags.append("s")
        if "f" in tile.deviating_modes: flags.append("f")
        if "sl" in tile.deviating_modes: flags.append("sl")
        if tile.zones_can_move: flags.append("zm")
        if tile.zones_can_rotate: flags.append("zr")

        #tiles.append({"n": next(key for key, value in main.tile_types.items() if value.get("image") == tile.type), "x": tile.rect.x, "y": tile.rect.y, "w": tile.rect.width, "h": tile.rect.height, "s": tile.speed, "as": tile.anim_speed, "c": tile.chain_speed,
        #              "hp": tile.hp, "ss": tile.step_sound, "ds": tile.destroy_sound, "da": destroy_anim, "iw": tile.image.get_width(), "ih": tile.image.get_height(), "fl": flags})
        tiles.append({"n": next(key for key, value in main.tile_types.items() if value.get("img") == tile.type), "x": tile.rect.x, "y": tile.rect.y, "s": tile.speed, "iw": tile.image.get_width(), "ih": tile.image.get_height(), "c": tile.chain_speed, "fl": flags})
      
      for collectible in layer.collectibles:
        flags = []
        if collectible.price_exchange: flags.append("pe")
        if collectible.price_decrement: flags.append("pd")
        if collectible.zones_can_move: flags.append("zm")
        if collectible.zones_can_rotate: flags.append("zr")
        if not collectible.solid: flags.append("non-solid")
        if not collectible.spawn_as_visible: flags.append("hidden")

        # collectibles.append({"n": collectible.name, "x": collectible.rect.x, "y": collectible.rect.y, "w": collectible.rect.width, "h": collectible.rect.height,
        #                     "so": collectible.sound, "fr": collectible.frames, "v": collectible.value, "s": collectible.speed,
        #                     "ps": collectible.price_stat, "pv": collectible.price_value, "ptp": collectible.price_text_position, "ptm": collectible.price_text_mode,
        #                     "dds": collectible.debt_drop_sound, "font": collectible.font_str, "fs": collectible.font_size, "cs": collectible.trigger_cutscene, "fl": flags})
        
        collectibles.append({"t": collectible.index_type, "x": collectible.rect.x, "y": collectible.rect.y, "cs": collectible.trigger_cutscene, "s": collectible.spawn_speed, "fl": flags})
      
      for actor in layer.actors:
        drops = []
        actions = []
        for drop in main.collectible_types:
          for entitys_drop in actor.drops:
            if entitys_drop.name == drop.name: drops.append(drop.name)
        flags = []
        if not actor.spawn_as_visible: flags.append("hidden")
        
        # actors.append({"type": actor.name,
        #               "x": actor.rect.x, "y": actor.rect.y, "width": actor.rect.width, "height": actor.rect.height,
        #               "speed": actor.speed, "leap": actor.jump_force, "hp": actor.hp, "range": actor.range, "in_dir": actor.initial_direction,
        #               "stat": actor.stat, "value": actor.value, "behaviors": actor.behaviors, "drops": drops,
        #               "defeat_anim": actor.defeat_anim, "jump_s": actor.jump_sound, "land_s": actor.land_sound,
        #               "defeat_s": actor.defeat_sound, "trap_s": actor.trap_sound, "notice_s": actor.notice_sound,
        #               "speech_s": actor.speech_sound, "dialogue": actor.dialogue, "u_delay": actor.letter_delay,
        #               "font": actor.font_str, "fsize": actor.font_size, "fcolor": actor.font_color, "flags": flags})
        actors.append({"type": actor.type_index,
                      "x": actor.rect.x, "y": actor.rect.y, "in_dir": actor.initial_direction, "dialogue": actor.dialogue, "u_delay": actor.letter_delay,
                      "font": actor.font_str, "fsize": actor.font_size, "fcolor": actor.font_color, "flags": flags})
        
      for text in layer.texts:
        flags = []
        if text.bold: flags.append("bold")
        if text.italic: flags.append("italic")
        if text.underline: flags.append("ul")
        if text.strikethrough: flags.append("st")
        if text.anti_aliasing: flags.append("antialias")
        if text.flip[0]: flags.append("fx")
        if text.flip[1]: flags.append("fy")
        if text.take_variable: flags.append("v")
        if text.player_or_team: flags.append("team")
        if not text.spawn_as_visible: flags.append("hidden")
        
        texts.append({"x": text.rect.x, "y": text.rect.y, "text": text.text, "font": text.font_str, "size": text.size, "color": text.color, "ol_color": text.outline_color, "bg_color": text.bg_color, "ol_thick": text.outline_thickness,
              "rotate": text.rotation, "scale": text.scale, "alpha": text.opacity, "layer": text.layer, "flags": flags, "align": text.align, "cap": text.capitalization_mode, "margin": text.margin, "dir": text.direction,
              "cs": text.character_string, "ti": text.take_index, "behave": text.behaviors})
      
      layers.append({"Label": layer.name, "Tiles": tiles, "Collectibles": collectibles, "Actors": actors, "Texts": texts, "Distance": layer.distance, "Shade": layer.shade})

    doors = []
    for door in room.doors:
      flags = []
      if not door.spawn_as_visible: flags.append("hidden")
      if not door.transition_override_ui: flags.append("or_ui")
      if not door.transition_flag_1: flags.append("tf1")
      if not door.transition_flag_2: flags.append("tf2")
      if not door.transition_pre_immobilize_player: flags.append("ipr")
      if not door.transition_post_immobilize_player: flags.append("ipo")
      if not door.requires_input: flags.append("ri")
      if not door.passable: flags.append("pass")
      if not door.transition_play_door_and_player_animation: flags.append("anim")
      doors.append({"name": door.type, "x": door.rect.x, "y": door.rect.y, "width": door.rect.width, "height": door.rect.height, "led_room": door.led_room, "led_pos": door.led_pos, "speed": door.speed,
                    "i_width": door.image.get_width(), "i_height": door.image.get_height(), "transition": door.transition, "t_spr": door.transition_speed_pre, "t_spo": door.transition_speed_post, "t_color": door.transition_color, "t_shape": door.transition_shape, "flags": flags})
    
    bgs = []
    for bg in room.backgrounds:
      flags = []
      if not bg.spawn_as_visible: flags.append("hidden")
      if bg.foreground: flags.append("fg")
      if bg.take_variable: flags.append("v")
      if bg.player_or_team: flags.append("team")
      if not bg.spawn_as_visible: flags.append("hidden")
      
      bgs.append({"image_path": bg.image_file_without_dir, "x": bg.rect.x, "y": bg.rect.y, "width": bg.rect.width, "height": bg.rect.height,
                  "repeat_x": bg.repeat_x, "repeat_y": bg.repeat_y, "speed": bg.speed, "distance": bg.distance, "marges": bg.marges,
                  "x_scroll": bg.x_scroll, "y_scroll": bg.y_scroll, "hm": bg.hm_for_move, "vm": bg.vm_for_move, "as": bg.anim_speed,
                  "cs": bg.character_string, "ti": bg.take_index, "flags": flags})

    zones = []
    for zone in room.zones:
      flags = []
      if zone.multi_active: flags.append("multi")
      if zone.entity_active: flags.append("entity")
      if zone.void: flags.append("void")
      if zone.ease_motion: flags.append("ease")
      zones.append({"x": zone.rect.x, "y": zone.rect.y, "width": zone.rect.width, "height": zone.rect.height, "g": round(zone.gravity, 1), "event": zone.trigger_event, "cutscene": zone.trigger_cutscene,
                    "enter_s": zone.enter_sound, "exit_s": zone.exit_sound, "dim": zone.track_volume, "color": zone.color, "ts": zone.tile_speed, "tr": zone.tile_rotation, "flags": flags})
      
    css = []
    for cs in room.cutscenes:
      animations = []
      for anim in cs.animations:
        if anim["Object"] != "Main" and type(anim["Object"]) != list: x, y = anim["Object"].rect.x, anim["Object"].rect.y; cs_object = (anim["Object"].name if type(anim["Object"]).__name__ != "Background" else anim["Object"].image_file_without_dir, x, y, type(anim["Object"]).__name__)
        else: cs_object = "Main"
        animations.append({"Object": cs_object, "Frame": anim["Frame"], "Rect": anim["Rect"], "SOCR": anim["SOCR"], "Hidden": anim["Hidden"], "Speed": anim["Speed"], "X Speed": anim["X Speed"], "Y Speed": anim["Y Speed"], "Rotate": anim["Rotate"], "X Scale": anim["X Scale"], "Y Scale": anim["Y Scale"], "Action": anim["Action"], "Dir": anim["Dir"], "SFX": anim["SFX"], "Track": anim["Track"], "Show UI": anim["Show UI"], "Hide UI": anim["Hide UI"], "B1": anim["B1"], "B2": anim["B2"], "I1": anim["I1"], "I2": anim["I2"], "I3": anim["I3"], "I4": anim["I4"]})

      css.append({"Name": cs.name, "Animations": animations, "Events": cs.conditions, "Stat": cs.stat_required, "Gate1": cs.condition_gate, "Gate2": cs.condition_stat_gate})

    #iterating through every item and removing surfaces and other non-json serializable things
    menu = room.menu.copy()
    menu.pop("down_sfx", None)
    menu.pop("up_sfx", None)

    new_items = []
    for button in room.menu["items"]:
      new_button = button.copy()
      for key in ("Text_Surface", "Text_SurfaceS", "Image_Surface", "Image_SurfaceS", "Timer", "Timer2", "SFX"): new_button.pop(key, None)
      new_items.append(new_button)
    menu["items"] = new_items
    
    room_flags = []
    if room.hm: room_flags.append("hm")
    if room.vm: room_flags.append("vm")
    if not room.show_player: room_flags.append("hide_player")
    rooms.append({"Name": room.name, "Layers": layers[::-1], "Doors": doors, "Backgrounds": bgs, "Zones": zones, "Cutscenes": css, "Track": room.track, "Track1": room.first_track, "Borders": room.borders, "Threshold": room.move_threshold, "SUI": room.show_ui, "HUI": room.hide_ui, "UIM": room.ui_modes, "Scroll_Mode": room.scroll_mode, "Flags": room_flags, "Gravity": room.gravity, "Shader": room.shader, "Menu": menu})
    
  
  save["Rooms"] = rooms
  
  players = []
  for player in main.players:
    # actions = []
    flags = []
    if not player.spawn_as_visible: flags.append("hidden")
    if player.accelerated_travel: flags.append("at")
    if player.bump_cancel_momentum: flags.append("bcm")
    if player.hide_if_out: flags.append("hio")
    if player.in_spawn: flags.append("in")
    # for state in player.states:
    #   if state in player.actions:
    #     frants = []
    #     that_anim = player.actions[state]
    #     rate, loop = that_anim.rate, that_anim.loop
    #     condition_stat = that_anim.condition_stat
    #     prioritize_action = that_anim.prioritize_action
    #     allow_travel, allow_jump = that_anim.allow_travel, that_anim.allow_jump
    #     allow_flip, gravity, = that_anim.allow_flip, that_anim.apply_gravity
    #     aer, ter, sub = that_anim.aerial, that_anim.terrestial, that_anim.subaqueous
    #     cog, cow, coj, coh = that_anim.cancel_on_ground, that_anim.cancel_on_walk, that_anim.cancel_on_jump, that_anim.cancel_on_hit
    #     dirrel, guc = that_anim.directional_relative, that_anim.continue_until_cancel
    #     tm, combo = that_anim.trigger_mode, that_anim.combo
    #     for frant in player.actions[state].frants:
    #       frants.append({"frame": frant.frame, "xm": frant.move_x, "ym": frant.move_y, "xg": frant.gain_x, "yg": frant.gain_y, "damage": frant.damage, "xkb": frant.knockback_x, "ykb": frant.knockback_y,
    #                     "sd": frant.self_destruct, "lt": frant.loop_to, "l": frant.loops_spawn, "proj": frant.projectiles, "sound": frant.sound, "r": ((frant.rect.x, frant.rect.y), (frant.rect.width, frant.rect.height)), "ar": ((frant.attack_rect.x, frant.attack_rect.y), (frant.attack_rect.width, frant.attack_rect.height))})
    #     actions.append({"Action": state, "Rate": rate, "Loop": loop, "CS": condition_stat, "Prioritize": prioritize_action, "Allow Travel": allow_travel, "Allow Jump": allow_jump, "Allow Flip": allow_flip,
    #                     "Gravity": gravity, "Aer": aer, "Ter": ter, "Sub": sub, "C Ground": cog, "C Walk": cow, "C Jump": coj, "C Hit": coh, "DR": dirrel, "GUC": guc, "TM": tm, "Combo": combo, "Frants": frants})
    # players.append({"x": player.spawn_location[0], "y": player.spawn_location[1], "width": player.rect.width, "height": player.rect.height,
    #                 "speed": player.speed, "leap": player.jump_force, "character": player.character, "jump_s": player.jump_sound, "land_s": player.land_sound, 
    #                 "defeat_s": player.defeat_sound, "beat_s": player.beat_sound, "hurt_s": player.hurt_sound, "Actions": actions, "state_controls": player.state_controls,
    #                 "accelerated_travel": player.accelerated_travel, "bump_cancel_momentum": player.bump_cancel_momentum, "index": player.player_index, "flags": flags})
    players.append({"x": player.spawn_location[0], "y": player.spawn_location[1], "character": player.character.character, "index": player.player_index, "team": player.team, "flags": flags})

  # coin_types = []
  # for coin_type in main.collectible_types:
  #   coin_types.append({"name": coin_type.name, "stat": coin_type.stat, "value": coin_type.value, "sound": coin_type.sound})
  # save["Collectible_Types"] = coin_types

  save["Tile_Types"] = main.tile_types

  save["Entity_Types"] = main.entity_types

  save["Collectible_Types"] = main.collectible_types

  save["Players"] = players
  
  projectiles = []
  for proj in main.projectiles:
    flags = []
    if proj.deal_again: flags.append("deal")
    if proj.pierce: flags.append("pierce")
    if proj.stoppable: flags.append("stop")
    if proj.returnable: flags.append("turn")
    if proj.oscil_ease: flags.append("oe")
    if proj.stop_at_collision: flags.append("stop_ac")
    if proj.die_at_collision: flags.append("die_ac")
    if proj.guided: flags.append("guide")
    if proj.beam: flags.append("beam")
    if proj.directional_relative: flags.append("dr")
    if proj.bounce: flags.append("bounce")
    if proj.around_platform: flags.append("orbit")
    projectile = {"n": proj.name, "s": proj.speed, "l": proj.lifespan, "as": proj.anim_speed, "minr": proj.set_pos_min_range, "maxr": proj.set_pos_max_range, "os": proj.oscil_speed, "f": proj.frequency, "v": proj.vibrate,
                  "w": proj.weight, "awa": proj.apply_weight_after, "sma": proj.stop_motion_after, "smf": proj.stop_motion_for, "pm": proj.pos_mode, "flags": flags}
    projectiles.append(projectile)
    
  save["Projectiles"] = projectiles
  
  for stat in main.game_stats: save["Stats"]["data_types"][stat] = {"<class 'int'>": "int", "<class 'bool'>": "bool", "<class 'str'>": "str", "<class 'float'>": "float"}[str(main.game_stats[stat])]
  
  ui_instances = main.ui.instances.copy()
  try:
    for ui in ui_instances:
      #if "Hidden" in ui_instances[ui]: ui_instances[ui].remove("Hidden")
      try: del ui_instances[ui]["Hidden"]
      except: pass
      for mode in ui_instances[ui]["Modes"]:
        #ui_instances[ui][mode].pop("Font"); ui_instances[ui][mode].pop("Surface"); ui_instances[ui][mode][key].pop("Surface 2"); ui_instances[ui][mode][key].pop("Text Surface"); ui_instances[ui][mode][key].pop("Timer")
        #for key in ui_instances[ui][mode]:
        try: del ui_instances[ui][mode]["Font"]
        except: pass
        try: del ui_instances[ui][mode]["Surface"]
        except: pass
        try: del ui_instances[ui][mode]["Surface 2"]
        except: pass
        try: del ui_instances[ui][mode]["Text Surface"]
        except: pass
        try: del ui_instances[ui][mode]["Timer"]
        except: pass
        try: del ui_instances[ui][mode]["Deceive"]
        except: pass
          #print("Key", key, type(ui_instances[ui][mode][key]))
        #print("Key", key, type(ui_instances[ui][mode]))
  except: pass
  #except Exception as e: print(e)
  save["UI"] = ui_instances

  characters = {}
  for index, character in enumerate(main.character_types):
    chr = main.character_types[character]["object"]
    actions = []
    for state in chr.states:
      if state in chr.actions:
        frants = []
        that_anim = chr.actions[state]
        rate, loop = that_anim.rate, that_anim.loop
        condition_stat = that_anim.condition_stat
        flags = []
        if that_anim.prioritize_action: flags.append("pr")
        if that_anim.allow_travel: flags.append("at")
        if that_anim.allow_jump: flags.append("aj")
        if that_anim.allow_flip: flags.append("af")
        if that_anim.apply_gravity: flags.append("ag")
        if that_anim.aerial: flags.append("a")
        if that_anim.terrestial: flags.append("t")
        if that_anim.subaqueous: flags.append("s")
        if that_anim.cancel_on_ground: flags.append("cg")
        if that_anim.cancel_on_walk: flags.append("cw")
        if that_anim.cancel_on_jump: flags.append("cj")
        if that_anim.cancel_on_hit: flags.append("ch")
        if that_anim.directional_relative: flags.append("dr")
        if that_anim.continue_until_cancel: flags.append("guc")
        tm, combo = that_anim.trigger_mode, that_anim.combo
        cutscene_trigger = that_anim.cutscene_trigger
        for frant in chr.actions[state].frants:
          frants.append({"frame": frant.frame, "xm": frant.move_x, "ym": frant.move_y, "xg": frant.gain_x, "yg": frant.gain_y, "damage": frant.damage, "xkb": round(frant.knockback_x, 1), "ykb": round(frant.knockback_y, 1),
                        "lt": frant.loop_to, "l": frant.loops_spawn, "cu": frant.combo_unit, "sd": frant.self_destruct, "proj": frant.projectiles, "sound": frant.sound, "r": ((frant.rect.x, frant.rect.y), (frant.rect.width, frant.rect.height)), "ar": ((frant.attack_rect.x, frant.attack_rect.y), (frant.attack_rect.width, frant.attack_rect.height))})
        actions.append({"Action": state, "Rate": rate, "Loop": loop, "CS": condition_stat, "Cut": cutscene_trigger, "Flags": flags, "TM": tm, "Combo": combo, "Frants": frants})
    characters[str(index)] = ({"type": chr.character, "speed": chr.speed, "leap": chr.jump_force, "defeat_anim": chr.defeat_anim, "jump_s": chr.jump_sound,
                       "land_s": chr.land_sound, "defeat_s": chr.defeat_sound, "Actions": actions, "state_controls": chr.state_controls, "flags": main.character_types[character]["flags"]})

  save["Characters"] = characters

  #screen.blit(fontmedium.render("Saving...", True, "White"), (2, HEIGHT - 25))
  try: out_ = open("Saves/games/" + name, "w"); json.dump(save, out_); out_.close()
  except Exception as e: print(e)








def load_game(name, main, editor_mode=True):
  #screen.blit(fontmedium.render("Loading...", True, "White"), (2, HEIGHT - 25))
  try: in_ = open("Saves/games/" + name, "r"); save = json.load(in_)
  except FileNotFoundError: out_ = open("Saves/games/" + name, "w"); save = get_empty_save(main, True); json.dump(save, out_)

  main.reset(main.active_directory)
  main.rooms.clear()

  # for coin_type_index, coin_type_1 in enumerate(save["Collectible_Types"]): main.collectible_types.append(Collectible_Type(
  #   save["Collectible_Types"][coin_type_index]["name"], save["Collectible_Types"][coin_type_index]["stat"],
  #   save["Collectible_Types"][coin_type_index]["value"], save["Collectible_Types"][coin_type_index]["sound"], main))

  # for index, entity_type in enumerate(save["Entity_Types"]):
  #   drops = []
  #   for collectible_type_index, drop in enumerate(main.collectible_types):
  #     for entitys_drop in save["Entity_Types"][entity_type]["drops"]:
  #       if entitys_drop == drop.name: drops.append(drop.name)
  #   main.entity_types[str(index)] = Entity_Type(
  #   main.character_types[next(key for key, value in main.character_types.items() if value.get("type") == save["Entity_Types"][entity_type]["character"])]["object"],
  #   save["Entity_Types"][entity_type]["hp"],
  #   save["Entity_Types"][entity_type]["stat"], save["Entity_Types"][entity_type]["value"],
  #   save["Entity_Types"][entity_type]["behaviors"], save["Entity_Types"][entity_type]["range"],
  #   drops, save["Entity_Types"][entity_type]["defeat_anim"], main)

  tile_files = os.listdir(main.active_directory + "Assets/tiles/")

  main.tile_types = save["Tile_Types"]

  if len(main.tile_types) != len(tile_files):
    remember_tiles = main.tile_types.copy()
    main.tile_types = {}
    former_tiles_index = 0
    for index, tex in enumerate(tile_files):
      if not tex in [v["img"] for v in remember_tiles.values()]:
        if os.path.isdir(main.active_directory + "Assets/tiles/" + tex): img = pygame.image.load(main.active_directory + "Assets/tiles/" + tex + "/1.png").convert_alpha(); main.tile_types[str(index)] = {"img": tex, "size": [img.get_width(), img.get_height()], "off": [0, 0], "ramp": 0, "hp": -1, "team": 0, "anim_s": 1, "destr_delay": 0, "step_sfx": "", "destr_sfx": "", "destr_anim": "Disappear", "flags": ["anim", "solid"]}
        else: img = pygame.image.load(main.active_directory + "Assets/tiles/" + tex).convert_alpha(); main.tile_types[str(index)] = {"img": tex, "size": [img.get_width(), img.get_height()], "off": [0, 0], "ramp": 0, "hp": -1, "team": 0, "anim_s": 1, "destr_delay": 0, "step_sfx": "", "destr_sfx": "", "destr_anim": "Disappear", "flags": ["solid"]}
      else:
        if os.path.isdir(main.active_directory + "Assets/tiles/" + tex): img = pygame.image.load(main.active_directory + "Assets/tiles/" + tex + "/1.png").convert_alpha(); main.tile_types[str(index)] = {"img": tex, "size": remember_tiles[str(former_tiles_index)]["size"], "off": remember_tiles[str(former_tiles_index)]["off"], "ramp": remember_tiles[str(former_tiles_index)]["ramp"], "hp": remember_tiles[str(former_tiles_index)]["hp"], "team": remember_tiles[str(former_tiles_index)]["team"], "anim_s": remember_tiles[str(former_tiles_index)]["anim_s"], "destr_delay": remember_tiles[str(former_tiles_index)]["destr_delay"], "step_sfx": remember_tiles[str(former_tiles_index)]["step_sfx"], "destr_sfx": remember_tiles[str(former_tiles_index)]["destr_sfx"], "destr_anim": remember_tiles[str(former_tiles_index)]["destr_anim"], "flags": remember_tiles[str(former_tiles_index)]["flags"]}
        else: img = pygame.image.load(main.active_directory + "Assets/tiles/" + tex).convert_alpha(); main.tile_types[str(index)] = {"img": tex, "size": remember_tiles[str(former_tiles_index)]["size"], "off": remember_tiles[str(former_tiles_index)]["off"], "ramp": remember_tiles[str(former_tiles_index)]["ramp"], "hp": remember_tiles[str(former_tiles_index)]["hp"], "team": remember_tiles[str(former_tiles_index)]["team"], "anim_s": remember_tiles[str(former_tiles_index)]["anim_s"], "destr_delay": remember_tiles[str(former_tiles_index)]["destr_delay"], "step_sfx": remember_tiles[str(former_tiles_index)]["step_sfx"], "destr_sfx": remember_tiles[str(former_tiles_index)]["destr_sfx"], "destr_anim": remember_tiles[str(former_tiles_index)]["destr_anim"], "flags": remember_tiles[str(former_tiles_index)]["flags"]}
        former_tiles_index += 1
        
    # for index, (key, value) in enumerate(remember_tiles.items()):
    #   if any(os.path.basename(f) == value["img"] for f in tile_files):
    #     new_index = 0
    #     while value["img"] in list(main.tile_types.values()): new_index += 1
    #     if os.path.isdir(main.active_directory + "Assets/tiles/" + value["img"]): img = pygame.image.load(main.active_directory + "Assets/tiles/" + value["img"] + "/1.png").convert_alpha(); main.tile_types[str(new_index)] = {"img": value["img"], "size": [img.get_width(), img.get_height()], "off": [0, 0], "ramp": 0, "hp": -1, "team": 0, "anim_s": 1, "destr_delay": 0, "step_sfx": "", "destr_sfx": "", "destr_anim": "Disappear", "flags": ["anim", "solid"]}
    #     else: img = pygame.image.load(main.active_directory + "Assets/tiles/" + value["img"] + ".png").convert_alpha(); main.tile_types[str(new_index)] = {"img": value["img"], "size": [img.get_width(), img.get_height()], "off": [0, 0], "ramp": 0, "hp": -1, "team": 0, "anim_s": 1, "destr_delay": 0, "step_sfx": "", "destr_sfx": "", "destr_anim": "Disappear", "flags": ["solid"]}
  
  #print(main.tile_types)

  main.entity_types = save["Entity_Types"]
  main.collectible_types = save["Collectible_Types"]

  #if not main.tile_types[next(key for key, value in main.tile_types.items() if value.get("img") == index)] in tile_files:
  # if not save["Tile_Types"]:
  #   main.tile_types = {}
  #   for index, tex in enumerate(main.tileset):
  #     if os.path.isdir(main.active_directory + f"Assets/tiles/" + tex): img = pygame.image.load(main.active_directory + "Assets/tiles/" + tex + "/1.png").convert_alpha(); main.tile_types[index] = {"image": tex, "size": [img.get_width(), img.get_height()], "off": [0, 0], "ramp", "hp": -1, "step_sfx": "", "destr_sfx": "", "destr_anim": "", "flags": ["solid"]}
  #     else: img = pygame.image.load(main.active_directory + "Assets/tiles/" + tex).convert_alpha(); main.tile_types[index] = {"img": tex, "size": [img.get_width(), img.get_height()], "off": [0, 0], "ramp", "hp": -1, "step_sfx": "", "destr_sfx": "", "destr_anim": "", "flags": ["solid"]}
  # else:
  #   if type(save["Tile_Types"]["0"]) == dict:
  #     main.tile_types = save["Tile_Types"]
  #   else:
  #     main.tile_types = {}
  #     for index, tex in enumerate(main.tileset):
  #       if os.path.isdir(main.active_directory + f"Assets/tiles/" + tex): img = pygame.image.load(main.active_directory + "Assets/tiles/" + tex + "/1.png").convert_alpha(); main.tile_types[index] = {"image": tex, "size": [img.get_width(), img.get_height()], "off": [0, 0], "ramp", "hp": -1, "step_sfx": "", "destr_sfx": "", "destr_anim": "", "flags": ["solid"]}
  #       else: img = pygame.image.load(main.active_directory + "Assets/tiles/" + tex).convert_alpha(); main.tile_types[index] = {"img": tex, "size": [img.get_width(), img.get_height()], "off": [0, 0], "ramp", "hp": -1, "step_sfx": "", "destr_sfx": "", "destr_anim": "", "flags": ["solid"]}


  for chr_index, chr in enumerate(save["Characters"]):
    try:
      that_chr = Character(save["Characters"][chr]["type"], main)
      that_chr.speed = save["Characters"][chr]["speed"]
      that_chr.jump_force = save["Characters"][chr]["leap"]
      that_chr.defeat_anim = save["Characters"][chr]["defeat_anim"]
      that_chr.jump_sound = save["Characters"][chr]["jump_s"]
      that_chr.land_sound = save["Characters"][chr]["land_s"]
      that_chr.defeat_sound = save["Characters"][chr]["defeat_s"]
      that_chr.state_controls = save["Characters"][chr]["state_controls"]
      if that_chr.jump_sound: that_chr.jump_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_chr.jump_sound)
      if that_chr.land_sound: that_chr.land_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_chr.land_sound)
      if that_chr.defeat_sound: that_chr.defeat_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_chr.defeat_sound)
      state_index = 0
      try:
        for state in that_chr.states:
          if state in [item["Action"] for item in save["Characters"][chr]["Actions"]]:
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]] = Action(save["Characters"][chr]["Actions"][state_index]["Rate"], save["Characters"][chr]["Actions"][state_index]["Loop"], that_chr.images_dict[state.lower()], None)
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].condition_stat = save["Characters"][chr]["Actions"][state_index]["CS"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].prioritize_action = "pr" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].allow_travel = "at" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].allow_jump = "aj" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].allow_flip = "af" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].apply_gravity = "ag" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].aerial = "a" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].terrestial = "t" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].subaqueous = "s" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].cancel_on_ground = "cg" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].cancel_on_walk = "cw" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].cancel_on_jump = "cj" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].cancel_on_hit = "ch" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].directional_relative = "dr" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].continue_until_cancel = "guc" in save["Characters"][chr]["Actions"][state_index]["Flags"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].cutscene_trigger = save["Characters"][chr]["Actions"][state_index]["Cut"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].trigger_mode = save["Characters"][chr]["Actions"][state_index]["TM"]
            that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].combo = save["Characters"][chr]["Actions"][state_index]["Combo"]
            for frant_index, frant in enumerate(that_chr.actions[save["Characters"][chr]["Actions"][state_index]["Action"]].frants):
              try:
                frant.frame = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["frame"]
                frant.move_x = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["xm"]
                frant.move_y = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["ym"]
                frant.gain_x = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["xg"]
                frant.gain_y = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["yg"]
                frant.damage = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["damage"]
                frant.knockback_x = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["xkb"]
                frant.knockback_y = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["ykb"]
                frant.self_destruct = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["sd"]
                frant.loop_to = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["lt"]
                frant.loops = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["l"]
                frant.loops_spawn = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["l"]
                frant.projectiles = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["proj"]
                frant.sound = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["sound"]
                try:
                  frant.rect = pygame.FRect(save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["r"])
                  frant.attack_rect = pygame.FRect(save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["ar"])
                except: pass
                try:
                  frant.combo_unit = save["Characters"][chr]["Actions"][state_index]["Frants"][frant_index]["cu"]
                except: pass
                if frant.sound and type(frant.sound) != list: frant.sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + frant.sound)
              except: pass
            state_index += 1
          else: that_chr.actions[state] = Action(100, True, that_chr.images_dict[state.lower()], that_chr)
      except: pass
      if that_chr != None: main.character_types[chr] = {"type": that_chr.character, "object": that_chr, "flags": save["Characters"][chr]["flags"]}
    except FileNotFoundError: pass

  for player_index, player in enumerate(save["Players"]):
    that_player = Player(save["Players"][player_index]["x"], save["Players"][player_index]["y"],
                        main.character_types[next(key for key, value in main.character_types.items() if value.get("type") == save["Players"][player_index]["character"])]["object"], main=main)
    that_player.spawn_location = [save["Players"][player_index]["x"], save["Players"][player_index]["y"]]
    that_player.accelerated_travel = "at" in save["Players"][player_index]["flags"]
    that_player.bump_cancel_momentum = "bcm" in save["Players"][player_index]["flags"]
    that_player.hide_if_out = "hio" in save["Players"][player_index]["flags"]
    that_player.in_spawn = "in" in save["Players"][player_index]["flags"]
    try: that_player.team = save["Players"][player_index]["team"]
    except: pass
    that_player.player_index = save["Players"][player_index]["index"]#player_index
    that_player.port = main.ports[that_player.player_index]
    main.players.append(that_player)


  for room_index, room in enumerate(save["Rooms"]):
    that_room = Room(save["Rooms"][room_index]["Name"], main=main)
    layer_buttons = []
    for layer_index, layer in enumerate(room["Layers"]):
      that_layer = Layer("L" + str(layer_index + 1), main=main)
      for tile_index, tile in enumerate(layer["Tiles"]):
        t = save["Rooms"][room_index]["Layers"][layer_index]["Tiles"][tile_index]
        that_tile = Tile(t["x"], t["y"], save["Tile_Types"][str(t["n"])]["img"], main=main)
        #except KeyError: that_tile = Tile(t["x"], t["y"], t["w"], t["h"], t["n"], "solid" in t["fl"], "slip" in t["fl"], "flat" in t["fl"], main=main)
        that_tile.speed = t["s"]
        that_tile.spawn_speed = t["s"]
        that_tile.image = pygame.transform.scale(that_tile.image, (t["iw"], t["ih"]))
        that_tile.spawn_as_visible = not "hidden" in t["fl"]
        that_tile.destroy_if_stood_on = "diso" in t["fl"]
        that_tile.destroy_if_head_bump = "dihb" in t["fl"]
        that_tile.instigator = "inst" in t["fl"]
        that_tile.only_breakable_by_chains = "obc" in t["fl"]
        that_tile.zones_can_move = "zm" in t["fl"]
        that_tile.zones_can_rotate = "zr" in t["fl"]
        if "s" in t["fl"]: that_tile.deviating_modes.append("s")
        if "f" in t["fl"]: that_tile.deviating_modes.append("f")
        if "sl" in t["fl"]: that_tile.deviating_modes.append("sl")
        that_tile.chain_speed = t["c"]
        if "destr_delay" in t: that_tile.destroy_delay = t["destr_delay"]
        #that_tile.step_sound = t["ss"]
        #that_tile.destroy_sound = t["ds"]
        #that_tile.hp = t["hp"]
        #that_tile.spawn_hp = t["hp"]
        #that_tile.destroy_anim = t["da"]
        #if t["da"] == "-": that_tile.destroy_anim = "Disappear"
        #if that_tile.step_sound:
        #  if type(that_tile.step_sound) == list: that_tile.step_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_tile.step_sound[0])
        #  else: that_tile.step_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_tile.step_sound)
        #if that_tile.destroy_sound:
        #  if type(that_tile.destroy_sound) == list: that_tile.destroy_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_tile.destroy_sound[0])
        #  that_tile.destroy_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_tile.destroy_sound)
        that_layer.tiles.append(that_tile)
      
      for coin_index, coin in enumerate(layer["Collectibles"]):
        c = save["Rooms"][room_index]["Layers"][layer_index]["Collectibles"][coin_index]
        # the_type = None
        # for main_coin_type in main.collectible_types:
        #   for coin_type_index, coin_type_name in enumerate(save["Collectible_Types"]):
        #     if c["t"] == main_coin_type.name: the_type = main_coin_type
        that_coin = Collectible(c["x"], c["y"], main.collectible_types[c["t"]]["img"], main=main)
        that_coin.spawn_speed = c["s"]
        that_coin.speed = c["s"]
        that_coin.zones_can_move = "zm" in c["fl"]
        that_coin.zones_can_rotate = "zr" in c["fl"]
        # that_coin.price_stat = c["ps"]
        # that_coin.price_value = c["pv"]
        # that_coin.price_text_position = c["ptp"]
        # that_coin.price_text_mode = c["ptm"]
        # that_coin.debt_drop_sound = c["dds"]
        # that_coin.trigger_cutscene = c["cs"]
        # that_coin.price_exchange = "pe" in c["fl"]
        # that_coin.price_decrement = "pd" in c["fl"]
        that_coin.grabbable = not "ng" in c["fl"]
        that_coin.spawn_as_visible = not "hidden" in c["fl"]
        that_layer.collectibles.append(that_coin)

      for actor_index, entity in enumerate(layer["Actors"]):
        e = save["Rooms"][room_index]["Layers"][layer_index]["Actors"][actor_index]
        # the_type = None
        # for entity_type in main.entity_types:
        #   for entity_type_index, entity_type_name in enumerate(save["Entity_Types"]):
        #     if e["character"] == entity_type.name: the_type = entity_type
        that_entity = Entity(e["x"], e["y"], main.entity_types[e["type"]], main=main, font=e["font"], font_size=e["fsize"]) #entity_types_dict[e["character"]]
        # that_entity.speed = entity["speed"]
        that_entity.dialogue = e["dialogue"]
        that_entity.letter_delay = e["u_delay"]
        that_entity.initial_direction = e["in_dir"]
        # that_entity.jump_sound = e["jump_s"]
        # if that_entity.jump_sound:
        #   if type(that_entity.jump_sound) == list: that_entity.jump_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_entity.jump_sound[0])
        #   else: that_entity.jump_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_entity.jump_sound)
        # that_entity.land_sound = e["land_s"]
        # if that_entity.land_sound:
        #   if type(that_entity.land_sound) == list: that_entity.land_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_entity.land_sound[0])
        #   else: that_entity.land_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_entity.land_sound)
        # that_entity.defeat_sound = e["defeat_s"]
        # if that_entity.defeat_sound:
        #   if type(that_entity.defeat_sound) == list: that_entity.defeat_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_entity.defeat_sound[0])
        #   else: that_entity.defeat_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_entity.defeat_sound)
        # that_entity.trap_sound = e["trap_s"]
        # if that_entity.trap_sound:
        #   if type(that_entity.trap_sound) == list: that_entity.trap_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_entity.trap_sound[0])
        #   else: that_entity.trap_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_entity.trap_sound)
        # that_entity.notice_sound = e["notice_s"]
        # if that_entity.notice_sound:
        #   if type(that_entity.notice_sound) == list: that_entity.notice_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_entity.notice_sound[0])
        #   else: that_entity.notice_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_entity.notice_sound)
        # that_entity.speech_sound = e["speech_s"]
        # if that_entity.speech_sound:
        #   if type(that_entity.speech_sound) == list: that_entity.speech_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_entity.speech_sound[0])
        #   else: that_entity.speech_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_entity.speech_sound)
        that_entity.spawn_as_visible = not "hidden" in e["flags"]
        that_layer.actors.append(that_entity)
        that_entity.ai = AI(that_entity)

      for text_index, text in enumerate(layer["Texts"]):
        t = save["Rooms"][room_index]["Layers"][layer_index]["Texts"][text_index]
        that_text = Text(t["x"], t["y"], t["font"], t["size"], main=main)
        that_text.color = t["color"]
        that_text.outline_color = t["ol_color"]
        that_text.bg_color = t["bg_color"]
        that_text.rotation = t["rotate"]
        that_text.opacity = t["alpha"]
        that_text.scale = t["scale"]
        that_text.layer = t["layer"]
        that_text.outline_thickness = t["ol_thick"]
        that_text.bold = "bold" in t["flags"]
        that_text.italic = "italic" in t["flags"]
        that_text.underline = "ul" in t["flags"]
        that_text.strikethrough = "st" in t["flags"]
        that_text.flip[0] = "fx" in t["flags"]
        that_text.flip[1] = "fy" in t["flags"]
        that_text.anti_aliasing = "antialias" in t["flags"]
        that_text.take_variable = "v" in t["flags"]
        that_text.player_or_team = "team" in t["flags"]
        that_text.spawn_as_visible = not "hidden" in t["flags"]
        that_text.align = t["align"]
        if "cap" in t: that_text.capitalization_mode = t["cap"]
        if "cs" in t: that_text.character_string = t["cs"]
        if "ti" in t: that_text.take_index = t["ti"]
        that_text.margin = t["margin"]
        that_text.direction = t["dir"]
        that_text.behaviors = t["behave"]
        that_text.text = t["text"]
        that_text.name = t["text"]
        that_text.spawn_location = [that_text.rect.x, that_text.rect.y]
        that_text.regenerate()
        that_layer.texts.append(that_text)

      that_layer.distance = save["Rooms"][room_index]["Layers"][layer_index]["Distance"]
      that_layer.name = save["Rooms"][room_index]["Layers"][layer_index]["Label"]
      that_layer.shade = save["Rooms"][room_index]["Layers"][layer_index]["Shade"]
      that_room.layers.append(that_layer)
    
    for layer_index in list(range(len(room["Layers"])))[::-1]:
      layer_buttons.append(main.button_class(1 + (33 * layer_index), HEIGHT - 33, 32, 32, f"Access Layer {'L' + str(layer_index + 1)}", "", main.buttons_for_dragging_load[3], layer_index, button_type="Layer", room=room_index))
    
    for door_index, door in enumerate(save["Rooms"][room_index]["Doors"]):
      that_door = Door(save["Rooms"][room_index]["Doors"][door_index]["x"], save["Rooms"][room_index]["Doors"][door_index]["y"],
                      save["Rooms"][room_index]["Doors"][door_index]["name"], save["Rooms"][room_index]["Doors"][door_index]["led_room"], main=main)
      that_door.led_pos = save["Rooms"][room_index]["Doors"][door_index]["led_pos"]
      that_door.speed = save["Rooms"][room_index]["Doors"][door_index]["speed"]
      that_door.image = pygame.transform.scale(that_door.image, (save["Rooms"][room_index]["Doors"][door_index]["i_width"], save["Rooms"][room_index]["Doors"][door_index]["i_height"]))
      that_door.transition = save["Rooms"][room_index]["Doors"][door_index]["transition"]
      that_door.transition_speed_pre = save["Rooms"][room_index]["Doors"][door_index]["t_spr"]
      that_door.transition_speed_post = save["Rooms"][room_index]["Doors"][door_index]["t_spo"]
      that_door.transition_color = save["Rooms"][room_index]["Doors"][door_index]["t_color"]
      that_door.transition_shape = save["Rooms"][room_index]["Doors"][door_index]["t_shape"]
      that_door.spawn_as_visible = not "hidden" in save["Rooms"][room_index]["Doors"][door_index]["flags"]
      that_door.transition_override_ui = "or_ui" in save["Rooms"][room_index]["Doors"][door_index]["flags"]
      that_door.transition_flag_1 = "tf1" in save["Rooms"][room_index]["Doors"][door_index]["flags"]
      that_door.transition_flag_2 = "tf2" in save["Rooms"][room_index]["Doors"][door_index]["flags"]
      that_door.passable = not "pass" in save["Rooms"][room_index]["Doors"][door_index]["flags"]
      that_door.spawn_passable = not "pass" in save["Rooms"][room_index]["Doors"][door_index]["flags"]
      that_door.zones_can_move = "zm" in save["Rooms"][room_index]["Doors"][door_index]["flags"]
      that_door.zones_can_rotate = "zr" in save["Rooms"][room_index]["Doors"][door_index]["flags"]
      #that_door.transition_pre_immobilize_player = not "ipr" in save["Rooms"][room_index]["Doors"][door_index]["flags"]
      #that_door.transition_post_immobilize_player = not "ipo" in save["Rooms"][room_index]["Doors"][door_index]["flags"]
      #that_door.requires_input = not "ri" in save["Rooms"][room_index]["Doors"][door_index]["flags"]
      #that_door.transition_play_door_and_player_animation = "anim" in save["Rooms"][room_index]["Doors"][door_index]["flags"]
      that_room.doors.append(that_door)

    for bg_index, background in enumerate(save["Rooms"][room_index]["Backgrounds"]):
      that_bg = Background(save["Rooms"][room_index]["Backgrounds"][bg_index]["x"], save["Rooms"][room_index]["Backgrounds"][bg_index]["y"],
                          save["Rooms"][room_index]["Backgrounds"][bg_index]["image_path"], save["Rooms"][room_index]["Backgrounds"][bg_index]["speed"],
                          save["Rooms"][room_index]["Backgrounds"][bg_index]["distance"], main=main)
      that_bg.marges = save["Rooms"][room_index]["Backgrounds"][bg_index]["marges"]
      that_bg.repeat_x = save["Rooms"][room_index]["Backgrounds"][bg_index]["repeat_x"]; that_bg.repeat_y = save["Rooms"][room_index]["Backgrounds"][bg_index]["repeat_y"]
      that_bg.x_scroll = save["Rooms"][room_index]["Backgrounds"][bg_index]["x_scroll"]; that_bg.y_scroll = save["Rooms"][room_index]["Backgrounds"][bg_index]["y_scroll"]
      that_bg.hm_for_move = save["Rooms"][room_index]["Backgrounds"][bg_index]["hm"]; that_bg.vm_for_move = save["Rooms"][room_index]["Backgrounds"][bg_index]["vm"]
      that_bg.spawn_as_visible = not "hidden" in save["Rooms"][room_index]["Backgrounds"][bg_index]["flags"]
      that_bg.foreground = "fg" in save["Rooms"][room_index]["Backgrounds"][bg_index]["flags"]
      that_bg.take_variable = "v" in save["Rooms"][room_index]["Backgrounds"][bg_index]["flags"]
      that_bg.player_or_team = "team" in save["Rooms"][room_index]["Backgrounds"][bg_index]["flags"]
      that_bg.anim_speed = save["Rooms"][room_index]["Backgrounds"][bg_index]["as"]
      try:
        that_bg.character_string = save["Rooms"][room_index]["Backgrounds"][bg_index]["cs"]
        that_bg.take_index = save["Rooms"][room_index]["Backgrounds"][bg_index]["ti"]
      except: pass
      that_room.backgrounds.append(that_bg)

    for bg_index in list(range(len(room["Backgrounds"])))[::-1]:
      main.buttons[0].append(main.button_class(1 + (33 * (bg_index)), HEIGHT - 50, 32, 16, f"BG {str(bg_index + 1)} Options", "", main.buttons_for_dragging_load[4], bg_index, button_type="Background Layer", room=room_index))

    for zone_index, zone in enumerate(room["Zones"]):
      that_zone = Zone(save["Rooms"][room_index]["Zones"][zone_index]["x"], save["Rooms"][room_index]["Zones"][zone_index]["y"], main=main)
      that_zone.rect.width = save["Rooms"][room_index]["Zones"][zone_index]["width"]
      that_zone.rect.height = save["Rooms"][room_index]["Zones"][zone_index]["height"]
      try: that_zone.rect.gravity = save["Rooms"][room_index]["Zones"][zone_index]["g"]
      except: pass
      that_zone.trigger_event = save["Rooms"][room_index]["Zones"][zone_index]["event"]
      that_zone.trigger_cutscene = save["Rooms"][room_index]["Zones"][zone_index]["cutscene"]
      that_zone.tile_speed = save["Rooms"][room_index]["Zones"][zone_index]["ts"]
      try: that_zone.tile_rotation = save["Rooms"][room_index]["Zones"][zone_index]["tr"]
      except: pass
      that_zone.multi_active = "multi" in save["Rooms"][room_index]["Zones"][zone_index]["flags"]
      that_zone.entity_active = "entity" in save["Rooms"][room_index]["Zones"][zone_index]["flags"]
      that_zone.void = "void" in save["Rooms"][room_index]["Zones"][zone_index]["flags"]
      that_zone.ease_motion = "ease" in save["Rooms"][room_index]["Zones"][zone_index]["flags"]
      that_zone.enter_sound = save["Rooms"][room_index]["Zones"][zone_index]["enter_s"]
      if that_zone.enter_sound:
        if type(that_zone.enter_sound) == list: that_zone.enter_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_zone.enter_sound[0])
        else: that_zone.enter_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_zone.enter_sound)
      that_zone.exit_sound = save["Rooms"][room_index]["Zones"][zone_index]["exit_s"]
      if that_zone.exit_sound:
        if type(that_zone.exit_sound) == list: that_zone.exit_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_zone.exit_sound[0])
        else: that_zone.exit_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + that_zone.exit_sound)
      that_zone.track_volume = save["Rooms"][room_index]["Zones"][zone_index]["dim"]
      that_zone.color = save["Rooms"][room_index]["Zones"][zone_index]["color"]
      that_zone.surface = pygame.Surface((that_zone.rect.width, that_zone.rect.height))
      that_zone.texture = pygame.image.load("Assets/editor/zone texture.png").convert_alpha()
      that_zone.texture.fill(that_zone.color, special_flags=pygame.BLEND_RGB_MIN)
      that_room.zones.append(that_zone)

    for cs_index, cs in enumerate(room["Cutscenes"]):
      that_cs = Cutscene(save["Rooms"][room_index]["Cutscenes"][cs_index]["Name"])
      animations = save["Rooms"][room_index]["Cutscenes"][cs_index]["Animations"]
      try:
        that_cs.conditions = save["Rooms"][room_index]["Cutscenes"][cs_index]["Events"]
        #that_cs.stat_required = save["Rooms"][room_index]["Cutscenes"][cs_index]["Stat"]
        that_cs.condition_gate = save["Rooms"][room_index]["Cutscenes"][cs_index]["Gate1"]
        that_cs.condition_stat_gate = save["Rooms"][room_index]["Cutscenes"][cs_index]["Gate2"]
      except: pass

      for anim in animations:
        for player in main.players:
          if type(anim["Object"]) == tuple or type(anim["Object"]) == list:
            if player.name == anim["Object"][0] and player.rect.x == anim["Object"][1] and player.rect.y == anim["Object"][2] and anim["Object"][3] == "Player": anim["Object"] = player; break
        for layer in that_room.layers:
          for tile in layer.tiles:
            if type(anim["Object"]) == tuple or type(anim["Object"]) == list:
              if tile.name == anim["Object"][0] and tile.rect.x == anim["Object"][1] and tile.rect.y == anim["Object"][2] and anim["Object"][3] == "Tile": anim["Object"] = tile; break
          for coin in layer.collectibles:
            if type(anim["Object"]) == tuple or type(anim["Object"]) == list:
              if coin.name == anim["Object"][0] and coin.rect.x == anim["Object"][1] and coin.rect.y == anim["Object"][2] and anim["Object"][3] == "Collectible": anim["Object"] = coin; break
          for actor in layer.actors:
            if type(anim["Object"]) == tuple or type(anim["Object"]) == list:
              if actor.name == anim["Object"][0] and actor.rect.x == anim["Object"][1] and actor.rect.y == anim["Object"][2] and anim["Object"][3] == "Actor": anim["Object"] = actor; break
          for text in layer.texts:
            if type(anim["Object"]) == tuple or type(anim["Object"]) == list:
              if text.name == anim["Object"][0] and text.rect.x == anim["Object"][1] and text.rect.y == anim["Object"][2] and anim["Object"][3] == "Text": anim["Object"] = text; break
        for bg in that_room.backgrounds:
          if type(anim["Object"]) == tuple or type(anim["Object"]) == list:
            if bg.image_file_without_dir == anim["Object"][0] and bg.rect.x == anim["Object"][1] and bg.rect.y == anim["Object"][2] and anim["Object"][3] == "Background": anim["Object"] = bg; break
        for door in that_room.doors:
          if type(anim["Object"]) == tuple or type(anim["Object"]) == list:
            if door.name == anim["Object"][0] and door.rect.x == anim["Object"][1] and door.rect.y == anim["Object"][2] and anim["Object"][3] == "Door": anim["Object"] = door; break
        if type(anim["Object"]) == tuple or type(anim["Object"]) == list:
          if "Camera" == anim["Object"][0] and anim["Object"][3] == "Camera": anim["Object"] = main.camera
        if not "Speed" in anim: anim["Speed"] = 0
      that_cs.animations = animations

      for x, button in enumerate([(f"Edit Cutscene {len(that_room.cutscenes) + 1}", "cog", main.buttons_for_dragging_load[0], that_cs), (f"Rename Cutscene {len(that_room.cutscenes) + 1}", "pencil", main.buttons_for_dragging_load[1], that_cs), (f"Delete Cutscene {len(that_room.cutscenes) + 1}", "delete", main.buttons_for_dragging_load[2], that_cs)]):
        that_cs.buttons.append(main.button_class((WIDTH - 148) + 95 + (x * 17), 32, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", button[2], button[3], target_object="Cutscene"))

      that_room.cutscenes.append(that_cs)

    if "Menu" in save["Rooms"][room_index]:
      that_room.menu = save["Rooms"][room_index]["Menu"]
      if save["Rooms"][room_index]["Menu"]["down_s"] == "": that_room.menu["down_sfx"] = None
      elif type(save["Rooms"][room_index]["Menu"]["down_s"]) != list: that_room.menu["down_sfx"] = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + save["Rooms"][room_index]["Menu"]["down_s"])
      if save["Rooms"][room_index]["Menu"]["up_s"] == "": that_room.menu["up_sfx"] = None
      elif type(save["Rooms"][room_index]["Menu"]["up_s"]) != list: that_room.menu["up_sfx"] = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + save["Rooms"][room_index]["Menu"]["up_s"])
      for button in that_room.menu["items"]:
        try:
          try: font = pygame.Font(button["Text_DataS"][0], button["Text_DataS"][1])
          except: font = pygame.font.SysFont(button["Text_DataS"][0], button["Text_DataS"][1])
        except: font = pygame.Font(None, button["Text_DataS"][1])
        font.set_script("Arab")
        font.set_bold(button["Text_DataS"][7])
        font.set_italic(button["Text_DataS"][8])
        font.set_underline(button["Text_DataS"][9])
        font.set_strikethrough(button["Text_DataS"][10])
        if button["Text_DataS"][12] == "Left": font.align = pygame.FONT_LEFT
        if button["Text_DataS"][12] == "Center": font.align = pygame.FONT_CENTER
        if button["Text_DataS"][12] == "Right": font.align = pygame.FONT_RIGHT
        if button["Text_DataS"][14] == "LTR": font.set_direction(pygame.DIRECTION_LTR)
        if button["Text_DataS"][14] == "RTL": font.set_direction(pygame.DIRECTION_RTL)
        if button["Text_DataS"][14] == "TTB": font.set_direction(pygame.DIRECTION_TTB)
        if button["Text_DataS"][14] == "BTT": font.set_direction(pygame.DIRECTION_BTT)
        text = button["Text_DataS"][3]
        if button["Text_DataS"][20] == "All decapitalize": text = text.lower()
        elif button["Text_DataS"][20] == "All capitalize": text = text.upper()
        elif button["Text_DataS"][20] == "First capitalize": text = text.capitalize()
        else: text = button["Text_DataS"][3]
        if button["Text_DataS"][5] == "Transparent": image = font.render(text, button["Text_DataS"][11], button["Text_DataS"][4], wraplength=button["Text_DataS"][13]).convert_alpha()
        else: image = font.render(text, button["Text_DataS"][11], button["Text_DataS"][4], button["Text_DataS"][5], button["Text_DataS"][13]).convert_alpha()
        if button["Text_DataS"][16][0] > 0 and button["Text_DataS"][16][1] > 0: image = pygame.transform.scale(image, (button["Text_DataS"][16][0], button["Text_DataS"][16][1]))
        elif button["Text_DataS"][16][0] > 0: image = pygame.transform.scale(image, (button["Text_DataS"][16][0], image.get_height()))
        elif button["Text_DataS"][16][1] > 0: image = pygame.transform.scale(image, (image.get_width(), button["Text_DataS"][16][1]))
        image = pygame.transform.rotate(image, button["Text_DataS"][15])
        image = pygame.transform.flip(image, button["Text_DataS"][19][0], button["Text_DataS"][19][1])
        if button["Text_DataS"][18]:
          ol_image = image
          image = pygame.mask.from_surface(image).convolve(pygame.mask.Mask((button["Text_DataS"][18], button["Text_DataS"][18]), fill=True)).to_surface(setcolor=button["Text_DataS"][6], unsetcolor=image.get_colorkey()).convert_alpha()
          image.blit(ol_image, (button["Text_DataS"][18] / 2, button["Text_DataS"][18] / 2))
        image.set_alpha(button["Text_DataS"][17])
        button["Text_SurfaceS"] = image
        
        try:
          try: font = pygame.Font(button["Text_Data"][0], button["Text_Data"][1])
          except: font = pygame.font.SysFont(button["Text_Data"][0], button["Text_Data"][1])
        except: font = pygame.Font(None, button["Text_Data"][1])
        font.set_script("Arab")
        font.set_bold(button["Text_Data"][7])
        font.set_italic(button["Text_Data"][8])
        font.set_underline(button["Text_Data"][9])
        font.set_strikethrough(button["Text_Data"][10])
        if button["Text_Data"][12] == "Left": font.align = pygame.FONT_LEFT
        if button["Text_Data"][12] == "Center": font.align = pygame.FONT_CENTER
        if button["Text_Data"][12] == "Right": font.align = pygame.FONT_RIGHT
        if button["Text_Data"][14] == "LTR": font.set_direction(pygame.DIRECTION_LTR)
        if button["Text_Data"][14] == "RTL": font.set_direction(pygame.DIRECTION_RTL)
        if button["Text_Data"][14] == "TTB": font.set_direction(pygame.DIRECTION_TTB)
        if button["Text_Data"][14] == "BTT": font.set_direction(pygame.DIRECTION_BTT)
        text = button["Text_Data"][3]
        if button["Text_Data"][20] == "All decapitalize": text = text.lower()
        elif button["Text_Data"][20] == "All capitalize": text = text.upper()
        elif button["Text_Data"][20] == "First capitalize": text = text.capitalize()
        else: text = button["Text_Data"][3]
        if button["Text_Data"][5] == "Transparent": image = font.render(text, button["Text_Data"][11], button["Text_Data"][4], wraplength=button["Text_Data"][13]).convert_alpha()
        else: image = font.render(text, button["Text_Data"][11], button["Text_Data"][4], button["Text_Data"][5], button["Text_Data"][13]).convert_alpha()
        if button["Text_Data"][16][0] > 0 and button["Text_Data"][16][1] > 0: image = pygame.transform.scale(image, (button["Text_Data"][16][0], button["Text_Data"][16][1]))
        elif button["Text_Data"][16][0] > 0: image = pygame.transform.scale(image, (button["Text_Data"][16][0], image.get_height()))
        elif button["Text_Data"][16][1] > 0: image = pygame.transform.scale(image, (image.get_width(), button["Text_Data"][16][1]))
        image = pygame.transform.rotate(image, button["Text_Data"][15])
        image = pygame.transform.flip(image, button["Text_Data"][19][0], button["Text_Data"][19][1])
        if button["Text_Data"][18]:
          ol_image = image
          image = pygame.mask.from_surface(image).convolve(pygame.mask.Mask((button["Text_Data"][18], button["Text_Data"][18]), fill=True)).to_surface(setcolor=button["Text_Data"][6], unsetcolor=image.get_colorkey()).convert_alpha()
          image.blit(ol_image, (button["Text_Data"][18] / 2, button["Text_Data"][18] / 2))
        image.set_alpha(button["Text_Data"][17])
        button["Text_Surface"] = image

        if button["Image_PathS"]:
          if os.path.isdir(button["Image_PathS"]):
            button["Image_SurfaceS"] = []
            for image in sorted(os.listdir(button["Image_PathS"]), key=extract_number): button["Image_SurfaceS"].append(pygame.image.load(main.active_directory + button["Image_PathS"] + "/" + image).convert_alpha())
          else: button["Image_SurfaceS"] = pygame.image.load(main.active_directory + str(button["Image_PathS"])).convert_alpha(); button["Anim_RateS"] = -1
        else: button["Image_SurfaceS"] = None

        if button["Image_Path"]:
          if os.path.isdir(button["Image_Path"]):
            button["Image_Surface"] = []
            for image in sorted(os.listdir(button["Image_Path"]), key=extract_number): button["Image_Surface"].append(pygame.image.load(main.active_directory + button["Image_Path"] + "/" + image).convert_alpha())
          else: button["Image_Surface"] = pygame.image.load(main.active_directory + str(button["Image_Path"])).convert_alpha(); button["Anim_Rate"] = -1
        else: button["Image_Surface"] = None

        button["Timer"] = Timer()
        button["Timer2"] = Timer()

        if button["S"] == "": button["SFX"] = None
        elif type(button["S"]) != list: button["SFX"] = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + button["S"])

    that_room.layers.reverse()
    main.buttons[0] += layer_buttons
    that_room.borders = save["Rooms"][room_index]["Borders"]
    that_room.spawn_borders = save["Rooms"][room_index]["Borders"]
    that_room.track = save["Rooms"][room_index]["Track"]
    that_room.first_track = save["Rooms"][room_index]["Track1"]
    that_room.hm = "hm" in save["Rooms"][room_index]["Flags"]
    that_room.vm = "vm" in save["Rooms"][room_index]["Flags"]
    that_room.spawn_hm = "hm" in save["Rooms"][room_index]["Flags"]
    that_room.spawn_vm = "vm" in save["Rooms"][room_index]["Flags"]
    that_room.show_player = not "hide_player" in save["Rooms"][room_index]["Flags"]
    try: that_room.shader = save["Rooms"][room_index]["Shader"]
    except: pass
    try: that_room.gravity = save["Rooms"][room_index]["Gravity"]
    except: pass
    that_room.scroll_mode = save["Rooms"][room_index]["Scroll_Mode"]
    that_room.move_threshold = save["Rooms"][room_index]["Threshold"]
    that_room.show_ui = save["Rooms"][room_index]["SUI"]
    that_room.hide_ui = save["Rooms"][room_index]["HUI"]
    main.rooms.append(that_room)

  for stat in save["Stats"]["data_types"]:
    if save["Stats"]["data_types"][stat] == "int": main.game_stats[stat] = int
    if save["Stats"]["data_types"][stat] == "bool": main.game_stats[stat] = bool
    if save["Stats"]["data_types"][stat] == "str": main.game_stats[stat] = str
    if save["Stats"]["data_types"][stat] == "float": main.game_stats[stat] = float
  main.game_stats_initpoint = save["Stats"]["starting_points"]
  main.game_stats_effect = save["Stats"]["effects"]
  main.game_stats_range = save["Stats"]["ranges"]
  main.spawn_game_stats_range = save["Stats"]["ranges"]
  
  main.game_name = save["Title"]
  main.publisher = save["Publisher"]
  main.width = save["Display"]["Width"]
  main.height = save["Display"]["Height"]
  main.fps = save["Display"]["FPS"]
  main.tiles_size = save["Display"]["Tiles Size"]
  main.snap_tile_image = save["Display"]["Snap Tile Image"]
  main.snap_tile_rect = save["Display"]["Snap Tile Rect"]
  #main.input_hold = save["Input Press or Hold"]

  try:
    for ui in save["UI"].values():
      for mode in ui["Modes"]:
        main.ui.add_instance(ui[mode]["Stat"], main.ui.format_ui_component(ui[mode]["Stat"], corner=ui[mode]["Corner"], x_margin=ui[mode]["X Margin"], y_margin=ui[mode]["Y Margin"], rotation=ui[mode]["Rotate"], text=ui[mode]["Text"], multi_align=ui[mode]["MA"], multi_align_offset=ui[mode]["MAO"],
        iteration=ui[mode]["I"], i_x=ui[mode]["I X"], i_y=ui[mode]["I Y"], i_offset=ui[mode]["I Offset"], i_wrap_length=ui[mode]["I WL"], i_angle=ui[mode]["I Angle"], i_align=ui[mode]["I Align"], image_path=ui[mode]["I Image"], image_path2=ui[mode]["I Image 2"], frame_speed=ui[mode]["I FS"], antialias=ui[mode]["AA"],
        bar=ui[mode]["Bar"], vertical_bar=ui[mode]["B V"], b_x=ui[mode]["B X"], b_y=ui[mode]["B Y"], b_length=ui[mode]["B Len"], b_thickness=ui[mode]["B Thi"], b_outline=ui[mode]["B OL"], color1=ui[mode]["C1"], color2=ui[mode]["C2"], color3=ui[mode]["C3"], color4=ui[mode]["C4"], font=ui[mode]["Font STR"], font_size=ui[mode]["Font Size"], text_color=ui[mode]["TC"], text_color_outline=ui[mode]["TCOL"], text_color_bg=ui[mode]["TCBG"], text_outline_thickness=ui[mode]["TOL"], scene_mode=ui["SM"]))
  except:
    for ui in save["UI"].values():
      main.ui.add_instance(ui["Stat"], main.ui.format_ui_component(ui["Stat"], corner=ui["Corner"], x_margin=ui["X Margin"], y_margin=ui["Y Margin"], rotation=ui["Rotate"], text=ui["Text"], multi_align=ui[mode]["MA"], multi_align_offset=ui[mode]["MAO"],
      iteration=ui["I"], i_x=ui["I X"], i_y=ui["I Y"], i_offset=ui["I Offset"], i_wrap_length=ui["I WL"], i_angle=ui["I Angle"], i_align=ui["I Align"], image_path=ui["I Image"], image_path2=ui["I Image 2"], frame_speed=ui["I FS"], antialias=ui["AA"],
      bar=ui["Bar"], vertical_bar=ui["B V"], b_x=ui["B X"], b_y=ui["B Y"], b_length=ui["B Len"], b_thickness=ui["B Thi"], b_outline=ui["B OL"], color1=ui["C1"], color2=ui["C2"], color3=ui["C3"], color4=ui["C4"], font=ui["Font STR"], font_size=ui["Font Size"], text_color=ui["TC"], text_color_outline=ui["TCOL"], text_color_bg=ui["TCBG"], text_outline_thickness=ui["TOL"], scene_mode=ui["SM"]))

  for ui in main.ui.instances: main.ui.regenerate(ui)

  try:
    main.top_tiles = main.rooms[main.selected_room].layers[::-1][0].tiles
    main.top_collectibles = main.rooms[main.selected_room].layers[::-1][0].collectibles
    main.top_actors = main.rooms[main.selected_room].layers[::-1][0].actors
  except: main.top_tiles = []; main.top_collectibles = []; main.top_actors = []
  
  main.selected_object = None

  if "Projectiles" in save:
    for proj_index, proj in enumerate(save["Projectiles"]):
      that_proj = ProjectileType(save["Projectiles"][proj_index]["n"], main)
      that_proj.speed = save["Projectiles"][proj_index]["s"]
      that_proj.lifespan = save["Projectiles"][proj_index]["l"]
      that_proj.anim_speed = save["Projectiles"][proj_index]["as"]
      that_proj.set_pos_min_range = save["Projectiles"][proj_index]["minr"]
      that_proj.set_pos_max_range = save["Projectiles"][proj_index]["maxr"]
      that_proj.oscil_speed = save["Projectiles"][proj_index]["os"]
      that_proj.frequency = save["Projectiles"][proj_index]["f"]
      that_proj.vibrate = save["Projectiles"][proj_index]["v"]
      that_proj.weight = save["Projectiles"][proj_index]["w"]
      that_proj.apply_weight_after = save["Projectiles"][proj_index]["awa"]
      that_proj.pos_mode = save["Projectiles"][proj_index]["pm"]
      that_proj.stop_motion_after = save["Projectiles"][proj_index]["sma"]
      that_proj.stop_motion_for = save["Projectiles"][proj_index]["smf"]
      that_proj.deal_again = "deal" in save["Projectiles"][proj_index]["flags"]
      that_proj.pierce = "pier" in save["Projectiles"][proj_index]["flags"]
      that_proj.stoppable = "stop" in save["Projectiles"][proj_index]["flags"]
      that_proj.returnable = "turn" in save["Projectiles"][proj_index]["flags"]
      that_proj.oscil_ease = "oe" in save["Projectiles"][proj_index]["flags"]
      that_proj.stop_at_collision = "stop_ac" in save["Projectiles"][proj_index]["flags"]
      that_proj.die_at_collision = "die_ac" in save["Projectiles"][proj_index]["flags"]
      that_proj.guided = "guide" in save["Projectiles"][proj_index]["flags"]
      that_proj.beam = "beam" in save["Projectiles"][proj_index]["flags"]
      that_proj.directional_relative = "dr" in save["Projectiles"][proj_index]["flags"]
      that_proj.bounce = "bounce" in save["Projectiles"][proj_index]["flags"]
      that_proj.around_platform = "orbit" in save["Projectiles"][proj_index]["flags"]
      main.projectiles.append(that_proj)

  main.camera.rect.width, main.camera.rect.height = main.width, main.height

def load_game_attributes(game_savefile):
  save = json.load(open("Saves/games/" + game_savefile, "r"))
  if len(save["Players"]) == 0: mc = "No Players"
  else: mc = save["Players"][0]["character"]
  return {"Protagonist": mc, "Level Amount": len(save["Rooms"]), "1st Level": save["Rooms"][0]["Name"]}





















def save_game_state(name, main, index):
  save = {"Game": main.game_name, "Current Room": main.current_room, "Scroll": [main.camera.scroll[0], main.camera.scroll[1]], "Track": main.track, "Track Position": pygame.mixer.music.get_pos(), "Current Key": main.selected_key, "Stats": {"ranges": main.game_stats_range}, "Players": [], "UI": []} #"Input Press or Hold": main.input_hold, 
  rooms = []
  for room in main.rooms:
    layers = []#lemme make a file 
    for layer in room.layers: #did you import the module or * if you import the module you're in of course it's gonna circle
      tiles = []
      collectibles = []
      actors = []
      texts = []

      for tile in layer.tiles:
        flags = []
        if tile.hidden: flags.append("hidden")
        if tile.destroyed: flags.append("out")
        if tile.alive: flags.append("a")
        tiles.append({"x": tile.rect.x, "y": tile.rect.y, "s": tile.speed, "cs": tile.cs_speed, "hp": tile.hp, "fl": flags})
      
      for collectible in layer.collectibles:
        flags = []
        if collectible.hidden: flags.append("hidden")
        if collectible.grabbable: flags.append("grabbable")
        if collectible.alive: flags.append("a")
        collectibles.append({"x": collectible.rect.x, "y": collectible.rect.y, "s": collectible.speed, "cs": collectible.cs_speed, "fl": flags})
      
      for actor in layer.actors:
        flags = []
        if actor.hidden: flags.append("hidden")
        if actor.alive: flags.append("a")
        actors.append({"x": actor.rect.x, "y": actor.rect.y, "w": actor.rect.width, "h": actor.rect.height,
                       "state": actor.state, "frame": actor.frame, "flipped": actor.flipped, "rl": actor.respawn_location,
                       "s": actor.speed, "leap": actor.jump_force, "hp": actor.hp, "chr": actor.name,
                       "stats": actor.stats, "cs_s": actor.cs_speed, "flags": flags})
        
      for text in layer.texts:
        flags = []
        if not text.spawn_as_visible: flags.append("hidden")
        texts.append({"x": text.rect.x, "y": text.rect.y, "cs_s": text.cs_speed, "flags": flags})
      
      layers.append({"Tiles": tiles, "Collectibles": collectibles, "Actors": actors, "Texts": texts, "Shade": layer.shade})

    doors = []
    for door in room.doors:
      flags = []
      if door.hidden: flags.append("hidden")
      doors.append({"x": door.rect.x, "y": door.rect.y, "s": door.speed, "cs_s": door.cs_speed, "flags": flags})
    
    bgs = []
    for bg in room.backgrounds:
      flags = []
      if bg.hidden: flags.append("hidden")
      bgs.append({"x": bg.rect.x, "y": bg.rect.y, "w": bg.rect.width, "h": bg.rect.height, "cs_s": bg.cs_speed, "frame": bg.timer.tally, "flags": flags})
      
    css = []
    for cs in room.cutscenes:
      flags = []
      if cs.passed: flags.append("passed")

      css.append({"flags": flags})
    
    rooms.append({"Name": room.name, "Layers": layers[::-1], "Doors": doors, "Backgrounds": bgs, "Cutscenes": css, "Borders": room.borders, "Horizontal_Mirror": room.hm, "Vertical_Mirror": room.vm, "Selected_Item": room.selected_item})
  
  save["Rooms"] = rooms

  players = []
  for player in main.players:
    flags = []
    if player.hidden: flags.append("hidden")
    if player.in_: flags.append("in")
    if player.alive: flags.append("a")
    players.append({"x": player.rect.x, "y": player.rect.y, "w": player.rect.width, "h": player.rect.height, "s": player.speed, "leap": player.jump_force, "state": player.state, "frame": player.frame, "flipped": player.flipped,
                    "cs_s": player.cs_speed, "respawn_loc": player.respawn_location, "character": player.name, "state_controls": player.state_controls, "stats": player.stats, "flags": flags})

  save["Players"] = players

  for ui in main.ui.instances:
    #if "Hidden" in ui_instances[ui]: ui_instances[ui].remove("Hidden")
    save["UI"].append([main.ui.instances[ui]["Hidden"], main.ui.instances[ui]["Current"]])

  #screen.blit(fontmedium.render("Saving...", True, "White"), (2, HEIGHT - 25))
  out_ = open("Saves/states/" + name + " Slot " + str(index), "w"); json.dump(save, out_); out_.close()





def load_game_state(name, main, index):
  #screen.blit(fontmedium.render("Loading...", True, "White"), (2, HEIGHT - 25))
  in_ = open("Saves/states/" + name + " Slot " + str(index), "r"); save = json.load(in_)
  if main.game_name == save["Game"]:
    for player_index, player in enumerate(main.players):
      player.rect.x = save["Players"][player_index]["x"]
      player.rect.y = save["Players"][player_index]["y"]
      player.rect.width = save["Players"][player_index]["w"]
      player.rect.height = save["Players"][player_index]["h"]
      player.name = save["Players"][player_index]["character"]
      player.character = main.character_types[next(key for key, value in main.character_types.items() if value.get("type") == player.name)]["object"]
      player.speed = save["Players"][player_index]["s"]
      player.cs_speed = save["Players"][player_index]["cs_s"]
      if type(save["Players"][player_index]["cs_s"]) == tuple: player.cs_speed = save["Players"][player_index]["cs_s"][0]
      else: player.cs_speed = save["Players"][player_index]["cs_s"]
      player.jump_force = save["Players"][player_index]["leap"]
      player.state = save["Players"][player_index]["state"]
      player.frame = save["Players"][player_index]["frame"]
      if player.state in player.character.actions: player.frame = save["Players"][player_index]["frame"]
      player.stats = save["Players"][player_index]["stats"]
      player.flipped = save["Players"][player_index]["flipped"]
      player.respawn_location = save["Players"][player_index]["respawn_loc"]
      player.hidden = "hidden" in save["Players"][player_index]["flags"]
      player.in_ = "in" in save["Players"][player_index]["flags"]
      player.alive = "a" in save["Players"][player_index]["flags"]

    for room_index, room in enumerate(main.rooms):
      for layer_index, layer in enumerate(room.layers):
        for tile_index, tile in enumerate(layer.tiles):
          if tile_index < len(save["Rooms"][room_index]["Layers"][layer_index]["Tiles"]):
            t = save["Rooms"][room_index]["Layers"][layer_index]["Tiles"][tile_index]
            tile.rect.x = t["x"]
            tile.rect.y = t["y"]
            tile.speed = t["s"]
            if type(t["cs"]) == tuple: tile.cs_speed = t["cs"][0]
            else: tile.cs_speed = t["cs"]
            tile.hidden = "hidden" in t["fl"]
            tile.destroyed = "out" in t["fl"]
            tile.alive = "a" in t["fl"]
            tile.hp = t["hp"]
        
        for coin_index, coin in enumerate(layer.collectibles):
          if coin_index < len(save["Rooms"][room_index]["Layers"][layer_index]["Collectibles"]):
            c = save["Rooms"][room_index]["Layers"][layer_index]["Collectibles"][coin_index]
            coin.rect.x = c["x"]
            coin.rect.y = c["y"]
            coin.speed = c["s"]
            if type(c["cs"]) == tuple: coin.cs_speed = c["cs"][0]
            else: coin.cs_speed = c["cs"]
            coin.hidden = "hidden" in c["fl"]
            coin.grabbable = "grabbable" in c["fl"]
            coin.alive = "a" in c["fl"]

        for actor_index, entity in enumerate(layer.actors):
          if actor_index < len(save["Rooms"][room_index]["Layers"][layer_index]["Actors"]):
            e = save["Rooms"][room_index]["Layers"][layer_index]["Actors"][actor_index]
            entity.rect.x = e["x"]
            entity.rect.y = e["y"]
            entity.rect.width = e["w"]
            entity.rect.height = e["h"]
            entity.speed = e["s"]
            entity.leap = e["leap"]
            entity.state = e["state"]
            entity.frame = e["frame"]
            entity.stats = e["stats"]
            entity.hp = e["hp"]
            if entity.state in entity.character.actions: entity.frame = e["frame"]
            entity.flipped = e["flipped"]
            if type(e["cs_s"]) == tuple: entity.cs_speed = e["cs_s"][0]
            else: entity.cs_speed = e["cs_s"]
            entity.respawn_location = e["rl"]
            entity.alive = "a" in e["flags"]
            entity.hidden = "hidden" in e["flags"]

        for text_index, text in enumerate(layer.texts):
          if text_index < len(save["Rooms"][room_index]["Layers"][layer_index]["Texts"]):
            t = save["Rooms"][room_index]["Layers"][layer_index]["Texts"][text_index]
            text.rect.x = t["x"]
            text.rect.y = t["y"]
            if type(t["cs_s"]) == tuple: text.cs_speed = t["cs_s"][0]
            else: text.cs_speed = t["cs_s"]
            text.spawn_as_visible = not "hidden" in t["flags"]
          
        layer.shade = save["Rooms"][room_index]["Layers"][layer_index]["Shade"]
      
      for door_index, door in enumerate(room.doors):
        if door_index < len(save["Rooms"][room_index]["Doors"]):
          door.rect.x = save["Rooms"][room_index]["Doors"][door_index]["x"]
          door.rect.y = save["Rooms"][room_index]["Doors"][door_index]["y"]
          door.speed = save["Rooms"][room_index]["Doors"][door_index]["s"]
          door.cs_speed = save["Rooms"][room_index]["Doors"][door_index]["cs_s"]
          if type(save["Rooms"][room_index]["Doors"][door_index]["cs_s"]) == tuple: door.cs_speed = save["Rooms"][room_index]["Doors"][door_index]["cs_s"][0]
          else: door.cs_speed = save["Rooms"][room_index]["Doors"][door_index]["cs_s"]
          door.hidden = "hidden" in save["Rooms"][room_index]["Doors"][door_index]["flags"]
          door.passable = not "pass" in save["Rooms"][room_index]["Doors"][door_index]["flags"]

      for bg_index, background in enumerate(room.backgrounds):
        if bg_index < len(save["Rooms"][room_index]["Backgrounds"]):
          background.rect.x = save["Rooms"][room_index]["Backgrounds"][bg_index]["x"]
          background.rect.y = save["Rooms"][room_index]["Backgrounds"][bg_index]["y"]
          if type(save["Rooms"][room_index]["Backgrounds"][bg_index]["cs_s"]) == tuple: background.cs_speed = save["Rooms"][room_index]["Backgrounds"][bg_index]["cs_s"][0]
          else: background.cs_speed = save["Rooms"][room_index]["Backgrounds"][bg_index]["cs_s"]
          background.timer.tally = save["Rooms"][room_index]["Backgrounds"][bg_index]["frame"]
          background.hidden = "hidden" in save["Rooms"][room_index]["Backgrounds"][bg_index]["flags"]

      for cs_index, cs in enumerate(room.cutscenes):
        if cs_index < len(save["Rooms"][room_index]["Cutscenes"]):
          cs.passed = "passed" in save["Rooms"][room_index]["Cutscenes"][cs_index]["flags"]

      room.borders = save["Rooms"][room_index]["Borders"]
      room.hm = save["Rooms"][room_index]["Horizontal_Mirror"]
      room.vm = save["Rooms"][room_index]["Vertical_Mirror"]
      room.selected_item = save["Rooms"][room_index]["Selected_Item"]

    main.game_stats_range = save["Stats"]["ranges"]
    
    main.game_name = save["Game"]
    #main.input_hold = save["Input Press or Hold"]
    main.current_room = save["Current Room"]
    main.selected_key = save["Current Key"]
    main.track = save["Track"]
    if main.rooms[main.current_room].track:
      pygame.mixer.music.load("Sounds/tracks/" + main.rooms[main.current_room].track)
      pygame.mixer.music.play(-1, 0.0)
      pygame.mixer.music.set_pos(save["Track Position"] / 1000)
    elif main.rooms[main.current_room].first_track:
      pygame.mixer.music.load("Sounds/tracks/" + main.rooms[main.current_room].first_track)
      pygame.mixer.music.play(1, 0.0)
      pygame.mixer.music.set_pos(save["Track Position"] / 1000)
    else: pygame.mixer.music.stop()
    main.camera.scroll = save["Scroll"]

    for ui_index, ui in enumerate(main.ui.instances):
      main.ui.instances[ui]["Hidden"] = save["UI"][ui_index][0]
      main.ui.instances[ui]["Current"] = save["UI"][ui_index][1]

    return True
  else: return False