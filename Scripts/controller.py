import pygame
from pygame.locals import *

class Controller:
  def __init__(self, index, device="Default", rumble=False, deadzone=0.7):
    self.device = device
    self.buttons = {
      "Press": {"a": False, "b": False, "x": False, "y": False, "right": False, "left": False, "up": False, "down": False, "l": False, "r": False, "select": False, "start": False},
      "Hold": {"a": False, "b": False, "x": False, "y": False, "right": False, "left": False, "up": False, "down": False, "l": False, "r": False, "select": False, "start": False},
      "Release": {"a": False, "b": False, "x": False, "y": False, "right": False, "left": False, "up": False, "down": False, "l": False, "r": False, "select": False, "start": False}
      }
    self.rumble = rumble
    self.deadzone = deadzone
    self.power = 100
    self.index = index

  def disable(self):
    self.buttons = {
      "Press": {"a": False, "b": False, "x": False, "y": False, "right": False, "left": False, "up": False, "down": False, "l": False, "r": False, "select": False, "start": False},
      "Hold": {"a": False, "b": False, "x": False, "y": False, "right": False, "left": False, "up": False, "down": False, "l": False, "r": False, "select": False, "start": False},
      "Release": {"a": False, "b": False, "x": False, "y": False, "right": False, "left": False, "up": False, "down": False, "l": False, "r": False, "select": False, "start": False}}


k_down, k_up, k_right, k_left, k_a, k_b, k_x, k_y, k_z, k_l, k_r, k_select, k_start, k_back = False, False, False, False, False, False, False, False, False, False, False, False, False, False

controller_states = {
  1: {"Press": {"A": False, "B": False, "X": False, "Y": False, "Right": False, "Left": False, "Up": False, "Down": False,
        "Shoulder_L": False, "Shoulder_R": False, "Z": False, "SELECT": False, "START": False},
      "Hold": {"A": False, "B": False, "X": False, "Y": False, "Right": False, "Left": False, "Up": False, "Down": False,
        "Shoulder_L": False, "Shoulder_R": False, "Z": False, "SELECT": False, "START": False},
      "Release": {"A": False, "B": False, "X": False, "Y": False, "Right": False, "Left": False, "Up": False, "Down": False,
        "Shoulder_L": False, "Shoulder_R": False, "Z": False, "SELECT": False, "START": False}},

  2: {"Press": {"A": False, "B": False, "X": False, "Y": False, "Right": False, "Left": False, "Up": False, "Down": False,
        "Shoulder_L": False, "Shoulder_R": False, "Z": False, "SELECT": False, "START": False},
      "Hold": {"A": False, "B": False, "X": False, "Y": False, "Right": False, "Left": False, "Up": False, "Down": False,
        "Shoulder_L": False, "Shoulder_R": False, "Z": False, "SELECT": False, "START": False},
      "Release": {"A": False, "B": False, "X": False, "Y": False, "Right": False, "Left": False, "Up": False, "Down": False,
        "Shoulder_L": False, "Shoulder_R": False, "Z": False, "SELECT": False, "START": False}},

  3: {"Press": {"A": False, "B": False, "X": False, "Y": False, "Right": False, "Left": False, "Up": False, "Down": False,
        "Shoulder_L": False, "Shoulder_R": False, "Z": False, "SELECT": False, "START": False},
      "Hold": {"A": False, "B": False, "X": False, "Y": False, "Right": False, "Left": False, "Up": False, "Down": False,
        "Shoulder_L": False, "Shoulder_R": False, "Z": False, "SELECT": False, "START": False},
      "Release": {"A": False, "B": False, "X": False, "Y": False, "Right": False, "Left": False, "Up": False, "Down": False,
        "Shoulder_L": False, "Shoulder_R": False, "Z": False, "SELECT": False, "START": False}},

  4: {"Press": {"A": False, "B": False, "X": False, "Y": False, "Right": False, "Left": False, "Up": False, "Down": False,
        "Shoulder_L": False, "Shoulder_R": False, "Z": False, "SELECT": False, "START": False},
      "Hold": {"A": False, "B": False, "X": False, "Y": False, "Right": False, "Left": False, "Up": False, "Down": False,
        "Shoulder_L": False, "Shoulder_R": False, "Z": False, "SELECT": False, "START": False},
      "Release": {"A": False, "B": False, "X": False, "Y": False, "Right": False, "Left": False, "Up": False, "Down": False,
        "Shoulder_L": False, "Shoulder_R": False, "Z": False, "SELECT": False, "START": False}}}

def button_handler(main):
  global k_down, k_up, k_right, k_left, k_a, k_b, k_x, k_y, k_z, k_l, k_r, k_select, k_start, k_back
  k_back = False
  
  if ((main.gamestate == 1 and not main.editor_mode) or (main.gamestate == 10 and main.editor_mode)):
    for port in main.ports:
      controller_states[port.index]["Press"]["A"] = False
      controller_states[port.index]["Press"]["B"] = False
      controller_states[port.index]["Press"]["X"] = False
      controller_states[port.index]["Press"]["Y"] = False
      controller_states[port.index]["Press"]["Right"] = False
      controller_states[port.index]["Press"]["Left"] = False
      controller_states[port.index]["Press"]["Up"] = False
      controller_states[port.index]["Press"]["Down"] = False
      controller_states[port.index]["Press"]["Shoulder_L"] = False
      controller_states[port.index]["Press"]["Shoulder_R"] = False
      controller_states[port.index]["Press"]["Z"] = False
      controller_states[port.index]["Press"]["SELECT"] = False
      controller_states[port.index]["Press"]["START"] = False
      controller_states[port.index]["Release"]["A"] = False
      controller_states[port.index]["Release"]["B"] = False
      controller_states[port.index]["Release"]["X"] = False
      controller_states[port.index]["Release"]["Y"] = False
      controller_states[port.index]["Release"]["Right"] = False
      controller_states[port.index]["Release"]["Left"] = False
      controller_states[port.index]["Release"]["Up"] = False
      controller_states[port.index]["Release"]["Down"] = False
      controller_states[port.index]["Release"]["Shoulder_L"] = False
      controller_states[port.index]["Release"]["Shoulder_R"] = False
      controller_states[port.index]["Release"]["Z"] = False
      controller_states[port.index]["Release"]["SELECT"] = False
      controller_states[port.index]["Release"]["START"] = False
    for event in pygame.event.get():
      for port in main.ports:
        if event.type == JOYDEVICEADDED:
          joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
          #print("Current Controller Devices:", joysticks)
          #for joystick in joysticks: print(joystick.get_name())
        if event.type == JOYDEVICEREMOVED:
          joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
          #print("Current Controller Devices:", joysticks)
          #for joystick in joysticks: print(joystick.get_name(), joystick.get_power_level())
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: k_back = True
        if event.type == pygame.QUIT: main.quit()
        if port.device == "Default":
          if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN: controller_states[port.index]["Press"]["START"], controller_states[port.index]["Hold"]["START"] = True, True
            if event.key == pygame.K_e or event.key == pygame.K_z or event.key == pygame.K_SPACE or event.key == pygame.K_KP6: controller_states[port.index]["Press"]["A"], controller_states[port.index]["Hold"]["A"] = True, True
            if event.key == pygame.K_q or event.key == pygame.K_x or event.key == pygame.K_BACKSPACE or event.key == pygame.K_KP2: controller_states[port.index]["Press"]["B"], controller_states[port.index]["Hold"]["B"] = True, True
            if event.key == pygame.K_o or event.key == pygame.K_c or event.key == pygame.K_KP8: controller_states[port.index]["Press"]["X"], controller_states[port.index]["Hold"]["X"] = True, True
            if event.key == pygame.K_p or event.key == pygame.K_v or event.key == pygame.K_KP4: controller_states[port.index]["Press"]["Y"], controller_states[port.index]["Hold"]["Y"] = True, True
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d: controller_states[port.index]["Press"]["Right"], controller_states[port.index]["Hold"]["Right"] = True, True
            if event.key == pygame.K_LEFT or event.key == pygame.K_a: controller_states[port.index]["Press"]["Left"], controller_states[port.index]["Hold"]["Left"] = True, True
            if event.key == pygame.K_UP or event.key == pygame.K_w: controller_states[port.index]["Press"]["Up"], controller_states[port.index]["Hold"]["Up"] = True, True
            if event.key == pygame.K_DOWN or event.key == pygame.K_s: controller_states[port.index]["Press"]["Down"], controller_states[port.index]["Hold"]["Down"] = True, True
            if event.key == pygame.K_i: controller_states[port.index]["Press"]["SELECT"], controller_states[port.index]["Hold"]["SELECT"] = True, True
            if event.key == pygame.K_z or event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT: controller_states[port.index]["Press"]["Z"], controller_states[port.index]["Hold"]["Z"] = True, True
            if event.key == pygame.K_MINUS: controller_states[port.index]["Press"]["Shoulder_L"], controller_states[port.index]["Hold"]["Shoulder_L"] = True, True
            if event.key == pygame.K_EQUALS: controller_states[port.index]["Press"]["Shoulder_R"], controller_states[port.index]["Hold"]["Shoulder_R"] = True, True
          if event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN: controller_states[port.index]["Release"]["START"], controller_states[port.index]["Hold"]["START"] = True, False
            if event.key == pygame.K_e or event.key == pygame.K_z or event.key == pygame.K_SPACE or event.key == pygame.K_KP6: controller_states[port.index]["Release"]["A"], controller_states[port.index]["Hold"]["A"] = True, False
            if event.key == pygame.K_q or event.key == pygame.K_x or event.key == pygame.K_BACKSPACE or event.key == pygame.K_KP2: controller_states[port.index]["Release"]["B"], controller_states[port.index]["Hold"]["B"] = True, False
            if event.key == pygame.K_o or event.key == pygame.K_c or event.key == pygame.K_KP8: controller_states[port.index]["Release"]["X"], controller_states[port.index]["Hold"]["X"] = True, False
            if event.key == pygame.K_p or event.key == pygame.K_v or event.key == pygame.K_KP4: controller_states[port.index]["Release"]["Y"], controller_states[port.index]["Hold"]["Y"] = True, False
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d: controller_states[port.index]["Release"]["Right"], controller_states[port.index]["Hold"]["Right"] = True, False
            if event.key == pygame.K_LEFT or event.key == pygame.K_a: controller_states[port.index]["Release"]["Left"], controller_states[port.index]["Hold"]["Left"] = True, False
            if event.key == pygame.K_UP or event.key == pygame.K_w: controller_states[port.index]["Release"]["Up"], controller_states[port.index]["Hold"]["Up"] = True, False
            if event.key == pygame.K_DOWN or event.key == pygame.K_s: controller_states[port.index]["Release"]["Down"], controller_states[port.index]["Hold"]["Down"] = True, False
            if event.key == pygame.K_i: controller_states[port.index]["Release"]["SELECT"], controller_states[port.index]["Hold"]["SELECT"] = True, False
            if event.key == pygame.K_z or event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT: controller_states[port.index]["Release"]["Z"], controller_states[port.index]["Hold"]["Z"] = True, False
            if event.key == pygame.K_MINUS: controller_states[port.index]["Release"]["Shoulder_L"], controller_states[port.index]["Hold"]["Shoulder_L"] = True, False
            if event.key == pygame.K_EQUALS: controller_states[port.index]["Release"]["Shoulder_R"], controller_states[port.index]["Hold"]["Shoulder_R"] = True, False
            if event.key == pygame.K_ESCAPE: k_back = False
          if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: controller_states[port.index]["Press"]["A"], controller_states[port.index]["Hold"]["A"] = True, True
            if event.button == 3: controller_states[port.index]["Press"]["B"], controller_states[port.index]["Hold"]["B"] = True, True
          if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: controller_states[port.index]["Release"]["A"], controller_states[port.index]["Hold"]["A"] = True, False
            if event.button == 3: controller_states[port.index]["Release"]["B"], controller_states[port.index]["Hold"]["B"] = True, False
        elif port.device != None:
          if event.type == JOYBUTTONDOWN:
            if event.button == 0: controller_states[port.index]["Press"]["X"], controller_states[port.index]["Hold"]["X"] = True, True #x A
            if event.button == 1: controller_states[port.index]["Press"]["A"], controller_states[port.index]["Hold"]["A"] = True, True #o B
            if event.button == 2: controller_states[port.index]["Press"]["B"], controller_states[port.index]["Hold"]["B"] = True, True #□ X
            if event.button == 3: controller_states[port.index]["Press"]["Y"], controller_states[port.index]["Hold"]["Y"] = True, True #△ Y
            if event.button == 4: controller_states[port.index]["Press"]["Shoulder_L"], controller_states[port.index]["Hold"]["Shoulder_L"] = True, True #l
            if event.button == 5: controller_states[port.index]["Press"]["Shoulder_r"], controller_states[port.index]["Hold"]["Shoulder_R"] = True, True #r
            if event.button == 8: controller_states[port.index]["Press"]["SELECT"], controller_states[port.index]["Hold"]["SELECT"] = True, True #l
            if event.button == 9: controller_states[port.index]["Press"]["START"], controller_states[port.index]["Hold"]["START"] = True, True #r
          axis_values = [0, 0]
          if event.type == JOYAXISMOTION:
            if abs(event.value) > 0.1: axis_values[event.axis] = event.value
            controller_states[port.index]["Press"]["Up"] = axis_values[1] < -port.deadzone
            controller_states[port.index]["Press"]["Down"] = axis_values[1] > port.deadzone
            controller_states[port.index]["Press"]["Left"] = axis_values[0] < -port.deadzone
            controller_states[port.index]["Press"]["Right"] = axis_values[0] > port.deadzone
            controller_states[port.index]["Hold"]["Up"] = axis_values[1] < -port.deadzone
            controller_states[port.index]["Hold"]["Down"] = axis_values[1] > port.deadzone
            controller_states[port.index]["Hold"]["Left"] = axis_values[0] < -port.deadzone
            controller_states[port.index]["Hold"]["Right"] = axis_values[0] > port.deadzone
            controller_states[port.index]["Release"]["Up"] = axis_values[1] < -port.deadzone
            controller_states[port.index]["Release"]["Down"] = axis_values[1] > port.deadzone
            controller_states[port.index]["Release"]["Left"] = axis_values[0] < -port.deadzone
            controller_states[port.index]["Release"]["Right"] = axis_values[0] > port.deadzone
          if event.type == JOYBUTTONUP:
            if event.button == 0: controller_states[port.index]["Release"]["X"], controller_states[port.index]["Hold"]["X"] = True, False #x A
            if event.button == 1: controller_states[port.index]["Release"]["A"], controller_states[port.index]["Hold"]["A"] = True, False #o B
            if event.button == 2: controller_states[port.index]["Release"]["B"], controller_states[port.index]["Hold"]["B"] = True, False #□ X
            if event.button == 3: controller_states[port.index]["Release"]["Y"], controller_states[port.index]["Hold"]["Y"] = True, False #△ Y
            if event.button == 4: controller_states[port.index]["Release"]["Shoulder_L"], controller_states[port.index]["Hold"]["Shoulder_L"] = True, False #l
            if event.button == 5: controller_states[port.index]["Release"]["Shoulder_R"], controller_states[port.index]["Hold"]["Shoulder_R"] = True, False #r
            if event.button == 8: controller_states[port.index]["Release"]["SELECT"], controller_states[port.index]["Hold"]["SELECT"] = True, False #l
            if event.button == 9: controller_states[port.index]["Release"]["START"], controller_states[port.index]["Hold"]["START"] = True, False #r
    for port in main.ports:
      port.buttons["Press"]["a"] = controller_states[port.index]["Press"]["A"]
      port.buttons["Press"]["b"] = controller_states[port.index]["Press"]["B"]
      port.buttons["Press"]["x"] = controller_states[port.index]["Press"]["X"]
      port.buttons["Press"]["y"] = controller_states[port.index]["Press"]["Y"]
      port.buttons["Press"]["right"] = controller_states[port.index]["Press"]["Right"]
      port.buttons["Press"]["left"] = controller_states[port.index]["Press"]["Left"]
      port.buttons["Press"]["up"] = controller_states[port.index]["Press"]["Up"]
      port.buttons["Press"]["down"] = controller_states[port.index]["Press"]["Down"]
      port.buttons["Press"]["l"] = controller_states[port.index]["Press"]["Shoulder_L"]
      port.buttons["Press"]["r"]= controller_states[port.index]["Press"]["Shoulder_R"]
      port.buttons["Press"]["select"] = controller_states[port.index]["Press"]["SELECT"]
      port.buttons["Press"]["start"] = controller_states[port.index]["Press"]["START"]
      port.buttons["Hold"]["a"] = controller_states[port.index]["Hold"]["A"]
      port.buttons["Hold"]["b"] = controller_states[port.index]["Hold"]["B"]
      port.buttons["Hold"]["x"] = controller_states[port.index]["Hold"]["X"]
      port.buttons["Hold"]["y"] = controller_states[port.index]["Hold"]["Y"]
      port.buttons["Hold"]["right"] = controller_states[port.index]["Hold"]["Right"]
      port.buttons["Hold"]["left"] = controller_states[port.index]["Hold"]["Left"]
      port.buttons["Hold"]["up"] = controller_states[port.index]["Hold"]["Up"]
      port.buttons["Hold"]["down"] = controller_states[port.index]["Hold"]["Down"]
      port.buttons["Hold"]["l"] = controller_states[port.index]["Hold"]["Shoulder_L"]
      port.buttons["Hold"]["r"]= controller_states[port.index]["Hold"]["Shoulder_R"]
      port.buttons["Hold"]["select"] = controller_states[port.index]["Hold"]["SELECT"]
      port.buttons["Hold"]["start"] = controller_states[port.index]["Hold"]["START"]
      port.buttons["Release"]["a"] = controller_states[port.index]["Release"]["A"]
      port.buttons["Release"]["b"] = controller_states[port.index]["Release"]["B"]
      port.buttons["Release"]["x"] = controller_states[port.index]["Release"]["X"]
      port.buttons["Release"]["y"] = controller_states[port.index]["Release"]["Y"]
      port.buttons["Release"]["right"] = controller_states[port.index]["Release"]["Right"]
      port.buttons["Release"]["left"] = controller_states[port.index]["Release"]["Left"]
      port.buttons["Release"]["up"] = controller_states[port.index]["Release"]["Up"]
      port.buttons["Release"]["down"] = controller_states[port.index]["Release"]["Down"]
      port.buttons["Release"]["l"] = controller_states[port.index]["Release"]["Shoulder_L"]
      port.buttons["Release"]["r"]= controller_states[port.index]["Release"]["Shoulder_R"]
      port.buttons["Release"]["select"] = controller_states[port.index]["Release"]["SELECT"]
      port.buttons["Release"]["start"] = controller_states[port.index]["Release"]["START"]
  else:
    k_l, k_r, k_back, k_start, k_select = False, False, False, False, False
    if main.gamestate != 0 and main.gamestate != 7 and main.gamestate != 11 and main.gamestate != 24 and main.gamestate != 27: k_down, k_up, k_right, k_left = False, False, False, False
    if main.gamestate != 7 and main.gamestate != 11 and main.gamestate != 27:
      k_a, k_b, k_x = False, False, False
      #if main.gamestate != 24 and main.gamestate != 6 and main.gamestate != 16 and main.gamestate != 17: k_y = False
    for event in pygame.event.get():
      if event.type == pygame.QUIT: main.quit()
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN: k_start = True
        if event.key == pygame.K_e or event.key == pygame.K_z or event.key == pygame.K_SPACE or event.key == pygame.K_KP6: k_a = True
        if event.key == pygame.K_q or event.key == pygame.K_x or event.key == pygame.K_BACKSPACE or event.key == pygame.K_KP2: k_b = True
        if event.key == pygame.K_o or event.key == pygame.K_c or event.key == pygame.K_KP8: k_x = True
        if event.key == pygame.K_p or event.key == pygame.K_v or event.key == pygame.K_KP4: k_y = True
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d: k_right = True
        if event.key == pygame.K_LEFT or event.key == pygame.K_a: k_left = True
        if event.key == pygame.K_UP or event.key == pygame.K_w: k_up = True
        if event.key == pygame.K_DOWN or event.key == pygame.K_s: k_down = True
        if event.key == pygame.K_i: k_select = True
        if event.key == pygame.K_z or event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT: k_z = True
        if event.key == pygame.K_MINUS: k_l = True
        if event.key == pygame.K_EQUALS: k_r = True
        if event.key == pygame.K_ESCAPE:
          if main.gamestate == 0 and main.editor_mode:
            main.user_certainty = not main.user_certainty
            if main.user_certainty: main.error_sfx.play()
          else: k_back = True
      if event.type == pygame.KEYUP:
        if event.key == pygame.K_RETURN: k_start = False
        if event.key == pygame.K_e or event.key == pygame.K_z or event.key == pygame.K_SPACE or event.key == pygame.K_KP6: k_a = False
        if event.key == pygame.K_q or event.key == pygame.K_q or event.key == pygame.K_BACKSPACE or event.key == pygame.K_KP2: k_b = False
        if event.key == pygame.K_o or event.key == pygame.K_c or event.key == pygame.K_KP8: k_x = False
        if event.key == pygame.K_p or event.key == pygame.K_v or event.key == pygame.K_KP4: k_y = False
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d: k_right = False
        if event.key == pygame.K_LEFT or event.key == pygame.K_a: k_left = False
        if event.key == pygame.K_UP or event.key == pygame.K_w: k_up = False
        if event.key == pygame.K_DOWN or event.key == pygame.K_s: k_down = False
        if event.key == pygame.K_i: k_select = False
        if event.key == pygame.K_z or event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT: k_z = False
        if event.key == pygame.K_MINUS: k_l = False
        if event.key == pygame.K_EQUALS: k_r = False
        if event.key == pygame.K_ESCAPE: k_back = False
      if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1: k_a = True
        if event.button == 3: k_b = True
      if event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1: k_a = False
        if event.button == 3: k_b = False
      if event.type == JOYBUTTONDOWN:
        if event.button == 0: k_x = True #x A
        if event.button == 1: k_a = True #o B
        if event.button == 2: k_b = True #□ X
        if event.button == 3: k_y = True #△ Y
        if event.button == 4: k_l = True #l
        if event.button == 5: k_r = True #r
        if event.button == 8: k_select = True #l
        if event.button == 9: k_start = True #r
      axis_values = [0, 0, 0, 0]
      if event.type == JOYAXISMOTION:
        if abs(event.value) > 0.1: axis_values[event.axis] = event.value
        k_up = axis_values[1] < -0.7
        k_down = axis_values[1] > 0.7
        k_left = axis_values[0] < -0.7
        k_right = axis_values[0] > 0.7
      if event.type == JOYBUTTONUP:
        if event.button == 0: k_x = False #x A
        if event.button == 1: k_a = False #o B
        if event.button == 2: k_b = False #□ X
        if event.button == 3: k_y = False #△ Y
        if event.button == 4: k_l = False #l
        if event.button == 5: k_r = False #r
        if event.button == 8: k_select = False #l
        if event.button == 9: k_start = False #r
  return {"A": k_a, "B": k_b, "Y": k_y, "X": k_x, "Right": k_right, "Left": k_left, "Up": k_up, "Down": k_down, "Z": k_z, "L": k_l, "R": k_r, "Select": k_select, "Start": k_start, "Back": k_back}