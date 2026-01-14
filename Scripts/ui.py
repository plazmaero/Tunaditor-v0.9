import pygame, json, os
from pygame._sdl2.video import Window, Renderer, Texture, Image
from Scripts.timers import Timer
from Scripts.settings import *
from math import cos, sin, radians, pi
from pygame.sysfont import *

class UI:
  def __init__(self, main):
    assert main != None, "ValueError: Main can't be None"
    
    self.main = main
    self.instances = {}
    self.next_id = 0

  def add_instance(self, name:str = "", components:dict = {}):
    for mode in components["Modes"]:
      try:
        try:
          if type(components[mode]["Font STR"]) == pygame.Font: components[mode]["Font"] = components[mode]["Font STR"]
          elif components[mode]["Font STR"] != None: components[mode]["Font"] = components[mode]["Font STR"]; components[mode]["Font"] = pygame.Font(components[mode]["Font STR"], components[mode]["Font Size"])
          else: components[mode]["Font"] = pygame.Font(None, components["Font Size"])
        except: components[mode]["Font"] = pygame.Font(self.main.active_directory + "Fonts/" + components[mode]["Font STR"], components[mode]["Font Size"]); components[mode]["Font STR"] = components[mode]["Font"]
      except: components[mode]["Font"] = pygame.font.SysFont(components[mode]["Font"], components[mode]["Font Size"])

      components[mode]["Text Surface"] = components[mode]["Font"].render(components[mode]["Text"], components[mode]["AA"], components[mode]["TC"]).convert_alpha()
      components[mode]["Text Surface"] = pygame.transform.rotate(components[mode]["Text Surface"], components[mode]["Rotate"])

      if components[mode]["I Image"]:
        if type(components[mode]["I Image"]) != list:
          if os.path.isdir(self.main.active_directory + "Assets/images/" + components[mode]["I Image"]):
            components[mode]["Surface"] = []
            for image in sorted(os.listdir(self.main.active_directory + "Assets/images/" + components[mode]["I Image"]), key=extract_number): components[mode]["Surface"].append(pygame.image.load(self.main.active_directory + f"Assets/images/" + components[mode]["I Image"] + "/" + image).convert_alpha())
          else: components[mode]["Surface"] = pygame.image.load(self.main.active_directory + "Assets/images/" + components[mode]["I Image"]).convert_alpha()
        else:
          components[mode]["Surface"] = ["indexed"]
          for index, image in enumerate(components[mode]["I Image"]): components[mode]["Surface"].append(pygame.image.load(self.main.active_directory + f"Assets/images/" + components[mode]["I Image"][index]).convert_alpha())

      if components[mode]["I Image 2"]:
        if type(components[mode]["I Image 2"]) != list:
          if os.path.isdir(self.main.active_directory + "Assets/images/" + components[mode]["I Image 2"]):
            components[mode]["Surface 2"] = []
            for image in sorted(os.listdir(self.main.active_directory + "Assets/images/" + components[mode]["I Image 2"]), key=extract_number): components[mode]["Surface"].append(pygame.image.load(self.main.active_directory + f"Assets/images/" + components[mode]["I Image"] + "/" + image).convert_alpha())
          else: components[mode]["Surface 2"] = pygame.image.load(self.main.active_directory + "Assets/images/" + components[mode]["I Image 2"]).convert_alpha()
        else:
          components[mode]["Surface 2"] = ["indexed"]
          for index, image in enumerate(components[mode]["I Image 2"]): components[mode]["Surface 2"].append(pygame.image.load(self.main.active_directory + f"Assets/images/" + components[mode]["I Image 2"][index]).convert_alpha())

      assert isinstance(name, str), "ValueError: Name is not a string."
      assert isinstance(components, dict), "ValueError: Components is not a dictionary."
      if name != "":
        self.instances[name] = components
      else:
        self.instances[str(self.next_id)] = components
        self.next_id += 1

  def add_mode(self, mode:str = "1", components:dict = {}):
      try:
        try:
          if type(components[mode]["Font STR"]) == pygame.Font: components[mode]["Font"] = components[mode]["Font STR"]
          elif components[mode]["Font STR"] != None: components[mode]["Font"] = components[mode]["Font STR"]; components[mode]["Font"] = pygame.Font(components[mode]["Font STR"], components[mode]["Font Size"])
          else: components[mode]["Font"] = pygame.Font(None, components["Font Size"])
        except: components[mode]["Font"] = pygame.Font(self.main.active_directory + "Fonts/" + components[mode]["Font STR"], components[mode]["Font Size"]); components[mode]["Font STR"] = components[mode]["Font"]
      except: components[mode]["Font"] = pygame.font.SysFont(components[mode]["Font"], components[mode]["Font Size"])

      components[mode]["Text Surface"] = components[mode]["Font"].render(components[mode]["Text"], components[mode]["AA"], components[mode]["TC"]).convert_alpha()
      components[mode]["Text Surface"] = pygame.transform.rotate(components[mode]["Text Surface"], components[mode]["Rotate"])

      if components[mode]["I Image"]:
        if type(components[mode]["I Image"]) != list:
          if os.path.isdir(self.main.active_directory + "Assets/images/" + components[mode]["I Image"]):
            components[mode]["Surface"] = []
            for image in sorted(os.listdir(self.main.active_directory + "Assets/images/" + components[mode]["I Image"]), key=extract_number): components[mode]["Surface"].append(pygame.image.load(self.main.active_directory + f"Assets/images/" + components[mode]["I Image"] + "/" + image).convert_alpha())
          else: components[mode]["Surface"] = pygame.image.load(self.main.active_directory + "Assets/images/" + components[mode]["I Image"]).convert_alpha()
        else:
          components[mode]["Surface"] = ["indexed"]
          for index, image in enumerate(components[mode]["I Image"]): components[mode]["Surface"].append(pygame.image.load(self.main.active_directory + f"Assets/images/" + components[mode]["I Image"][index]).convert_alpha())

      if components[mode]["I Image 2"]:
        if type(components[mode]["I Image 2"]) != list:
          if os.path.isdir(self.main.active_directory + "Assets/images/" + components[mode]["I Image 2"]):
            components[mode]["Surface 2"] = []
            for image in sorted(os.listdir(self.main.active_directory + "Assets/images/" + components[mode]["I Image 2"]), key=extract_number): components[mode]["Surface"].append(pygame.image.load(self.main.active_directory + f"Assets/images/" + components[mode]["I Image"] + "/" + image).convert_alpha())
          else: components[mode]["Surface 2"] = pygame.image.load(self.main.active_directory + "Assets/images/" + components[mode]["I Image 2"]).convert_alpha()
        else:
          components[mode]["Surface 2"] = ["indexed"]
          for index, image in enumerate(components[mode]["I Image 2"]): components[mode]["Surface 2"].append(pygame.image.load(self.main.active_directory + f"Assets/images/" + components[mode]["I Image 2"][index]).convert_alpha())
    
  def delete_instance(self, name:str):
    assert isinstance(name, str), "ValueError: Name is not a string."
    self.instances.pop(name)

  def format_ui_component(self, stat:str, corner:str, x_margin:int, y_margin:int, rotation:int, text:str, multi_align:str, multi_align_offset:int, iteration:bool, i_x:int, i_y:int, i_offset:int, i_wrap_length:int, i_angle:int, i_align:str, image_path:str, image_path2:str, frame_speed:int, antialias:bool, bar:bool, vertical_bar:bool, b_x:int, b_y:int, b_length:int, b_thickness:int, b_outline:int, color1:tuple, color2:tuple, color3:tuple, color4:tuple, font:str, font_size:int, text_color:tuple, text_color_outline:tuple, text_color_bg:tuple, text_outline_thickness:int, scene_mode:int=1):
    return {"Modes": ["1"], "Current": "1", "Hidden": False, "SM": scene_mode, "1": {"Stat": stat, "Corner": corner, "X Margin": x_margin, "Y Margin": y_margin, "Rotate": rotation, "Text": text, "MA": multi_align, "MAO": multi_align_offset, "I": iteration, "I X": i_x, "I Y": i_y, "I Offset": i_offset, "I WL": i_wrap_length, "I Angle": i_angle, "I Align": i_align, "I Image": image_path, "I Image 2": image_path2, "I FS": frame_speed, "AA": antialias, "Bar": bar, "B V": vertical_bar, "B X": b_x, "B Y": b_y, "B Len": b_length, "B Thi": b_thickness, "B OL": b_outline, "C1": color1, "C2": color2, "C3": color3, "C4": color4, "Font STR": font, "Font Size": font_size, "TC": text_color, "TCOL": text_color_outline, "TCBG": text_color_bg, "TOL": text_outline_thickness, "Font": None, "Surface": None, "Surface 2": None, "Text Surface": None, "Timer": Timer(), "Deceive": [0, 0]}}
  
  def format_ui_mode(self, stat:str, corner:str, x_margin:int, y_margin:int, rotation:int, text:str, multi_align:str, multi_align_offset:int, iteration:bool, i_x:int, i_y:int, i_offset:int, i_wrap_length:int, i_angle:int, i_align:str, image_path:str, image_path2:str, frame_speed:int, antialias:bool, bar:bool, vertical_bar:bool, b_x:int, b_y:int, b_length:int, b_thickness:int, b_outline:int, color1:tuple, color2:tuple, color3:tuple, color4:tuple, font:str, font_size:int, text_color:tuple, text_color_outline:tuple, text_color_bg:tuple, text_outline_thickness:int):
    return {"Stat": stat, "Corner": corner, "X Margin": x_margin, "Y Margin": y_margin, "Rotate": rotation, "Text": text, "MA": multi_align, "MAO": multi_align_offset, "I": iteration, "I X": i_x, "I Y": i_y, "I Offset": i_offset, "I WL": i_wrap_length, "I Angle": i_angle, "I Align": i_align, "I Image": image_path, "I Image 2": image_path2, "I FS": frame_speed, "AA": antialias, "Bar": bar, "B V": vertical_bar, "B X": b_x, "B Y": b_y, "B Len": b_length, "B Thi": b_thickness, "B OL": b_outline, "C1": color1, "C2": color2, "C3": color3, "C4": color4, "Font STR": font, "Font Size": font_size, "TC": text_color, "TCOL": text_color_outline, "TCBG": text_color_bg, "TOL": text_outline_thickness, "Font": None, "Surface": None, "Surface 2": None, "Text Surface": None, "Timer": Timer(), "Deceive": [0, 0]}

  def load(self, path:str):
    assert isinstance(path, str), "ValueError: Path is not a string."
    assert os.path.isfile(path), "FileError: File doesn't exist."
        
    with open(path, "r") as file:
      data = json.loads(file.read())["data"]
      for item in data: self.add_instance(components = item)

  def regenerate(self, instance):
    for mode in self.instances[instance]["Modes"]:
      try: self.instances[instance][mode]["Font"] = pygame.Font(self.instances[instance][mode]["Font STR"], self.instances[instance][mode]["Font Size"])
      except: self.instances[instance][mode]["Font"] = pygame.font.SysFont(self.instances[instance][mode]["Font STR"], self.instances[instance][mode]["Font Size"])
      if self.instances[instance][mode]["TCBG"] == "Transparent": self.instances[instance][mode]["Text Surface"] = self.instances[instance][mode]["Font"].render(self.instances[instance][mode]["Text"], self.instances[instance][mode]["AA"], self.instances[instance][mode]["TC"]).convert_alpha()
      else: self.instances[instance][mode]["Text Surface"] = self.instances[instance][mode]["Font"].render(self.instances[instance][mode]["Text"], self.instances[instance][mode]["AA"], self.instances[instance][mode]["TC"], self.instances[instance][mode]["TCBG"]).convert_alpha()
      self.instances[instance][mode]["Text Surface"] = pygame.transform.rotate(self.instances[instance][mode]["Text Surface"], self.instances[instance][mode]["Rotate"])
      if self.instances[instance][mode]["TOL"]:
        ol_image = self.instances[instance][mode]["Text Surface"]
        self.instances[instance][mode]["Text Surface"] = pygame.mask.from_surface(self.instances[instance][mode]["Text Surface"]).convolve(pygame.mask.Mask((self.instances[instance][mode]["TOL"], self.instances[instance][mode]["TOL"]), fill=True)).to_surface(setcolor=self.instances[instance][mode]["TCOL"], unsetcolor=self.instances[instance][mode]["Text Surface"].get_colorkey()).convert_alpha()
        self.instances[instance][mode]["Text Surface"].blit(ol_image, (self.instances[instance][mode]["TOL"] / 2, self.instances[instance][mode]["TOL"] / 2))

  def render(self, screen, clock):
    i = self.instances
    for player_index, player in enumerate(self.main.players):
      for c in self.instances:
        current = i[c]["Current"]
        for mode in self.main.rooms[self.main.current_room].ui_modes:
          if mode[0] == i[c]["SM"]: i[c]["Current"] = str(mode[1])
        if i[c]["Current"] in i[c]["Modes"]:
          if not i[c]["Hidden"]:
            xa, ya = 0, 0
            if len(self.main.players) > 1:
              player_offset = player_index - (len(self.main.players) - 1) / 2
              if i[c][current]["MA"] == "right": xa = i[c][current]["MAO"] * player_index
              if i[c][current]["MA"] == "center_horizontal": xa = i[c][current]["MAO"] * player_offset
              if i[c][current]["MA"] == "left": xa = -i[c][current]["MAO"] * player_index
              if i[c][current]["MA"] == "up": ya = i[c][current]["MAO"] * player_index
              if i[c][current]["MA"] == "center_vertical": ya = i[c][current]["MAO"] * player_offset
              if i[c][current]["MA"] == "down": ya = -i[c][current]["MAO"] * player_index

            if i[c][current]["Bar"]:
              if self.main.game_stats[i[c][current]["Stat"]] == int or self.main.game_stats[i[c][current]["Stat"]] == float:
                stat_value = player.stats[i[c][current]["Stat"]]
                stat_min = self.main.game_stats_range[i[c][current]["Stat"]][0]
                stat_max = self.main.game_stats_range[i[c][current]["Stat"]][1]
                if not i[c][current]["B V"]:
                  if stat_value - stat_min != 0 and stat_max - stat_min != 0 and stat_min < stat_max: fill_length = (stat_value - stat_min) / (stat_max - stat_min) * i[c][current]["B Len"]
                  else: fill_length = 0
                  if i[c][current]["I Align"] == 'Left': fill_start_x = i[c][current]["B X"]
                  elif i[c][current]["I Align"] == 'Center': fill_start_x = i[c][current]["B X"] + (i[c][current]["B Len"] - fill_length) / 2
                  elif i[c][current]["I Align"] == 'Right': fill_start_x = i[c][current]["B X"] + i[c][current]["B Len"] - fill_length
                  if i[c][current]["C2"] != "Transparent": pygame.draw.rect(screen, i[c][current]["C2"], ((i[c][current]["B X"] + xa, i[c][current]["B Y"] + ya), (i[c][current]["B Len"], i[c][current]["B Thi"])))
                  if fill_length > 0: pygame.draw.rect(screen, i[c][current]["C1"], ((fill_start_x + xa, i[c][current]["B Y"] + ya), (fill_length, i[c][current]["B Thi"])))
                  if i[c][current]["B OL"]: pygame.draw.rect(screen, i[c][current]["C3"], ((i[c][current]["B X"] + xa, i[c][current]["B Y"] + ya), (i[c][current]["B Len"], i[c][current]["B Thi"])), width=i[c][current]["B OL"])
                else:
                  if stat_value - stat_min != 0 and stat_max - stat_min != 0 and stat_min < stat_max: fill_length = (stat_value - stat_min) / (stat_max - stat_min) * i[c][current]["B Len"]
                  else: fill_length = 0
                  if i[c][current]["I Align"] == 'Left': fill_start_y = i[c][current]["B Y"]
                  elif i[c][current]["I Align"] == 'Center': fill_start_y = i[c][current]["B Y"] + (i[c][current]["B Len"] - fill_length) / 2
                  elif i[c][current]["I Align"] == 'Right': fill_start_y = i[c][current]["B Y"] + i[c][current]["B Len"] - fill_length
                  if i[c][current]["C2"] != "Transparent": pygame.draw.rect(screen, i[c][current]["C2"], ((i[c][current]["B X"] + xa, i[c][current]["B Y"] + ya), (i[c][current]["B Thi"], i[c][current]["B Len"])))
                  if fill_length > 0: pygame.draw.rect(screen, i[c][current]["C1"], ((i[c][current]["B X"] + xa, fill_start_y), (i[c][current]["B Thi"] + ya, fill_length)))
                  if i[c][current]["B OL"]: pygame.draw.rect(screen, i[c][current]["C3"], ((i[c][current]["B X"] + xa, i[c][current]["B Y"] + ya), (i[c][current]["B Thi"], i[c][current]["B Len"])), width=i[c][current]["B OL"])
              elif self.main.game_stats[i[c][current]["Stat"]] == bool:
                if not i[c][current]["B V"]:
                  if i[c][current]["C2"] != "Transparent": pygame.draw.rect(screen, i[c][current]["C2"], ((i[c][current]["B X"] + xa, i[c][current]["B Y"] + ya), (i[c][current]["B Len"], i[c][current]["B Thi"])))
                  if player.stats[i[c][current]["Stat"]]: pygame.draw.rect(screen, i[c][current]["C1"], ((i[c][current]["B X"] + xa, i[c][current]["B Y"] + ya), (i[c][current]["B Len"], i[c][current]["B Thi"])))
                  if i[c][current]["B OL"]: pygame.draw.rect(screen, i[c][current]["C3"], ((i[c][current]["B X"] + xa, i[c][current]["B Y"] + ya), (i[c][current]["B Len"], i[c][current]["B Thi"])), width=i[c][current]["B OL"])
                else:
                  if i[c][current]["C2"] != "Transparent": pygame.draw.rect(screen, i[c][current]["C2"], ((i[c][current]["B X"] + xa, i[c][current]["B Y"] + ya), (i[c][current]["B Thi"], i[c][current]["B Len"])))
                  if player.stats[i[c][current]["Stat"]]: pygame.draw.rect(screen, i[c][current]["C1"], ((i[c][current]["B X"] + xa, i[c][current]["B Y"] + ya), (i[c][current]["B Thi"], i[c][current]["B Len"])))
                  if i[c][current]["B OL"]: pygame.draw.rect(screen, i[c][current]["C3"], ((i[c][current]["B X"] + xa, i[c][current]["B Y"] + ya), (i[c][current]["B Thi"], i[c][current]["B Len"])), width=i[c][current]["B OL"])

            if i[c][current]["Text"]:
              try:
                text = i[c][current]["Text"]
                if not "<var>" in i[c][current]["Text"] and not "<img>" in i[c][current]["Text"] and not "<fps>" in i[c][current]["Text"]:
                  i[c][current]["Text Surface"] = i[c][current]["Font"].render(text, i[c][current]["AA"], i[c][current]["TC"]).convert_alpha()

                if "<var>" in i[c][current]["Text"]:
                  if i[c][current]["Stat"] in self.main.game_stats: text = i[c][current]["Text"].replace("<var>", str(player.stats[i[c][current]["Stat"]]))
                  else: text = i[c][current]["Text"].replace("<var>", "Stat Doesn't Exist")

                if "<fps>" in i[c][current]["Text"]:
                  text = text.replace("<fps>", str(clock.get_fps()))
                
                i[c][current]["Text Surface"] = i[c][current]["Font"].render(text, i[c][current]["AA"], i[c][current]["TC"]).convert_alpha()
              except:
                try:
                  try:
                    if type(i[c][current]["Font STR"]) == pygame.Font: i[c][current]["Font"] = i[c][current]["Font STR"]
                    elif i[c][current]["Font STR"] != None: i[c][current]["Font"] = i[c][current]["Font STR"]; i[c][current]["Font"] = pygame.Font(i[c][current]["Font STR"], i[c][current]["Font Size"])
                    else: i[c][current]["Font"] = pygame.Font(None, i[c][current]["Font Size"])
                  except: i[c][current]["Font"] = pygame.Font(self.main.active_directory + "Fonts/" + i[c][current]["Font STR"], i[c][current]["Font Size"]); i[c][current]["Font STR"] = i[c][current]["Font"]
                except: i[c][current]["Font"] = pygame.font.SysFont(i[c][current]["Font"], i[c][current]["Font Size"])
                i[c][current]["Text Surface"] = i[c][current]["Font"].render(text, i[c][current]["AA"], i[c][current]["TC"]).convert_alpha()

              if "<img>" in i[c][current]["Text"] and i[c][current]["Surface"] and i[c][current]["Surface"] != "":
                parts = i[c][current]["Text"].split("<img>")
                x_offset = 0
                surfaces = []
                for part in parts:
                  if "<var>" in part:
                    if i[c][current]["Stat"] in self.main.game_stats: text_surface = i[c][current]["Font"].render(part.replace("<var>", str(player.stats[i[c][current]["Stat"]])), i[c][current]["AA"], i[c][current]["TC"]).convert_alpha()
                    else: text_surface = i[c][current]["Font"].render(part.replace("<var>", "Stat Doesn't Exist"), i[c][current]["AA"], i[c][current]["TC"]).convert_alpha()
                  else: text_surface = i[c][current]["Font"].render(part, i[c][current]["AA"], i[c][current]["TC"]).convert_alpha()

                  if "<fps>" in part: text_surface = i[c][current]["Font"].render(part.replace("<fps>", str(clock.get_fps())), i[c][current]["AA"], i[c][current]["TC"]).convert_alpha()
                  else: text_surface = i[c][current]["Font"].render(part, i[c][current]["AA"], i[c][current]["TC"]).convert_alpha()

                  surfaces.append((text_surface, x_offset)); x_offset += text_surface.get_width()
                  if part != parts[-1]:
                    if type(i[c][current]["Surface"]) == list:
                      if "indexed" in i[c][current]["Surface"] and (self.main.game_stats[i[c][current]["Stat"]] == int or self.main.game_stats[i[c][current]["Stat"]] == float): surface = i[c][current]["Surface"][(player.stats[i[c][current]["Stat"]] % (len(i[c][current]["Surface"]) - 1)) + 1]
                      else: surface = i[c][current]["Surface"][i[c][current]["Timer"].keep_count(i[c][current]["I FS"], len(i[c][current]["Surface"]), 0)]
                    else: surface = i[c][current]["Surface"]
                    surfaces.append((surface, x_offset)); x_offset += surface.get_width()

                i[c][current]["Text Surface"] = pygame.Surface((x_offset, max(s[0].get_height() for s in surfaces)), pygame.SRCALPHA).convert_alpha()
                for surface, offset in surfaces: i[c][current]["Text Surface"].blit(surface, (offset, 0))

              if i[c][current]["Rotate"] != 0: i[c][current]["Text Surface"] = pygame.transform.rotate(i[c][current]["Text Surface"], i[c][current]["Rotate"])

              if i[c][current]["Corner"] == "Up Left": x, y = 0 + i[c][current]["X Margin"] + xa, 0 + i[c][current]["Y Margin"] + ya
              if i[c][current]["Corner"] == "Up": x, y = (self.main.width / 2) - (i[c][current]["Text Surface"].get_width() / 2) + xa, 0 + i[c][current]["Y Margin"] + ya
              if i[c][current]["Corner"] == "Up Right": x, y = ((self.main.width) - (i[c][current]["Text Surface"].get_width())) - i[c][current]["X Margin"] + xa, 0 + i[c][current]["Y Margin"] + ya
              if i[c][current]["Corner"] == "Left": x, y = 0 + i[c][current]["X Margin"] + xa, ((self.main.height / 2) - (i[c][current]["Text Surface"].get_height() / 2)) + i[c][current]["Y Margin"] + ya
              if i[c][current]["Corner"] == "Center": x, y = ((self.main.width / 2) - (i[c][current]["Text Surface"].get_width() / 2)) + i[c][current]["X Margin"] + xa, ((self.main.height / 2) - (i[c][current]["Text Surface"].get_height() / 2)) + i[c][current]["X Margin"] + ya
              if i[c][current]["Corner"] == "Right": x, y = ((self.main.width) - (i[c][current]["Text Surface"].get_width())) - i[c][current]["X Margin"] + xa, ((self.main.height / 2) - (i[c][current]["Text Surface"].get_height() / 2)) + i[c][current]["Y Margin"] + ya
              if i[c][current]["Corner"] == "Down Left": x, y = 0 + i[c][current]["X Margin"] + xa, ((self.main.height) - (i[c][current]["Text Surface"].get_height())) - i[c][current]["Y Margin"] + ya
              if i[c][current]["Corner"] == "Down": x, y = ((self.main.width / 2) - (i[c][current]["Text Surface"].get_width() / 2)) + i[c][current]["X Margin"] + xa, ((self.main.height) - (i[c][current]["Text Surface"].get_height())) - i[c][current]["Y Margin"] + ya
              if i[c][current]["Corner"] == "Down Right": x, y = ((self.main.width) - (i[c][current]["Text Surface"].get_width())) - i[c][current]["X Margin"] + xa, ((self.main.height) - (i[c][current]["Text Surface"].get_height())) - i[c][current]["Y Margin"] + ya
              if i[c][current]["Text Surface"] != None: screen.blit(i[c][current]["Text Surface"], (x, y))

            if i[c][current]["I Image"] and i[c][current]["I"]:
              if self.main.game_stats[i[c][current]["Stat"]] == int or self.main.game_stats[i[c][current]["Stat"]] == float:
                if self.main.game_stats_range[i[c][current]["Stat"]][0] < self.main.game_stats_range[i[c][current]["Stat"]][1] and i[c][current]["I Image 2"]:
                  for iterator in range(self.main.game_stats_range[i[c][current]["Stat"]][1]):
                    angle = radians(i[c][current]["I Angle"] - 90)
                    if type(i[c][current]["Surface"]) == list:
                      if "indexed" in i[c][current]["Surface"]: surface = i[c][current]["Surface"][(iterator % (len(i[c][current]["Surface"]) - 1)) + 1]
                      else: surface = i[c][current]["Surface"][i[c][current]["Timer"].keep_count(i[c][current]["I FS"], len(i[c][current]["Surface"]), 0)]
                    else: surface = i[c][current]["Surface"]
                    if type(i[c][current]["Surface 2"]) == list:
                      if "indexed" in i[c][current]["Surface 2"]: surface2 = i[c][current]["Surface 2"][(iterator % (len(i[c][current]["Surface 2"]) - 1)) + 1]
                      else: surface2 = i[c][current]["Surface 2"][i[c][current]["Timer"].keep_count(i[c][current]["I FS"], len(i[c][current]["Surface 2"]), 0)]
                    else: surface2 = i[c][current]["Surface 2"]
                    offset_x = (i[c][current]["I Offset"] + surface.get_width()) * cos(angle); offset_y = (i[c][current]["I Offset"] + surface.get_height()) * sin(angle)
                    x = i[c][current]["I X"] + (iterator * offset_x); y = i[c][current]["I Y"] + (iterator * offset_y)
                    try: row = iterator // i[c][current]["I WL"]
                    except ZeroDivisionError: row = i[c][current]["I WL"]
                    col = iterator % i[c][current]["I WL"]
                    max_images_in_row = min(i[c][current]["I WL"], self.main.game_stats_range[i[c][current]["Stat"]][1] - row * i[c][current]["I WL"])
                    row_width = (max_images_in_row - 1) * (i[c][current]["I Offset"] + surface.get_width())
                    if i[c][current]["I Align"] == "Left": initial_x = i[c][current]["I X"]
                    elif i[c][current]["I Align"] == "Right": initial_x = i[c][current]["I X"] - row_width
                    elif i[c][current]["I Align"] == "Center": initial_x = i[c][current]["I X"] - (row_width / 2)
                    x = initial_x + (col * offset_x) + (row * (i[c][current]["I Offset"] + surface.get_width()) * cos(angle + pi / 2))
                    y = i[c][current]["I Y"] + (col * offset_y) + (row * (i[c][current]["I Offset"] + surface.get_height()) * sin(angle + pi / 2))
                    if player.stats[i[c][current]["Stat"]] > iterator: screen.blit(surface, (x + xa, y + ya))
                    else: screen.blit(surface2, (x + xa, y + ya))

                else:
                  for iterator in range(round(player.stats[i[c][current]["Stat"]])):
                    angle = radians(i[c][current]["I Angle"] - 90)
                    if type(i[c][current]["Surface"]) == list:
                      if "indexed" in i[c][current]["Surface"]: surface = i[c][current]["Surface"][(iterator % (len(i[c][current]["Surface"]) - 1)) + 1]
                      else: surface = i[c][current]["Surface"][i[c][current]["Timer"].keep_count(i[c][current]["I FS"], len(i[c][current]["Surface"]), 0)]
                    else: surface = i[c][current]["Surface"]
                    offset_x = (i[c][current]["I Offset"] + surface.get_width()) * cos(angle); offset_y = (i[c][current]["I Offset"] + surface.get_height()) * sin(angle)
                    x = i[c][current]["I X"] + (iterator * offset_x); y = i[c][current]["I Y"] + (iterator * offset_y)
                    try: row = iterator // i[c][current]["I WL"]
                    except ZeroDivisionError: row = i[c][current]["I WL"]
                    col = iterator % i[c][current]["I WL"]
                    max_images_in_row = min(i[c][current]["I WL"], player.stats[i[c][current]["Stat"]] - row * i[c][current]["I WL"])
                    row_width = (max_images_in_row - 1) * (i[c][current]["I Offset"] + surface.get_width())
                    if i[c][current]["I Align"] == "Left": initial_x = i[c][current]["I X"]
                    elif i[c][current]["I Align"] == "Right": initial_x = i[c][current]["I X"] - row_width
                    elif i[c][current]["I Align"] == "Center": initial_x = i[c][current]["I X"] - (row_width / 2)
                    x = initial_x + (col * offset_x) + (row * (i[c][current]["I Offset"] + surface.get_width()) * cos(angle + pi / 2))
                    y = i[c][current]["I Y"] + (col * offset_y) + (row * (i[c][current]["I Offset"] + surface.get_height()) * sin(angle + pi / 2))
                    screen.blit(surface, (x + xa, y + ya))

              elif self.main.game_stats[i[c][current]["Stat"]] == str:
                for index, iterator in enumerate(str(player.stats[i[c][current]["Stat"]])):
                  angle = radians(i[c][current]["I Angle"])
                  if type(i[c][current]["Surface"]) == list:
                    if "indexed" in i[c][current]["Surface"]:
                      try: surface = i[c][current]["Surface"][(index % (len(i[c][current]["Surface"]) - 1)) + 1]
                      except IndexError: surface = i[c][current]["Surface"][0]
                    else: surface = i[c][current]["Surface"][i[c][current]["Timer"].keep_count(i[c][current]["I FS"], len(i[c][current]["Surface"]), 0)]
                  else: surface = i[c][current]["Surface"]
                  offset_x = (i[c][current]["I Offset"] + surface.get_width()) * cos(angle); offset_y = (i[c][current]["I Offset"] + surface.get_height()) * sin(angle)
                  x = i[c][current]["I X"] + (index * offset_x); y = i[c][current]["I Y"] + (index * offset_y)
                  try: row = index // i[c][current]["I WL"]
                  except ZeroDivisionError: row = i[c][current]["I WL"]
                  col = index % i[c][current]["I WL"]
                  max_images_in_row = min(i[c][current]["I WL"], len(player.stats[i[c][current]["Stat"]]) - row * i[c][current]["I WL"])
                  row_width = (max_images_in_row - 1) * (i[c][current]["I Offset"] + surface.get_width())
                  if i[c][current]["I Align"] == "Left": initial_x = i[c][current]["I X"]
                  elif i[c][current]["I Align"] == "Right": initial_x = i[c][current]["I X"] - row_width
                  elif i[c][current]["I Align"] == "Center": initial_x = i[c][current]["I X"] - (row_width / 2)
                  x = initial_x + (col * offset_x) + (row * (i[c][current]["I Offset"] + surface.get_width()) * cos(angle + pi / 2))
                  y = i[c][current]["I Y"] + (col * offset_y) + (row * (i[c][current]["I Offset"] + surface.get_height()) * sin(angle + pi / 2))
                  screen.blit(surface, (x + xa, y + ya))

              elif self.main.game_stats[i[c][current]["Stat"]] == bool:
                if player.stats[i[c][current]["Stat"]]:
                  if type(i[c][current]["Surface"]) == list: surface = i[c][current]["Surface"][i[c][current]["Timer"].keep_count(i[c][current]["I FS"], len(i[c][current]["Surface"]), 0)]
                  else: surface = i[c][current]["Surface"]
                  screen.blit(surface, (i[c][current]["I X"] + xa, i[c][current]["I Y"] + ya))