import pygame, moderngl, random, psutil, platform, threading, pickle
from pygame.locals import *
from pygame._sdl2.video import Window, Renderer, Texture, Image
from pygame.sysfont import *
from Scripts.room import Room, Tile, Door, Background, Collectible_Type, Collectible, Entity_Type, Zone, Text, Layer, Camera, Cutscene
from Scripts.controller import *
from save_and_load import *
from Scripts.actor import *
from Scripts.ui import *
from Scripts.timers import Timer
from Scripts.settings import *
from Scripts.client import Client
from collections import defaultdict
from array import array
from time import time, sleep
from datetime import datetime
from ping3 import verbose_ping


#cpu = cpuinfo.get_cpu_info()['brand_raw']

cpu = platform.processor()
pf = platform.platform()
pf_system = platform.system()
architecture = platform.architecture()

#Init pygame
pygame.init()
pygame.mixer.init(44100, -16, 4, 2048)
pygame.joystick.init()

#Init display
screen = pygame.Surface(RESOLUTION)
display = pygame.Surface(RESOLUTION) # | pygame.FULLSCREEN
window = pygame.display.set_mode(RESOLUTION, flags = pygame.SCALED | pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.OPENGL | pygame.FULLSCREEN)# | pygame.FULLSCREEN

pygame.display.set_caption('Tunaditor ' + TUNADİTOR_VERSİON)
pygame.display.set_icon(pygame.image.load("Assets/editor/joypad.png").convert_alpha())
pygame.mouse.set_pos((WIDTH / 2, HEIGHT / 2))

#Init clock for FPS
clock = pygame.time.Clock()

#OpenGL commands
ctx = moderngl.create_context()
vertices = ctx.buffer(data=array("f", [
    # Positions         # Texture Coords
    -0.75,  1.0, 0.0,    0.0, 0.0, # top left
     0.75,  1.0, 0.0,    1.0, 0.0, # top right
    -0.75, -1.0, 0.0,    0.0, 1.0, # bottom left
     0.75, -1.0, 0.0,    1.0, 1.0, # bottom right
]))

shader_buffer = (vertices, "3f 2f", "position", "texCoords")
program = ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)
render_object = ctx.vertex_array(program, [shader_buffer])

#Built-in sounds
button_sfx = pygame.mixer.Sound("Sounds/editor/button.wav")
selection_sfx = pygame.mixer.Sound("Sounds/editor/select.wav")
scrollup_sfx = pygame.mixer.Sound("Sounds/editor/scroll_up.wav")
scrolldown_sfx = pygame.mixer.Sound("Sounds/editor/scroll_down.wav")
increase_by_sfx = pygame.mixer.Sound("Sounds/editor/increase_by.wav")
decrease_by_sfx = pygame.mixer.Sound("Sounds/editor/decrease_by.wav")
switch_page_sfx = pygame.mixer.Sound("Sounds/editor/switch_page.wav")
switch_key_sfx = pygame.mixer.Sound("Sounds/editor/switch_key.wav")
error_sfx = pygame.mixer.Sound("Sounds/editor/error.wav")

#Init font sizes
fonttiny = pygame.Font(None, 12)
fontsmaller2 = pygame.Font(None, 15)
fontsmaller = pygame.Font(None, 16)
fontlittle = pygame.Font(None, 20)
fontsmall = pygame.Font(None, 24)
fontmedium = pygame.Font(None, 30)
fontbig = pygame.Font(None, 35)

fontmediumnone = pygame.Font(None, 30)

kfont = pygame.Font(None, 30)

launcherfonttiny = pygame.font.SysFont("MS Gothic", 12)
launcherfontsmaller = pygame.font.SysFont("MS Gothic", 16)
launcherfontlittle = pygame.font.SysFont("MS Gothic", 20)
launcherfontsmall = pygame.font.SysFont("MS Gothic", 24)
launcherfontmedium = pygame.font.SysFont("MS Gothic", 30)


config = {"Language": "EN", "Color Swizzle": "BGRA", "Render Filter": "Linear", "Mode": "Pygame", "Account": {"username": "", "password": ""}}


with open("config.json", "r") as file: config = json.load(file)


#Watch stream
#oh quick
#it loads 'cuz there should be errors
#Ye
#Well
#We can have tile 0 say the steel tile with no terrain upper, and we can have a list of it's borders
#I'm so confused but let me sketch something like it in ms paint

#Init custom cursors
pygame.mouse.set_visible(False)

lg = config["Language"]

cursor_surf = pygame.image.load("Assets/editor/cursor.png").convert_alpha()
cursor2_surf = pygame.image.load("Assets/editor/cursor flip.png").convert_alpha()
paused_surf = pygame.Surface(RESOLUTION)
joypad_surf = pygame.image.load("Assets/editor/joypad.png").convert_alpha()
display_surf = pygame.image.load("Assets/editor/display for ui.png").convert_alpha()
png_surf = pygame.image.load("Assets/editor/png.png").convert_alpha()
stop_playtesting_surf = pygame.transform.scale2x(pygame.image.load("Assets/editor/stop.png").convert_alpha())
stop_playtesting_surf.set_alpha(175)
paused_surf.fill((0, 0, 40))
paused_surf.set_alpha(150)

cutscene_margin = 148








#Functions
def render_grid():
  ts = main.tiles_size
  if k_z: ts = 1
  for i in range((main.height * 25) // main.tiles_size):
    pygame.draw.line(screen, "Dark Grey", (0, (i*main.tiles_size) - main.camera.scroll[1]), (800, (i*main.tiles_size) - main.camera.scroll[1]))
    if i == 0: pygame.draw.line(screen, "Red", (0, (i*main.tiles_size) - main.camera.scroll[1]), (800, (i*main.tiles_size) - main.camera.scroll[1]))
    elif i % (main.height / main.tiles_size) == 0: pygame.draw.line(screen, "Blue", (0, (i*main.tiles_size) - main.camera.scroll[1]), (800, (i*main.tiles_size) - main.camera.scroll[1]), 1); screen.blit(fontsmaller.render(str(round(i*ts)), True, "White"), (10, (i*main.tiles_size) - main.camera.scroll[1]))
    elif i % 2 == 0 or ts != 1: screen.blit(fonttiny.render(str(round(i*ts)), True, "Dark Gray"), (2, (i*main.tiles_size) - main.camera.scroll[1]))
  for i in range((main.width * 25) // main.tiles_size): #!!!! Hey, why so many conditions
    pygame.draw.line(screen, "Dark Grey", ((i*main.tiles_size) - main.camera.scroll[0], 0), ((i*main.tiles_size) - main.camera.scroll[0], 600))
    if i == 0: pygame.draw.line(screen, "Red", ((i*main.tiles_size) - main.camera.scroll[0], 0), ((i*main.tiles_size) - main.camera.scroll[0], 600))
    elif i % (main.width / main.tiles_size) == 0: pygame.draw.line(screen, "Blue", ((i*main.tiles_size) - main.camera.scroll[0], 0), ((i*main.tiles_size) - (main.camera.scroll[0] - 2), 600), 1); screen.blit(fontsmaller.render(str(round(i*ts)), True, "White"), ((i*main.tiles_size) - main.camera.scroll[0], 125))
    elif i % 2 == 0 or ts != 1: screen.blit(fonttiny.render(str(round(i*ts)), True, "Dark Gray"), ((i*main.tiles_size) - (main.camera.scroll[0] - 2), 115))
  pygame.draw.line(screen, "Green", ((main.rooms[main.selected_room].borders["right"]) - main.camera.scroll[0], 0), ((main.rooms[main.selected_room].borders["right"]) - main.camera.scroll[0], 600))
  pygame.draw.line(screen, "Yellow", ((main.rooms[main.selected_room].borders["left"]) - main.camera.scroll[0], 0), ((main.rooms[main.selected_room].borders["left"]) - main.camera.scroll[0], 600))
  pygame.draw.line(screen, "Yellow", (0, (main.rooms[main.selected_room].borders["top"]) - main.camera.scroll[1]), (800, (main.rooms[main.selected_room].borders["top"]) - main.camera.scroll[1]))
  pygame.draw.line(screen, "Green", (0, (main.rooms[main.selected_room].borders["bottom"]) - main.camera.scroll[1]), (800, (main.rooms[main.selected_room].borders["bottom"]) - main.camera.scroll[1]))
  if main.width % main.tiles_size != 0 or main.height % main.tiles_size != 0: screen.blit(fontsmaller.render(l[lg]["Display Resolution and Tile Size do not Match Up!"], True, "Red"), (2, HEIGHT - 14))


#Go to state of the editor
def go_to(game_state): global k_a; k_a = False; main.gamestate = game_state; main.user_certainty = False; main.current_room = main.selected_room; main.on_page = main.on_page * int(game_state != 44); main.saves = os.listdir("Saves/games/"); main.frame_timer.reset(); main.playback_on = False; main.playtest_on = False
def go_to_main(none): global k_a; k_a = False; main.gamestate = 0; main.user_certainty = False; main.current_room = main.selected_room; main.on_page = 0
def go_to_rgs(none): global k_a; k_a = False; main.gamestate = main.remember_gs; main.user_certainty = False; main.current_room = main.selected_room

#Quit game
def save_quit(none): save_game_file(None)
def quit_without_save(none): main.editor_mode = False; main.user_certainty = False; main.reset("")
def quit(none): main.quit()

def set_page(page):
  main.on_page = page
  # This was actually so that when you press profile, it shows you a "you're not logged in" page #
  if (main.on_page == 13 or main.on_page == 14 or main.on_page == 17) and not main.client_instance.online: main.on_page = 24
  if (main.on_page == 13 or main.on_page == 14) and not main.client_instance.logged: #Yeah but let's keep note of it
    main.on_page = 25

  #if main.on_page == 13:  #I see so we must get this back right #k
  #  room_name = main.join_text_username #Follow me rq 
  #  #??
  #  main.client.portal.packet["MESSAGE"] = main.client.user_data["user"]
  #  main.client.portal.packet["SUCCESS"] = True
  #  main.client.portal.packet["TYPE"] = "LOBBYINFO"
  #  main.client.portal.send_data(main.client.client, main.client.portal.packet, "OBJECT")
  #  #recv_lobby = main.client.portal.recv_data(main.client.client, "OBJECT")
  #  
  #  if main.client.portal.temporary_packet["SUCCESS"]:
  #    main.set_display_text("Room created successfully")
  #    main.room_host = main.client.portal.temporary_packet["MESSAGE"]["name"] #this should be {"Kaan": {}}
  #    main.room_players = main.client.portal.temporary_packet["MESSAGE"]["users"] #okay let's see apparently it wasn't even setting it as a key
#
  #  else:#Hello
  #    main.set_display_text("Room wasn't created")

def join_game_room(none):
  main.on_page = 13 # But not the funct ion themselves that will raise error, just empty the functions
  try: #i see
    main.set_display_text("Joined room")
    main.client.portal.packet["MESSAGE"] = [main.join_text_username, main.client.username]
    main.client.portal.packet["SUCCESS"] = False
    main.client.portal.packet["TYPE"] = "LOBBYJOIN"
    main.client.portal.send_data(main.client.client, main.client.portal.packet, "OBJECT")
  except:
    main.set_display_text("Room doesn't exist")
    main.on_page = 14
#this is where the client should send the join request yes
#I gotta do something at lobby.py
#I see
def retry_server_link(none):
  main.client_instance = Client()
  if main.client_instance.online: console.log("Reconnect success.", "Green"); main.set_display_text("Reconnect success!"); main.on_page = 0
  else: console.log("Reconnect failed.", "Red"); main.set_display_text("Reconnect failed.")


def delete_game_room(none):
  pass


def confirm_account(none):
  main.rename_text_username
  main.rename_text_password #Let's work with user id

  if main.client_instance.online:
      
  #Log in 
    if main.on_page == 18: 
      cred = {}
      pack = {}
      pack["id"] = "login"
      pack["msg"] = {"user_name": main.rename_text_username, "password": main.rename_text_password}
      main.client_instance.s.send(pickle.dumps(pack)) #so we send our cred here
      

    #Register
    if main.on_page == 21:
      cred = {}
      pack = {}
      #user_data = input("Please enter username:")
      #pass_data = input("Please enter password:") #we need the text field out put here instead of these
      cred["user_name"] =  main.rename_text_username
      cred["password"] = main.rename_text_password#? follow me
      pack["id"] = "signup" 
      pack["msg"] = cred
      main.client_instance.s.send(pickle.dumps(pack))
      #Wait, where was the code that was responsible to connect to server?

# To add log out button
#    for user in server.users:
#      if user.username == main.rename_text_username: main.logged_in_account = user
#    main.on_page = 0
#    main.launcher_buttons[0] = [button for button in main.launcher_buttons[0] if button.button_type != "Account Entry"]
#    main.launcher_buttons[0].append(Button(370, HEIGHT - 70, 100, 32, "", "Log out", exit_account, page=17, font=launcherfontsmall, with_sound=False, shift_x_hitbox=16))



#Well the server has to tell the client that come
#how?


# def confirm_account(none):
#   success = False

#   Log in
#   if main.on_page == 18:
#     if not main.rename_text_username in [user.username for user in server.users]:
#       main.set_display_text("Username and password don't match.")
#     else:
#       matches = False
#       for user in server.users:
#         if user.username == main.rename_text_username:
#           if user.password == main.rename_text_password: matches = True
#       if matches: main.set_display_text("Logged into account."); success = True
#       else: main.set_display_text("Username and password don't match.")
  
#   #Register
#   elif main.on_page == 21:
#     if main.rename_text_username in [user.username for user in server.users]: main.set_display_text("This username is already taken!")
#     else:
#       if main.rename_text_username:
#         if main.rename_text_password:
#           main.set_display_text("Created account.")
#           server.users.append(User(main.rename_text_username, main.rename_text_password, main))
#           success = True
#           #This is where we created an account successfully
#         else: main.set_display_text("Enter a password!")
#       else: main.set_display_text("Enter a username!")

#   if success:
#     for user in server.users:
#       if user.username == main.rename_text_username: main.logged_in_account = user
#     main.on_page = 0
#     main.launcher_buttons[0] = [button for button in main.launcher_buttons[0] if button.button_type != "Account Entry"]
#     main.launcher_buttons[0].append(Button(370, HEIGHT - 70, 100, 32, "", "Log out", exit_account, page=17, font=launcherfontsmall, with_sound=False, shift_x_hitbox=16))

def exit_account(none):
  main.client_instance.logged = False; main.set_display_text("Logged out"); main.on_page = 0; main.client_instance.username = ""; main.client_instance.password = ""
  for button in (button for button in main.launcher_buttons[0] if button.page == 17): main.launcher_buttons[0].remove(button)
  if not main.client_instance.logged:
    for x, button in enumerate([("Log into Account", 18), ("Create Account", 21)]):
      main.launcher_buttons[0].append(Button(30 + (x * 265), 280, launcherfontlittle.render(button[0], "Black", False).get_width() + 5, 26, "", button[0], set_page, target=button[1], font=launcherfontlittle, page=17, button_type="Account Entry", with_sound=False, shift_x_hitbox=16, shift_y_hitbox=-2))

def refresh_games(none):
  main.saves = os.listdir("Saves/games/")
  for button in [button for button in main.launcher_buttons[main.gamestate] if button.page == 6 and button.button_type == "Game"]: main.launcher_buttons[0].remove(button)
  for x, button in enumerate(main.saves):
    main.launcher_buttons[0].append(Button(40, 100 + (32 * x), WIDTH - 110, 22, "", button, load_game_from_launcher, target=[button, main], font=launcherfontlittle, page=6, with_sound=False, shift_x_hitbox=16, hide_above_y=100, hide_below_y=385, button_type="Game"))

def load_additional_packages(none): main.load_additional_packages = not main.load_additional_packages

def load_game_from_launcher(save:list):
  global FPS
  if os.path.isdir("Saves/games/" + save[0]): main.active_directory = "Saves/games/" + save[0] + "/"; load_game(save[0] + "/" + save[0], save[1], False)
  else: main.active_directory = ""; load_game(save[0], save[1], False)
  playtest(None); main.gamestate = 1; FPS = main.fps; main.camera.scroll = [0, 0]; main.playback_on = False; main.current_room = 0
  console.log("Starting game: " + main.game_name); instructions = ""
  for cs in main.rooms[main.current_room].cutscenes:
    if "Start of Room" in cs.conditions and not main.players: main.play_cutscene(cs); break
  restart_game(None)
  for instruction in [instruction for instruction in pygame.system.get_cpu_instruction_sets() if pygame.system.get_cpu_instruction_sets()[instruction]]: instructions += instruction + " "
  if main.publisher: main.display_text = "\n\n" + main.game_name + "\nby " + main.publisher + "\n\n  CPU Instructions:\n" + instructions
  else: main.display_text = "\n\n" + main.game_name + "\n\n  CPU Instructions:\n" + instructions
def save_game_state_from_launcher(save:list):
  if main.game_name: main.display_text = "\n\nSaving data..."; main.display_text_timer.reset(); run(); save_game_state(save[0], save[1], save[2]); main.display_text = "\n\nSaved data for game " + main.game_name + " in slot " + str(save[2]); run(); console.log("Saving data for game " + main.game_name + " in slot " + str(save[2]))
  else: main.display_text = "\n\nYou haven't loaded a game yet."; main.display_text_timer.reset()
def load_game_state_from_launcher(save:list):
  restart_game(None)
  try: main.display_text = "\n\nLoading data..."; main.display_text_timer.reset(); run(); load_game_state(save[0], save[1], save[2]); main.display_text = "\n\nLoaded data for game " + main.game_name + " from slot " + str(save[2]); run(); console.log("Loading data for game " + main.game_name + " in slot " + str(save[2]))
  except FileNotFoundError:
    if main.game_name: main.display_text = "\n\nCannot load save, save slot is missing!"; main.display_text_timer.reset()
    else: main.display_text = "\n\nCannot load slot data because there is no game card\ninserted."; main.display_text_timer.reset()
  except Exception as e: main.display_text = f"\n\nThe data you are looking for was corrupted.\n{e}"; main.display_text_timer.reset()
def restart_game(none):
  global FPS; main.current_room = 0; main.selected_room = 0; stop_playtest(None); playtest(None); main.gamestate = 1; FPS = main.fps; main.camera.scroll = [0, 0]; main.playback_on = False; main.game_paused = False; main.display_text = ""; main.on_page = 0
  for cs in main.rooms[main.current_room].cutscenes:
    if "Start of Room" in cs.conditions and not main.players: main.play_cutscene(cs); break
def eject(none): main.reset("")
def switch_to_editor(none): main.editor_mode = not main.editor_mode; stop_playtest(None); main.game_paused = False; main.display_text = ""

def select_player_index(player_index): main.selected_player = player_index
def plug_gamepad(gamepad): main.ports[main.selected_player].device = gamepad
def change_deadzone(by):
  main.ports[main.selected_player].deadzone += by
  if main.ports[main.selected_player].deadzone > 1.0: main.ports[main.selected_player].deadzone = 1.0
  if main.ports[main.selected_player].deadzone < 0.0: main.ports[main.selected_player].deadzone = 0.0
def toggle_rumble(none): main.ports[main.selected_player].rumble = not main.ports[main.selected_player].rumble
def refresh_joysticks(none):
  main.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
  for button in [button for button in main.launcher_buttons[0] if button.button_type == "Device"]: main.launcher_buttons[0].remove(button)
  for x, joystick in enumerate([None, "Default"] + main.joysticks):
    if joystick == None: main.launcher_buttons[0].append(Button(16, 190 + (24 * x), launcherfontsmaller.render("None", False, "White").get_width(), 20, "", None, plug_gamepad, target=joystick, font=launcherfontsmaller, page=9, button_type="Device", with_sound=False, shift_x_hitbox=16))
    elif joystick == "Default": main.launcher_buttons[0].append(Button(16, 190 + (24 * x), launcherfontsmaller.render("Default", False, "White").get_width(), 20, "", "Default", plug_gamepad, target=joystick, font=launcherfontsmaller, page=9, button_type="Device", with_sound=False, shift_x_hitbox=16))
    else: main.launcher_buttons[0].append(Button(16, 190 + (24 * x), launcherfontsmaller.render(joystick.get_name(), False, "White").get_width(), 20, "", joystick.get_name(), plug_gamepad, target=joystick, font=launcherfontsmaller, page=9, button_type="Device", with_sound=False, shift_x_hitbox=16))
def select_render_filter(filter): main.render_filter = filter
def select_color_swizzle(color_mode): main.color_swizzle = color_mode[::-1]
def open_console(none): console.hidden = not console.hidden; main.on_page = 0
def toggle_debug(none):
  global FPS
  if main.game_name: main.debug = not main.debug; console.log("Debug mode set to " + {True: "on", False: "off"}[main.debug]); main.on_page = 0
  else: main.set_display_text("No game card inserted!"); main.on_page = 0; FPS = main.fps
def set_language(language):
  global lg, fonttiny, fontsmaller2, fontsmaller, fontlittle, fontsmall, fontmedium, fontbig, launcherfonttiny, launcherfontsmaller, launcherfontlittle, launcherfontsmall, launcherfontmedium
  lg = language

  if lg != "JP" and lg != "AR":
    launcherfonttiny = pygame.font.SysFont("MS Gothic", 12)
    launcherfontsmaller = pygame.font.SysFont("MS Gothic", 16)
    launcherfontlittle = pygame.font.SysFont("MS Gothic", 20)
    launcherfontsmall = pygame.font.SysFont("MS Gothic", 24)
    launcherfontmedium = pygame.font.SysFont("MS Gothic", 30)
    fonttiny = pygame.Font(None, 12)
    fontsmaller2 = pygame.Font(None, 15)
    fontsmaller = pygame.Font(None, 16)
    fontlittle = pygame.Font(None, 20)
    fontsmall = pygame.Font(None, 24)
    fontmedium = pygame.Font(None, 30)
    fontbig = pygame.Font(None, 35)
  elif lg == "JP":
    fonttiny = pygame.font.SysFont("Bizud Gothic", round(12 / 1.3))
    fontsmaller2 = pygame.font.SysFont("Bizud Gothic", round(15 / 1.3))
    fontsmaller = pygame.font.SysFont("Bizud Gothic", round(16 / 1.3))
    fontlittle = pygame.font.SysFont("Bizud Gothic", round(20 / 1.3))
    fontsmall = pygame.font.SysFont("Bizud Gothic", round(24 / 1.3))
    fontmedium = pygame.font.SysFont("Bizud Gothic", round(30 / 1.7))
    fontbig = pygame.font.SysFont("Bizud Gothic", round(35 / 2))
  elif lg == "AR":
    launcherfonttiny = pygame.font.SysFont("Dubai Regular", 11)
    launcherfontsmaller = pygame.font.SysFont("Dubai Regular", 15)
    launcherfontlittle = pygame.font.SysFont("Dubai Regular", 18)
    launcherfontsmall = pygame.font.SysFont("Dubai Regular", 22)
    launcherfontmedium = pygame.font.SysFont("Dubai Regular", 28)
    fonttiny = pygame.font.SysFont("Segoe UI Semilight", round(12 / 1.3))
    fontsmaller2 = pygame.font.SysFont("Segoe UI Semilight", round(15 / 1.3))
    fontsmaller = pygame.font.SysFont("Segoe UI Semilight", round(16 / 1.3))
    fontlittle = pygame.font.SysFont("Segoe UI Semilight", round(20 / 1.3))
    fontsmall = pygame.font.SysFont("Segoe UI Semilight", round(24 / 1.3))
    fontmedium = pygame.font.SysFont("Segoe UI Semilight", round(30 / 1.7))
    fontbig = pygame.font.SysFont("Segoe UI Semilight", round(35 / 2))
    fonttiny.set_script("Arab")
    fontsmaller2.set_script("Arab")
    fontsmaller.set_script("Arab")
    fontlittle.set_script("Arab")
    fontsmall.set_script("Arab")
    fontmedium.set_script("Arab")
    fontbig.set_script("Arab")
    launcherfonttiny.set_script("Arab")
    launcherfontsmaller.set_script("Arab")
    launcherfontlittle.set_script("Arab")
    launcherfontsmall.set_script("Arab")
    launcherfontmedium.set_script("Arab")
    fonttiny.set_direction(pygame.DIRECTION_RTL)
    fontsmaller2.set_direction(pygame.DIRECTION_RTL)
    fontsmaller.set_direction(pygame.DIRECTION_RTL)
    fontlittle.set_direction(pygame.DIRECTION_RTL)
    fontsmall.set_direction(pygame.DIRECTION_RTL)
    fontmedium.set_direction(pygame.DIRECTION_RTL)
    fontbig.set_direction(pygame.DIRECTION_RTL)
    launcherfonttiny.set_direction(pygame.DIRECTION_RTL)
    launcherfontsmaller.set_direction(pygame.DIRECTION_RTL)
    launcherfontlittle.set_direction(pygame.DIRECTION_RTL)
    launcherfontsmall.set_direction(pygame.DIRECTION_RTL)
    launcherfontmedium.set_direction(pygame.DIRECTION_RTL)
  
  main.refresh_buttons()

def add_letter_on_username(letter): main.rename_text_username = str(main.rename_text_username); main.rename_text_username += letter
def remove_letter_on_username(none): main.rename_text_username = str(main.rename_text_username)[:-1]
def add_letter_on_password(letter): main.rename_text_password = str(main.rename_text_password); main.rename_text_password += letter
def remove_letter_on_password(none): main.rename_text_password = str(main.rename_text_password)[:-1]

def add_letter_on_create_username(letter): main.rename_text_username = str(main.rename_text_username); main.rename_text_username += letter
def remove_letter_on_create_username(none): main.rename_text_username = str(main.rename_text_username)[:-1]
def add_letter_on_create_password(letter): main.rename_text_password = str(main.rename_text_password); main.rename_text_password += letter
def remove_letter_on_create_password(none): main.rename_text_password = str(main.rename_text_password)[:-1]

def add_letter_on_join_username(letter): main.join_text_username = str(main.join_text_username); main.join_text_username += letter
def remove_letter_on_join_username(none): main.join_text_username = str(main.join_text_username)[:-1]

#İ
# Room Editor
#Add object in the game
def add_object(none): main.gamestate = 1
#Delete object in the game
def delete_object(none):
  try: 
    if   isinstance(main.selected_object, Player)      : main.players.remove(main.selected_object); main.selected_object = None
    elif isinstance(main.selected_object, Door)        : main.rooms[main.selected_room].doors.remove(main.selected_object); main.selected_object = None
    elif isinstance(main.selected_object, Tile)        : main.rooms[main.selected_room].layers[0].tiles.remove(main.selected_object); main.selected_object = None
    elif isinstance(main.selected_object, Collectible) : main.rooms[main.selected_room].layers[0].collectibles.remove(main.selected_object); main.selected_object = None
    elif isinstance(main.selected_object, Entity)      : main.rooms[main.selected_room].layers[0].actors.remove(main.selected_object); main.selected_object = None
    elif isinstance(main.selected_object, Background)  : main.rooms[main.selected_room].backgrounds.remove(main.selected_object); main.selected_object = None
    elif isinstance(main.selected_object, Zone)        : main.rooms[main.selected_room].zones.remove(main.selected_object); main.selected_object = None
    elif isinstance(main.selected_object, Text)        : main.rooms[main.selected_room].layers[main.selected_object.layer - 1].texts.remove(main.selected_object); main.selected_object = None
  except: main.selected_object = None
#Customize object in the game
def edit(none):
  try:
    if isinstance(main.selected_object, Player):
      main.gamestate = 19
      main.buttons[19].clear()
      if len(main.characters) > 21:
        for index, entity in enumerate(main.characters):
          try: pygame.image.load(main.active_directory + "Assets/characters/" + entity + "/idle/1.png"); main.buttons[19].append(Button(((WIDTH / 2) - 22) + ((index % 13) * 17), 65 + math.floor(index / 13) * 17, 16, 16, entity, main.active_directory + "Assets/characters/" + entity + "/idle/1.png", select_player, entity, button_type="Character"))
          except: main.buttons[19].append(Button(((WIDTH / 2) - 22) + ((index % 13) * 17), 65 + math.floor(index / 13) * 17, 16, 16, entity, main.active_directory + "Assets/characters/" + entity + "/down/idle/1.png", select_player, entity, button_type="Character"))
      else:
        for index, entity in enumerate(main.characters):
          try: pygame.image.load(main.active_directory + "Assets/characters/" + entity + "/idle/1.png"); main.buttons[19].append(Button(((WIDTH / 2) - 24) + ((index % 7) * 33), 65 + math.floor(index / 7) * 33, 32, 32, entity, main.active_directory + "Assets/characters/" + entity + "/idle/1.png", select_player, entity, button_type="Character"))
          except: main.buttons[19].append(Button(((WIDTH / 2) - 24) + ((index % 7) * 33), 65 + math.floor(index / 7) * 33, 32, 32, entity, main.active_directory + "Assets/characters/" + entity + "/down/idle/1.png", select_player, entity, button_type="Character"))
      
      # temp = [select_sfx6, select_sfx5, select_sfx4, select_sfx3, select_sfx2, select_sfx]
      # for x in range(5): main.buttons[19].append(Button(64, HEIGHT - (62 + (x * 32)), 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", temp[x + 1], target=19))

      for x, button in enumerate([("Decrease X Spawn", "less", change_spawn_x_oe, -1), ("İncrease X Spawn", "more", change_spawn_x_oe, 1)]):
        main.buttons[19].append(Button(60 + (x * 132), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Y Spawn", "less", change_spawn_y_oe, -1), ("İncrease Y Spawn", "more", change_spawn_y_oe, 1)]):
        main.buttons[19].append(Button(60 + (x * 132), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Team", "less", change_team, -1), ("İncrease Team", "more", change_team, 1)]):
        main.buttons[19].append(Button(60 + (x * 132), 150, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      #154 | 150, 190
      main.buttons[19].append(Button(54, HEIGHT - 56, 32, 32, "Toggle Player In by Default", "Assets/editor/load.png", toggle_player_in))
      main.buttons[19].append(Button(88, HEIGHT - 56, 32, 32, "Hide Player if Out", "Assets/editor/hidden.png", hide_player_if_out))
      main.buttons[19].append(Button(WIDTH - 120, HEIGHT - 56, 32, 32, "Head Bump Cancels Y Momentum", "Assets/editor/cancel momentum.png", toggle_hump_head_cancel_y_momentum))
      main.buttons[19].append(Button(WIDTH - 86, HEIGHT - 56, 32, 32, "Accelerated Travel", "Assets/editor/x.png", toggle_accelerated_travel))
    if isinstance(main.selected_object, Tile):
      main.gamestate = 20
      main.buttons[20].clear()
      #if main.selected_object.is_animating:
      #  for x, button in enumerate([("Decrease Animation Speed", "less", -1), ("İncrease Animation Speed", "more", 1)]): main.buttons[20].append(Button(((WIDTH / 2) + 4) + (x * 148), 28, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_animation_speed, target=button[2]))
      for x, button in enumerate([("Decrease X", "less", change_tile_x, -1), ("İncrease X", "more", change_tile_x, 1)]):
        main.buttons[20].append(Button(60 + (x * 132), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Y", "less", change_tile_y, -1), ("İncrease Y", "more", change_tile_y, 1)]):
        main.buttons[20].append(Button(60 + (x * 132), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease X Speed", "less", change_speed_x_oe, -0.25), ("İncrease X Speed", "more", change_speed_x_oe, 0.25)]):
        main.buttons[20].append(Button(60 + (x * 132), 150, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Y Speed", "less", change_speed_y_oe, -0.25), ("İncrease Y Speed", "more", change_speed_y_oe, 0.25)]):
        main.buttons[20].append(Button(60 + (x * 132), 190, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Chain Speed", "less", change_tile_chain_speed, -1), ("İncrease Chain Speed", "more", change_tile_chain_speed, 1)]):
        main.buttons[20].append(Button(60 + (x * 132), 230, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for y, button in enumerate([("Set Only Breakable", "tiles", change_tile_obc), ("Toggle Solid", "solid", change_tile_solid), ("Toggle Flat", "flat", change_tile_flat), ("Toggle Slippery", "ice", change_tile_slippery)]):
        main.buttons[20].append(Button(60, 270 + (y * 34), 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
      main.buttons[20].append(Button(226, 70, 32, 32, "Zones Can Set Speed", "Assets/editor/arrows.png", change_can_be_moved_by_zones))
      main.buttons[20].append(Button(226, 110, 32, 32, "Zones Can Set Rotation", "Assets/editor/repeat.png", change_can_be_rotated_by_zones))
      #for x, button in enumerate([("Decrease HP", "less", change_tile_hp, -1), ("İncrease HP", "more", change_tile_hp, 1)]):
      #  main.buttons[20].append(Button(60 + (x * 132), 270, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      #main.buttons[20].append(Button(64, HEIGHT - 128, 32, 32, "Destroy İf Head Bump", "Assets/editor/bump on.png", change_tile_destroy_if_head_bump))
      #main.buttons[20].append(Button(116, HEIGHT - 128, 32, 32, "Destroy İf Stood On", "Assets/editor/stand on.png", change_tile_destroy_if_stood_on))
      #main.buttons[20].append(Button(64, HEIGHT - 94, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx, target=20))
      #main.buttons[20].append(Button(64, HEIGHT - 62, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx2, target=20))
      #for x, button in enumerate(main.destroy_anims):
      #  main.buttons[20].append(Button(WIDTH / 2, 75 + (x * 17), 128, 16, "Apply Tile Destruct Animation", button, change_tile_destroy_anim, target=button, font=fontsmall, button_type="Destroy Animation"))
    if isinstance(main.selected_object, Collectible):
      main.gamestate = 21
      main.buttons[21].clear()
      for index, cs in enumerate(main.rooms[main.selected_room].cutscenes):
        main.buttons[21].append(Button((WIDTH / 2) + 40, 62 + (index * 25), fontsmall.render(cs.name, True, "White").get_width(), 16, "Trigger this Cutscene", cs.name, select_cutscene_for_collectible, target=cs.name, button_type="Cutscene Name", font=fontsmall))
      main.buttons[21].append(Button(WIDTH - 86, HEIGHT - 60, 32, 32, "Set prices", "Assets/editor/tag.png", go_to_prices))
      for x, button in enumerate([("Decrease X", "less", change_tile_x, -1), ("İncrease X", "more", change_tile_x, 1)]):
        main.buttons[21].append(Button(60 + (x * 132), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Y", "less", change_tile_y, -1), ("İncrease Y", "more", change_tile_y, 1)]):
        main.buttons[21].append(Button(60 + (x * 132), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease X Speed", "less", change_speed_x_oe, -0.25), ("İncrease X Speed", "more", change_speed_x_oe, 0.25)]):
        main.buttons[21].append(Button(60 + (x * 132), 150, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Y Speed", "less", change_speed_y_oe, -0.25), ("İncrease Y Speed", "more", change_speed_y_oe, 0.25)]):
        main.buttons[21].append(Button(60 + (x * 132), 190, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      main.buttons[21].append(Button(226, 70, 32, 32, "Zones Can Set Speed", "Assets/editor/arrows.png", change_can_be_moved_by_zones))
      main.buttons[21].append(Button(226, 110, 32, 32, "Zones Can Set Rotation", "Assets/editor/repeat.png", change_can_be_rotated_by_zones))
    if isinstance(main.selected_object, Entity):
      main.gamestate = 23
      main.buttons[23].clear()
      # main.buttons[23].append(Button(64, HEIGHT - 222, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx, target=23))
      # main.buttons[23].append(Button(64, HEIGHT - 190, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx2, target=23))
      # main.buttons[23].append(Button(64, HEIGHT - 158, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx3, target=23))
      # main.buttons[23].append(Button(64, HEIGHT - 126, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx4, target=23))
      # main.buttons[23].append(Button(64, HEIGHT - 94, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx5, target=23))
      # main.buttons[23].append(Button(64, HEIGHT - 62, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx6, target=23))
      #NOTED: These lines are commented out, they allow you to change the character of an entity, but loading the game up causes the game to be unable to find the entity type to the associated entity itself because of the differences of the character they inhibit
      #if len(main.characters) > 21:
      #  for index, entity in enumerate(main.characters): main.buttons[23].append(Button(((WIDTH / 2) - 22) + ((index % 13) * 17), 65 + math.floor(index / 13) * 17, 16, 16, entity, main.active_directory + "Assets/characters/" + entity + "/idle/1.png", select_player, entity, button_type="Character"))
      #else:
      #  for index, entity in enumerate(main.characters): main.buttons[23].append(Button(((WIDTH / 2) - 24) + ((index % 7) * 33), 65 + math.floor(index / 7) * 33, 32, 32, entity, main.active_directory + "Assets/characters/" + entity + "/idle/1.png", select_player, entity, button_type="Character"))
      main.buttons[23].append(Button(WIDTH - 86, HEIGHT - 56, 32, 32, "Manage Dialogues", "Assets/editor/details.png", manage_dialogues))
      main.buttons[23].append(Button(WIDTH - 120, HEIGHT - 56, 32, 32, "Manage Bossfight", "Assets/editor/bossfight.png", go_to, target=52))
      for index, button in enumerate(("right", "left", "up", "down", "static")): main.buttons[23].append(Button(WIDTH - 96, HEIGHT - (78 + (22 * index)), 48, 20, "Set Spawn Direction", button, set_entity_direction, button, button_type="Direction", font=fontlittle))
      for index in range(1, 5): main.buttons[23].append(Button(300 + (index * 34), 27, 32, 32, "Set Player Partner Target", f"Assets/editor/turn into {index}.png", set_entity_player_partner, index, button_type="Player Partner TO"))
      for index in range(1, 5): main.buttons[23].append(Button(300 + (index * 34), 61, 32, 32, "Set Player Partner Target", f"Assets/editor/turn into {index}.png", set_entity_player_partner, index, button_type="Player Partner SW"))
    if isinstance(main.selected_object, Background): main.gamestate = 18; main.selected_background = main.rooms[main.selected_room].backgrounds.index(main.selected_object)
    if isinstance(main.selected_object, Door): main.gamestate = 32
    if isinstance(main.selected_object, Zone):
      main.gamestate = 22
      main.buttons[22].clear()
      for x, button in enumerate([("Decrease X", "less", change_x, -1), ("İncrease X Speed", "more", change_x, 1)]):
        main.buttons[22].append(Button(60 + (x * 132), 60, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Y", "less", change_y, -1), ("İncrease Y Speed", "more", change_y, 1)]):
        main.buttons[22].append(Button(60 + (x * 132), 100, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Width", "less", change_zone_width, -1), ("İncrease Width", "more", change_zone_width, 1)]):
        main.buttons[22].append(Button(60 + (x * 132), 140, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Height", "less", change_zone_height, -1), ("İncrease Height", "more", change_zone_height, 1)]):
        main.buttons[22].append(Button(60 + (x * 132), 180, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Dim Sound", "dimmer sound", zone_dim_track, -0.1), ("Louden Sound", "dim sound", zone_dim_track, 0.1)]):
        main.buttons[22].append(Button(60 + (x * 132), 220, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for index, cs in enumerate(main.rooms[main.selected_room].cutscenes):
        main.buttons[22].append(Button((WIDTH / 2) - 10, 232 + (index * 20), fontsmall.render(cs.name, True, "White").get_width(), 16, "Trigger this Cutscene", cs.name, select_cutscene, target=cs.name, button_type="Cutscene Name", font=fontsmall))
      for x, button in enumerate([("Decrease X Speed for Tiles", "less", change_x_overlapping_tile_speed, -0.25), ("İncrease X Speed for Tiles", "more", change_x_overlapping_tile_speed, 0.25)]):
        main.buttons[22].append(Button(255 + (x * 164), 60, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Y Speed for Tiles", "less", change_y_overlapping_tile_speed, -0.25), ("İncrease Y Speed for Tiles", "more", change_y_overlapping_tile_speed, 0.25)]):
        main.buttons[22].append(Button(255 + (x * 164), 100, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Y Rotation for Tiles", "less", change_overlapping_tile_rotational_speed, -1), ("İncrease Y Rotation for Tiles", "more", change_overlapping_tile_rotational_speed, 1)]):
        main.buttons[22].append(Button(255 + (x * 164), 140, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      main.buttons[22].append(Button(255, 180, 32, 32, "Ease Movement", "Assets/editor/ease.png", zone_ease))
      for x, button in enumerate([(l[lg]["Decrease Gravity"], "less", -0.1), (l[lg]["İncrease Gravity"], "more", 0.1)]):
        main.buttons[22].append(Button(300 + (x * 128), 180, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_zone_gravity, target=button[2]))
      main.buttons[22].append(Button(64, HEIGHT - 196, 32, 32, "Elimination Zone", "Assets/editor/void.png", zone_void))
      main.buttons[22].append(Button(64, HEIGHT - 164, 32, 32, "Activate for Actors", "Assets/editor/dog.png", zone_entity_active))
      main.buttons[22].append(Button(64, HEIGHT - 132, 32, 32, "Toggle Multi-Active", "Assets/editor/multiactive.png", zone_multi_active))
      main.buttons[22].append(Button(64, HEIGHT - 94, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx, target=22))
      main.buttons[22].append(Button(64, HEIGHT - 62, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx2, target=22))
      for x, color in enumerate(basic_colors):
        main.buttons[22].append(Button((WIDTH - 134) + math.floor(x / 4) * 16, 360 + ((x % 4) * 16), 16, 16, color, "", zone_color, target=basic_colors[color], color=basic_colors[color], button_type="Zone Color"))
    if isinstance(main.selected_object, Text):
      main.gamestate = 43
      main.buttons[43].clear()
      for x, button in enumerate([("Decrease X", "less", change_text_x, -1), ("İncrease X", "more", change_text_x, 1)]):
        main.buttons[43].append(Button(60 + (x * 132), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Y", "less", change_text_y, -1), ("İncrease Y", "more", change_text_y, 1)]):
        main.buttons[43].append(Button(60 + (x * 132), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Font Size", "less", change_text_font_size, -1), ("İncrease Font Size", "more", change_text_font_size, 1)]):
        main.buttons[43].append(Button(60 + (x * 132), 150, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease X Scale", "less", change_text_x_scale, -1), ("İncrease X Scale", "more", change_text_x_scale, 1)]):
        main.buttons[43].append(Button(60 + (x * 132), 190, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Y Scale", "less", change_text_y_scale, -1), ("İncrease Y Scale", "more", change_text_y_scale, 1)]):
        main.buttons[43].append(Button(60 + (x * 132), 230, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Margin", "less", change_text_margin, -1), ("İncrease Margin", "more", change_text_margin, 1)]):
        main.buttons[43].append(Button(60 + (x * 132), 270, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Turn Counter-Clockwise", "ccw", change_text_rotation, 1), ("Turn Clockwise", "cw", change_text_rotation, -1)]):
        main.buttons[43].append(Button(60 + (x * 132), 310, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Decrease Opacity", "less", change_text_opacity, -5), ("İncrease Opacity", "more", change_text_opacity, +5)]):
        main.buttons[43].append(Button(60 + (x * 132), 350, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Closer Layer", "less", change_text_layer, -1), ("Further Layer", "more", change_text_layer, +1)]):
        main.buttons[43].append(Button(60 + (x * 132), 390, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Thin Outline", "less", change_text_outline_thickness, -1), ("Thick Outline", "more", change_text_outline_thickness, +1)]):
        main.buttons[43].append(Button(224 + (x * 132), 390, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
      for x, button in enumerate([("Set Text", "text", rename, main.selected_object), ("Set Font", "font", go_to, 44), ("Toggle Anti-Aliasing", "antialias", change_text_anti_alias, None), ("Toggle Strikethrough", "strikethrough", change_text_strikethrough, None), ("Toggle Underline", "underline", change_text_underline, None), ("Toggle İtalic", "italic", change_text_italic, None), ("Toggle Bold", "bold", change_text_bold, None), ("Paste Text Data", "paste text data", paste_text_data_to_text_object, None), ("Copy Text Data", "copy text data", copy_text_data, None)]):
        if button != None: main.buttons[43].append(Button(WIDTH - (86 + (x * 34)), 24, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], button[3], 43, "Text"))
      for x, button in enumerate([("Align Right", "align right", change_text_align, "Right"), ("Align Center", "align center", change_text_align, "Center"), ("Align Left", "align left", change_text_align, "Left"), ("Capitilize All", "all caps", set_text_capitalization, "All capitalize"), ("Decapitilize", "all decaps", set_text_capitalization, "All decapitalize"), ("Capitilize First", "first caps", set_text_capitalization, "First capitalize")]):
        main.buttons[43].append(Button(WIDTH - (86 + (x * 34)), 58, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], button[3]))
      for x, button in enumerate([("Set Direction: Bottom to Top", "dir btt", change_text_dir, "BTT"), ("Set Direction: Top to Bottom", "dir ttb", change_text_dir, "TTB"), ("Set Direction: Right to Left", "dir rtl", change_text_dir, "RTL"), ("Set Direction: Left to Right", "dir ltr", change_text_dir, "LTR"), ("Flip Y", "vertical", change_text_flipy, None), ("Flip X", "horizontal", change_text_flipx, None)]): # ("Toggle Scrolling with Camera", "scroll", change_text_ui_mode, None)
        main.buttons[43].append(Button(WIDTH - (86 + (x * 34)), 92, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], button[3]))
      for x, color in enumerate(colors):#298
        if color != "Transparent": main.buttons[43].append(Button((WIDTH - 282) + math.floor(x / 15) * 16, 130 + ((x % 15) * 16), 16, 16, "Text Color > " + color, "", set_text_color, target=colors[color], color=colors[color], button_type="Color"))
      for x, color in enumerate(colors):#216
        if color != "Transparent" and x < 60: main.buttons[43].append(Button((WIDTH - 200) + math.floor(x / 15) * 16, 130 + ((x % 15) * 16), 16, 16, "Outline Color > " + color, "", set_text_outline_color, target=colors[color], color=colors[color], button_type="OL Color"))
      for x, color in enumerate(colors):
        main.buttons[43].append(Button((WIDTH - 134) + math.floor(x / 15) * 16, 130 + ((x % 15) * 16), 16, 16, "Background Color > " + color, "", set_text_bg_color, target=colors[color], color=colors[color], button_type="BG Color"))
      main.buttons[43].append(Button(426, 392, 32, 32, "Set Text to Player Character", "Assets/editor/set bg to chr.png", set_bg_to_chr, target=18))
      main.buttons[43].append(Button(392, 392, 32, 32, "Edit Text Behaviors", "Assets/editor/guided.png", edit_text_behaviors, target=18))
  except: main.selected_object = None
# Access rooms
def room(none): main.gamestate = 3
def add_cutscene(none):
  if len(main.rooms[main.selected_room].cutscenes) < 9:
    that_cs = Cutscene("Cutscene" + str(len(main.rooms[main.selected_room].cutscenes) + 1), len(main.rooms[main.selected_room].cutscenes))
    main.rooms[main.selected_room].cutscenes.append(that_cs)
    for x, button in enumerate([(l[lg]["Edit Cutscene"] + " " + str(len(main.rooms[main.selected_room].cutscenes)), "cog", access_cutscene, that_cs), (l[lg]["Rename Cutscene"] + " " + str(len(main.rooms[main.selected_room].cutscenes)), "pencil", rename, that_cs), (l[lg]["Delete Cutscene"] + " " + str(len(main.rooms[main.selected_room].cutscenes)), "delete", delete_cutscene, that_cs)]):
      that_cs.buttons.append(Button((WIDTH - cutscene_margin) + 95 + (x * 17), 32, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", button[2], button[3], target_object="Cutscene"))
def access_layer(layer):
  main.selected_layer = layer - 1; main.gamestate = 7; main.selected_tile = ()
  for button in main.buttons[7]:
    if button.button_type == "Tile": main.buttons[7].remove(button)
  for button in main.buttons[7]:
    if button.button_type == "Tile": main.buttons[7].remove(button)
  for button in main.buttons[7]:
    if button.button_type == "Tile": main.buttons[7].remove(button)
  main.on_page = 1
  for index, tile in enumerate(main.tileset):
    if os.path.isdir(main.active_directory + f"Assets/tiles/" + tile):
      images = []
      image_paths = []
      for image in sorted(os.listdir(main.active_directory + f"Assets/tiles/" + tile), key=extract_number): images.append(pygame.image.load(main.active_directory + f"Assets/tiles/" + tile + "/" + image).convert_alpha()); image_paths.append(main.active_directory + f"Assets/tiles/" + tile + "/" + image)
      tup = (tile, images, index, tile); main.tiles.append(tup)
      main.buttons[7].append(Button(2 + ((resetint(index, 90) % 30) * 17), 25 + math.floor(resetint(index, 89) / 30) * 17, 16, 16, tile, image_paths, select_tile, tup, page=(index // 90) + 1, button_type="Tile", with_sound=False))
    else:
      tup = (tile, pygame.image.load(main.active_directory + "Assets/tiles/" + tile).convert_alpha(), index, tile); main.tiles.append(tup)
      main.buttons[7].append(Button(2 + ((resetint(index, 90) % 30) * 17), 25 + math.floor(resetint(index, 89) / 30) * 17, 16, 16, tile[:-4], main.active_directory + "Assets/tiles/" + tile, select_tile, tup, page=(index // 90) + 1, button_type="Tile", with_sound=False))
    main.page_amount = (index // 90) + 1
  #main.buttons[7].append(Button())
def background_options(bg):
  try: main.selected_background = bg - 1; main.gamestate = 18; main.selected_object = main.rooms[main.selected_room].backgrounds[main.selected_background]
  except: pass
def access_cutscene(cutscene): global k_a; k_a = False; main.selected_cutscene = main.rooms[main.selected_room].cutscenes.index(cutscene); main.gamestate = 24; main.selected_key = 0; main.frame_timer.reset(); main.playback_on = False; main.playtest_on = False
def save_game_file(none):
  #if len(main.players): mc = main.players[0].character + " game"
  #else: mc = "game"
  #files_in_path = len(find_files_with_prefix("Saves/games/", mc))
  #save_game(mc + " " + str(files_in_path + 1), main); main.saves = os.listdir("Saves/games/")
  main.on_page = 1
  main.gamestate = 4; main.remember_gs = 0
  main.rename_target = main.game_name
  main.rename_text = main.game_name
  main.target_object = "Title"; main.instance_target = "Title"
  main.text_cursor = len(main.rename_text)
def load_game_file(none):
  if os.path.isdir("Saves/games/" + main.saves[main.selected_itemy]): main.active_directory = "Saves/games/" + main.saves[main.selected_itemy] + "/"; load_game(main.saves[main.selected_itemy] + "/" + main.saves[main.selected_itemy], main)
  else: main.active_directory = ""; load_game(main.saves[main.selected_itemy], main)
  #load_all_chr(None)
def toggle_show_hide(none): main.selected_object.spawn_as_visible = not main.selected_object.spawn_as_visible

# Add Instance
def add_layer(none):
  if len(main.rooms[main.selected_room].layers) < 11: main.rooms[main.selected_room].layers.append(Layer("L" + str(len(main.rooms[main.selected_room].layers) + 1), main=main)); main.gamestate = 0; main.buttons[0].append(Button(1 + (33 * (len(main.rooms[main.selected_room].layers) - 1)), HEIGHT - 33, 32, 32, f"Access Layer {'L' + str(len(main.rooms[main.selected_room].layers))}", "", access_layer, len(main.rooms[main.selected_room].layers), button_type="Layer", room=main.selected_room))
def add_player(none):
  if main.character_types:
    if len(main.players) < 4:
      character = main.character_types["0"]["object"]
      that_player = Player(0, 0, character, main, main.ports[len(main.players)], index=len(main.players))
      main.players.append(that_player); main.gamestate = 0 #it's still a red square
def add_entity_type(none):
  main.gamestate = 12; main.selected_value = 0
  main.buttons[12].clear(); main.buttons[26].clear()
  width = 0; height = 0
  for behavior in main.behaviors:
    text = fontsmall.render(behavior + ",", True, "White")
    if width + 19 + text.get_width() > WIDTH - 90: height += 25; width = 0
    width += text.get_width() + 10
    main.buttons[12].append(Button(35 + width - text.get_width(), 220 + height, text.get_width() + 7, 25, l[lg]["Toggle Behavior"], behavior, select_behavior, target=behavior, target_gs=12, target_object="Behavior", text_color="White", font=fontsmall))
  for index, entity in enumerate(main.characters):
    try: pygame.image.load(main.active_directory + "Assets/characters/" + entity + "/idle/1.png"); that_one_entity = Actor(0, 0, 0, 0, entity, main); tup = (entity, that_one_entity.image, index); main.buttons[12].append(Button(59 + ((index % 12) * 33), 65 + math.floor(index / 12) * 33, 32, 32, entity, main.active_directory + "Assets/characters/" + entity + "/idle/1.png", select_tile, tup, button_type="Character")); del that_one_entity
    except: that_one_entity = Actor(0, 0, 0, 0, entity, main); tup = (entity, that_one_entity.image, index); main.buttons[12].append(Button(59 + ((index % 12) * 33), 65 + math.floor(index / 12) * 33, 32, 32, entity, main.active_directory + "Assets/characters/" + entity + "/down/idle/1.png", select_tile, tup, button_type="Character")); del that_one_entity
  main.buttons[12].append(Button(WIDTH - 90, HEIGHT - 60, 32, 32, l[lg]["Next Page"], "Assets/editor/next.png", go_to, 25))
  #Page 3
  for index, coin in enumerate(main.collectible_types): main.buttons[26].append(Button(53 + ((index % 24) * 17), 325 + math.floor(index / 24) * 17, 16, 16, coin.name, main.active_directory + "Assets/collectibles/" + coin.name + "/" + coin.frames[0], select_drop, coin, button_type="Coin"))
  width = 0; height = 0
  for x, button in enumerate([(l[lg]["Decrease"], "less", change_value, -1), (l[lg]["Increase"], "more", change_value, 1)]):
    main.buttons[26].append(Button(60 + (x * 180), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
  for x, button in enumerate([(l[lg]["Decrease Decimal"], "less", change_value, -0.25), (l[lg]["Increase Decimal"], "more", change_value, 0.25)]):
    main.buttons[26].append(Button(92 + (x * 132), 116, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
  for stat in main.game_stats:
    text = fontsmaller.render(stat + ",", True, "White")
    if width + 60 + text.get_width() > WIDTH - 50: height += 16; width = 0
    width += text.get_width() + 10
    main.buttons[26].append(Button(50 + width - text.get_width(), 165 + height, text.get_width() + 7, 16, l[lg]["Use Stat"], stat, select_stat, target=stat, text_color={int: "Light blue", bool: "Light Yellow", str: "Pink", float: "Light Green"}[main.game_stats[stat]], font=fontsmaller))
  main.buttons[26].append(Button(WIDTH - 84, HEIGHT - 59, 32, 32, l[lg]["Finish Entity Type"], "Assets/editor/check mark.png", make_entity_type, 25))
def add_collectible_type(none):
  if main.gamestate != 13: main.gamestate = 13; main.selected_value = 1; main.selected_bool = True
  main.buttons[13].clear()
  for index, coin in enumerate(main.collectibles): that_one_coin = Collectible_Type(coin, "", 0, None, main); tup = (coin, that_one_coin.images, index); main.buttons[13].append(Button(104 + ((index % 18) * 17), 75 + math.floor(index / 18) * 17, 16, 16, coin, main.active_directory + "Assets/collectibles/" + coin + "/" + that_one_coin.frames[0], select_tile, tup, button_type="Coin")); del that_one_coin
  width = 0; height = 0
  try:
    if main.game_stats[main.selected_stat] == int or main.game_stats[main.selected_stat] == float:
      for x, button in enumerate([(l[lg]["Decrease"], "less", change_value, -1), (l[lg]["Increase"], "more", change_value, 1)]):
        main.buttons[13].append(Button(106 + (x * 180), HEIGHT - 266, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    if main.game_stats[main.selected_stat] == float:
      for x, button in enumerate([(l[lg]["Decrease Decimal"], "less", change_value, -0.25), (l[lg]["Increase Decimal"], "more", change_value, 0.25)]):
        main.buttons[13].append(Button(138 + (x * 132), HEIGHT - 258, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    if main.game_stats[main.selected_stat] == bool:
      for x, button in enumerate(["True", "False", "Negate"]):
        main.buttons[13].append(Button(106 + (x * 96), HEIGHT - 266, 64, 22, "Set as " + {"True": "True", "False": "False", "Negate": "Negation"}[button], button, change_bool, button, font=fontsmall, button_type="Boolean"))
  except: pass
  for stat in main.game_stats:
    text = fontsmaller.render(stat + ",", True, "White")
    if width + 120 + text.get_width() > WIDTH - 90: height += 16; width = 0
    width += text.get_width() + 10
    main.buttons[13].append(Button(85 + width - text.get_width(), (HEIGHT - 225) + height, text.get_width() + 7, 16, l[lg]["Use Stat"], stat, select_stat, target=stat, text_color={int: "Light blue", bool: "Light Yellow", str: "Pink", float: "Light Green"}[main.game_stats[stat]], font=fontsmaller, button_type="Stat"))
  main.buttons[13].append(Button(106, HEIGHT - 62, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx, target=13))
def add_background(none):
  if len(main.rooms[main.selected_room].backgrounds) < 11: main.gamestate = 17; main.selected_speed, main.selected_value = [0, 0], 1.0
def add_zone(none): main.gamestate = 0; main.rooms[main.selected_room].zones.append(Zone(snapint((WIDTH / 2) + main.camera.scroll[0], main.tiles_size), snapint((HEIGHT / 2) + main.camera.scroll[1], main.tiles_size), main=main))
def add_text(none):
  main.gamestate = 0
  if not len(main.rooms[main.selected_room].layers): main.rooms[main.selected_room].layers.append(Layer("L" + str(len(main.rooms[main.selected_room].layers) + 1), main=main)); main.gamestate = 0; main.buttons[0].append(Button(1 + (33 * (len(main.rooms[main.selected_room].layers) - 1)), HEIGHT - 33, 32, 32, l[lg]["Access Layer L"] + " " + str(len(main.rooms[main.selected_room].layers)), "", access_layer, len(main.rooms[main.selected_room].layers), button_type="Layer", room=main.selected_room))
  main.rooms[main.selected_room].layers[0].texts.append(Text(snapint((WIDTH / 2) + main.camera.scroll[0], main.tiles_size), snapint((HEIGHT / 2) + main.camera.scroll[1], main.tiles_size), font=fontmedium, font_size=30, main=main))

# Rooms Manager
def add_room(none): main.rooms.append(Room("Room" + str(len(main.rooms) + 1), main=main))
def edit_room(none): main.gamestate = 5; main.on_page = 1
def edit_menu(none): main.gamestate = 58
def delete_room(room):
  if len(main.rooms) > 1: main.rooms.remove(room)
def create_door(none):
  if type(main.selected_object).__name__ == "Tile": main.rooms[main.current_room].doors.append(Door(main.selected_object.rect.x, main.selected_object.rect.y, main.selected_object.type, main.selected_room, main=main)); main.rooms[main.current_room].layers[0].tiles.remove(main.selected_object); main.selected_object = None
  if main.selected_object == None: main.rooms[main.current_room].doors.append(Door(snapint((main.camera.scroll[0]) - (main.tiles_size / 2), main.tiles_size), snapint((main.camera.scroll[1]) - (main.tiles_size / 2), main.tiles_size), "/", main.selected_room, main=main))
def move_room_up(none):
  a = main.selected_room
  b = main.selected_room - 1
  for room in main.rooms:
    for door in room.doors:
      if door.led_room == a: door.led_room = b
      elif door.led_room == b: door.led_room = a
  index = main.rooms.index(main.rooms[main.selected_room])
  room = main.rooms.pop(index)
  main.rooms.insert(index - 1, room)
  main.selected_room -= 1
  for button in main.buttons[0]:
    if button.button_type == "Layer" and button.room == main.selected_room + 1: button.room -= 1
    elif button.button_type == "Layer" and button.room == main.selected_room: button.room += 1
  for button in main.buttons[0]:
    if button.button_type == "Background Layer" and button.room == main.selected_room + 1: button.room -= 1
    elif button.button_type == "Background Layer" and button.room == main.selected_room: button.room += 1
def move_room_down(none):
  a = main.selected_room
  b = main.selected_room + 1
  for room in main.rooms:
    for door in room.doors:
      if door.led_room == a: door.led_room = b
      elif door.led_room == b: door.led_room = a
  index = main.rooms.index(main.rooms[main.selected_room])
  room = main.rooms.pop(index)
  main.rooms.insert(index + 1, room)
  main.selected_room += 1
  for button in main.buttons[0]:
    if button.button_type == "Layer" and button.room == main.selected_room - 1: button.room += 1
    elif button.button_type == "Layer" and button.room == main.selected_room: button.room -= 1
  for button in main.buttons[0]:
    if button.button_type == "Background Layer" and button.room == main.selected_room - 1: button.room += 1
    elif button.button_type == "Background Layer" and button.room == main.selected_room: button.room -= 1

  
#Game Settings
def change_tiles_size(remember_gs, rename_target, target_object): main.gamestate = 9; main.remember_gs = remember_gs; main.rename_target = rename_target; main.rename_text = rename_target; main.target_object = target_object; main.instance_target = rename_target
def snap_tiles_image_size(none): main.snap_tile_image = not main.snap_tile_image
def snap_tiles_rect_size(none): main.snap_tile_rect = not main.snap_tile_rect
def manage_tiles(remember_gs):
  main.gamestate = 53; main.remember_gs = remember_gs
  for button in main.buttons[53]:
    if button.button_type == "Tile Type": main.buttons[53].remove(button)
  for index, button in enumerate(main.tile_types):
    if "anim" in main.tile_types[str(index)]["flags"]: main.buttons[53].append(Button(((index % 10) * 26) + 1, (math.floor(index / 10) * 26) + 1, 25, 25, main.tile_types[str(index)]["img"], [main.active_directory + "Assets/tiles/" + main.tile_types[str(index)]["img"] + "/" + img for img in os.listdir(main.active_directory + "Assets/tiles/" + main.tile_types[str(index)]["img"])], select_tile_type, str(index), button_type="Tile Type"))
    else: main.buttons[53].append(Button(((index % 10) * 26) + 1, (math.floor(index / 10) * 26) + 1, 25, 25, main.tile_types[str(index)]["img"], main.active_directory + "Assets/tiles/" + main.tile_types[str(index)]["img"], select_tile_type, str(index), button_type="Tile Type"))
  for button in main.buttons[53]:
    if button.button_type == "Tile Type": main.buttons[53].remove(button)
  for button in main.buttons[53]:
    if button.button_type == "Tile Type": main.buttons[53].remove(button)
  for button in main.buttons[53]:
    if button.button_type == "Tile Type": main.buttons[53].remove(button)
  for button in main.buttons[53]:
    if button.button_type == "Tile Type": main.buttons[53].remove(button)
  for button in main.buttons[53]:
    if button.button_type == "Tile Type": main.buttons[53].remove(button)
  for button in main.buttons[53]:
    if button.button_type == "Tile Type": main.buttons[53].remove(button)
  for button in main.buttons[53]:
    if button.button_type == "Tile Type": main.buttons[53].remove(button)
  for index, button in enumerate(main.tile_types):
    if "anim" in main.tile_types[str(index)]["flags"]: main.buttons[53].append(Button(((index % 10) * 26) + 1, (math.floor(index / 10) * 26) + 1, 25, 25, main.tile_types[str(index)]["img"], [main.active_directory + "Assets/tiles/" + main.tile_types[str(index)]["img"] + "/" + img for img in os.listdir(main.active_directory + "Assets/tiles/" + main.tile_types[str(index)]["img"])], select_tile_type, str(index), button_type="Tile Type"))
    else: main.buttons[53].append(Button(((index % 10) * 26) + 1, (math.floor(index / 10) * 26) + 1, 25, 25, main.tile_types[str(index)]["img"], main.active_directory + "Assets/tiles/" + main.tile_types[str(index)]["img"], select_tile_type, str(index), button_type="Tile Type"))
def manage_entities(remember_gs):
  main.gamestate = 54; main.remember_gs = remember_gs
  for button in main.buttons[54]:
    if button.button_type == "Character Type": main.buttons[54].remove(button)
  for index, button in enumerate(main.character_types):
    if "td" in main.character_types[str(index)]["flags"]: main.buttons[54].append(Button(((index % 10) * 26) + 1, (math.floor(index / 10) * 26) + 1, 25, 25, main.character_types[str(index)]["type"], main.active_directory + "Assets/characters/" + main.character_types[str(index)]["type"] + "/down/idle/1.png", select_character_type, str(index), button_type="Character Type"))
    else: main.buttons[54].append(Button(((index % 10) * 26) + 1, (math.floor(index / 10) * 26) + 1, 25, 25, main.character_types[str(index)]["type"], main.active_directory + "Assets/characters/" + main.character_types[str(index)]["type"] + "/idle/1.png", select_character_type, str(index), button_type="Character Type"))
  for button in main.buttons[54]:
    if button.button_type == "Character Type": main.buttons[54].remove(button)
  for button in main.buttons[54]:
    if button.button_type == "Character Type": main.buttons[54].remove(button)
  for button in main.buttons[54]:
    if button.button_type == "Character Type": main.buttons[54].remove(button)
  for button in main.buttons[54]:
    if button.button_type == "Character Type": main.buttons[54].remove(button)
  for button in main.buttons[54]:
    if button.button_type == "Character Type": main.buttons[54].remove(button)
  for button in main.buttons[54]:
    if button.button_type == "Character Type": main.buttons[54].remove(button)
  for button in main.buttons[54]:
    if button.button_type == "Character Type": main.buttons[54].remove(button)
  for button in main.buttons[54]:
    if button.button_type == "Character Type": main.buttons[54].remove(button)
  for button in main.buttons[54]:
    if button.button_type == "Character Type": main.buttons[54].remove(button)
  for button in main.buttons[54]:
    if button.button_type == "Character Type": main.buttons[54].remove(button)
  for button in main.buttons[54]:
    if button.button_type == "Character Type": main.buttons[54].remove(button)
  for button in main.buttons[54]:
    if button.button_type == "Character Type": main.buttons[54].remove(button)
  for index, button in enumerate(main.character_types):
    if "td" in main.character_types[str(index)]["flags"]: main.buttons[54].append(Button(((index % 10) * 26) + 1, (math.floor(index / 10) * 26) + 1, 25, 25, main.character_types[str(index)]["type"], main.active_directory + "Assets/characters/" + main.character_types[str(index)]["type"] + "/down/idle/1.png", select_character_type, str(index), button_type="Character Type"))
    else: main.buttons[54].append(Button(((index % 10) * 26) + 1, (math.floor(index / 10) * 26) + 1, 25, 25, main.character_types[str(index)]["type"], main.active_directory + "Assets/characters/" + main.character_types[str(index)]["type"] + "/idle/1.png", select_character_type, str(index), button_type="Character Type"))
def manage_collectibles(remember_gs):
  main.gamestate = 55; main.remember_gs = remember_gs
  for button in main.buttons[55]:
    if button.button_type == "Collectible Type": main.buttons[55].remove(button)
  for index, button in enumerate(main.collectible_types): main.buttons[55].append(Button(((index % 10) * 26) + 1, (math.floor(index / 10) * 26) + 1, 25, 25, main.collectible_types[str(index)]["img"], [main.active_directory + "Assets/collectibles/" + main.collectible_types[str(index)]["img"] + "/" + img for img in os.listdir(main.active_directory + "Assets/collectibles/" + main.collectible_types[str(index)]["img"])], select_collectible_type, str(index), button_type="Collectible Type"))
  for button in main.buttons[55]:
    if button.button_type == "Collectible Type": main.buttons[55].remove(button)
  for button in main.buttons[55]:
    if button.button_type == "Collectible Type": main.buttons[55].remove(button)
  for button in main.buttons[55]:
    if button.button_type == "Collectible Type": main.buttons[55].remove(button)
  for button in main.buttons[55]:
    if button.button_type == "Collectible Type": main.buttons[55].remove(button)
  for button in main.buttons[55]:
    if button.button_type == "Collectible Type": main.buttons[55].remove(button)
  for button in main.buttons[55]:
    if button.button_type == "Collectible Type": main.buttons[55].remove(button)
  for button in main.buttons[55]:
    if button.button_type == "Collectible Type": main.buttons[55].remove(button)
  for button in main.buttons[55]:
    if button.button_type == "Collectible Type": main.buttons[55].remove(button)
  for button in main.buttons[55]:
    if button.button_type == "Collectible Type": main.buttons[55].remove(button)
  for index, button in enumerate(main.collectible_types): main.buttons[55].append(Button(((index % 10) * 26) + 1, (math.floor(index / 10) * 26) + 1, 25, 25, main.collectible_types[str(index)]["img"], [main.active_directory + "Assets/collectibles/" + main.collectible_types[str(index)]["img"] + "/" + img for img in os.listdir(main.active_directory + "Assets/collectibles/" + main.collectible_types[str(index)]["img"])], select_collectible_type, str(index), button_type="Collectible Type"))
def manage_projectiles(remember_gs): main.gamestate = 49; main.remember_gs = remember_gs

#Edit Tile
def select_tile_type(tile): main.selected_tile_type = tile; main.frame_timer.reset()
def select_character_type(character): main.selected_character_type = character
def select_collectible_type(collectible): main.selected_collectible_type = collectible; main.frame_timer.reset()
def toggle_solid(none):
  if "solid" in main.tile_types[main.selected_tile_type]["flags"]:
    main.tile_types[main.selected_tile_type]["flags"].remove("solid")
  else: main.tile_types[main.selected_tile_type]["flags"].append("solid")
def toggle_slippery(none):
  if "ice" in main.tile_types[main.selected_tile_type]["flags"]:
    main.tile_types[main.selected_tile_type]["flags"].remove("ice")
  else: main.tile_types[main.selected_tile_type]["flags"].append("ice")
def toggle_flatness(none):
  if "flat" in main.tile_types[main.selected_tile_type]["flags"]:
    main.tile_types[main.selected_tile_type]["flags"].remove("flat")
  else: main.tile_types[main.selected_tile_type]["flags"].append("flat")
def change_tile_hitbox_x(by):
  main.tile_types[main.selected_tile_type]["off"][0] += by
def change_tile_hitbox_y(by):
  main.tile_types[main.selected_tile_type]["off"][1] += by
def change_tile_hitbox_width(by):
  main.tile_types[main.selected_tile_type]["size"][0] += by
def change_tile_hitbox_height(by):
  main.tile_types[main.selected_tile_type]["size"][1] += by
def change_tile_chain_speed(by):
  main.tile_types[main.selected_tile_type]["chain_s"] += by
  if main.tile_types[main.selected_tile_type]["chain_s"] < 0: main.tile_types[main.selected_tile_type]["chain_s"] = 0
def change_tile_type_hp(by):
  main.tile_types[main.selected_tile_type]["hp"] += by
  if main.tile_types[main.selected_tile_type]["hp"] < -1: main.tile_types[main.selected_tile_type]["hp"] = -1
def change_tile_type_anim_rate(by):
  main.tile_types[main.selected_tile_type]["anim_s"] += by
  if main.tile_types[main.selected_tile_type]["anim_s"] < 1: main.tile_types[main.selected_tile_type]["anim_s"] = 1
def change_tile_type_team(by): main.tile_types[main.selected_tile_type]["team"] += by
def change_tile_type_destroy_if_stood_on(none):
  if "diso" in main.tile_types[main.selected_tile_type]["flags"]:
    main.tile_types[main.selected_tile_type]["flags"].remove("diso")
  else: main.tile_types[main.selected_tile_type]["flags"].append("diso")
def change_tile_type_destroy_if_head_bump(none):
  if "dihb" in main.tile_types[main.selected_tile_type]["flags"]:
    main.tile_types[main.selected_tile_type]["flags"].remove("dihb")
  else: main.tile_types[main.selected_tile_type]["flags"].append("dihb")
def change_tile_type_destroy_anim(anim):
  main.tile_types[main.selected_tile_type]["destr_anim"] = anim
  #if main.selected_object.destroy_anim == "disappear": main.selected_object.instigator = False
  #else: main.selected_object.instigator = True

#Edit Entity
def select_entity_type(entity): main.selected_entity_type = entity; main.frame_timer.reset()
def change_character_speed(by):
  main.character_types[main.selected_character_type]["object"].speed += by
  #if main.character_types[main.selected_character_type]["object"].speed < -1: main.character_types[main.selected_character_type]["object"].speed = -1
def change_character_leap(by):
  main.character_types[main.selected_character_type]["object"].jump_force += by
  #if main.character_types[main.selected_character_type]["object"].jump_force < -1: main.character_types[main.selected_character_type]["object"].jump_force = -1
def change_character_type_defeat_anim(anim):
  main.character_types[main.selected_character_type]["object"].defeat_anim = anim
def set_character_able_to_wall_slide(none):
  if "wallslide" in main.character_types[main.selected_character_type]["flags"]:
    main.character_types[main.selected_character_type]["flags"].remove("wallslide")
  else: main.character_types[main.selected_character_type]["flags"].append("wallslide")
def edit_entities(none):
  main.gamestate = 56
  for button in main.buttons[56]:
    if button.button_type == "Entity Type": main.buttons[56].remove(button)
  for button in main.buttons[56]:
    if button.button_type == "Entity Type": main.buttons[56].remove(button)
  for button in main.buttons[56]:
    if button.button_type == "Entity Type": main.buttons[56].remove(button)
  for button in main.buttons[56]:
    if button.button_type == "Entity Type": main.buttons[56].remove(button)
  for button in main.buttons[56]:
    if button.button_type == "Entity Type": main.buttons[56].remove(button)
  for button in main.buttons[56]:
    if button.button_type == "Entity Type": main.buttons[56].remove(button)
  for index, entity in enumerate(main.entity_types):
    try: pygame.image.load(main.active_directory + "Assets/characters/" + main.entity_types[str(index)]["character"] + "/idle/1.png"); main.buttons[56].append(Button(((index % 10) * 26) + 1, (math.floor(index / 10) * 26) + 1, 25, 25, main.entity_types[str(index)]["character"], main.active_directory + "Assets/characters/" + main.entity_types[str(index)]["character"] + "/idle/1.png", select_entity_type, str(index), button_type="Entity Type"))
    except: pygame.image.load(main.active_directory + "Assets/characters/" + main.entity_types[str(index)]["character"] + "/down/idle/1.png"); main.buttons[56].append(Button(((index % 10) * 26) + 1, (math.floor(index / 10) * 26) + 1, 25, 25, main.entity_types[str(index)]["character"], main.active_directory + "Assets/characters/" + main.entity_types[str(index)]["character"] + "/down/idle/1.png", select_entity_type, str(index), button_type="Entity Type"))
def add_entity(none): index = len(main.entity_types); main.entity_types[str(index)] = {"character": main.character_types[main.selected_character_type]["type"], "index": str(index), "hp": 1, "stat": "", "value": 0, "team": 0, "behaviors": [], "range": 0, "drops": [], "flags": []}; edit_entities(None)
def change_entity_hp(by):
  main.entity_types[main.selected_entity_type]["hp"] += by
  if main.entity_types[main.selected_entity_type]["hp"] < 0: main.entity_types[main.selected_entity_type]["hp"] = 0
def change_entity_team(by):
  main.entity_types[main.selected_entity_type]["team"] += by
  if main.entity_types[main.selected_entity_type]["team"] < 0: main.entity_types[main.selected_entity_type]["team"] = 0
def set_entity_stat(stat):
  if main.entity_types[main.selected_entity_type]["stat"] == stat: main.entity_types[main.selected_entity_type]["stat"] = ""
  else: main.entity_types[main.selected_entity_type]["stat"] = stat
  if main.entity_types[main.selected_entity_type]["stat"]:
    if main.game_stats[main.entity_types[main.selected_entity_type]["stat"]] == int or main.game_stats[main.entity_types[main.selected_entity_type]["stat"]] == float: main.entity_types[main.selected_entity_type]["value"] = 0
    if main.game_stats[main.entity_types[main.selected_entity_type]["stat"]] == bool or main.game_stats[main.entity_types[main.selected_entity_type]["stat"]] == string: main.entity_types[main.selected_entity_type]["value"] = "True"
def change_entity_value(by): main.entity_types[main.selected_entity_type]["value"] += by
def change_entity_bool(by): main.entity_types[main.selected_entity_type]["value"] = by

#Edit Collectible
def change_collectible_anim_speed(by):
  main.collectible_types[main.selected_collectible_type]["anim_s"] += by
  if main.collectible_types[main.selected_collectible_type]["anim_s"] < -1: main.collectible_types[main.selected_collectible_type]["anim_s"] = -1
def set_collectible_stat(stat):
  if main.collectible_types[main.selected_collectible_type]["stat"] == stat: main.collectible_types[main.selected_collectible_type]["stat"] = ""
  else: main.collectible_types[main.selected_collectible_type]["stat"] = stat
  if main.collectible_types[main.selected_collectible_type]["stat"]:
    if main.game_stats[main.collectible_types[main.selected_collectible_type]["stat"]] == int or main.game_stats[main.collectible_types[main.selected_collectible_type]["stat"]] == float: main.collectible_types[main.selected_collectible_type]["value"] = 0
    if main.game_stats[main.collectible_types[main.selected_collectible_type]["stat"]] == bool or main.game_stats[main.collectible_types[main.selected_collectible_type]["stat"]] == string: main.collectible_types[main.selected_collectible_type]["value"] = "True"
def change_collectible_value(by): main.collectible_types[main.selected_collectible_type]["value"] += by
def change_collectible_bool(by): main.collectible_types[main.selected_collectible_type]["value"] = by
  
# Cutscene Tab
def delete_cutscene(cutscene): main.rooms[main.selected_room].cutscenes.remove(cutscene)
    
# Rename Screen
def rename(remember_gs, rename_target, target_object):
  main.on_page = 1
  main.gamestate = 4; main.remember_gs = remember_gs; main.rename_target = rename_target
  if remember_gs != 15 and remember_gs != 29 and remember_gs != 30  and remember_gs != 33 and remember_gs != 35 and remember_gs != 43: main.rename_text = rename_target.name
  elif remember_gs == 43: main.rename_text = rename_target.text
  else: main.rename_text = rename_target
  main.target_object = target_object; main.instance_target = rename_target
  main.text_cursor = len(main.rename_text)
#def add_letter(letter): main.rename_text = str(main.rename_text); main.rename_text += letter
#def remove_letter(none): main.rename_text = str(main.rename_text)[:-1]
def add_letter(letter): text = str(main.rename_text); pos = main.text_cursor; main.rename_text = text[:pos] + letter + text[pos:]; main.text_cursor += 1
def remove_letter(none):
  if main.text_cursor > 0: text = str(main.rename_text); main.rename_text = text[:main.text_cursor-1] + text[main.text_cursor:]; main.text_cursor -= 1
def add_space(none): text = str(main.rename_text); main.rename_text = text[:main.text_cursor] + " " + text[main.text_cursor:]; main.text_cursor += 1
def add_alif_hamza(none): text = str(main.rename_text); pos = main.text_cursor; main.rename_text = text[:pos] + "ٵ" + text[pos:]; main.text_cursor += 1
def add_near_close_near_front_unrounded_vowel_with_breve_below(none): text = str(main.rename_text); pos = main.text_cursor; main.rename_text = text[:pos] + "ɪ̯" + text[pos:]; main.text_cursor += 1
def copy_text(none): main.clipboard_text = main.rename_text
def paste_text(none): main.rename_text = main.clipboard_text; main.text_cursor = len(main.rename_text)
def partial_paste_text(none): text = str(main.rename_text); pos = main.text_cursor; main.rename_text = text[:pos] + main.clipboard_text + text[pos:]; main.text_cursor += len(main.clipboard_text)

# Edit Room
def set_scrolling_mode(mode): main.rooms[main.selected_room].scroll_mode = mode
def hide_player_for_room(none): main.rooms[main.selected_room].show_player = not main.rooms[main.selected_room].show_player
def allow_hm(none): main.rooms[main.selected_room].hm = not main.rooms[main.selected_room].hm; main.rooms[main.selected_room].spawn_hm = main.rooms[main.selected_room].hm
def allow_vm(none): main.rooms[main.selected_room].vm = not main.rooms[main.selected_room].vm; main.rooms[main.selected_room].spawn_vm = main.rooms[main.selected_room].vm
def play_track(path):
  global song
  try:
    if main.gamestate == 5: song = pygame.mixer.Sound(main.active_directory + "Sounds/tracks/" + main.rooms[main.selected_room].track); pygame.mixer_music.load(main.active_directory + "Sounds/tracks/" + main.rooms[main.selected_room].track); pygame.mixer.music.play(1, 0.0)
    else: song = pygame.mixer.Sound(main.active_directory + "Sounds/tracks/" + main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Track"]); pygame.mixer.music.load(main.active_directory + "Sounds/tracks/" + main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Track"]); pygame.mixer.music.play(1, 0.0)
  except: pass
def stop_track(none): pygame.mixer.music.stop()
def select_track(none): main.gamestate = 6; main.selecting_first_track = False
def play_track2(path):
  global song
  try:
    if main.gamestate == 5: song = pygame.mixer.Sound(main.active_directory + "Sounds/tracks/" + main.rooms[main.selected_room].first_track); pygame.mixer_music.load(main.active_directory + "Sounds/tracks/" + main.rooms[main.selected_room].first_track); pygame.mixer.music.play(1, 0.0)
    else: song = pygame.mixer.Sound(main.active_directory + "Sounds/tracks/" + main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Dir"]); pygame.mixer.music.load(main.active_directory + "Sounds/tracks/" + main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Dir"]); pygame.mixer.music.play(1, 0.0)
  except: pass
def select_track2(none): main.gamestate = 6; main.selecting_first_track = True
def remove_track(none):
  main.gamestate = 5
  if main.selecting_first_track: main.rooms[main.selected_room].first_track = ""
  else: main.rooms[main.selected_room].track = ""
def select_track_for_cs(none): main.gamestate = 42; main.remember_gs = 41; main.selecting_first_track = False
def select_track_for_cs2(none): main.gamestate = 42; main.remember_gs = 41; main.selecting_first_track = True
def stop_track_for_cs(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Track"] = "Stop"
def add_track(none):
  main.selected_track = main.tracks[main.selected_itemy]; main.gamestate = 5
  if main.selecting_first_track: main.rooms[main.selected_room].first_track = main.selected_track
  else: main.rooms[main.selected_room].track = main.selected_track
def add_track_for_cs(none):
  if main.selecting_first_track: main.selected_track = main.tracks[main.selected_itemy]; main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Dir"] = main.selected_track; main.gamestate = 41
  else: main.selected_track = main.tracks[main.selected_itemy]; main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Track"] = main.selected_track; main.gamestate = 41
def remove_track_for_cs(none):
  if main.selecting_first_track: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Dir"] = ""; main.gamestate = 41
  else: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Track"] = ""; main.gamestate = 41
def change_borders(remember_gs, rename_target, target_object): main.gamestate = 9; main.remember_gs = remember_gs; main.rename_target = rename_target; main.rename_text = rename_target; main.target_object = target_object; main.instance_target = rename_target
def show_ui_for_room(none):
  if not main.selected_ui_sm in main.rooms[main.selected_room].show_ui: main.rooms[main.selected_room].show_ui.append(main.selected_ui_sm)
  else: main.rooms[main.selected_room].show_ui.remove(main.selected_ui_sm)
def hide_ui_for_room(none):
  if not main.selected_ui_sm in main.rooms[main.selected_room].hide_ui: main.rooms[main.selected_room].hide_ui.append(main.selected_ui_sm)
  else: main.rooms[main.selected_room].hide_ui.remove(main.selected_ui_sm)
def set_ui_mode_for_token(none):
  if not (main.selected_ui_sm, main.selected_ui_mode_for_tm) in main.rooms[main.selected_room].ui_modes: main.rooms[main.selected_room].ui_modes.append((main.selected_ui_sm, main.selected_ui_mode_for_tm))
  else: main.rooms[main.selected_room].ui_modes.remove((main.selected_ui_sm, main.selected_ui_mode_for_tm))
def set_room_mode(mode): main.rooms[main.selected_room].mode = mode
def change_room_gravity(by): main.rooms[main.selected_room].gravity += by

# Brush Mode
def select_tile(tile): main.selected_tile = tile
def edit_layer(none): main.gamestate = 8
def cac(none):
  for button in main.buttons[11]:
    if button.button_type == "Coin": main.buttons[11].remove(button)
  for button in main.buttons[11]:
    if button.button_type == "Coin": main.buttons[11].remove(button)
  for button in main.buttons[11]:
    if button.button_type == "Coin": main.buttons[11].remove(button)
  main.gamestate = 11
  for index, coin in enumerate(main.collectible_types):
    frames = os.listdir(main.active_directory + "Assets/collectibles/" + main.collectible_types[coin]["img"])
    images = []
    for image in frames: images.append(pygame.image.load(main.active_directory + "Assets/collectibles/" + main.collectible_types[coin]["img"] + "/" + image).convert_alpha())
    tup = (main.collectible_types[coin]["img"], images, index, coin)
    main.buttons[11].append(Button(2 + ((index % 30) * 17), 25 + math.floor(index / 30) * 17, 16, 16, tup[0], main.active_directory + "Assets/collectibles/" + tup[0] + "/1.png", select_tile, tup, button_type="Coin", with_sound=False))
def ea(none):
  for button in main.buttons[27]:
    if button.button_type == "Entity": main.buttons[27].remove(button)
  for button in main.buttons[27]:
    if button.button_type == "Entity": main.buttons[27].remove(button)
  for button in main.buttons[27]:
    if button.button_type == "Entity": main.buttons[27].remove(button)
  main.gamestate = 27
  for index, entity in enumerate(main.entity_types):
    try: tup = (main.entity_types[str(entity)]["character"], "Assets/characters/" + main.entity_types[str(entity)]["character"] + "/idle/1.png", index, main.entity_types[str(entity)]); main.buttons[27].append(Button(2 + ((index % 30) * 17), 25 + math.floor(index / 30) * 17, 16, 16, tup[0], main.active_directory + tup[1], select_tile, tup, button_type="Entity", with_sound=False))
    except: tup = (main.entity_types[str(entity)]["character"], "Assets/characters/" + main.entity_types[str(entity)]["character"] + "/down/idle/1.png", index, main.entity_types[str(entity)]); main.buttons[27].append(Button(2 + ((index % 30) * 17), 25 + math.floor(index / 30) * 17, 16, 16, tup[0], main.active_directory + tup[0], select_tile, tup, button_type="Entity", with_sound=False))

# Edit Layer
def change_layer_distance(by): main.rooms[main.selected_room].layers[main.selected_layer].distance += by
def change_layer_shade(by):
  main.rooms[main.selected_room].layers[main.selected_layer].shade += by
  if main.rooms[main.selected_room].layers[main.selected_layer].shade < 0: main.rooms[main.selected_room].layers[main.selected_layer].shade = 0
  if main.rooms[main.selected_room].layers[main.selected_layer].shade > 250: main.rooms[main.selected_room].layers[main.selected_layer].shade = 250
def delete_layer(none):
  main.rooms[main.selected_room].layers.remove(main.rooms[main.selected_room].layers[main.selected_layer]); main.gamestate = 0
  for index, layer in enumerate(main.rooms[main.selected_room].layers): layer.label = "L" + str(index + 1)
  for button in [button for button in main.buttons[0] if button.button_type == "L" + str(main.selected_layer + 1)]: main.buttons[0].remove(button)

#CAC
def delete_collectible_type(none):
  try:
    for coin in [coin for coin in main.rooms[main.selected_room].layers[main.selected_layer].collectibles if coin.type == main.selected_tile[3]]: main.rooms[main.selected_room].layers[main.selected_layer].collectibles.remove(coin)
    main.collectible_types.remove(main.selected_tile[3]); main.selected_tile = ()
    main.buttons[11].clear()
    main.buttons[11].append(Button(WIDTH - 21, 100 - 21, 19, 19, "Delete Collectible Type Object", "Assets/editor/delete.png", delete_collectible_type))
    for index, coin in enumerate(main.collectible_types): tup = (coin.name, coin.images, index, coin); main.buttons[11].append(Button(2 + ((index % 30) * 17), 25 + math.floor(index / 30) * 17, 16, 16, coin.name, main.active_directory + "Assets/collectibles/" + coin.name + "/" + coin.frames[0], select_tile, tup, button_type="Coin"))
  except: pass
  
#New Entity Type
#def select_behavior(behavior):
#  done = False
#  if behavior in main.selected_behaviors and not done: main.selected_behaviors.remove(behavior); done = True
#  if (not done) and (not behavior in main.selected_behaviors): main.selected_behaviors.append(behavior); done = True
def select_behavior(behavior):
  if behavior in main.entity_types[main.selected_entity_type]["behaviors"]: main.entity_types[main.selected_entity_type]["behaviors"].remove(behavior)
  elif not behavior in main.entity_types[main.selected_entity_type]["behaviors"]: main.entity_types[main.selected_entity_type]["behaviors"].append(behavior)
def select_text_behavior(behavior):
  if behavior in main.selected_object.behaviors: main.selected_object.behaviors.remove(behavior)
  elif not behavior in main.selected_object.behaviors: main.selected_object.behaviors.append(behavior)

#New Collectible
def change_value(by): main.selected_value += by
def change_bool(boolean): main.selected_bool = boolean
def select_stat(stat):
  main.selected_stat = stat
  if main.gamestate == 13: add_collectible_type(None)
def select_sfx(remember_gs): main.gamestate = 16; main.remember_gs = remember_gs; main.choosing_sfx = 1
def make_collectible_type(none):
  if main.game_stats[main.selected_stat] == bool: main.selected_value = main.selected_bool
  main.collectible_types.append(Collectible_Type(main.selected_tile[0], main.selected_stat, main.selected_value, main.selected_sfx, main)); main.selected_tile = (); main.selected_stat = ""; main.selected_value = 1; main.selected_sfx = ""; main.gamestate = 0

#General Game Settings - Stats
def add_int_stat(none): main.game_stats[f"Stat {len(main.game_stats) + 1}"] = int; main.game_stats_initpoint[f"Stat {len(main.game_stats)}"] = 0; main.game_stats_effect[f"Stat {len(main.game_stats)}"] = "None"; main.game_stats_range[f"Stat {len(main.game_stats)}"] = [0, 0]
def add_bool_stat(none): main.game_stats[f"Stat {len(main.game_stats) + 1}"] = bool; main.game_stats_initpoint[f"Stat {len(main.game_stats)}"] = False; main.game_stats_effect[f"Stat {len(main.game_stats)}"] = "None"
def add_str_stat(none): main.game_stats[f"Stat {len(main.game_stats) + 1}"] = str; main.game_stats_initpoint[f"Stat {len(main.game_stats)}"] = ""; main.game_stats_effect[f"Stat {len(main.game_stats)}"] = "None"
def add_float_stat(none): main.game_stats[f"Stat {len(main.game_stats) + 1}"] = float; main.game_stats_initpoint[f"Stat {len(main.game_stats)}"] = 0.0; main.game_stats_effect[f"Stat {len(main.game_stats)}"] = "None"; main.game_stats_range[f"Stat {len(main.game_stats)}"] = [0.0, 0.0]
def delete_stat(none):
  try: main.game_stats.pop(list(main.game_stats)[list(main.game_stats).index(main.selected_stat)]); main.game_stats_initpoint.pop(list(main.game_stats)[list(main.game_stats).index(main.selected_stat)]); main.game_stats_range.pop(list(main.game_stats)[list(main.game_stats).index(main.selected_stat)])
  except: pass
  try: main.game_stats_effect.pop(list(main.game_stats)[list(main.game_stats).index(main.selected_stat)])
  except: pass
  for index, ui in enumerate(main.ui.instances.values()):
    if main.ui.instances[main.selected_stat][str(index + 1)]["Stat"] == main.selected_stat: main.ui.instances.pop(main.selected_stat); break
  main.selected_stat = None
  #{'Stat 1': {'Modes': ['1'], 'Current': '1', 'Hidden': False, 'SM': 1, '1': {'Stat': 'Stat 1', 'Corner': 'Up Left', 'X Margin': 5, 'Y Margin': 5, 'Rotate': 0, 'Text': 'SS', 'I': False, 'I X': 10, 'I Y': 10, 'I Offset': 2, 'I WL': 16, 'I Angle': 90, 'I Align': 'Left', 'I Image': '', 'I Image 2': '', 'I FS': 1, 'AA': True, 'Bar': False, 'B V': False, 'B X': 2, 'B Y': 2, 'B Len': 100, 'B Thi': 10, 'B OL': 0, 'C1': (0, 255, 0), 'C2': (255, 0, 0), 'C3': (0, 0, 0), 'C4': (255, 255, 255), 'Font STR': None, 'Font Size': 30, 'TC': (255, 255, 255), 'TCOL': (0, 0, 0), 'TCBG': 'Transparent', 'TOL': 0, 'Font': <pygame.font.Font object at 0x000001C72DCF0C60>, 'Surface': None, 'Surface 2': None, 'Text Surface': <Surface(26x22x32, global_alpha=255)>, 'Timer': <Scripts.timers.Timer object at 0x000001C72E50DF10>}}}
def select_statistic(stat): main.selected_stat = stat
def set_stat_init(stat):
  if main.game_stats[stat] == str: main.gamestate = 4
  if main.game_stats[stat] == int: main.gamestate = 9
  if main.game_stats[stat] == bool: main.gamestate = 37
  if main.game_stats[stat] == float: main.gamestate = 9
  main.remember_gs = 15; main.rename_target = main.game_stats_initpoint[main.selected_stat]; main.rename_text = main.game_stats_initpoint[main.selected_stat]; main.target_object = "Stat"; main.instance_target = main.game_stats_initpoint[main.selected_stat]
def set_stat_effect(none):
  main.gamestate = 34
  main.buttons[34].clear()
  if main.game_stats[main.selected_stat] == int or main.game_stats[main.selected_stat] == float: # Health
    for index, stat in enumerate([("HP", "heart", "hp"), ("Stagger (increases knockback)", "heart", "stagger"), ("Main Score", "main score", "main score"), ("Speed", "run", "speed"), ("Leap", "arrow point up", "leap"), ("Set", "set", "set")]):
      main.buttons[34].append(Button(110 + (index * 34), 130, 32, 32, "Effect: " + stat[0], "Assets/editor/" + stat[1] + ".png", set_effect, stat[2], button_type="Effect"))
  if main.game_stats[main.selected_stat] == bool:
    for index, stat in enumerate([("Ability for A Button", "a button", "ability a"), ("Ability for B Button", "b button", "ability b"), ("Ability for X Button", "x button", "ability x"), ("Ability for Y Button", "y button", "ability y")]):
      main.buttons[34].append(Button(110 + (index * 34), 130, 32, 32, f"Effect: {stat[0]}", "Assets/editor/" + stat[1] + ".png", set_effect, stat[2], button_type="Effect"))
    #for index, stat in enumerate([("Ability for A Button for Click", "a button click", "ability a click"), ("Ability for B Button for Click", "b button click", "ability b click"), ("Ability for X Button for Click", "x button click", "ability x click"), ("Ability for Y Button for Click", "y button click", "ability y click")]):
    #  main.buttons[34].append(Button(110 + (index * 34), 164, 32, 32, f"Effect: {stat[0]}", "Assets/editor/" + stat[1] + ".png", set_effect, stat[2], button_type="Effect"))
    #for index, stat in enumerate([("Ability for A Button for Hold", "a button hold", "ability a hold"), ("Ability for B Button for Hold", "b button hold", "ability b hold"), ("Ability for X Button for Hold", "x button hold", "ability x hold"), ("Ability for Y Button for Hold", "y button hold", "ability y hold")]):
    #  main.buttons[34].append(Button(110 + (index * 34), 198, 32, 32, f"Effect: {stat[0]}", "Assets/editor/" + stat[1] + ".png", set_effect, stat[2], button_type="Effect"))
  main.buttons[34].append(Button(WIDTH - 136, 104, 32, 32, "Go Back", "Assets/editor/back.png", go_to, target_gs=15))
  main.buttons[34].append(Button(WIDTH - 170, 104, 32, 32, "Remove Effect", "Assets/editor/delete.png", clear_stat_effect))
def set_stat_ui(none):
  try: main.ui.instances[main.selected_stat]; main.selected_ui = main.selected_stat; main.gamestate = 35
  except: main.ui.add_instance(main.selected_stat, main.ui.format_ui_component(stat=main.selected_stat, corner="Up Left", x_margin=5, y_margin=5, rotation=0, text="", multi_align="right", multi_align_offset=50, iteration=False, i_x=10, i_y=10, i_offset=2, i_wrap_length=16, i_angle=90, i_align="Left", image_path="", image_path2="", frame_speed=1, antialias=True, bar=False, vertical_bar=False, b_x=2, b_y=2, b_length=100, b_thickness=10, b_outline=0, color1=(0, 255, 0), color2=(255, 0, 0), color3=(0, 0, 0), color4=(255, 255, 255), font=None, font_size=30, text_color=(255, 255, 255), text_color_outline=(0, 0, 0), text_color_bg="Transparent", text_outline_thickness=0, scene_mode=1)); main.selected_ui = main.selected_stat; main.gamestate = 35
  main.selected_object = None; refresh_ui_buttons()
def set_stat_max(stat): main.gamestate = 9; main.remember_gs = 15; main.rename_target = main.game_stats_range[main.selected_stat][1]; main.rename_text = main.game_stats_range[main.selected_stat][1]; main.target_object = "Stat (Max)"; main.instance_target = main.game_stats_range[main.selected_stat][1]; main.spawn_game_stats_range = main.game_stats_range
def set_stat_min(stat): main.gamestate = 9; main.remember_gs = 15; main.rename_target = main.game_stats_range[main.selected_stat][0]; main.rename_text = main.game_stats_range[main.selected_stat][0]; main.target_object = "Stat (Min)"; main.instance_target = main.game_stats_range[main.selected_stat][0]; main.spawn_game_stats_range = main.game_stats_range

#SFX Library
def play_sfx(sfx): sfx.play()
def add_sfx(none):
  main.gamestate = main.remember_gs
  if main.gamestate != 20 and main.gamestate != 21 and main.gamestate != 22 and main.gamestate != 23 and main.gamestate != 31 and main.gamestate != 32 and main.gamestate != 41 and main.gamestate != 53 and main.gamestate != 54 and main.gamestate != 55 and main.gamestate != 58:
    if main.choosing_sfx == 1: main.selected_sfx = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 2: main.selected_sfx2 = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 3: main.selected_sfx3 = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 4: main.selected_sfx4 = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 5: main.selected_sfx5 = main.sfx[main.selected_itemy]
  elif main.gamestate == 20:
    if main.choosing_sfx == 1: main.selected_object.step_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 2: main.selected_object.destroy_sound = main.sfx[main.selected_itemy]
    if type(main.sfx[main.selected_itemy]) == list:
      if main.choosing_sfx == 1: main.selected_object.step_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.step_sound[0])
      if main.choosing_sfx == 2: main.selected_object.destroy_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.destroy_sound[0])
    else:
      if main.selected_object.step_sound: main.selected_object.step_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.step_sound)
      if main.selected_object.destroy_sound: main.selected_object.destroy_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.destroy_sound)
  elif main.gamestate == 21:
    if main.choosing_sfx == 1: main.selected_object.sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 2: main.selected_object.debt_drop_sound = main.sfx[main.selected_itemy]
    if type(main.sfx[main.selected_itemy]) == list:
      if main.choosing_sfx == 1: main.selected_object.sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.sound[0])
      if main.choosing_sfx == 2: main.selected_object.debt_drop_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.debt_drop_sound[0])
    else:
      if main.selected_object.sound: main.selected_object.sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.sound)
      if main.selected_object.debt_drop_sound: main.selected_object.debt_drop_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.debt_drop_sound)
  elif main.gamestate == 22:
    if main.choosing_sfx == 1: main.selected_object.enter_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 2: main.selected_object.exit_sound = main.sfx[main.selected_itemy]
    if type(main.sfx[main.selected_itemy]) == list:
      if main.choosing_sfx == 1: main.selected_object.enter_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.enter_sound[0])
      if main.choosing_sfx == 2: main.selected_object.exit_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.exit_sound[0])
    else:
      if main.selected_object.enter_sound: main.selected_object.enter_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.enter_sound)
      if main.selected_object.exit_sound: main.selected_object.exit_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.exit_sound)
  elif main.gamestate == 23:
    if main.choosing_sfx == 1: main.selected_object.jump_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 2: main.selected_object.land_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 3: main.selected_object.defeat_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 4: main.selected_object.trap_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 5: main.selected_object.notice_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 6: main.selected_object.speech_sound = main.sfx[main.selected_itemy]
    if type(main.sfx[main.selected_itemy]) == list:
      if main.choosing_sfx == 1: main.selected_object.jump_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.jump_sound[0])
      if main.choosing_sfx == 2: main.selected_object.land_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.land_sound[0])
      if main.choosing_sfx == 3: main.selected_object.defeat_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.defeat_sound[0])
      if main.choosing_sfx == 4: main.selected_object.trap_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.trap_sound[0])
      if main.choosing_sfx == 5: main.selected_object.notice_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.notice_sound[0])
      if main.choosing_sfx == 6: main.selected_object.speech_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.speech_sound[0])
    else:
      if main.selected_object.jump_sound: main.selected_object.jump_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.jump_sound)
      if main.selected_object.land_sound: main.selected_object.land_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.land_sound)
      if main.selected_object.defeat_sound: main.selected_object.defeat_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.defeat_sound)
      if main.selected_object.trap_sound: main.selected_object.trap_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.trap_sound)
      if main.selected_object.notice_sound: main.selected_object.notice_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.notice_sound)
      if main.selected_object.speech_sound: main.selected_object.speech_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.speech_sound)
  elif main.gamestate == 31:
    main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].sound = main.sfx[main.selected_itemy]
    if type(main.sfx[main.selected_itemy]) == list: main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].sound[0])
    else: main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].sound)
  elif main.gamestate == 32:
    if main.choosing_sfx == 1: main.selected_object.hover_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 2: main.selected_object.enter_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 3: main.selected_object.exit_sound = main.sfx[main.selected_itemy]
    if type(main.sfx[main.selected_itemy]) == list:
      if main.choosing_sfx == 1: main.selected_object.hover_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.hover_sound[0])
      if main.choosing_sfx == 2: main.selected_object.enter_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.enter_sound[0])
      if main.choosing_sfx == 3: main.selected_object.exit_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.exit_sound[0])
    else:
      if main.selected_object.hover_sound: main.selected_object.hover_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.hover_sound)
      if main.selected_object.enter_sound: main.selected_object.enter_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.enter_sound)
      if main.selected_object.exit_sound: main.selected_object.exit_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.selected_object.exit_sound)
  elif main.gamestate == 41:
    main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["SFX"] = main.sfx[main.selected_itemy]
  elif main.gamestate == 53:
    if main.choosing_sfx == 1: main.tile_types[main.selected_tile_type]["step_sfx"] = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 2: main.tile_types[main.selected_tile_type]["destr_sfx"] = main.sfx[main.selected_itemy]
  elif main.gamestate == 54:
    if main.choosing_sfx == 1: main.character_types[main.selected_character_type]["object"].jump_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 2: main.character_types[main.selected_character_type]["object"].land_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 3: main.character_types[main.selected_character_type]["object"].beat_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 4: main.character_types[main.selected_character_type]["object"].hurt_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 5: main.character_types[main.selected_character_type]["object"].defeat_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 6: main.character_types[main.selected_character_type]["object"].trap_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 7: main.character_types[main.selected_character_type]["object"].notice_sound = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 8: main.character_types[main.selected_character_type]["object"].speech_sound = main.sfx[main.selected_itemy]
    if type(main.sfx[main.selected_itemy]) == list:
      if main.choosing_sfx == 1: main.character_types[main.selected_character_type]["object"].jump_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].jump_sound[0])
      if main.choosing_sfx == 2: main.character_types[main.selected_character_type]["object"].land_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].land_sound[0])
      if main.choosing_sfx == 3: main.character_types[main.selected_character_type]["object"].beat_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].beat_sound[0])
      if main.choosing_sfx == 4: main.character_types[main.selected_character_type]["object"].hurt_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].hurt_sound[0])
      if main.choosing_sfx == 5: main.character_types[main.selected_character_type]["object"].defeat_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].defeat_sound[0])
      if main.choosing_sfx == 6: main.character_types[main.selected_character_type]["object"].trap_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].trap_sound[0])
      if main.choosing_sfx == 7: main.character_types[main.selected_character_type]["object"].notice_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].notice_sound[0])
      if main.choosing_sfx == 8: main.character_types[main.selected_character_type]["object"].speech_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].speech_sound[0])
    else:
      if main.character_types[main.selected_character_type]["object"].jump_sound: main.character_types[main.selected_character_type]["object"].jump_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].jump_sound)
      if main.character_types[main.selected_character_type]["object"].land_sound: main.character_types[main.selected_character_type]["object"].land_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].land_sound)
      if main.character_types[main.selected_character_type]["object"].beat_sound: main.character_types[main.selected_character_type]["object"].beat_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].beat_sound)
      if main.character_types[main.selected_character_type]["object"].hurt_sound: main.character_types[main.selected_character_type]["object"].hurt_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].hurt_sound)
      if main.character_types[main.selected_character_type]["object"].defeat_sound: main.character_types[main.selected_character_type]["object"].defeat_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].defeat_sound)
      if main.character_types[main.selected_character_type]["object"].trap_sound: main.character_types[main.selected_character_type]["object"].trap_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].trap_sound)
      if main.character_types[main.selected_character_type]["object"].notice_sound: main.character_types[main.selected_character_type]["object"].notice_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].notice_sound)
      if main.character_types[main.selected_character_type]["object"].speech_sound: main.character_types[main.selected_character_type]["object"].speech_sfx = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.character_types[main.selected_character_type]["object"].speech_sound)
  elif main.gamestate == 55:
    if main.choosing_sfx == 1: main.collectible_types[main.selected_collectible_type]["sfx"] = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 2: main.collectible_types[main.selected_collectible_type]["debt_sfx"] = main.sfx[main.selected_itemy]
    if main.choosing_sfx == 3: main.collectible_types[main.selected_collectible_type]["blocked_sfx"] = main.sfx[main.selected_itemy]
  elif main.gamestate == 58:
    if main.choosing_sfx == 1:
      main.rooms[main.selected_room].menu["down_s"] = main.sfx[main.selected_itemy]
      if type(main.sfx[main.selected_itemy]) != list: main.rooms[main.selected_room].menu["down_sfx"] = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.sfx[main.selected_itemy])
    if main.choosing_sfx == 2:
      main.rooms[main.selected_room].menu["up_s"] = main.sfx[main.selected_itemy]
      if type(main.sfx[main.selected_itemy]) != list: main.rooms[main.selected_room].menu["up_sfx"] = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.sfx[main.selected_itemy])
    if main.choosing_sfx == 3:
      for button in main.rooms[main.selected_room].menu["items"]:
        if button["I"] == main.selected_menu_item_index:
          button["S"] = main.sfx[main.selected_itemy]
          if type(main.sfx[main.selected_itemy]) != list: button["SFX"] = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.sfx[main.selected_itemy])
def remove_sfx(none):
  main.gamestate = main.remember_gs
  if main.gamestate != 20 and main.gamestate != 21 and main.gamestate != 22 and main.gamestate != 23 and main.gamestate != 31 and main.gamestate != 41 and main.gamestate != 53 and main.gamestate != 54 and main.gamestate != 55 and main.gamestate != 58:
    if main.choosing_sfx == 1: main.selected_sfx = ""
    if main.choosing_sfx == 2: main.selected_sfx2 = ""
    if main.choosing_sfx == 3: main.selected_sfx3 = ""
    if main.choosing_sfx == 4: main.selected_sfx4 = ""
    if main.choosing_sfx == 5: main.selected_sfx5 = ""
  elif main.gamestate == 20:
    if main.choosing_sfx == 1: main.selected_object.step_sound = ""
    if main.choosing_sfx == 2: main.selected_object.destroy_sound = ""
  elif main.gamestate == 21:
    if main.choosing_sfx == 1: main.selected_object.sound = ""
    if main.choosing_sfx == 2: main.selected_object.debt_drop_sound = ""
  elif main.gamestate == 22:
    if main.choosing_sfx == 1: main.selected_object.enter_sound = ""
    if main.choosing_sfx == 2: main.selected_object.exit_sound = ""
  elif main.gamestate == 23:
    if main.choosing_sfx == 1: main.selected_object.jump_sound = ""
    if main.choosing_sfx == 2: main.selected_object.land_sound = ""
    if main.choosing_sfx == 3: main.selected_object.defeat_sound = ""
    if main.choosing_sfx == 4: main.selected_object.trap_sound = ""
    if main.choosing_sfx == 5: main.selected_object.notice_sound = ""
    if main.choosing_sfx == 6: main.selected_object.speech_sound = ""
  elif main.gamestate == 31:
    main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].sound = ""
    main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].sfx = None
  elif main.gamestate == 41:
    main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["SFX"] = ""
  elif main.gamestate == 53:
    if main.choosing_sfx == 1: main.tile_types[main.selected_tile_type]["step_sfx"] = ""
    if main.choosing_sfx == 2: main.tile_types[main.selected_tile_type]["destr_sfx"] = ""
  elif main.gamestate == 54:
    if main.choosing_sfx == 1: main.character_types[main.selected_character_type]["object"].jump_sound = ""
    if main.choosing_sfx == 2: main.character_types[main.selected_character_type]["object"].land_sound = ""
    if main.choosing_sfx == 3: main.character_types[main.selected_character_type]["object"].beat_sound = ""
    if main.choosing_sfx == 4: main.character_types[main.selected_character_type]["object"].hurt_sound = ""
    if main.choosing_sfx == 5: main.character_types[main.selected_character_type]["object"].defeat_sound = ""
    if main.choosing_sfx == 6: main.character_types[main.selected_character_type]["object"].trap_sound = ""
    if main.choosing_sfx == 7: main.character_types[main.selected_character_type]["object"].notice_sound = ""
    if main.choosing_sfx == 8: main.character_types[main.selected_character_type]["object"].speech_sound = ""
  elif main.gamestate == 55:
    if main.choosing_sfx == 1: main.collectible_types[main.selected_collectible_type]["step_sfx"] = ""
    if main.choosing_sfx == 2: main.collectible_types[main.selected_collectible_type]["destr_sfx"] = ""
    if main.choosing_sfx == 3: main.collectible_types[main.selected_collectible_type]["blocked_sfx"] = ""
  elif main.gamestate == 58:
    if main.choosing_sfx == 1:
      main.rooms[main.selected_room].menu["down_s"] = ""
      main.rooms[main.selected_room].menu["down_sfx"] = None
    if main.choosing_sfx == 2:
      main.rooms[main.selected_room].menu["up_s"] = ""
      main.rooms[main.selected_room].menu["up_sfx"] = None
    if main.choosing_sfx == 3:
      for button in main.rooms[main.selected_room].menu["items"]:
        if button["I"] == main.selected_menu_item_index:
          button["S"] = ""
          button["SFX"] = None

#BG Library
def add_bg(none): main.gamestate = 0; main.rooms[main.selected_room].backgrounds.append(Background(snapint((WIDTH / 2) + main.camera.scroll[0], main.tiles_size), snapint((HEIGHT / 2) + main.camera.scroll[1], main.tiles_size), "Assets/backgrounds/" + main.backgrounds[main.selected_itemy], main.selected_speed, main.selected_value, main=main)); main.selected_speed, main.selected_value = [0, 0], 0; main.buttons[0].append(Button(1 + (33 * (len(main.rooms[main.selected_room].backgrounds) - 1)), HEIGHT - 50, 32, 16, f"BG {str(len(main.rooms[main.selected_room].backgrounds))} Options", "", background_options, len(main.rooms[main.selected_room].backgrounds), button_type="Background Layer", room=main.selected_room))
def change_speedx(by): main.selected_speed[0] += by
def change_speedy(by): main.selected_speed[1] += by

#BG Options
def change_distance_bg(by): main.rooms[main.selected_room].backgrounds[main.selected_background].distance += by
def delete_bg(none): main.rooms[main.selected_room].backgrounds.remove(main.rooms[main.selected_room].backgrounds[main.selected_background]); main.gamestate = 0; main.selected_object = None; main.selected_background = 0
def change_speed_x_bg(by): main.rooms[main.selected_room].backgrounds[main.selected_background].speed[0] += by
def change_speed_y_bg(by): main.rooms[main.selected_room].backgrounds[main.selected_background].speed[1] += by
def change_x_bg(by): main.rooms[main.selected_room].backgrounds[main.selected_background].rect.x += by; main.rooms[main.selected_room].backgrounds[main.selected_background].rect.x = snapint(main.rooms[main.selected_room].backgrounds[main.selected_background].rect.x, 10); main.rooms[main.selected_room].backgrounds[main.selected_background].spawn_location[0] = main.rooms[main.selected_room].backgrounds[main.selected_background].rect.x
def change_y_bg(by): main.rooms[main.selected_room].backgrounds[main.selected_background].rect.y += by; main.rooms[main.selected_room].backgrounds[main.selected_background].rect.y = snapint(main.rooms[main.selected_room].backgrounds[main.selected_background].rect.y, 10); main.rooms[main.selected_room].backgrounds[main.selected_background].spawn_location[1] = main.rooms[main.selected_room].backgrounds[main.selected_background].rect.y
def repeat_x_bg(none): main.rooms[main.selected_room].backgrounds[main.selected_background].repeat_x = not main.rooms[main.selected_room].backgrounds[main.selected_background].repeat_x
def repeat_y_bg(none): main.rooms[main.selected_room].backgrounds[main.selected_background].repeat_y = not main.rooms[main.selected_room].backgrounds[main.selected_background].repeat_y
def toggle_x_scroll_bg(none): main.rooms[main.selected_room].backgrounds[main.selected_background].x_scroll = not main.rooms[main.selected_room].backgrounds[main.selected_background].x_scroll
def toggle_y_scroll_bg(none): main.rooms[main.selected_room].backgrounds[main.selected_background].y_scroll = not main.rooms[main.selected_room].backgrounds[main.selected_background].y_scroll
def toggle_hm_bg(none): main.rooms[main.selected_room].backgrounds[main.selected_background].hm_for_move = not main.rooms[main.selected_room].backgrounds[main.selected_background].hm_for_move
def toggle_vm_bg(none): main.rooms[main.selected_room].backgrounds[main.selected_background].vm_for_move = not main.rooms[main.selected_room].backgrounds[main.selected_background].vm_for_move
def change_x_marge_bg(by): main.rooms[main.selected_room].backgrounds[main.selected_background].marges[0] += by
def change_y_marge_bg(by): main.rooms[main.selected_room].backgrounds[main.selected_background].marges[1] += by
def change_bg_order_front(none):
  try: main.rooms[main.selected_room].backgrounds[main.selected_background], main.rooms[main.selected_room].backgrounds[main.selected_background - 1] = main.rooms[main.selected_room].backgrounds[main.selected_background - 1], main.rooms[main.selected_room].backgrounds[main.selected_background]
  except: pass
def change_bg_order_back(none):
  try: main.rooms[main.selected_room].backgrounds[main.selected_background], main.rooms[main.selected_room].backgrounds[main.selected_background + 1] = main.rooms[main.selected_room].backgrounds[main.selected_background + 1], main.rooms[main.selected_room].backgrounds[main.selected_background]
  except: pass
def change_animation_speed(by):
  if isinstance(main.selected_object, Tile):
    main.selected_object.anim_speed += by
    if main.selected_object.anim_speed < 0: main.selected_object.anim_speed = 0
  if isinstance(main.selected_object, Background):
    main.rooms[main.selected_room].backgrounds[main.selected_background].anim_speed += by
    if main.rooms[main.selected_room].backgrounds[main.selected_background].anim_speed < 0: main.rooms[main.selected_room].backgrounds[main.selected_background].anim_speed = 0
def toggle_foreground(none): main.rooms[main.selected_room].backgrounds[main.selected_background].foreground = not main.rooms[main.selected_room].backgrounds[main.selected_background].foreground
def set_bg_to_chr(none): main.gamestate = 29; main.remember_gs = 18
def copy_image_path_from_bg(none): main.clipboard_image_path = main.rooms[main.selected_room].backgrounds[main.selected_background].image_file_without_dir; main.clipboard_anim_rate = main.rooms[main.selected_room].backgrounds[main.selected_background].anim_speed
def edit_text_behaviors(none): main.gamestate, main.remember_gs = 60, 43

def add_shader(remember_gs): main.gamestate = 48; main.remember_gs = remember_gs
def apply_shader(none):
  main.rooms[main.selected_room].shader = main.shaders[main.selected_itemy]
  with open(main.active_directory + "Shaders/" + main.shaders[main.selected_itemy], "r", encoding="utf-8") as file: shader_code = file.read()
  main.rooms[main.selected_room].shader_prog = ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=shader_code)
  main.rooms[main.selected_room].shader_vao = ctx.vertex_array(main.rooms[main.selected_room].shader_prog, [shader_buffer])
  main.gamestate = main.remember_gs
def remove_shader(shader): main.rooms[main.selected_room].shader = ""; main.rooms[main.selected_room].shader_prog = 0; main.rooms[main.selected_room].shader_vao = 0; main.gamestate = main.remember_gs

#Edit Player
def change_speed_oe(by): main.selected_object.speed += by
def change_leap_oe(by): main.selected_object.jump_force += by
def select_player(character):
  main.selected_object.character_spawn = main.character_types[next(key for key, value in main.character_types.items() if value.get("type") == character)]["object"]
  main.selected_object.character = main.character_types[next(key for key, value in main.character_types.items() if value.get("type") == character)]["object"]
  main.selected_object.name = character
  # main.selected_object.states = []
  
  # if os.listdir(main.active_directory + "Assets/characters/" + player) == ["down", "left", "right", "up"]: main.selected_object.mode = "topdown"; mode = "topdown"
  # else: main.selected_object.mode = "platformer"; mode = "platformer"
  
  # if main.selected_object.image != None:
  #   if mode == "platformer": main.selected_object.images_dict, main.selected_object.states = main.selected_object.load_images(main.active_directory + "Assets/characters/" + player); main.selected_object.rect.width = pygame.image.load(main.active_directory + "Assets/characters/" + player + "/idle/1.png").get_width(); main.selected_object.rect.height = pygame.image.load(main.active_directory + "Assets/characters/" + player + "/idle/1.png").get_height()
  #   elif mode == "topdown":
  #     main.selected_object.images_dict = {"down": {}, "left": {}, "right": {}, "up": {}}
  #     for dir in ["down", "left", "right", "up"]: main.selected_object.images_dict[dir], main.selected_object.states = main.selected_object.load_images(main.active_directory + "Assets/characters/" + main.selected_object.character + "/" + dir)
  #     main.selected_object.rect.width = pygame.image.load(main.active_directory + "Assets/characters/" + player + "/down/idle/1.png").get_width(); main.selected_object.rect.height = pygame.image.load(main.active_directory + "Assets/characters/" + player + "/down/idle/1.png").get_height()
  #   main.selected_object.actions = {}
  #   if mode == "platformer":
  #     for state in main.selected_object.states:
  #       try: main.selected_object.actions[state] = Action(main.selected_object.state_anims[state][0], main.selected_object.state_anims[state][1], main.selected_object.images_dict[state], main.selected_object)
  #       except: main.selected_object.actions[state] = Action(120, True, main.selected_object.images_dict[state], main.selected_object)
  #   elif mode == "topdown":
  #     main.selected_object.actions = {"down": {}, "left": {}, "right": {}, "up": {}}
  #     for dir in ["down", "left", "right", "up"]:
  #       for state in main.selected_object.states:
  #         try: main.selected_object.actions[dir][state.lower()] = Action(main.selected_object.state_anims[state.lower()][0], main.selected_object.state_anims[state.lower()][1], main.selected_object.images_dict[state.lower()], main.selected_object)
  #         except:
  #           try: main.selected_object.actions[dir][state.lower()] = Action(100, True, main.selected_object.images_dict[state.lower()], main.selected_object)
  #           except: pass
  # else: main.selected_object.animation = None
  # main.selected_object.mode = mode

def change_team(by): main.selected_object.team += by
def change_spawn_x_oe(by):
  try: main.selected_object.spawn_location[0] += by * main.tiles_size; main.selected_object.rect.x += by * main.tiles_size
  except: pass
def change_spawn_y_oe(by):
  try: main.selected_object.spawn_location[1] += by * main.tiles_size; main.selected_object.rect.y += by * main.tiles_size
  except: pass
def toggle_player_in(none): main.selected_object.in_spawn = not main.selected_object.in_spawn
def hide_player_if_out(none): main.selected_object.hide_if_out = not main.selected_object.hide_if_out
def toggle_hump_head_cancel_y_momentum(none): main.selected_object.bump_cancel_momentum = not main.selected_object.bump_cancel_momentum
def toggle_accelerated_travel(none): main.selected_object.accelerated_travel = not main.selected_object.accelerated_travel
def edit_action_controls(none):
  main.gamestate = 31; main.selected_frame = 1
  #main.on_page = 1
  #for player in main.players:
  #  if player.character == main.selected_object.character: main.selected_object = player
  main.buttons[31].clear()
  main.buttons[31].append(Button(( (WIDTH / 4) - 10) + 46, 397, 15, 15, "A Button", "", select_button, "A Button"))
  main.buttons[31].append(Button(( (WIDTH / 4) - 10) + 32, 411, 15, 15, "B Button", "", select_button, "B Button"))
  main.buttons[31].append(Button(( (WIDTH / 4) - 10) + 20, 397, 15, 15, "Y Button", "", select_button, "Y Button"))
  main.buttons[31].append(Button(( (WIDTH / 4) - 10) + 32, 385, 15, 15, "X Button", "", select_button, "X Button"))
  main.buttons[31].append(Button(( (WIDTH / 4) - 10) - 60, 397, 15, 15, "D-Pad Left", "", select_button, "D-Pad Left"))
  main.buttons[31].append(Button(( (WIDTH / 4) - 10) - 48, 410, 15, 15, "D-Pad Down", "", select_button, "D-Pad Down"))
  main.buttons[31].append(Button(( (WIDTH / 4) - 10) - 36, 397, 15, 15, "D-Pad Right", "", select_button, "D-Pad Right"))
  main.buttons[31].append(Button(( (WIDTH / 4) - 10) - 48, 385, 15, 15, "D-Pad Up", "", select_button, "D-Pad Up"))
  main.buttons[31].append(Button(( (WIDTH / 4) - 10) + 3, 384, 15, 15, "Start", "", select_button, "Start"))
  main.buttons[31].append(Button(( (WIDTH / 4) - 10) - 18, 384, 15, 15, "Select", "", select_button, "Select"))
  main.buttons[31].append(Button(( (WIDTH / 4) - 10) + 44, 371, 15, 15, "R Shoulder", "", select_button, "R Shoulder"))
  main.buttons[31].append(Button(( (WIDTH / 4) - 10) - 58, 371, 15, 15, "L Shoulder", "", select_button, "L Shoulder"))
  if main.character_types[main.selected_character_type]["object"].mode == "platformer":
    for x, button in enumerate(main.character_types[main.selected_character_type]["object"].actions): main.buttons[31].append(Button(300, 45 + (x * 24), maxint(fontsmall.render(button, True, "White").get_width() * 1.3, 120), 22, "Link/Customize Action", button, select_state, target=button, font=fontsmall, button_type="State", text_color={True: "Blue", False: "White"}[button in ["idle", "walk", "jump", "away", "door", "fly", "turn", "walkstart", "slide", "climb", "defeat"]]))
  elif main.character_types[main.selected_character_type]["object"].mode == "topdown": 
    for x, button in enumerate(main.character_types[main.selected_character_type]["object"].actions[main.selected_direction]): main.buttons[31].append(Button(300, 45 + (x * 24), maxint(fontsmall.render(button, True, "White").get_width() * 1.3, 120), 22, "Link/Customize Action", button, select_state, target=button, font=fontsmall, button_type="State", text_color="White"))
  if main.selected_state:
    for x, button in enumerate([("Unlink Button", "unlink", unlink_button), ("Deselect State", "check mark", deselect_state)]):
      main.buttons[31].append(Button(54 + (x * 34), HEIGHT - 121, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    for x, button in enumerate([("Side", "side"), ("Up", "up"), ("Down", "down", ), ("All Around", "all around"), ("Up + Down", "updown"), ("Right", "right"), ("Left", "left"), ("No", "none")]):
      main.buttons[31].append(Button(185 + (math.floor(x / 4) * 17), ((HEIGHT - 85) + ((x % 4) * 17)), 16, 16, button[0] + " Combo", "Assets/editor/combo " + button[1] + ".png", state_set_combo, button[1]))
    for x, button in enumerate([("Press Trigger", "button trigger press", "Press"), ("Hold Trigger", "button trigger hold", "Hold"), ("Release Trigger", "button trigger release", "Release")]):
      main.buttons[31].append(Button(54 + ((x + 2) * 34), HEIGHT - 121, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", state_trigger_mode, button[2]))
    if main.selected_state == "away":
      for x, button in enumerate([("Decrease Sleep Delay", "less", -(main.fps // 4)), ("İncrease Sleep Delay", "more", (main.fps // 4))]):
        main.buttons[31].append(Button(54 + (x * 80), HEIGHT - 146, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", state_away_delay, target=button[2]))
      for x, button in enumerate([("Decrease Wake Up Delay", "less", -(main.fps // 4)), ("İncrease Wake Up Delay", "more", (main.fps // 4))]):
        main.buttons[31].append(Button(149 + (x * 80), HEIGHT - 146, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", state_wake_delay, target=button[2]))
    main.buttons[31].append(Button(WIDTH - 119, 8, 32, 32, "Prioritize Action", "Assets/editor/crown.png", prioritize_action))
    for x, button in enumerate([("Allow Moving during Action", "run button", state_allow_travel), ("Allow Jumping during Action", "jump button", state_allow_jump), ("Allow Facing other Sides during Action", "flip", state_allow_flip), ("Apply/Cancel Gravity during Action", "galaxy", state_apply_gravity), ("Toggle Aerial Action", "cloud", state_apply_aerial), ("Toggle Terrestial Action", "standing", state_apply_terrestial), ("Toggle Subaqueous Action", "underwater", state_apply_subaqueous), ("Cancel Action if Walking", "arrow below cross", state_cancel_on_walk), ("Cancel Action if on Ground", "smashdown", state_cancel_on_ground), ("Cancel Action if Jumped", "cut arrow up", state_cancel_on_jump), ("Cancel Action if Hit", "explode", state_cancel_on_hit), ("Enable Relative to Direction", "right overpower", state_relative_to_dir), ("Continue Action Until Cancelled", "point to cross", state_continue_until_cancel)]):
      main.buttons[31].append(Button(WIDTH - 85, 8 + (x * 33), 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    for x, button in enumerate([("Decrease Animation Speed", "less", -10), ("İncrease Animation Speed", "more", 10)]):
      main.buttons[31].append(Button(60 + (x * 132), 50, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_anim_speed, target=button[2]))
    main.buttons[31].append(Button(222, 50, 32, 32, "Toggle Looping", "Assets/editor/repeat.png", toggle_anim_loop))
    for x, button in enumerate([("Decrease Frame's X Motion", "less", -1), ("İncrease Frame's X Motion", "more", 1)]):
      main.buttons[31].append(Button(60 + (x * 80), 93, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_move_x, target=button[2], page=1))
    for x, button in enumerate([("Decrease Frame's Y Motion", "less", -1), ("İncrease Frame's Y Motion", "more", 1)]):
      main.buttons[31].append(Button(155 + (x * 80), 93, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_move_y, target=button[2], page=1))
    for x, button in enumerate([("Decrease Frame's X Velocity", "less", -1), ("İncrease Frame's X Velocity", "more", 1)]):
      main.buttons[31].append(Button(60 + (x * 100), 113, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_gain_x, target=button[2], page=1))
    for x, button in enumerate([("Decrease Frame's Y Velocity", "less", -1), ("İncrease Frame's Y Velocity", "more", 1)]):
      main.buttons[31].append(Button(175 + (x * 100), 113, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_gain_y, target=button[2], page=1))
    for x, button in enumerate([("Decrease Frame's Damage", "less", -1), ("İncrease Frame's Damage", "more", 1)]):
      main.buttons[31].append(Button(62 + (x * 90), 133, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_damage, target=button[2], page=1))
    for x, button in enumerate([("Decrease Frame's Self-Damage", "less", -1), ("İncrease Frame's Self-Damage", "more", 1)]):
      main.buttons[31].append(Button(167 + (x * 115), 133, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_self_damage, target=button[2], page=1))
    for x, button in enumerate([("Decrease Frame's Knockback X", "less", -0.1), ("İncrease Frame's Knockback X", "more", 0.1)]):
      main.buttons[31].append(Button(62 + (x * 60), 153, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_knockback_x, target=button[2], page=1))
    for x, button in enumerate([("Decrease Frame's Knockback Y", "less", -0.1), ("İncrease Frame's Knockback Y", "more", 0.1)]):
      main.buttons[31].append(Button(62 + (x * 60), 173, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_knockback_y, target=button[2], page=1))
    for x, button in enumerate([("Decrease Loop's Return", "less", -1), ("İncrease Loop's Return", "more", 1)]):
      main.buttons[31].append(Button(137 + (x * 80), 153, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_loop_return, target=button[2], page=1))
    for x, button in enumerate([("Decrease Loop Count", "less", -1), ("İncrease Loop Count", "more", 1)]):
      main.buttons[31].append(Button(233 + (x * 45), 153, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_loops, target=button[2], page=1))
    for x, button in enumerate([("Decrease Combo Unit", "less", -1), ("İncrease Combo Unit", "more", 1)]):
      main.buttons[31].append(Button(137 + (x * 115), 173, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_combo_unit, target=button[2], page=1))
    main.buttons[31].append(Button(62, 189, 16, 16, "Set Sound Effect", "Assets/editor/note.png", select_sfx, target=31, page=1))

    for x, button in enumerate([("Decrease Selected Projectile", "less", -1), ("İncrease Selected Projectile", "more", 1)]):
      main.buttons[31].append(Button(60 + (x * 100), 93, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_selected_projectile, target=button[2], page=2))
    for x, button in enumerate([("Add Projectile to Frame", "add", add_projectile_to_frant), ("Remove Projectile to Frame", "minus", remove_projectile_to_frant)]):
      main.buttons[31].append(Button(60 + (x * 18), 112, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", button[2], page=2))
    
    for x, button in enumerate([("Decrease Frame's X Hitbox", "less", -1), ("İncrease Frame's X Hitbox", "more", 1)]):
      main.buttons[31].append(Button(170 + (x * 50), 94, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_hitbox_x, target=button[2], page=3))
    for x, button in enumerate([("Decrease Frame's Y Hitbox", "less", -1), ("İncrease Frame's Y Hitbox", "more", 1)]):
      main.buttons[31].append(Button(170 + (x * 50), 114, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_hitbox_y, target=button[2], page=3))
    for x, button in enumerate([("Decrease Frame's Hitbox Width", "less", -1), ("İncrease Frame's Hitbox Width", "more", 1)]):
      main.buttons[31].append(Button(170 + (x * 50), 134, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_hitbox_width, target=button[2], page=3))
    for x, button in enumerate([("Decrease Frame's Hitbox Height", "less", -1), ("İncrease Frame's Hitbox Height", "more", 1)]):
      main.buttons[31].append(Button(170 + (x * 50), 154, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_hitbox_height, target=button[2], page=3))
    for x, button in enumerate([("Decrease Frame's X Attack Hitbox", "less", -1), ("İncrease Frame's X Attack Hitbox", "more", 1)]):
      main.buttons[31].append(Button(233 + (x * 50), 94, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_attack_hitbox_x, target=button[2], page=3))
    for x, button in enumerate([("Decrease Frame's Y Attack Hitbox", "less", -1), ("İncrease Frame's Y Attack Hitbox", "more", 1)]):
      main.buttons[31].append(Button(233 + (x * 50), 114, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_attack_hitbox_y, target=button[2], page=3))
    for x, button in enumerate([("Decrease Frame's Attack Hitbox Width", "less", -1), ("İncrease Frame's Attack Hitbox Width", "more", 1)]):
      main.buttons[31].append(Button(233 + (x * 50), 134, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_attack_hitbox_width, target=button[2], page=3))
    for x, button in enumerate([("Decrease Frame's Attack Hitbox Height", "less", -1), ("İncrease Frame's Attack Hitbox Height", "more", 1)]):
      main.buttons[31].append(Button(233 + (x * 50), 154, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_frame_attack_hitbox_height, target=button[2], page=3))
    main.buttons[31].append(Button(175, 175, fontsmall.render("Apply to All", True, "White").get_width() + 5, 24, "(Excluding Attack)", "Apply to All", change_frame_hitbox_apply_to_all, page=3, font=fontsmall, shift_x_hitbox=5, shift_y_hitbox=-5))
    
    width = 0; height = 0
    for stat in (stat for stat in main.game_stats if main.game_stats[stat] == bool):
      text = fontsmaller.render(stat + ",", True, "White")
      if width + text.get_width() > WIDTH / 2.5: height += 16; width = 0
      width += text.get_width() + 10
      main.buttons[31].append(Button(230 + width - text.get_width(), 385 + height, text.get_width() + 7, 16, "Set Action for a Condition", stat, select_ability_condition, target=stat, text_color="Light Yellow", font=fontsmaller))
  try:
    if "topdown" in main.character_types[main.selected_character_type]['flags']: main.chr_frames = os.listdir(main.active_directory + f"Assets/characters/{main.character_types[main.selected_character_type]['type']}/" + main.dir_preview_mode + "/" + main.selected_state + "/")
    else: main.chr_frames = os.listdir(main.active_directory + f"Assets/characters/{main.character_types[main.selected_character_type]['type']}/{main.selected_state}/")
  except: main.character_types[main.selected_character_type]['object'].actions.pop(main.selected_state.lower(), None); deselect_state(None)
  if main.selected_state:
    if main.character_types[main.selected_character_type]["object"].mode == "platformer":
      if len(main.chr_frames) > 21:
        for index, frame in enumerate(main.chr_frames): main.buttons[31].append(Button(50 + ((index % 13) * 17), 207 + math.floor(index / 13) * 17, 16, 16, f"Frame {index + 1}", main.active_directory + "Assets/characters/" + main.character_types[main.selected_character_type]["type"] + "/" + main.selected_state + "/" + str(index + 1) + ".png", select_frame, index + 1, button_type="Frame"))
      else:
        for index, frame in enumerate(main.chr_frames): main.buttons[31].append(Button(50 + ((index % 7) * 33), 207 + math.floor(index / 7) * 33, 32, 32, f"Frame {index + 1}", main.active_directory + "Assets/characters/" + main.character_types[main.selected_character_type]["type"] + "/" + main.selected_state + "/" + str(index + 1) + ".png", select_frame, index + 1, button_type="Frame"))
    elif main.character_types[main.selected_character_type]["object"].mode == "topdown":
      if len(main.chr_frames) > 21:
        for index, frame in enumerate(main.chr_frames): main.buttons[31].append(Button(50 + ((index % 13) * 17), 207 + math.floor(index / 13) * 17, 16, 16, f"Frame {index + 1}", main.active_directory + "Assets/characters/" + main.character_types[main.selected_character_type]["type"] + "/" + main.dir_preview_mode + "/" + main.selected_state + "/" + str(index + 1) + ".png", select_frame, index + 1, button_type="Frame"))
      else:
        for index, frame in enumerate(main.chr_frames): main.buttons[31].append(Button(50 + ((index % 7) * 33), 207 + math.floor(index / 7) * 33, 32, 32, f"Frame {index + 1}", main.active_directory + "Assets/characters/" + main.character_types[main.selected_character_type]["type"] + "/" + main.dir_preview_mode + "/" + main.selected_state + "/" + str(index + 1) + ".png", select_frame, index + 1, button_type="Frame"))

#Edit Tile
def change_tile_x(by): main.selected_object.rect.x += by * main.tiles_size; main.selected_object.spawn_location[0] = main.selected_object.rect.x
def change_tile_y(by): main.selected_object.rect.y += by * main.tiles_size; main.selected_object.spawn_location[1] = main.selected_object.rect.y
def change_speed_x_oe(by): main.selected_object.speed[0] += by; main.selected_object.spawn_speed[0] += by
def change_speed_y_oe(by): main.selected_object.speed[1] += by; main.selected_object.spawn_speed[1] += by
def change_tile_chain_speed(by):
  main.selected_object.chain_speed += by
  if main.selected_object.chain_speed < 0: main.selected_object.chain_speed = 0
  if main.selected_object.chain_speed == 0: main.selected_object.instigator = False
  else: main.selected_object.instigator = True
def change_tile_hp(by):
  main.selected_object.hp += by
  if main.selected_object.hp < -1: main.selected_object.hp = 0
  main.selected_object.spawn_hp = main.selected_object.hp
def change_tile_obc(none): main.selected_object.only_breakable_by_chains = not main.selected_object.only_breakable_by_chains
def change_tile_solid(none):
  if "s" in main.selected_object.deviating_modes: main.selected_object.deviating_modes.remove("s")
  else: main.selected_object.deviating_modes.append("s")
def change_tile_flat(none):
  if "f" in main.selected_object.deviating_modes: main.selected_object.deviating_modes.remove("f")
  else: main.selected_object.deviating_modes.append("f")
def change_tile_slippery(none):
  if "sl" in main.selected_object.deviating_modes: main.selected_object.deviating_modes.remove("sl")
  else: main.selected_object.deviating_modes.append("sl")
def change_can_be_moved_by_zones(none): main.selected_object.zones_can_move = not main.selected_object.zones_can_move
def change_can_be_rotated_by_zones(none): main.selected_object.zones_can_rotate = not main.selected_object.zones_can_rotate
# def change_tile_destroy_if_stood_on(none): main.selected_object.destroy_if_stood_on = not main.selected_object.destroy_if_stood_on
# def change_tile_destroy_if_head_bump(none): main.selected_object.destroy_if_head_bump = not main.selected_object.destroy_if_head_bump
# def change_tile_destroy_anim(anim):
#   main.selected_object.destroy_anim = anim
#   if main.selected_object.destroy_anim == "disappear": main.selected_object.instigator = False
#   else: main.selected_object.instigator = True


#Edit Collectible
def select_cutscene_for_collectible(cs):
  if main.selected_object.trigger_cutscene == cs: main.selected_object.trigger_cutscene = ""
  else: main.selected_object.trigger_cutscene = cs
def go_to_prices(none):
  main.gamestate = 36
  width = 0; height = 0
  main.buttons[36].clear()
  for x, button in enumerate([("Decrease Price", "less", change_price_value, -1), ("Increase Price", "more", change_price_value, 1)]):
    main.buttons[36].append(Button(54 + (x * 180), 326, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
  for x, button in enumerate([("Decrease Price Decimal", "less", change_price_value, -0.25), ("Increase Price Decimal", "more", change_price_value, 0.25)]):
    main.buttons[36].append(Button(86 + (x * 132), 334, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
  for stat in main.game_stats:
    text = fontsmaller.render(stat + ",", True, "White")
    if width + 120 + text.get_width() > WIDTH - 30: height += 16; width = 0
    width += text.get_width() + 10
    main.buttons[36].append(Button(55 + width - text.get_width(), 190 + height, text.get_width() + 7, 16, "Use Stat", stat, change_price_stat, target=stat, text_color={int: "Light blue", bool: "Light Yellow", str: "Pink", float: "Light Green"}[main.game_stats[stat]], font=fontsmaller))
  for x, button in enumerate(["Below", "Above", "Left", "Right"]):
    main.buttons[36].append(Button(275, 100 + (x * 20), fontsmall.render(button, True, "White").get_width(), 24, "Pick Text Layout", button, pick_price_text_position, target=button, font=fontsmall))
  for x, button in enumerate(["Value Stat", "Stat Value", "Value Image", "Image Value", "Do not show"]):
    main.buttons[36].append(Button(275, 200 + (x * 20), fontsmall.render(button, True, "White").get_width(), 24, "Pick Text Mode", button, pick_price_text_mode, target=button, font=fontsmall))
  main.buttons[36].append(Button(WIDTH - 120, 27, 32, 32, "Toggle Exchange Mode", "Assets/editor/exchange.png", toggle_exchange_mode))
  main.buttons[36].append(Button(WIDTH - 86, 27, 32, 32, "Toggle Dynamic Drop Mode", "Assets/editor/decrement.png", toggle_drop_mode))

#Edit Zone
def change_x(by): main.selected_object.rect.x += by * main.tiles_size
def change_y(by): main.selected_object.rect.y += by * main.tiles_size
def change_zone_width(by):
  main.selected_object.rect.width += (by * main.tiles_size) - (int(main.selected_object.rect.width == 2) * 2)
  if main.selected_object.rect.width <= 0: main.selected_object.rect.width = 2
  main.selected_object.surface = pygame.Surface((main.selected_object.rect.width, main.selected_object.rect.height))
def change_zone_height(by):
  main.selected_object.rect.height += (by * main.tiles_size) - (int(main.selected_object.rect.height == 2) * 2)
  if main.selected_object.rect.height <= 0: main.selected_object.rect.height = 2
  main.selected_object.surface = pygame.Surface((main.selected_object.rect.width, main.selected_object.rect.height))
def select_cutscene(cs):
  if main.gamestate != 59:
    if main.selected_object.trigger_cutscene == cs: main.selected_object.trigger_cutscene = ""
    else: main.selected_object.trigger_cutscene = cs
  else:
    for button in main.rooms[main.selected_room].menu["items"]:
      if button["I"] == main.selected_menu_item_index:
        if button["A"] == cs: button["A"] = ""
        else: button["A"] = cs
def zone_multi_active(none): main.selected_object.multi_active = not main.selected_object.multi_active
def zone_entity_active(none): main.selected_object.entity_active = not main.selected_object.entity_active
def zone_ease(none): main.selected_object.ease_motion = not main.selected_object.ease_motion
def change_zone_gravity(by): main.selected_object.gravity += by
def zone_void(none): main.selected_object.void = not main.selected_object.void
def zone_dim_track(by):
  main.selected_object.track_volume += by
  if main.selected_object.track_volume < 0.0: main.selected_object.track_volume = 0.0
  if main.selected_object.track_volume > 1.0: main.selected_object.track_volume = 1.0
def zone_color(color): main.selected_object.color = color; main.selected_object.texture = pygame.image.load("Assets/editor/zone texture.png").convert_alpha(); main.selected_object.texture.fill(main.selected_object.color, special_flags=pygame.BLEND_RGB_MIN)
def change_x_overlapping_tile_speed(by): main.selected_object.tile_speed[0] += by
def change_y_overlapping_tile_speed(by): main.selected_object.tile_speed[1] += by
def change_overlapping_tile_rotational_speed(by): main.selected_object.tile_rotation += by


#Edit Entity
def set_entity_direction(dir): main.selected_object.initial_direction = dir
def set_entity_player_partner(player_index): main.selected_object.player_partner = player_index
def manage_dialogues(none):
  main.gamestate = 33; main.buttons[33].clear()
  for index, dialogue in enumerate(main.selected_object.dialogue):
    text = fontsmall.render(dialogue, True, "White")
    main.buttons[33].append(Button(53, 55 + (index * 15), text.get_width(), 20, "Select Dialogue", dialogue, select_dialogue, index, font=fontsmall, button_type="Dialogue"))
  main.buttons[33].append(Button(WIDTH - 86, 26, 32, 32, "Add Dialogue", "Assets/editor/add.png", add_dialogue))
  try:
    main.buttons[33].append(Button(WIDTH - 122, 26, 32, 32, "Delete Dialogue", "Assets/editor/delete.png", delete_dialogue))
    main.buttons[33].append(Button(WIDTH - 156, 26, 32, 32, "Set Dialogue", "Assets/editor/pencil.png", rename, main.selected_object.dialogue[main.selected_dl], 33, "Dialogue"))
  except: pass
  try:
    main.selected_object.letter_delay[main.selected_dl]
    main.buttons[33].append(Button(WIDTH - 190, 26, 32, 32, "Speed Up Letter Delay", "Assets/editor/more.png", change_dialogue_letter_delay, 5))
    main.buttons[33].append(Button(WIDTH - 250, 26, 32, 32, "Slow Down Letter Delay", "Assets/editor/less.png", change_dialogue_letter_delay, -5))
  except: pass

#Edit Cutscene
def playback_start(none):
  global FPS; main.playback_on = True; FPS = main.fps
  if pygame.mixer.music.get_pos() > 1: pygame.mixer.music.unpause()
  else: pygame.mixer.music.stop(); scs = main.selected_cutscene; clear_game(); main.selected_cutscene = scs

def playback_pause(none): global FPS; main.playback_on = False; FPS = 240; pygame.mixer.music.pause()

def playback_stop(none):
  pygame.mixer.music.stop(); global FPS; pygame.mixer.music.stop()
  for player in main.players: player.clear(); player.rect.x, player.rect.y = player.spawn_location[0], player.spawn_location[1]
  main.camera.rect.x, main.camera.rect.y = 0, 0; main.camera.scroll = [0, 0]; scs = main.selected_cutscene; clear_game(); main.selected_cutscene = scs; main.playback_on = False; FPS = 240

def scene_repos(none):
  global k_a; k_a = False
  if main.selected_object is not None:
    main.gamestate = 38
    present = False
    for key_object in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations:
      if key_object["Frame"] == main.selected_key and key_object["Object"] == main.selected_object and (key_object["Hidden"] == True or key_object["Rect"] != None): present = True
    if not present: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations.append({"Object": main.selected_object, "Frame": main.selected_key, "Rect": None, "SOCR": False, "Hidden": False, "Speed": 0, "X Speed": 0, "Y Speed": 0, "Speed": 0, "Rotate": 0, "X Scale": 0, "Y Scale": 0, "Action": "", "Dir": "", "SFX": "", "Track": "", "Show UI": [], "Hide UI": [], "B1": False, "B2": False, "I1": -1, "I2": -1, "I3": -1, "I4": -1})
    for key_index, key_object in enumerate(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations):
      if key_object["Frame"] == main.selected_key and key_object["Object"] == main.selected_object: main.selected_cutscene_attrib = key_object; main.selected_cutscene_attrib_index = key_index
def scene_move(none):
  global k_a; k_a = False
  if main.selected_object is not None:
    main.gamestate = 39
    present = False
    for key_object in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations:
      if key_object["Frame"] == main.selected_key and key_object["Object"] == main.selected_object: present = True
    if not present: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations.append({"Object": main.selected_object, "Frame": main.selected_key, "Rect": None, "SOCR": False, "Hidden": False, "Speed": 0, "X Speed": 0, "Y Speed": 0, "Speed": 0, "Rotate": 0, "X Scale": 0, "Y Scale": 0, "Action": "", "Dir": "", "SFX": "", "Track": "", "Show UI": [], "Hide UI": [], "B1": False, "B2": False, "I1": -1, "I2": -1, "I3": -1, "I4": -1})
    for key_index, key_object in enumerate(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations):
      if key_object["Frame"] == main.selected_key and key_object["Object"] == main.selected_object: main.selected_cutscene_attrib = key_object; main.selected_cutscene_attrib_index = key_index
def scene_action(none):
  global k_a; k_a = False
  main.gamestate = 40
  main.buttons[40].clear()
  present = False
  if main.selected_object != None:
    for key_object in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations:
      if key_object["Frame"] == main.selected_key and key_object["Object"] == main.selected_object: present = True
    if not present: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations.append({"Object": main.selected_object, "Frame": main.selected_key, "Rect": None, "SOCR": False, "Hidden": False, "Speed": 0, "X Speed": 0, "Y Speed": 0, "Speed": 0, "Rotate": 0, "X Scale": 0, "Y Scale": 0, "Action": "", "Dir": "", "SFX": "", "Track": "", "Show UI": [], "Hide UI": [], "B1": False, "B2": False, "I1": -1, "I2": -1, "I3": -1, "I4": -1})
    for key_index, key_object in enumerate(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations):
      if key_object["Frame"] == main.selected_key and key_object["Object"] == "Main": main.selected_cutscene_attrib = key_object; main.selected_cutscene_attrib_index = key_index
      for key_index, key_object in enumerate(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations):
        if key_object["Frame"] == main.selected_key and key_object["Object"] == main.selected_object: main.selected_cutscene_attrib = key_object; main.selected_cutscene_attrib_index = key_index
  elif main.selected_object == None:
    for key_object in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations:
      if key_object["Frame"] == main.selected_key and key_object["Object"] == "Main": present = True
    if not present: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations.append({"Object": "Main", "Frame": main.selected_key, "Rect": None, "SOCR": False, "Hidden": False, "Speed": 0, "X Speed": 0, "Y Speed": 0, "Rotate": 10, "Speed": 0, "X Scale": 0, "Y Scale": 0, "Action": "", "Dir": "", "SFX": "", "Track": "", "Show UI": [], "Hide UI": [], "B1": False, "B2": False, "I1": -1, "I2": -1, "I3": -1, "I4": -1})
    for key_index, key_object in enumerate(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations):
      if key_object["Frame"] == main.selected_key and key_object["Object"] == "Main": main.selected_cutscene_attrib = key_object; main.selected_cutscene_attrib_index = key_index
  if type(main.selected_object).__name__ == "Camera":
    main.buttons[40].append(Button(426, HEIGHT - 58, 32, 32, "Follow Player", "Assets/editor/scroll.png", set_hidden_for_key))
    main.buttons[40].append(Button(426, HEIGHT - 92, 32, 32, "Follow Player", "Assets/editor/horizontal mirror.png", cutscene_allow_camera_horizontal_mirror))
    main.buttons[40].append(Button(426, HEIGHT - 126, 32, 32, "Follow Player", "Assets/editor/vertical mirror.png", cutscene_allow_camera_vertical_mirror))
    for y, button in enumerate([("Change Border for Key " + str(main.selected_key), "Right Border", change_borders, "right"), ("Change Border for Key " + str(main.selected_key), "Left Border", change_borders, "left"), ("Change Border for Key " + str(main.selected_key), "Top Border", change_borders, "top"), ("Change Border for Key " + str(main.selected_key), "Bottom Border", change_borders, "bottom")]):
      main.buttons[40].append(Button(55, 156 + (y * 34), 128, 32, button[0], button[1], button[2], target=str(main.rooms[main.selected_room].borders[button[3]]), target_object=button[3], target_gs=40))
  elif type(main.selected_object).__name__ == "Player" or type(main.selected_object).__name__ == "Entity":
    for x, button in enumerate(main.selected_object.character.states): main.buttons[40].append(Button(300, 60 + (x * 28), fontsmall.render(button, True, "White").get_width() * 1.3, 24, "Set Action for Frame " + str(main.selected_key), button, select_state_for_key, target=button, font=fontsmall, button_type="Action for Frame"))
    for x, button in enumerate((("Face Right", "arrow right", "right"), ("Face Left", "arrow left", "left"), ("Face Up", "arrow up", "up"), ("Face Down", "arrow down", "down"))): main.buttons[40].append(Button(58 + (x * 36), 64, 32, 32, button[0] + " for Frame " + str(main.selected_key), "Assets/editor/" + button[1] + ".png", face_dir_for_key, button[2], button_type="Directions for Frame"))
    if type(main.selected_object).__name__ == "Entity": main.buttons[40].append(Button(58 + (5 * 36), 64, 32, 32, "Activate Bossfight for Frame " + str(main.selected_key), "Assets/editor/bossfight trigger.png", select_state_for_key, "BOSSFIGHT", button_type="Action for Frame"))
    if type(main.selected_object).__name__ == "Player":
      if len(main.characters) > 21:
        for index, entity in enumerate(main.characters):
          try: pygame.image.load(main.active_directory + "Assets/characters/" + entity + "/idle/1.png"); main.buttons[40].append(Button(50 + ((index % 13) * 17), 265 + math.floor(index / 13) * 17, 16, 16, entity, main.active_directory + "Assets/characters/" + entity + "/idle/1.png", select_character_for_key, main.character_types[str(index)]["object"], button_type="Character for Frame"))
          except: main.buttons[40].append(Button(50 + ((index % 13) * 17), 265 + math.floor(index / 13) * 17, 16, 16, entity, main.active_directory + "Assets/characters/" + entity + "/down/idle/1.png", select_character_for_key, main.character_types[str(index)]["object"], button_type="Character for Frame"))
      else:
        for index, entity in enumerate(main.characters):
          try: pygame.image.load(main.active_directory + "Assets/characters/" + entity + "/idle/1.png"); main.buttons[40].append(Button(52 + ((index % 7) * 33), 265 + math.floor(index / 7) * 33, 32, 32, entity, main.active_directory + "Assets/characters/" + entity + "/idle/1.png", select_character_for_key, main.character_types[str(index)]["object"], button_type="Character for Frame"))
          except: main.buttons[40].append(Button(52 + ((index % 7) * 33), 265 + math.floor(index / 7) * 33, 32, 32, entity, main.active_directory + "Assets/characters/" + entity + "/down/idle/1.png", select_character_for_key, main.character_types[str(index)]["object"], button_type="Character for Frame"))
  elif type(main.selected_object).__name__ == "Tile":
    main.buttons[40].append(Button(426, HEIGHT - 58, 32, 32, "Destroy Tile", "Assets/editor/kaboom.png", set_destroy_tile_for_key))
  elif type(main.selected_object).__name__ == "Door":
    main.buttons[40].append(Button(426, HEIGHT - 58, 32, 32, "Transport Player", "Assets/editor/transport.png", set_transport_door_for_key))
  elif type(main.selected_object).__name__ == "Background":
    if main.selected_object.is_animating:
      for y, button in enumerate([("Remove Action", "remove action", remove_action_for_cs), ("Flip to Next Frame", "combo right", set_flip_for_bg), ("Flip to Previous Frame", "combo left", set_back_for_bg), ("Restart Animation", "from start", set_restart_for_bg), ("Random Frame", "dice", set_random_for_bg)]):
        main.buttons[40].append(Button(WIDTH - 86, 150 + (y * 34), 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
      main.buttons[40].append(Button(426, HEIGHT - 58, 32, 32, "Next Key when Background Animation Loops", "Assets/editor/next key upon completion.png", set_next_key_on_loop))
  elif main.selected_object == None:
    for x, button in enumerate([("Decrease Key " + str(main.selected_key) + " Rate", "less", -1), ("Increase Key " + str(main.selected_key) + " Rate", "more", 1)]):
      main.buttons[40].append(Button(54 + (x * 140), 85, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_key_rate, target=button[2]))
    for x, button in enumerate([("Decrease Uİ Token", "less", -1), ("İncrease Uİ Token", "more", 1)]):
      main.buttons[40].append(Button(150 + (x * 164), 250, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_selected_sm, target=button[2]))
    for x, button in enumerate([("Add to Show", "camera show", show_ui_for_cs), ("Add to Hide", "camera hide", hide_ui_for_cs)]):
      main.buttons[40].append(Button(116 + (x * 232), 250, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
def scene_audio(none):
  global k_a; k_a = False
  main.gamestate = 41
  present = False
  for key_object in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations:
    if key_object["Frame"] == main.selected_key and key_object["Object"] == "Main": present = True
  if not present: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations.append({"Object": "Main", "Frame": main.selected_key, "Rect": None, "SOCR": False, "Hidden": False, "Speed": 0, "X Speed": 0, "Y Speed": 0, "Rotate": 10, "Speed": 0, "X Scale": 0, "Y Scale": 0, "Action": "", "Dir": "", "SFX": "", "Track": "", "Show UI": [], "Hide UI": [], "B1": False, "B2": False, "I1": -1, "I2": -1, "I3": -1, "I4": -1})
  for key_index, key_object in enumerate(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations):
    if key_object["Frame"] == main.selected_key and key_object["Object"] == "Main": main.selected_cutscene_attrib = key_object; main.selected_cutscene_attrib_index = key_index
def select_scene_bool_condition(stat):
  if stat in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].stat_required: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].stat_required.remove(stat)
  else: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].stat_required.append(stat)


#New Entity Type Page 2
def change_speed_x(by): main.selected_speed[0] += by
def change_speed_y(by): main.selected_speed[1] += by
def change_range(by): main.selected_range += by
def change_hp(by): main.selected_hp += by
def pick_defeat_anim(anim): main.selected_animation = anim
def select_sfx2(remember_gs): main.gamestate = 16; main.remember_gs = remember_gs; main.choosing_sfx = 2
def select_sfx3(remember_gs): main.gamestate = 16; main.remember_gs = remember_gs; main.choosing_sfx = 3
def select_sfx4(remember_gs): main.gamestate = 16; main.remember_gs = remember_gs; main.choosing_sfx = 4
def select_sfx5(remember_gs): main.gamestate = 16; main.remember_gs = remember_gs; main.choosing_sfx = 5
def select_sfx6(remember_gs): main.gamestate = 16; main.remember_gs = remember_gs; main.choosing_sfx = 6
def select_sfx7(remember_gs): main.gamestate = 16; main.remember_gs = remember_gs; main.choosing_sfx = 7
def select_sfx8(remember_gs): main.gamestate = 16; main.remember_gs = remember_gs; main.choosing_sfx = 8
#New Entity Type Page 3
def select_drop(drop):
  done = False
  if drop in main.selected_drops and not done: main.selected_drops.remove(drop); done = True
  if (not done) and (not drop in main.selected_drops): main.selected_drops.append(drop); done = True
def make_entity_type(none): main.entity_types.append(Entity_Type(main.selected_tile[0], main.selected_speed[0], main.selected_speed[1], main.selected_hp, main.selected_stat, main.selected_value, main.selected_behaviors, main.selected_range, main.selected_drops, main.selected_animation, main.selected_sfx, main.selected_sfx2, main.selected_sfx3, main.selected_sfx4, main.selected_sfx5, main)); main.selected_range = 0; main.selected_drops = []; main.selected_value = 1; main.selected_animation = ""; main.selected_stat = ""; main.selected_hp = 1; main.selected_tile = (); main.selected_behaviors = []; main.selected_speed = [0, 0]; main.selected_sfx = ""; main.selected_sfx2 = ""; main.selected_sfx3 = ""; main.selected_sfx4 = ""; main.selected_sfx5 = ""; main.gamestate = 0

#EA
def delete_entity_type(none):
  try:
    for actor in [actor for actor in main.rooms[main.selected_room].layers[main.selected_layer].actors if actor.type == main.selected_tile[3]]: main.rooms[main.selected_room].layers[main.selected_layer].actors.remove(actor)
    main.entity_types.remove(main.selected_tile[3]); main.selected_tile = ()
    main.buttons[27].clear()
    main.buttons[27].append(Button(WIDTH - 21, 100 - 21, 19, 19, "Delete Actor Type Object", "Assets/editor/delete.png", delete_entity_type))
    for index, entity in enumerate(main.entity_types):
      try: pygame.image.load(main.active_directory + "Assets/characters/" + entity + "/idle/1.png"); tup = (entity.name, entity.image, index, entity); main.buttons[27].append(Button(2 + ((index % 30) * 17), 25 + math.floor(index / 30) * 17, 16, 16, tup[0], main.active_directory + "Assets/characters/" + tup[0] + "/idle/1.png", select_tile, tup, button_type="Entity"))
      except: tup = (entity.name, entity.image, index, entity); main.buttons[27].append(Button(2 + ((index % 30) * 17), 25 + math.floor(index / 30) * 17, 16, 16, tup[0], main.active_directory + "Assets/characters/" + tup[0] + "/down/idle/1.png", select_tile, tup, button_type="Entity"))
  except: pass

#Port Setting
#def toggle_press_and_hold(button): main.input_hold[button] = not main.input_hold[button]

#Set Text Before After Character Name
def set_before_text(none): rename(29, main.selected_object.character_string[0], "Before Text " + type(main.selected_object).__name__); main.selected_value = 0
def set_after_text(none): rename(29, main.selected_object.character_string[1], "After Text " + type(main.selected_object).__name__); main.selected_value = 1
def take_from_player(index): main.selected_object.take_index = index
def set_take_player_or_team(none): main.selected_object.player_or_team = not main.selected_object.player_or_team
def set_take_variable(none): main.selected_object.take_variable = not main.selected_object.take_variable

#Display Settings
def change_display(remember_gs, rename_target, target_object): main.gamestate = 9; main.remember_gs = remember_gs; main.rename_target = rename_target; main.rename_text = rename_target; main.target_object = target_object; main.instance_target = rename_target
def toggle_dt(none): main.use_dt = not main.use_dt
def enter_publisher(remember_gs, rename_target, target_object): main.gamestate = 4; main.remember_gs = remember_gs; main.rename_target = rename_target; main.rename_text = rename_target; main.target_object = target_object; main.instance_target = rename_target

#Action Controls
def select_button(button): main.selected_button = button
def select_state(state): main.selected_state = state; edit_action_controls(None)
def select_frame(frame): main.selected_frame = frame
def select_ability_condition(condition):
  if main.character_types[main.selected_character_type]["object"].actions[main.selected_state].condition_stat == condition: main.character_types[main.selected_character_type]["object"].actions[main.selected_state].condition_stat = ""
  else: main.character_types[main.selected_character_type]["object"].actions[main.selected_state].condition_stat = condition
def unlink_button(none):
  for button in main.character_types[main.selected_character_type]["object"].state_controls:
    if main.selected_state in main.character_types[main.selected_character_type]["object"].state_controls[button]: main.character_types[main.selected_character_type]["object"].state_controls[button].remove(main.selected_state)
def deselect_state(none): main.selected_state = ""; edit_action_controls(None)
def toggle_hold_state(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].hold = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].hold
def toggle_double_click_state(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].double_click = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].double_click
def state_away_delay(by):
  main.character_types[main.selected_character_type]["object"].away_delay += by
  if main.character_types[main.selected_character_type]["object"].away_delay < 0: main.character_types[main.selected_character_type]["object"].away_delay = 0
def state_wake_delay(by):
  main.character_types[main.selected_character_type]["object"].wake_up_delay += by
  if main.character_types[main.selected_character_type]["object"].wake_up_delay < 0: main.character_types[main.selected_character_type]["object"].wake_up_delay = 0
def prioritize_action(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].prioritize_action = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].prioritize_action
def state_allow_travel(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].allow_travel = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].allow_travel
def state_allow_jump(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].allow_jump = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].allow_jump
def state_allow_flip(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].allow_flip = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].allow_flip
def state_apply_gravity(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].apply_gravity = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].apply_gravity
def state_apply_aerial(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].aerial = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].aerial
def state_apply_terrestial(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].terrestial = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].terrestial
def state_apply_subaqueous(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].subaqueous = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].subaqueous
def state_cancel_on_walk(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].cancel_on_walk = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].cancel_on_walk
def state_cancel_on_ground(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].cancel_on_ground = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].cancel_on_ground
def state_cancel_on_jump(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].cancel_on_jump = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].cancel_on_jump
def state_cancel_on_hit(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].cancel_on_hit = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].cancel_on_hit
def state_relative_to_dir(none): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].directional_relative = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].directional_relative
def state_continue_until_cancel(none):  main.character_types[main.selected_character_type]["object"].actions[main.selected_state].continue_until_cancel = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].continue_until_cancel
def state_set_combo(combo): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].combo = combo
def state_trigger_mode(mode): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].trigger_mode = mode

def change_anim_speed(by):
  try:
    main.character_types[main.selected_character_type]["object"].actions[main.selected_state].rate += by
    if main.character_types[main.selected_character_type]["object"].actions[main.selected_state].rate < 0: main.character_types[main.selected_character_type]["object"].actions[main.selected_state].rate = 0
  except: pass
def toggle_anim_loop(none):
  try: main.character_types[main.selected_character_type]["object"].actions[main.selected_state].loop = not main.character_types[main.selected_character_type]["object"].actions[main.selected_state].loop
  except: pass
def change_frame_move_x(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].move_x += by
def change_frame_move_y(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].move_y += by
def change_frame_gain_x(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].gain_x += by
def change_frame_gain_y(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].gain_y += by
def change_frame_damage(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].damage += by
def change_frame_knockback_x(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].knockback_x += by
def change_frame_knockback_y(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].knockback_y += by
def change_frame_self_damage(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].self_destruct += by
def change_frame_loop_return(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].loop_to += by
def change_frame_loops(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].loops_spawn += by; main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].loops += by
def change_frame_combo_unit(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].combo_unit += by
def change_selected_projectile(by):
  main.selected_projectile += by
  if main.selected_projectile > len(main.projectiles): main.selected_projectile = 1
  if main.selected_projectile < 1: main.selected_projectile = len(main.projectiles)
def add_projectile_to_frant(none):
  if len(main.projectiles) and len(main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].projectiles) < 8:
    if not main.selected_projectile in main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].projectiles: main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].projectiles.append(main.selected_projectile)
def remove_projectile_to_frant(none):
  if main.selected_projectile in main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].projectiles: main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].projectiles.remove(main.selected_projectile)

def change_frame_hitbox_x(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].rect.x += by
def change_frame_hitbox_y(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].rect.y += by
def change_frame_hitbox_width(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].rect.width += by
def change_frame_hitbox_height(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].rect.height += by
def change_frame_attack_hitbox_x(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].attack_rect.x += by
def change_frame_attack_hitbox_y(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].attack_rect.y += by
def change_frame_attack_hitbox_width(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].attack_rect.width += by
def change_frame_attack_hitbox_height(by): main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].attack_rect.height += by
def change_frame_hitbox_apply_to_all(none):
  for frant in main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants:
    frant.rect.x = main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].rect.x
    frant.rect.y = main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].rect.y
    frant.rect.width = main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].rect.width
    frant.rect.height = main.character_types[main.selected_character_type]["object"].actions[main.selected_state].frants[main.selected_frame - 1].rect.height

#Edit Door
def change_door_x_dest(by): main.selected_object.led_pos[0] += by * main.tiles_size
def change_door_y_dest(by): main.selected_object.led_pos[1] += by * main.tiles_size
def change_door_x(by): main.selected_object.rect.x += by * main.tiles_size; main.selected_object.spawn_location[0] = main.selected_object.rect.x
def change_door_y(by): main.selected_object.rect.y += by * main.tiles_size; main.selected_object.spawn_location[1] = main.selected_object.rect.y
def change_door_dest(by):
  main.selected_object.led_room += by
  if main.selected_object.led_room >= len(main.rooms): main.selected_object.led_room = 0
  if main.selected_object.led_room < 0: main.selected_object.led_room = len(main.rooms) - 1
def change_door_input_requirement(none): main.selected_object.requires_input = not main.selected_object.requires_input
def change_door_passable(none): main.selected_object.passable = not main.selected_object.passable
def change_door_spawn_on_other_side(none): main.selected_object.spawn_door_on_other_side = not main.selected_object.spawn_door_on_other_side
def change_door_passable_on_other_side(none): main.selected_object.door_on_other_side_is_passable = not main.selected_object.door_on_other_side_is_passable
def change_door_play_anim_on_other_side(none): main.selected_object.play_anim_on_other_side = not main.selected_object.play_anim_on_other_side
def change_transition(transition):
  if transition in main.selected_object.transition: main.selected_object.transition.remove(transition)
  else: main.selected_object.transition.append(transition)
def change_door_prets(by):
  main.selected_object.transition_speed_pre += by
  if main.selected_object.transition_speed_pre < 1: main.selected_object.transition_speed_pre = 75
  if main.selected_object.transition_speed_pre > 75: main.selected_object.transition_speed_pre = 1
def change_door_postts(by):
  main.selected_object.transition_speed_post += by
  if main.selected_object.transition_speed_post < 1: main.selected_object.transition_speed_post = 75
  if main.selected_object.transition_speed_post > 75: main.selected_object.transition_speed_post = 1
def change_transition_color(color): main.selected_object.transition_color = color
def change_transition_shape(shape): main.selected_object.transition_shape = shape
def change_transition_f1(none): main.selected_object.transition_flag_1 = not main.selected_object.transition_flag_1
def change_transition_f2(none): main.selected_object.transition_flag_2 = not main.selected_object.transition_flag_2
def change_transition_override_ui(none): main.selected_object.transition_override_ui = not main.selected_object.transition_override_ui
def change_transition_pre_immobilize_player(none): main.selected_object.transition_pre_immobilize_player = not main.selected_object.transition_pre_immobilize_player
def change_transition_post_immobilize_player(none): main.selected_object.transition_post_immobilize_player = not main.selected_object.transition_post_immobilize_player
def change_transition_play_door_and_player_animation(none): main.selected_object.transition_play_door_and_player_animation = not main.selected_object.transition_play_door_and_player_animation

#Edit Dialogues
def select_dialogue(dl): main.selected_dl = dl; manage_dialogues(None)
def add_dialogue(none): main.selected_object.letter_delay.append(main.fps); main.selected_object.dialogue.append(["Hello, world!", "What is your name?", "What!?", "Let's go!", "Give it back!", "Save us!", "The fate of this village is in your hands", "I'll leave the rest up to you", "What are you talking about?", "I am so sorry...", "HAHAHAHA!!!", "Hey take it back!", "I promise.", "AAAAAAAGHH!!", "Is that... all you've got?", "You are right.", "This is it...!", "It's over."][random.randrange(0, 18)]); manage_dialogues(None)
def delete_dialogue(dl):
  try: main.selected_object.dialogue.remove(main.selected_object.dialogue[dl]); main.selected_object.letter_delay.pop(dl); manage_dialogues(None)
  except: pass
def change_dialogue_letter_delay(by):
  main.selected_object.letter_delay[main.selected_dl] += by
  if main.selected_object.letter_delay[main.selected_dl] <= 0: main.selected_object.letter_delay[main.selected_dl] = 120
  if main.selected_object.letter_delay[main.selected_dl] > 120: main.selected_object.letter_delay[main.selected_dl] = 5

#Edit User İnterface Uİ
def select_ui_corner(mode): main.ui.instances[main.selected_ui][main.selected_ui_mode]["Corner"] = mode
def change_ui_x_margin(by): main.ui.instances[main.selected_ui][main.selected_ui_mode]["X Margin"] += by
def change_ui_y_margin(by): main.ui.instances[main.selected_ui][main.selected_ui_mode]["Y Margin"] += by
def change_ui_angle(by):
  main.ui.instances[main.selected_ui][main.selected_ui_mode]["Rotate"] += by
  if main.ui.instances[main.selected_ui][main.selected_ui_mode]["Rotate"] < 0: main.ui.instances[main.selected_ui]["Rotate"] = 360
  if main.ui.instances[main.selected_ui][main.selected_ui_mode]["Rotate"] > 360: main.ui.instances[main.selected_ui]["Rotate"] = 0
  main.ui.regenerate(main.selected_ui)
def change_ui_font_scale(by):
  main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font Size"] += by
  if main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font Size"] <= 1: main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font Size"] = 1
  try: main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font"] = pygame.Font(main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"], main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font Size"])
  except: main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font"] = pygame.font.SysFont(main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"], main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font Size"])
  main.ui.regenerate(main.selected_ui)
def change_ui_font_outline(by):
  main.ui.instances[main.selected_ui][main.selected_ui_mode]["TOL"] += by
  if main.ui.instances[main.selected_ui][main.selected_ui_mode]["TOL"] < 0: main.ui.instances[main.selected_ui][main.selected_ui_mode]["TOL"] = 0
  main.ui.regenerate(main.selected_ui)
def change_ui_font_color(color): main.ui.instances[main.selected_ui][main.selected_ui_mode]["TC"] = color; main.ui.regenerate(main.selected_ui)
def change_ui_font_color_outline(color): main.ui.instances[main.selected_ui][main.selected_ui_mode]["TCOL"] = color; main.ui.regenerate(main.selected_ui)
def change_ui_font_color_bg(color): main.ui.instances[main.selected_ui][main.selected_ui_mode]["TCBG"] = color; main.ui.regenerate(main.selected_ui)
def change_ui_iteration_x(by): main.ui.instances[main.selected_ui][main.selected_ui_mode]["I X"] += by
def change_ui_iteration_y(by): main.ui.instances[main.selected_ui][main.selected_ui_mode]["I Y"] += by
def change_ui_iteration_offset(by): main.ui.instances[main.selected_ui][main.selected_ui_mode]["I Offset"] += by
def change_ui_iteration_wrap(by):
  main.ui.instances[main.selected_ui][main.selected_ui_mode]["I WL"] += by
  if main.ui.instances[main.selected_ui][main.selected_ui_mode]["I WL"] < 0: main.ui.instances[main.selected_ui][main.selected_ui_mode]["I WL"] = 0
def change_ui_iteration_angle(by):
  main.ui.instances[main.selected_ui][main.selected_ui_mode]["I Angle"] += by
  if main.ui.instances[main.selected_ui][main.selected_ui_mode]["I Angle"] < 0: main.ui.instances[main.selected_ui][main.selected_ui_mode]["I Angle"] = 360
  if main.ui.instances[main.selected_ui][main.selected_ui_mode]["I Angle"] > 360: main.ui.instances[main.selected_ui][main.selected_ui_mode]["I Angle"] = 0
def change_ui_align(mode): main.ui.instances[main.selected_ui][main.selected_ui_mode]["I Align"] = mode
def change_ui_elements_align_multiplayer(mode): main.ui.instances[main.selected_ui][main.selected_ui_mode]["MA"] = mode
def change_ui_elements_offset_multiplayer(by): main.ui.instances[main.selected_ui][main.selected_ui_mode]["MAO"] += by
def change_ui_iteration_animation_speed(by):
  main.ui.instances[main.selected_ui][main.selected_ui_mode]["I FS"] += by
  if main.ui.instances[main.selected_ui][main.selected_ui_mode]["I FS"] <= 1: main.ui.instances[main.selected_ui][main.selected_ui_mode]["I FS"] = 1
def enable_ui_iteration(none): main.ui.instances[main.selected_ui][main.selected_ui_mode]["I"] = not main.ui.instances[main.selected_ui][main.selected_ui_mode]["I"]; main.ui.instances[main.selected_ui][main.selected_ui_mode]["Bar"] = False; refresh_ui_buttons()
def enable_ui_bars(none): main.ui.instances[main.selected_ui][main.selected_ui_mode]["Bar"] = not main.ui.instances[main.selected_ui][main.selected_ui_mode]["Bar"]; main.ui.instances[main.selected_ui][main.selected_ui_mode]["I"] = False; refresh_ui_buttons()
def remove_ui_text(none): main.ui.instances[main.selected_ui][main.selected_ui_mode]["Text"] = "<var>"
def set_ui_text(none): rename(35, main.ui.instances[main.selected_ui][main.selected_ui_mode]["Text"], "Uİ Text")
def select_font(none): main.remember_gs = 35; go_to(44)
def select_ui_i_image(index=1): main.remember_gs = 35; main.selected_image_index = index; go_to(46)
def change_ui_bar_x(by): main.ui.instances[main.selected_ui][main.selected_ui_mode]["B X"] += by
def change_ui_bar_y(by): main.ui.instances[main.selected_ui][main.selected_ui_mode]["B Y"] += by
def change_ui_bar_length(by): main.ui.instances[main.selected_ui][main.selected_ui_mode]["B Len"] += by
def change_ui_bar_thickness(by): main.ui.instances[main.selected_ui][main.selected_ui_mode]["B Thi"] += by
def change_ui_bar_orientation(none): main.ui.instances[main.selected_ui][main.selected_ui_mode]["B V"] = not main.ui.instances[main.selected_ui][main.selected_ui_mode]["B V"]
def change_ui_bar_outline(by):
  main.ui.instances[main.selected_ui][main.selected_ui_mode]["B OL"] += by
  if main.ui.instances[main.selected_ui][main.selected_ui_mode]["B OL"] < 0: main.ui.instances[main.selected_ui][main.selected_ui_mode]["B OL"] = 0
def change_ui_bar_color(color): main.ui.instances[main.selected_ui][main.selected_ui_mode]["C1"] = color; main.ui.regenerate(main.selected_ui)
def change_ui_bar_color_outline(color): main.ui.instances[main.selected_ui][main.selected_ui_mode]["C3"] = color; main.ui.regenerate(main.selected_ui)
def change_ui_bar_color_bg(color): main.ui.instances[main.selected_ui][main.selected_ui_mode]["C2"] = color; main.ui.regenerate(main.selected_ui)
def change_ui_token(by):
  main.ui.instances[main.selected_ui]["SM"] += by
def change_ui_mode(by):
  main.selected_ui_mode = int(main.selected_ui_mode); main.selected_ui_mode += by; main.selected_ui_mode = str(main.selected_ui_mode)
  if int(main.selected_ui_mode) <= 0: main.selected_ui_mode = "1"
  try: main.ui.instances[main.selected_ui][main.selected_ui_mode]
  except: main.ui.instances[main.selected_ui][main.selected_ui_mode] = main.ui.format_ui_mode(stat=main.selected_stat, corner="Up Left", x_margin=5, y_margin=5, rotation=0, text="", iteration=False, i_x=10, i_y=10, i_offset=2, i_wrap_length=16, i_angle=90, i_align="Left", image_path="", image_path2="", frame_speed=1, antialias=True, bar=False, vertical_bar=False, b_x=2, b_y=2, b_length=100, b_thickness=10, b_outline=0, color1=(0, 255, 0), color2=(255, 0, 0), color3=(0, 0, 0), color4=(255, 255, 255), font=None, font_size=30, text_color=(255, 255, 255), text_color_outline=(0, 0, 0), text_color_bg="Transparent", text_outline_thickness=0); main.ui.add_mode(main.selected_ui_mode, main.ui.instances[main.selected_ui])
  refresh_ui_buttons(None)
def delete_stat_ui(none): main.ui.delete_instance(main.selected_ui); main.selected_ui = None; main.gamestate = 15
def edit_ui_behaviors(none): main.gamestate, main.remember_gs = 61, 35
def refresh_ui_buttons():
  main.buttons[35].clear()
  main.selected_ui = main.selected_stat
  main.buttons[35].append(Button(WIDTH - 256, 24, 32, 32, "Go Back", "Assets/editor/back.png", go_to, target_gs=15))
  main.buttons[35].append(Button(WIDTH - 222, 24, 32, 32, "Remove Uİ", "Assets/editor/delete.png", delete_stat_ui))
  main.buttons[35].append(Button(WIDTH - 188, 24, 32, 32, "Edit Behaviors", "Assets/editor/guided.png", edit_ui_behaviors))
  main.buttons[35].append(Button(WIDTH - 154, 24, 32, 32, "Enable Iteration Mode", "Assets/editor/iterator.png", enable_ui_iteration))
  main.buttons[35].append(Button(WIDTH - 120, 24, 32, 32, "Enable Bar Mode", "Assets/editor/bars.png", enable_ui_bars))
  main.buttons[35].append(Button(WIDTH - 86, 24, 32, 32, "Browse İmages (Primary)", "Assets/editor/image.png", select_ui_i_image, target=1))
  main.buttons[35].append(Button(WIDTH - 86, 58, 32, 32, "Browse İmages (Secondary)", "Assets/editor/image.png", select_ui_i_image, target=2))
  for x, button in enumerate([("Align İterations/Bar Right", "align right", "Right"), ("Align İterations/Bar Center", "align center", "Center"), ("Align İterations/Bar Left", "align left", "Left")]):
    main.buttons[35].append(Button(WIDTH - 86, 92 + (x * 34), 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_align, button[2]))
  for x, button in enumerate([("No Text, Only Value", "no text", remove_ui_text), ("Set Text Mode", "text", set_ui_text), ("Select Font", "font", select_font)]):
    main.buttons[35].append(Button(54 + (x * 34), HEIGHT - 57, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
  main.buttons[35].append(Button(56, 320, 10, 10, "Snap to Upper-Left Corner", "", select_ui_corner, "Up Left", button_type="Uİ Corner"))
  main.buttons[35].append(Button(90, 320, 10, 10, "Snap to Upper Edge", "", select_ui_corner, "Up", button_type="Uİ Corner"))
  main.buttons[35].append(Button(122, 320, 10, 10, "Snap to Upper-Right Corner", "", select_ui_corner, "Up Right", button_type="Uİ Corner"))
  main.buttons[35].append(Button(56, 347, 10, 10, "Snap to Left Edge", "", select_ui_corner, "Left", button_type="Uİ Corner"))
  main.buttons[35].append(Button(90, 347, 10, 10, "Snap to Center", "", select_ui_corner, "Center", button_type="Uİ Corner"))
  main.buttons[35].append(Button(122, 347, 10, 10, "Snap to Right Edge", "", select_ui_corner, "Right", button_type="Uİ Corner"))
  main.buttons[35].append(Button(56, 373, 10, 10, "Snap to Lower-Left Corner", "", select_ui_corner, "Down Left", button_type="Uİ Corner"))
  main.buttons[35].append(Button(90, 373, 10, 10, "Snap to Lower Edge", "", select_ui_corner, "Down", button_type="Uİ Corner"))
  main.buttons[35].append(Button(122, 373, 10, 10, "Snap to Lower-Right Corner", "", select_ui_corner, "Down Right", button_type="Uİ Corner"))
  for x, button in enumerate([("Decrease X Margin", "less", change_ui_x_margin, -1), ("İncrease X Margin", "more", change_ui_x_margin, 1)]):
    main.buttons[35].append(Button(60 + (x * 132), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
  for x, button in enumerate([("Decrease Y Margin", "less", change_ui_y_margin, -1), ("İncrease Y Margin", "more", change_ui_y_margin, 1)]):
    main.buttons[35].append(Button(60 + (x * 132), 100, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
  for x, button in enumerate([("Turn Counter-Clockwise", "ccw", change_ui_angle, 1), ("Turn Clockwise", "cw", change_ui_angle, -1)]):
    main.buttons[35].append(Button(60 + (x * 132), 130, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
  for x, button in enumerate([("Decrease Text Scale", "less", change_ui_font_scale, -1), ("İncrease Text Scale", "more", change_ui_font_scale, 1)]):
    main.buttons[35].append(Button(60 + (x * 132), 160, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
  for x, button in enumerate([("Thin Outline", "less", change_ui_font_outline, -1), ("Thick Outline", "more", change_ui_font_outline, 1)]):
    main.buttons[35].append(Button(60 + (x * 132), 190, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
  for x, color in enumerate(colors):
    if color != "Transparent": main.buttons[35].append(Button(55 + math.floor(x / 10) * 8, 235 + ((x % 10) * 8), 8, 8, "Text Color > " + color, "", change_ui_font_color, target=colors[color], color=colors[color], button_type="Color"))
  for x, color in enumerate(colors):
    if color != "Transparent": main.buttons[35].append(Button(120 + math.floor(x / 10) * 8, 235 + ((x % 10) * 8), 8, 8, "Outline Color > " + color, "", change_ui_font_color_outline, target=colors[color], color=colors[color], button_type="OL Color"))
  for x, color in enumerate(colors):
    main.buttons[35].append(Button(185 + math.floor(x / 10) * 8, 235 + ((x % 10) * 8), 8, 8, "Background Color > " + color, "", change_ui_font_color_bg, target=colors[color], color=colors[color], button_type="BG Color"))
  for x, button in enumerate([("Right", "right"), ("Center RL", "center_horizontal"), ("Left", "left"), ("Up", "up"), ("Center UD", "center_vertical"), ("Down", "down")]):
    main.buttons[35].append(Button(138 + (x * 34), 320, 32, 32, "Align Players' Elements " + button[0], "Assets/editor/align_elements_" + button[1] + ".png", change_ui_elements_align_multiplayer, button[1]))
  for x, button in enumerate([("Decrease Players' Uİ Offset", "less", -1), ("İncrease Players' Uİ Offset", "more", 1)]):
    main.buttons[35].append(Button(138 + (x * 132), 352, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_elements_offset_multiplayer, target=button[2]))
  for x, button in enumerate([("Decrease Edit Uİ Mode", "less", -1), ("İncrease Edit Uİ Mode", "more", 1)]):
    main.buttons[35].append(Button(340 + (x * 92), 316, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_mode, target=button[2]))
  for x, button in enumerate([("Decrease Uİ Token", "less", -1), ("İncrease Uİ Token", "more", 1)]):
    main.buttons[35].append(Button(340 + (x * 92), 350, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_token, target=button[2]))
  if main.ui.instances[main.selected_ui][main.selected_ui_mode]["I"]:
    for x, button in enumerate([("Decrease İteration X Position", "less", -1), ("İncrease İteration X Position", "more", 1)]):
      main.buttons[35].append(Button(260 + (x * 132), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_iteration_x, target=button[2]))
    for x, button in enumerate([("Decrease İteration Y Position", "less", -1), ("İncrease İteration Y Position", "more", 1)]):
      main.buttons[35].append(Button(260 + (x * 132), 100, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_iteration_y, target=button[2]))
    for x, button in enumerate([("Decrease İteration Offset", "less", -1), ("İncrease İteration Offset", "more", 1)]):
      main.buttons[35].append(Button(260 + (x * 132), 130, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_iteration_offset, target=button[2]))
    for x, button in enumerate([("Decrease İteration Wrapping Length", "less", -1), ("İncrease İteration Wrapping Length", "more", 1)]):
      main.buttons[35].append(Button(260 + (x * 132), 160, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_iteration_wrap, target=button[2]))
    for x, button in enumerate([("Decrease İteration Angle", "less", -1), ("İncrease İteration Angle", "more", 1)]):
      main.buttons[35].append(Button(260 + (x * 132), 190, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_iteration_angle, target=button[2]))
    for x, button in enumerate([("Decrease Animation Speed", "less", -1), ("İncrease Animation Speed", "more", 1)]):
      main.buttons[35].append(Button(260 + (x * 164), 220, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_iteration_animation_speed, target=button[2]))
  if main.ui.instances[main.selected_ui][main.selected_ui_mode]["Bar"]:
    for x, button in enumerate([("Decrease Bar X Position", "less", -1), ("İncrease Bar X Position", "more", 1)]):
      main.buttons[35].append(Button(260 + (x * 132), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_bar_x, target=button[2]))
    for x, button in enumerate([("Decrease Bar Y Position", "less", -1), ("İncrease Bar Y Position", "more", 1)]):
      main.buttons[35].append(Button(260 + (x * 132), 100, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_bar_y, target=button[2]))
    for x, button in enumerate([("Decrease Bar Length", "less", -1), ("İncrease Bar Length", "more", 1)]):
      main.buttons[35].append(Button(260 + (x * 132), 130, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_bar_length, target=button[2]))
    for x, button in enumerate([("Decrease Bar Thickness", "less", -1), ("İncrease Bar Thickness", "more", 1)]):
      main.buttons[35].append(Button(260 + (x * 132), 160, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_bar_thickness, target=button[2]))
    for x, button in enumerate([("Thin Bar Outline", "less", -1), ("Thick Bar Outline", "more", 1)]):
      main.buttons[35].append(Button(260 + (x * 132), 190, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_ui_bar_outline, target=button[2]))
    main.buttons[35].append(Button(WIDTH - 86, 188, 32, 32, "Turn Bar Orientation", "Assets/editor/turn bar.png", change_ui_bar_orientation))
    for x, color in enumerate(colors):
      if color != "Transparent": main.buttons[35].append(Button(250 + math.floor(x / 10) * 8, 235 + ((x % 10) * 8), 8, 8, "Bar Text Color > " + color, "", change_ui_bar_color, target=colors[color], color=colors[color], button_type="B Color"))
    for x, color in enumerate(colors):
      if color != "Transparent": main.buttons[35].append(Button(315 + math.floor(x / 10) * 8, 235 + ((x % 10) * 8), 8, 8, "Bar Outline Color > " + color, "", change_ui_bar_color_outline, target=colors[color], color=colors[color], button_type="B OL Color"))
    for x, color in enumerate(colors):
      main.buttons[35].append(Button(380 + math.floor(x / 10) * 8, 235 + ((x % 10) * 8), 8, 8, "Bar Background Color > " + color, "", change_ui_bar_color_bg, target=colors[color], color=colors[color], button_type="B BG Color"))

#Edit Collictible Price
def change_price_stat(stat): main.selected_object.price_stat = stat
def change_price_value(by): main.selected_object.price_value += by
def pick_price_text_position(pos): main.selected_object.price_text_position = pos
def pick_price_text_mode(mode): main.selected_object.price_text_mode = mode
def toggle_exchange_mode(none): main.selected_object.price_exchange = not main.selected_object.price_exchange
def toggle_drop_mode(none): main.selected_object.price_decrement = not main.selected_object.price_decrement

#Set Stat Effect
def set_effect(effect): main.game_stats_effect[main.selected_stat] = effect
def clear_stat_effect(none): go_to(15); main.game_stats_effect[main.selected_stat] = "None"

#Rebool
def rebool(boolean): main.rename_text = boolean

#Cutscene
def change_x_repos(by):
  if main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Rect"] != None: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Rect"][0] += by * main.tiles_size
def change_y_repos(by):
  if main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Rect"] != None: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Rect"][1] += by * main.tiles_size
def neglect_reposition(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Rect"] = None
def add_reposition(none):
  if main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Rect"] == None: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Rect"] = [main.selected_object.key_frame_rect.x, main.selected_object.key_frame_rect.y, main.selected_object.key_frame_rect.width, main.selected_object.key_frame_rect.height]
def stay_on_changed_rect(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["SOCR"] = not main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["SOCR"]
def set_hidden_for_key(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Hidden"] = not main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Hidden"]
def set_destroy_tile_for_key(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Action"] = "destroy"
def set_transport_door_for_key(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Action"] = "transport"

def remove_action_for_cs(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Action"] = ""

def set_flip_for_bg(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Action"] = "flip"
def set_back_for_bg(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Action"] = "back"
def set_restart_for_bg(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Action"] = "restart"
def set_random_for_bg(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Action"] = "random"
def set_next_key_on_loop(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["B1"] = not main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["B1"]

def change_cs_speed(by):
  main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Speed"] += by
  if main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Speed"] < 0: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Speed"] = 0
def change_x_cs_speed(by): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["X Speed"] += {True: by, False: main.tiles_size if by > 0 else -main.tiles_size}[main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Speed"] == 0]
def change_y_cs_speed(by): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Y Speed"] += {True: by, False: main.tiles_size if by > 0 else -main.tiles_size}[main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Speed"] == 0]

def cutscene_follow_player(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Hidden"] = not main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Hidden"]
def cutscene_allow_camera_horizontal_mirror(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["B1"] = not main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["B1"]
def cutscene_allow_camera_vertical_mirror(none): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["B2"] = not main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["B2"]

def select_state_for_key(state): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Action"] = state
def face_dir_for_key(dir): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Dir"] = dir
def select_character_for_key(chr): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["SFX"] = chr

def immobilize_for_key(none):
  present = False
  for key_object in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations:
    if key_object["Frame"] == main.selected_key and key_object["Object"] == "Main": present = True
  if not present: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations.append({"Object": "Main", "Frame": main.selected_key, "Rect": None, "SOCR": False, "Hidden": False, "Speed": 0, "X Speed": 0, "Y Speed": 0, "Rotate": 10, "Speed": 0, "X Scale": 0, "Y Scale": 0, "Action": "", "Dir": "", "SFX": "", "Track": "", "Show UI": [], "Hide UI": [], "B1": False, "B2": False, "I1": -1, "I2": -1, "I3": -1, "I4": -1})
  for key_index, key_object in enumerate(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations):
    if key_object["Frame"] == main.selected_key and key_object["Object"] == "Main": main.selected_cutscene_attrib = key_object; main.selected_cutscene_attrib_index = key_index
  main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Hidden"] = not main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Hidden"]

def await_input_key(none):
  present = False
  for key_object in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations:
    if key_object["Frame"] == main.selected_key and key_object["Object"] == "Main": present = True
  if not present: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations.append({"Object": "Main", "Frame": main.selected_key, "Rect": None, "SOCR": False, "Hidden": False, "Speed": 0, "X Speed": 0, "Y Speed": 0, "Rotate": 10, "Speed": 0, "X Scale": 0, "Y Scale": 0, "Action": "", "Dir": "", "SFX": "", "Track": "", "Show UI": [], "Hide UI": [], "B1": False, "B2": False, "I1": -1, "I2": -1, "I3": -1, "I4": -1})
  for key_index, key_object in enumerate(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations):
    if key_object["Frame"] == main.selected_key and key_object["Object"] == "Main": main.selected_cutscene_attrib = key_object; main.selected_cutscene_attrib_index = key_index
  main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["SOCR"] = not main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["SOCR"]

def delete_components_key(none):
  for key_object in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations:
    if key_object["Frame"] == main.selected_key and key_object["Object"] == main.selected_object: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations.remove(key_object)
  if main.selected_object == None:
    for key_object in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations:
      if key_object["Frame"] == main.selected_key and key_object["Object"] == "Main": main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations.remove(key_object)

def change_key_rate(by):
  main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Rotate"] += by
  if main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Rotate"] < 0: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Rotate"] = 0
def change_selected_sm(by): main.selected_ui_sm += by
def change_selected_ui_mode(by): main.selected_ui_mode_for_tm += by
def show_ui_for_cs(none):
  if not main.selected_ui_sm in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Show UI"]: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Show UI"].append(main.selected_ui_sm)
  else: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Show UI"].remove(main.selected_ui_sm)
def hide_ui_for_cs(none):
  if not main.selected_ui_sm in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Hide UI"]: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Hide UI"].append(main.selected_ui_sm)
  else: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Hide UI"].remove(main.selected_ui_sm)

#Cutscene Condition
def add_cs_condition(condition):
  if not condition in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].conditions: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].conditions.append(condition)
  else: main.rooms[main.selected_room].cutscenes[main.selected_cutscene].conditions.remove(condition)
def set_cs_condition_gate(gate): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].condition_gate = gate
def set_cs_condition_stat_gate(gate): main.rooms[main.selected_room].cutscenes[main.selected_cutscene].condition_stat_gate = gate

#Customize Text
def change_text_x(by): main.selected_object.rect.x += by * main.tiles_size; main.selected_object.spawn_location[0] = main.selected_object.rect.x
def change_text_y(by): main.selected_object.rect.y += by * main.tiles_size; main.selected_object.spawn_location[1] = main.selected_object.rect.y
def change_text_font_size(by):
  main.selected_object.size += by
  if main.selected_object.size <= 1: main.selected_object.size = 1
  main.selected_object.regenerate()
def change_text_margin(by):
  main.selected_object.margin += by
  if main.selected_object.margin < 1: main.selected_object.margin = 0
  main.selected_object.regenerate()
def change_text_rotation(by):
  main.selected_object.rotation += by
  if main.selected_object.rotation < 0: main.selected_object.rotation = 360
  if main.selected_object.rotation > 360: main.selected_object.rotation = 0
  main.selected_object.regenerate()
def change_text_x_scale(by):
  main.selected_object.scale[0] += by
  if main.selected_object.scale[0] < 1: main.selected_object.scale[0] = 0
  main.selected_object.regenerate()
def change_text_y_scale(by):
  main.selected_object.scale[1] += by
  if main.selected_object.scale[1] < 1: main.selected_object.scale[1] = 0
  main.selected_object.regenerate()
def change_text_opacity(by):
  main.selected_object.opacity += by
  if main.selected_object.opacity < 0: main.selected_object.opacity = 255
  if main.selected_object.opacity > 255: main.selected_object.opacity = 0
  main.selected_object.regenerate()
def change_text_layer(by):
  layer_before = main.selected_object.layer - 1
  main.selected_object.layer += by
  if main.selected_object.layer < 1: main.selected_object.layer = 1
  if main.selected_object.layer > 12: main.selected_object.layer = 11
  if main.selected_object.layer > len(main.rooms[main.selected_room].layers): main.rooms[main.selected_room].layers.append(Layer("L" + str(len(main.rooms[main.selected_room].layers) + 1), main=main)); main.gamestate = 0; main.buttons[0].append(Button(1 + (33 * (len(main.rooms[main.selected_room].layers) - 1)), HEIGHT - 33, 32, 32, f"Access Layer {'L' + str(len(main.rooms[main.selected_room].layers))}", "", access_layer, len(main.rooms[main.selected_room].layers), button_type="Layer", room=main.selected_room))
  layer_after = main.selected_object.layer - 1
  main.rooms[main.selected_room].layers[layer_before].texts.remove(main.selected_object)
  main.rooms[main.selected_room].layers[layer_after].texts.append(main.selected_object)
def change_text_outline_thickness(by):
  main.selected_object.outline_thickness += by
  if main.selected_object.outline_thickness < 0: main.selected_object.outline_thickness = 0
  main.selected_object.regenerate()
def change_text_bold(none): main.selected_object.bold = not main.selected_object.bold; main.selected_object.regenerate()
def change_text_italic(none): main.selected_object.italic = not main.selected_object.italic; main.selected_object.regenerate()
def change_text_underline(none): main.selected_object.underline = not main.selected_object.underline; main.selected_object.regenerate()
def change_text_strikethrough(none): main.selected_object.strikethrough = not main.selected_object.strikethrough; main.selected_object.regenerate()
def change_text_anti_alias(none): main.selected_object.anti_aliasing = not main.selected_object.anti_aliasing; main.selected_object.regenerate()
def change_text_align(mode): main.selected_object.align = mode; main.selected_object.regenerate()
def change_text_flipx(none): main.selected_object.flip[0] = not main.selected_object.flip[0]; main.selected_object.regenerate()
def change_text_flipy(none): main.selected_object.flip[1] = not main.selected_object.flip[1]; main.selected_object.regenerate()
def change_text_ui_mode(none): main.selected_object.ui_mode = not main.selected_object.ui_mode
def change_text_dir(mode): main.selected_object.direction = mode; main.selected_object.regenerate()
def set_text_color(color): main.selected_object.color = color; main.selected_object.regenerate()
def set_text_outline_color(color): main.selected_object.outline_color = color; main.selected_object.regenerate()
def set_text_bg_color(color): main.selected_object.bg_color = color; main.selected_object.regenerate()
def set_text_capitalization(mode):
  if main.selected_object.capitalization_mode == mode: main.selected_object.capitalization_mode = "Default"
  else: main.selected_object.capitalization_mode = mode
  main.selected_object.regenerate()
def copy_text_data(none): main.clipboard_text_data = [main.selected_object.font_str, main.selected_object.size, main.selected_object.behaviors.copy(), main.selected_object.text, main.selected_object.color, main.selected_object.bg_color, main.selected_object.outline_color, main.selected_object.bold, main.selected_object.italic, main.selected_object.underline, main.selected_object.strikethrough, main.selected_object.anti_aliasing, main.selected_object.align, main.selected_object.margin, main.selected_object.direction, main.selected_object.rotation, main.selected_object.scale.copy(), main.selected_object.opacity, main.selected_object.outline_thickness, main.selected_object.flip, main.selected_object.capitalization_mode, main.selected_object.take_variable, main.selected_object.character_string.copy(), main.selected_object.take_index, main.selected_object.player_or_team]
def paste_text_data_to_text_object(none):
  if main.selected_object != None:
    clipboard_text_data = main.clipboard_text_data.copy()
    main.selected_object.font_str = clipboard_text_data[0]
    main.selected_object.size = clipboard_text_data[1]
    main.selected_object.behaviors = clipboard_text_data[2]
    main.selected_object.text = clipboard_text_data[3]
    main.selected_object.color = clipboard_text_data[4]
    main.selected_object.bg_color = clipboard_text_data[5]
    main.selected_object.outline_color = clipboard_text_data[6]
    main.selected_object.bold = clipboard_text_data[7]
    main.selected_object.italic = clipboard_text_data[8]
    main.selected_object.underline = clipboard_text_data[9]
    main.selected_object.strikethrough = clipboard_text_data[10]
    main.selected_object.anti_aliasing = clipboard_text_data[11]
    main.selected_object.align = clipboard_text_data[12]
    main.selected_object.margin = clipboard_text_data[13]
    main.selected_object.direction = clipboard_text_data[14]
    main.selected_object.rotation = clipboard_text_data[15]
    main.selected_object.scale = clipboard_text_data[16]
    main.selected_object.opacity = clipboard_text_data[17]
    main.selected_object.outline_thickness = clipboard_text_data[18]
    main.selected_object.flip = clipboard_text_data[19]
    main.selected_object.capitalization_mode = clipboard_text_data[20]
    main.selected_object.take_variable = clipboard_text_data[21]
    main.selected_object.character_string = clipboard_text_data[22]
    main.selected_object.take_index = clipboard_text_data[23]
    main.selected_object.player_or_team = clipboard_text_data[24]
    try:
      try:
        if type(clipboard_text_data[0]) == str: main.selected_object.font_str = clipboard_text_data[0]; main.selected_object.font = pygame.Font(main.selected_object.font_str, clipboard_text_data[1])
        elif clipboard_text_data[0] == None: main.selected_object.font_str = ""; main.selected_object.font = pygame.Font(None, clipboard_text_data[1])
      except: main.selected_object.font = pygame.Font(main.active_directory + "Fonts/" + clipboard_text_data[0], clipboard_text_data[1]); main.selected_object.font_str = main.active_directory + "Fonts/" + clipboard_text_data[0]
    except: main.selected_object.font = pygame.font.SysFont(clipboard_text_data[0], clipboard_text_data[1]); main.selected_object.font_str = clipboard_text_data[0]
    main.selected_object.regenerate()

#Font Library
def add_font(none):
  if main.remember_gs == 35:
    try: main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font"] = pygame.Font("Fonts/" + main.fonts[main.selected_itemy], main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font Size"]); main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"] = "Fonts/" + main.fonts[main.selected_itemy]; main.gamestate = 35
    except: main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font"] = pygame.font.SysFont(main.fonts[main.selected_itemy], main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font Size"]); main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"] = main.fonts[main.selected_itemy]; main.gamestate = 35
    try:
      try:
        if type(main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"]) == pygame.Font: main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"] = None; main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font"] = main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"]
        elif main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"] != None: main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"] = main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font"]; main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font"] = pygame.Font(main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"], main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font Size"])
        else: main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"] = ""; main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font"] = pygame.Font(None, main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font Size"])
      except: main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font"] = pygame.Font("Fonts/" + main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"], main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font Size"]); main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"] = main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font"]
    except: main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"] = main.fonts[main.selected_itemy]; main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font"] = pygame.font.SysFont(main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font STR"], main.ui.instances[main.selected_ui][main.selected_ui_mode]["Font Size"])
  
  elif isinstance(main.selected_object, Text):
    try: tfont = pygame.Font("Fonts/" + main.fonts[main.selected_itemy], 20); main.selected_object.font_str = "Fonts/" + main.fonts[main.selected_itemy]; main.selected_object.regenerate(); main.gamestate = 43
    except: tfont = pygame.font.SysFont(main.fonts[main.selected_itemy], 20); main.selected_object.font_str = main.fonts[main.selected_itemy]; main.selected_object.regenerate(); main.gamestate = 43

#İmage Library
def add_image(none):
  if main.selected_object == None:
    if main.selected_image_index == 1:
      main.ui.instances[main.selected_ui][main.selected_ui_mode]["I Image"] = main.images[main.selected_itemy]
      if type(main.images[main.selected_itemy]) != list:
        if os.path.isdir(main.active_directory + "Assets/images/" + main.images[main.selected_itemy]):
          main.ui.instances[main.selected_ui][main.selected_ui_mode]["Surface"] = []
          for image in sorted(os.listdir(main.active_directory + "Assets/images/" + main.images[main.selected_itemy]), key=extract_number): main.ui.instances[main.selected_ui][main.selected_ui_mode]["Surface"].append(pygame.image.load(main.active_directory + f"Assets/images/" + main.images[main.selected_itemy] + "/" + image).convert_alpha())
        else: main.ui.instances[main.selected_ui][main.selected_ui_mode]["Surface"] = pygame.image.load(main.active_directory + "Assets/images/" + main.images[main.selected_itemy]).convert_alpha()
      else:
        main.ui.instances[main.selected_ui][main.selected_ui_mode]["Surface"] = ["indexed"]
        for index, image in enumerate(main.images[main.selected_itemy]): main.ui.instances[main.selected_ui][main.selected_ui_mode]["Surface"].append(pygame.image.load(main.active_directory + f"Assets/images/" + main.images[main.selected_itemy][index]).convert_alpha())
    if main.selected_image_index == 2:
      main.ui.instances[main.selected_ui][main.selected_ui_mode]["I Image 2"] = main.images[main.selected_itemy]
      if type(main.images[main.selected_itemy]) != list:
        if os.path.isdir(main.active_directory + "Assets/images/" + main.images[main.selected_itemy]):
          main.ui.instances[main.selected_ui][main.selected_ui_mode]["Surface 2"] = []
          for image in sorted(os.listdir(main.active_directory + "Assets/images/" + main.images[main.selected_itemy]), key=extract_number): main.ui.instances[main.selected_ui][main.selected_ui_mode]["Surface 2"].append(pygame.image.load(main.active_directory + f"Assets/images/" + main.images[main.selected_itemy] + "/" + image).convert_alpha())
        else: main.ui.instances[main.selected_ui][main.selected_ui_mode]["Surface 2"] = pygame.image.load(main.active_directory + "Assets/images/" + main.images[main.selected_itemy]).convert_alpha()
      else:
        main.ui.instances[main.selected_ui][main.selected_ui_mode]["Surface 2"] = ["indexed"]
        for index, image in enumerate(main.images[main.selected_itemy]): main.ui.instances[main.selected_ui][main.selected_ui_mode]["Surface 2"].append(pygame.image.load(main.active_directory + f"Assets/images/" + main.images[main.selected_itemy][index]).convert_alpha())
    go_to(35); main.selected_image_index = 1

def delete_projectile(none):
  if main.projectiles: main.projectiles.remove(main.projectiles[main.selected_itemy])

def change_proj_x_speed(by): main.projectiles[main.selected_itemy].speed[0] += by
def change_proj_y_speed(by): main.projectiles[main.selected_itemy].speed[1] += by
def change_proj_lifetime(by):
  main.projectiles[main.selected_itemy].lifespan += by
  if main.projectiles[main.selected_itemy].lifespan <= 0: main.projectiles[main.selected_itemy].lifespan = 0
  main.projectiles[main.selected_itemy].lifespan = round(main.projectiles[main.selected_itemy].lifespan, 2)
def change_proj_frame_speed(by):
  main.projectiles[main.selected_itemy].anim_speed += by
  if main.projectiles[main.selected_itemy].anim_speed < 1: main.projectiles[main.selected_itemy].anim_speed = 1
def change_proj_x_spawn_min(by):
  if by > 0 and main.projectiles[main.selected_itemy].set_pos_min_range[0] == main.projectiles[main.selected_itemy].set_pos_max_range[0]: main.projectiles[main.selected_itemy].set_pos_max_range[0] += by
  main.projectiles[main.selected_itemy].set_pos_min_range[0] += by
  if main.projectiles[main.selected_itemy].set_pos_min_range[0] > main.projectiles[main.selected_itemy].set_pos_max_range[0]: main.projectiles[main.selected_itemy].set_pos_min_range[0] = main.projectiles[main.selected_itemy].set_pos_max_range[0]
def change_proj_x_spawn_max(by):
  if by < 0 and main.projectiles[main.selected_itemy].set_pos_max_range[0] == main.projectiles[main.selected_itemy].set_pos_min_range[0]: main.projectiles[main.selected_itemy].set_pos_min_range[0] += by
  main.projectiles[main.selected_itemy].set_pos_max_range[0] += by
  if main.projectiles[main.selected_itemy].set_pos_max_range[0] < main.projectiles[main.selected_itemy].set_pos_min_range[0]: main.projectiles[main.selected_itemy].set_pos_max_range[0] = main.projectiles[main.selected_itemy].set_pos_min_range[0]
def change_proj_y_spawn_min(by):
  if by > 0 and main.projectiles[main.selected_itemy].set_pos_min_range[1] == main.projectiles[main.selected_itemy].set_pos_max_range[1]: main.projectiles[main.selected_itemy].set_pos_max_range[1] += by
  main.projectiles[main.selected_itemy].set_pos_min_range[1] += by
  if main.projectiles[main.selected_itemy].set_pos_min_range[1] > main.projectiles[main.selected_itemy].set_pos_max_range[1]: main.projectiles[main.selected_itemy].set_pos_min_range[1] = main.projectiles[main.selected_itemy].set_pos_max_range[1]
def change_proj_y_spawn_max(by):
  if by < 0 and main.projectiles[main.selected_itemy].set_pos_max_range[1] == main.projectiles[main.selected_itemy].set_pos_min_range[1]: main.projectiles[main.selected_itemy].set_pos_min_range[1] += by
  main.projectiles[main.selected_itemy].set_pos_max_range[1] += by
  if main.projectiles[main.selected_itemy].set_pos_max_range[1] < main.projectiles[main.selected_itemy].set_pos_min_range[1]: main.projectiles[main.selected_itemy].set_pos_max_range[1] = main.projectiles[main.selected_itemy].set_pos_min_range[1]
def toggle_proj_deal_again(none): main.projectiles[main.selected_itemy].deal_again = not main.projectiles[main.selected_itemy].deal_again
def toggle_proj_pierce(none): main.projectiles[main.selected_itemy].pierce = not main.projectiles[main.selected_itemy].pierce
def toggle_proj_stoppable(none): main.projectiles[main.selected_itemy].stoppable = not main.projectiles[main.selected_itemy].stoppable
def toggle_proj_returnable(none): main.projectiles[main.selected_itemy].returnable = not main.projectiles[main.selected_itemy].returnable
def toggle_proj_stop_at_collision(none): main.projectiles[main.selected_itemy].stop_at_collision = not main.projectiles[main.selected_itemy].stop_at_collision
def toggle_proj_die_at_collision(none): main.projectiles[main.selected_itemy].die_at_collision = not main.projectiles[main.selected_itemy].die_at_collision
def toggle_proj_sine(none): main.projectiles[main.selected_itemy].oscil_ease = not main.projectiles[main.selected_itemy].oscil_ease
def toggle_proj_guided(none): main.projectiles[main.selected_itemy].guided = not main.projectiles[main.selected_itemy].guided
def toggle_proj_beam(none): main.projectiles[main.selected_itemy].beam = not main.projectiles[main.selected_itemy].beam
def toggle_proj_dr(none): main.projectiles[main.selected_itemy].directional_relative = not main.projectiles[main.selected_itemy].directional_relative
def toggle_proj_bounce(none): main.projectiles[main.selected_itemy].bounce = not main.projectiles[main.selected_itemy].bounce
def toggle_proj_around_platform(none): main.projectiles[main.selected_itemy].around_platform = not main.projectiles[main.selected_itemy].around_platform
def change_proj_oscillation_speed(by):
  main.projectiles[main.selected_itemy].oscil_speed += by
  if main.projectiles[main.selected_itemy].oscil_speed < 0: main.projectiles[main.selected_itemy].oscil_speed = 0
def change_proj_frequency(by): main.projectiles[main.selected_itemy].frequency += by
def change_proj_vibrate(by): main.projectiles[main.selected_itemy].vibrate += by
def change_proj_weight_x(by): main.projectiles[main.selected_itemy].weight[0] += by
def change_proj_weight_y(by): main.projectiles[main.selected_itemy].weight[1] += by
def change_proj_apply_weight_after(by):
  main.projectiles[main.selected_itemy].apply_weight_after += by
  if main.projectiles[main.selected_itemy].apply_weight_after < 0: main.projectiles[main.selected_itemy].apply_weight_after = 0
def change_proj_stop_x_after(by):
  main.projectiles[main.selected_itemy].stop_motion_after[0] += by
  if main.projectiles[main.selected_itemy].stop_motion_after[0] < 0: main.projectiles[main.selected_itemy].stop_motion_after[0] = 0
def change_proj_stop_y_after(by):
  main.projectiles[main.selected_itemy].stop_motion_after[1] += by
  if main.projectiles[main.selected_itemy].stop_motion_after[1] < 0: main.projectiles[main.selected_itemy].stop_motion_after[1] = 0
def change_proj_stop_x_for(by):
  main.projectiles[main.selected_itemy].stop_motion_for[0] += by
  if main.projectiles[main.selected_itemy].stop_motion_for[0] < 0: main.projectiles[main.selected_itemy].stop_motion_for[0] = 0
def change_proj_stop_y_for(by):
  main.projectiles[main.selected_itemy].stop_motion_for[1] += by
  if main.projectiles[main.selected_itemy].stop_motion_for[1] < 0: main.projectiles[main.selected_itemy].stop_motion_for[1] = 0
def set_proj_pos_mode(mode): main.projectiles[main.selected_itemy].pos_mode = mode

def add_projectile(none): main.projectiles.append(ProjectileType(main.chr_projectiles[main.selected_itemy], main)); main.gamestate = 49

def remove_image(none):
  if main.selected_object == None:
    if main.selected_image_index == 1: main.ui.instances[main.selected_ui]["I Image"] = ""
    if main.selected_image_index == 2: main.ui.instances[main.selected_ui]["I Image 2"] = ""
    go_to(35); main.selected_image_index = 1

def add_menu_item(none): main.rooms[main.selected_room].menu["items"].append({"I": len(main.rooms[main.selected_room].menu["items"]), "X_I": 0, "Y_I": 0, "X_P": 0, "Y_P": 0, "TPX": 0, "TPY": 0, "IPX": 0, "IPY": 0, "X_PS": 0, "Y_PS": 0, "TPXS": 0, "TPYS": 0, "IPXS": 0, "IPYS": 0, "A": None, "T": "", "I_Anim_A": "DO", "O_Anim_A": "DO", "I_Anim_P": "DO", "O_Anim_P": "DO", "Cam_X": 0, "Cam_Y": 0, "Text_Data": ["None", 20, [], "", "White", "Transparent", "Black", False, False, False, False, False, "Left", 0, "LTR", 0, [0, 0], 255, 0, [False, False], "Default", False, ["", ""], 0, False], "Text_DataS": ["None", 20, [], "", "White", "Transparent", "Black", False, False, False, False, False, "Left", 0, "LTR", 0, [0, 0], 255, 0, [False, False], "Default", False, ["", ""], 0, False], "S": "", "Image_Path": "", "Image_PathS": "", "Anim_Rate": -1, "Anim_RateS": -1, "BX": 0, "BY": 0, "BW": 0, "BH": 0, "BT": 0, "BR": 0, "BD": 0, "BC": [], "BXS": 0, "BYS": 0, "BWS": 0, "BHS": 0, "BTS": 0, "BRS": 0, "BDS": 0, "BCS": [], "N1": "", "N2": "", "N3": "", "flags": [], "SFX": None, "Text_Surface": None, "Image_Surface": None, "Text_SurfaceS": None, "Image_SurfaceS": None, "Timer": Timer(), "Timer2": Timer(), "Clicked": False}); main.selected_menu_item_index = len(main.rooms[main.selected_room].menu["items"]) - 1
def remove_menu_item(none):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index: main.rooms[main.selected_room].menu["items"].remove(button)
  for index, button in enumerate(main.rooms[main.selected_room].menu["items"]): button["I"] = index
def paste_text_data_to_menu_item(none):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item:
        button["Text_Data"] = main.clipboard_text_data
        try:
          try: font = pygame.Font(button["Text_Data"][0], button["Text_Data"][1])
          except: font = pygame.font.SysFont(button["Text_Data"][0], button["Text_Data"][1])
        except: font = pygame.Font(None, button["Text_Data"][1])
        font.set_script("Arab"); font.set_bold(button["Text_Data"][7]); font.set_italic(button["Text_Data"][8]); font.set_underline(button["Text_Data"][9]); font.set_strikethrough(button["Text_Data"][10])
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
        image = pygame.transform.rotate(image, button["Text_Data"][15]); image = pygame.transform.flip(image, button["Text_Data"][19][0], button["Text_Data"][19][1])
        if button["Text_Data"][18]:
          ol_image = image; image = pygame.mask.from_surface(image).convolve(pygame.mask.Mask((button["Text_Data"][18], button["Text_Data"][18]), fill=True)).to_surface(setcolor=button["Text_Data"][6], unsetcolor=image.get_colorkey()).convert_alpha(); image.blit(ol_image, (button["Text_Data"][18] / 2, button["Text_Data"][18] / 2))
        image.set_alpha(button["Text_Data"][17]); button["Text_Surface"] = image
        button["Text_DataS"] = main.clipboard_text_data
        try:
          try: font = pygame.Font(button["Text_DataS"][0], button["Text_DataS"][1])
          except: font = pygame.font.SysFont(button["Text_DataS"][0], button["Text_DataS"][1])
        except: font = pygame.Font(None, button["Text_DataS"][1])
        font.set_script("Arab"); font.set_bold(button["Text_DataS"][7]); font.set_italic(button["Text_DataS"][8]); font.set_underline(button["Text_DataS"][9]); font.set_strikethrough(button["Text_DataS"][10])
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
        image = pygame.transform.rotate(image, button["Text_DataS"][15]); image = pygame.transform.flip(image, button["Text_DataS"][19][0], button["Text_DataS"][19][1])
        if button["Text_DataS"][18]:
          ol_image = image; image = pygame.mask.from_surface(image).convolve(pygame.mask.Mask((button["Text_DataS"][18], button["Text_DataS"][18]), fill=True)).to_surface(setcolor=button["Text_DataS"][6], unsetcolor=image.get_colorkey()).convert_alpha(); image.blit(ol_image, (button["Text_DataS"][18] / 2, button["Text_DataS"][18] / 2))
        image.set_alpha(button["Text_DataS"][17]); button["Text_SurfaceS"] = image
      else:
        if main.selected_menu_item_mode:
          button["Text_DataS"] = main.clipboard_text_data
          try:
            try: font = pygame.Font(button["Text_DataS"][0], button["Text_DataS"][1])
            except: font = pygame.font.SysFont(button["Text_DataS"][0], button["Text_DataS"][1])
          except: font = pygame.Font(None, button["Text_DataS"][1])
          font.set_script("Arab"); font.set_bold(button["Text_DataS"][7]); font.set_italic(button["Text_DataS"][8]); font.set_underline(button["Text_DataS"][9]); font.set_strikethrough(button["Text_DataS"][10])
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
          image = pygame.transform.rotate(image, button["Text_DataS"][15]); image = pygame.transform.flip(image, button["Text_DataS"][19][0], button["Text_DataS"][19][1])
          if button["Text_DataS"][18]:
            ol_image = image; image = pygame.mask.from_surface(image).convolve(pygame.mask.Mask((button["Text_DataS"][18], button["Text_DataS"][18]), fill=True)).to_surface(setcolor=button["Text_DataS"][6], unsetcolor=image.get_colorkey()).convert_alpha(); image.blit(ol_image, (button["Text_DataS"][18] / 2, button["Text_DataS"][18] / 2))
          image.set_alpha(button["Text_DataS"][17]); button["Text_SurfaceS"] = image
        else:
          button["Text_Data"] = main.clipboard_text_data
          try:
            try: font = pygame.Font(button["Text_Data"][0], button["Text_Data"][1])
            except: font = pygame.font.SysFont(button["Text_Data"][0], button["Text_Data"][1])
          except: font = pygame.Font(None, button["Text_Data"][1])
          font.set_script("Arab"); font.set_bold(button["Text_Data"][7]); font.set_italic(button["Text_Data"][8]); font.set_underline(button["Text_Data"][9]); font.set_strikethrough(button["Text_Data"][10])
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
          image = pygame.transform.rotate(image, button["Text_Data"][15]); image = pygame.transform.flip(image, button["Text_Data"][19][0], button["Text_Data"][19][1])
          if button["Text_Data"][18]:
            ol_image = image; image = pygame.mask.from_surface(image).convolve(pygame.mask.Mask((button["Text_Data"][18], button["Text_Data"][18]), fill=True)).to_surface(setcolor=button["Text_Data"][6], unsetcolor=image.get_colorkey()).convert_alpha(); image.blit(ol_image, (button["Text_Data"][18] / 2, button["Text_Data"][18] / 2))
          image.set_alpha(button["Text_Data"][17]); button["Text_Surface"] = image
def paste_image_to_menu_item(none):
  if main.clipboard_image_path:
    for button in main.rooms[main.selected_room].menu["items"]:
      if button["I"] == main.selected_menu_item_index:
        if main.selected_both_selected_and_unselected_menu_item:
          button["Image_Path"] = main.clipboard_image_path
          if os.path.isdir(main.clipboard_image_path):
            button["Image_Surface"] = []; button["Anim_Rate"] = main.clipboard_anim_rate
            for image in sorted(os.listdir(main.clipboard_image_path), key=extract_number): button["Image_Surface"].append(pygame.image.load(main.active_directory + main.clipboard_image_path + "/" + image).convert_alpha())
          else: button["Image_Surface"] = pygame.image.load(main.active_directory + button["Image_Path"]).convert_alpha(); button["Anim_Rate"] = -1
          button["Image_PathS"] = main.clipboard_image_path
          if os.path.isdir(main.clipboard_image_path):
            button["Image_SurfaceS"] = []; button["Anim_RateS"] = main.clipboard_anim_rate
            for image in sorted(os.listdir(main.clipboard_image_path), key=extract_number): button["Image_SurfaceS"].append(pygame.image.load(main.active_directory + main.clipboard_image_path + "/" + image).convert_alpha())
          else: button["Image_SurfaceS"] = pygame.image.load(main.active_directory + button["Image_PathS"]).convert_alpha(); button["Anim_RateS"] = -1
        else:
          if main.selected_menu_item_mode:
            button["Image_PathS"] = main.clipboard_image_path
            if os.path.isdir(main.clipboard_image_path):
              button["Image_SurfaceS"] = []; button["Anim_RateS"] = main.clipboard_anim_rate
              for image in sorted(os.listdir(main.clipboard_image_path), key=extract_number): button["Image_SurfaceS"].append(pygame.image.load(main.active_directory + main.clipboard_image_path + "/" + image).convert_alpha())
            else: button["Image_SurfaceS"] = pygame.image.load(main.active_directory + button["Image_PathS"]).convert_alpha(); button["Anim_RateS"] = -1
          else:
            button["Image_Path"] = main.clipboard_image_path
            if os.path.isdir(main.clipboard_image_path):
              button["Image_Surface"] = []; button["Anim_Rate"] = main.clipboard_anim_rate
              for image in sorted(os.listdir(main.clipboard_image_path), key=extract_number): button["Image_Surface"].append(pygame.image.load(main.active_directory + main.clipboard_image_path + "/" + image).convert_alpha())
            else: button["Image_Surface"] = pygame.image.load(main.active_directory + button["Image_Path"]).convert_alpha(); button["Anim_Rate"] = -1
def remove_text_data_from_menu_item(none):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item:
        button["Text_Data"] = ["None", 20, [], "", "White", "Transparent", "Black", False, False, False, False, False, "Left", 0, "LTR", 0, [0, 0], 255, 0, [False, False], "Default", False, ["", ""], 0, False]
        button["Text_Surface"] = None
        button["Text_DataS"] = ["None", 20, [], "", "White", "Transparent", "Black", False, False, False, False, False, "Left", 0, "LTR", 0, [0, 0], 255, 0, [False, False], "Default", False, ["", ""], 0, False]
        button["Text_SurfaceS"] = None
      else:
        if main.selected_menu_item_mode:
          button["Text_DataS"] = ["None", 20, [], "", "White", "Transparent", "Black", False, False, False, False, False, "Left", 0, "LTR", 0, [0, 0], 255, 0, [False, False], "Default", False, ["", ""], 0, False]
          button["Text_SurfaceS"] = None
        else:
          button["Text_Data"] = ["None", 20, [], "", "White", "Transparent", "Black", False, False, False, False, False, "Left", 0, "LTR", 0, [0, 0], 255, 0, [False, False], "Default", False, ["", ""], 0, False]
          button["Text_Surface"] = None
def remove_image_from_menu_item(none):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item:
        button["Image_Path"] = ""
        button["Image_Surface"] = None
        button["Anim_Rate"] = -1
        button["Image_PathS"] = ""
        button["Image_SurfaceS"] = None
        button["Anim_RateS"] = -1
      else:
        if main.selected_menu_item_mode:
          button["Image_PathS"] = ""
          button["Image_SurfaceS"] = None
          button["Anim_RateS"] = -1
        elif main.selected_both_selected_and_unselected_menu_item:
          button["Image_Path"] = ""
          button["Image_Surface"] = None
          button["Anim_Rate"] = -1
def change_menu_item_x_index(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      button["X_I"] += by
def change_menu_item_y_index(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      button["Y_I"] += by
def change_selected_menu_item_index(by): main.selected_menu_item_index += by
def move_selected_menu_item_index_up(none):
    items = main.rooms[main.selected_room].menu["items"]
    idx = main.selected_menu_item_index
    if idx > 0:
      items[idx], items[idx - 1] = items[idx - 1], items[idx]
      items[idx]["I"], items[idx - 1]["I"] = idx, idx - 1
      main.selected_menu_item_index -= 1
def move_selected_menu_item_index_down(none):
    items = main.rooms[main.selected_room].menu["items"]
    idx = main.selected_menu_item_index
    if idx < len(items) - 1:
      items[idx], items[idx + 1] = items[idx + 1], items[idx]
      items[idx]["I"], items[idx + 1]["I"] = idx, idx + 1
      main.selected_menu_item_index += 1
def change_menu_item_x_pos(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item: button["X_P"] += by; button["X_PS"] += by
      else:
        if main.selected_menu_item_mode: button["X_PS"] += by
        else: button["X_P"] += by
def change_menu_item_y_pos(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item: button["Y_P"] += by; button["Y_PS"] += by
      else:
        if main.selected_menu_item_mode: button["Y_PS"] += by
        else: button["Y_P"] += by
def change_menu_item_text_x_pos(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item: button["TPX"] += by; button["TPXS"] += by
      else:
        if main.selected_menu_item_mode: button["TPXS"] += by
        else: button["TPX"] += by
def change_menu_item_text_y_pos(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item: button["TPY"] += by; button["TPYS"] += by
      else:
        if main.selected_menu_item_mode: button["TPYS"] += by
        else: button["TPY"] += by
def change_menu_item_image_x_pos(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item: button["IPX"] += by; button["IPXS"] += by
      else:
        if main.selected_menu_item_mode: button["IPXS"] += by
        else: button["IPX"] += by
def change_menu_item_image_y_pos(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item: button["IPY"] += by; button["IPYS"] += by
      else:
        if main.selected_menu_item_mode: button["IPYS"] += by
        else: button["IPY"] += by
def change_menu_item_camera_x_susceptibility(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      button["Cam_X"] += by
def change_menu_item_camera_y_susceptibility(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      button["Cam_Y"] += by
def toggle_menu_start_appear(none):
  if "active" in main.rooms[main.selected_room].menu["flags"]: main.rooms[main.selected_room].menu["flags"].remove("active")
  else: main.rooms[main.selected_room].menu["flags"].append("active")
def toggle_reset_menu(none):
  if "reset" in main.rooms[main.selected_room].menu["flags"]: main.rooms[main.selected_room].menu["flags"].remove("reset")
  else: main.rooms[main.selected_room].menu["flags"].append("reset")
def toggle_make_menu_joinable(none):
  if "in" in main.rooms[main.selected_room].menu["flags"]: main.rooms[main.selected_room].menu["flags"].remove("in")
  else: main.rooms[main.selected_room].menu["flags"].append("in")
def switch_menu_item_mode(none): main.selected_menu_item_mode = not main.selected_menu_item_mode
def switch_menu_item_mode_edit_both(none): main.selected_both_selected_and_unselected_menu_item = not main.selected_both_selected_and_unselected_menu_item
def action_and_outline_settings(none):
  main.gamestate, main.remember_gs = 59, 58
  main.buttons[59].clear()
  if main.selected_menu_item_mode: s = " (Selected)"
  else: s = " (Unselected)"
  for index, cs in enumerate(main.rooms[main.selected_room].cutscenes):
    main.buttons[59].append(Button(50, 100 + (index * 25), fontsmall.render(cs.name, True, "White").get_width(), 16, "Trigger this Cutscene", cs.name, select_cutscene, target=cs.name, button_type="Cutscene Name", font=fontsmall))
  main.buttons[59].append(Button(418, 55, 32, 32, "Outline Around Text", "Assets/editor/text2.png", toggle_menu_item_outline_around_text))
  main.buttons[59].append(Button(452, 55, 32, 32, "Outline Around Image", "Assets/editor/image.png", toggle_menu_item_outline_around_image))
  main.buttons[59].append(Button(418, 350, 32, 32, "Remove Color", "Assets/editor/delete.png", remove_menu_item_outline_color))
  for x, button in enumerate([("Decrease X Displacement", "less", -1), ("İncrease X Displacement", "more", 1)]):
    main.buttons[59].append(Button(225 + (x * 150), 70, 32, 32, button[0] + s, "Assets/editor/" + button[1] + ".png", change_menu_item_outline_x_displacement, target=button[2]))
  for x, button in enumerate([("Decrease Y Displacement", "less", -1), ("İncrease Y Displacement", "more", 1)]):
    main.buttons[59].append(Button(225 + (x * 150), 110, 32, 32, button[0] + s, "Assets/editor/" + button[1] + ".png", change_menu_item_outline_y_displacement, target=button[2]))
  for x, button in enumerate([("Decrease Width Displacement", "less", -1), ("İncrease Width Displacement", "more", 1)]):
    main.buttons[59].append(Button(225 + (x * 150), 150, 32, 32, button[0] + s, "Assets/editor/" + button[1] + ".png", change_menu_item_outline_width_displacement, target=button[2]))
  for x, button in enumerate([("Decrease Height Displacement", "less", -1), ("İncrease Height Displacement", "more", 1)]):
    main.buttons[59].append(Button(225 + (x * 150), 190, 32, 32, button[0] + s, "Assets/editor/" + button[1] + ".png", change_menu_item_outline_height_displacement, target=button[2]))
  for x, button in enumerate([("Decrease Thickness", "less", -1), ("İncrease Thickness", "more", 1)]):
    main.buttons[59].append(Button(225 + (x * 150), 230, 32, 32, button[0] + s, "Assets/editor/" + button[1] + ".png", change_menu_item_outline_thickness, target=button[2]))
  for x, button in enumerate([("Decrease Radius", "less", -1), ("İncrease Radius", "more", 1)]):
    main.buttons[59].append(Button(225 + (x * 150), 270, 32, 32, button[0] + s, "Assets/editor/" + button[1] + ".png", change_menu_item_outline_radius, target=button[2]))
  for x, button in enumerate([("Decrease Color Rate", "less", -1), ("İncrease Color Rate", "more", 1)]):
    main.buttons[59].append(Button(225 + (x * 150), 310, 32, 32, button[0] + s, "Assets/editor/" + button[1] + ".png", change_menu_item_outline_color_rate, target=button[2]))
  for x, button in enumerate([("Decrease Color Index", "less", -1), ("İncrease Color Index", "more", 1)]):
    main.buttons[59].append(Button(225 + (x * 150), 350, 32, 32, button[0] + s, "Assets/editor/" + button[1] + ".png", change_menu_item_outline_color_index, target=button[2]))
  for x, color in enumerate(colors):
    main.buttons[59].append(Button((WIDTH - 94) + math.floor(x / 15) * 16, 100 + ((x % 15) * 16), 16, 16, "Outline Color > " + color, "", set_menu_item_outline_color, target=colors[color], color=colors[color], button_type="MIOL Color"))
def change_menu_item_outline_x_displacement(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item: button["BX"] += by; button["BXS"] += by
      else:
        if main.selected_menu_item_mode: button["BXS"] += by
        else: button["BX"] += by
def change_menu_item_outline_y_displacement(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item: button["BY"] += by; button["BYS"] += by
      else:
        if main.selected_menu_item_mode: button["BYS"] += by
        else: button["BY"] += by
def change_menu_item_outline_width_displacement(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item: button["BW"] += by; button["BWS"] += by
      else:
        if main.selected_menu_item_mode: button["BWS"] += by
        else: button["BW"] += by
def change_menu_item_outline_height_displacement(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item: button["BH"] += by; button["BHS"] += by
      else:
        if main.selected_menu_item_mode: button["BHS"] += by
        else: button["BH"] += by
def change_menu_item_outline_thickness(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item: button["BT"] += by; button["BTS"] += by
      else:
        if main.selected_menu_item_mode: button["BTS"] += by
        else: button["BT"] += by
def change_menu_item_outline_radius(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item: button["BR"] += by; button["BRS"] += by
      else:
        if main.selected_menu_item_mode: button["BRS"] += by
        else: button["BR"] += by
def change_menu_item_outline_color_rate(by):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if main.selected_both_selected_and_unselected_menu_item: button["BD"] += by; button["BDS"] += by
      else:
        if main.selected_menu_item_mode: button["BDS"] += by
        else: button["BD"] += by
def change_menu_item_outline_color_index(by):
  color_amount = 0
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index: color_amount = len(button["BCS"]) if main.selected_menu_item_mode else len(button["BC"])
  main.selected_menu_item_outline_color_index += by
  if main.selected_menu_item_outline_color_index < 0: main.selected_menu_item_outline_color_index = 0
  if main.selected_menu_item_outline_color_index > color_amount: main.selected_menu_item_outline_color_index = color_amount
def set_menu_item_outline_color(color):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      try:
        if main.selected_menu_item_mode: button["BCS"][main.selected_menu_item_outline_color_index] = color
        else: button["BC"][main.selected_menu_item_outline_color_index] = color
      except IndexError:
        if main.selected_menu_item_mode: button["BCS"].append(color)
        else: button["BC"].append(color)
def remove_menu_item_outline_color(color):
  try:
    for button in main.rooms[main.selected_room].menu["items"]:
      if button["I"] == main.selected_menu_item_index:
        try:
          if main.selected_menu_item_mode: button["BCS"].remove(button["BCS"][main.selected_menu_item_outline_color_index]); main.selected_menu_item_outline_color_index -= 1
          else: button["BC"].remove(button["BC"][main.selected_menu_item_outline_color_index]); main.selected_menu_item_outline_color_index -= 1
        except IndexError:
          if main.selected_menu_item_mode: button["BCS"].remove(button["BCS"][main.selected_menu_item_outline_color_index]); main.selected_menu_item_outline_color_index -= 1
          else: button["BC"].remove(button["BC"][main.selected_menu_item_outline_color_index]); main.selected_menu_item_outline_color_index -= 1
    if main.selected_menu_item_outline_color_index < 0: main.selected_menu_item_outline_color_index = 0
  except IndexError: pass
def toggle_menu_item_outline_around_text(none):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if "olat" in button["flags"]: button["flags"].remove("olat")
      else: button["flags"].append("olat")
def toggle_menu_item_outline_around_image(none):
  for button in main.rooms[main.selected_room].menu["items"]:
    if button["I"] == main.selected_menu_item_index:
      if "olai" in button["flags"]: button["flags"].remove("olai")
      else: button["flags"].append("olai")

def playtest(none):
  global FPS, k_z; main.gamestate = 10; FPS = main.fps; main.playback_on = False
  if k_z: main.current_room = 0; main.selected_room = 0
  try:
    if main.rooms[main.current_room].first_track: pygame.mixer.music.load(main.active_directory + f"Sounds/tracks/{main.rooms[main.selected_room].first_track}"); pygame.mixer.music.play(1, 0.0); main.track = main.rooms[main.selected_room].first_track
    else: pygame.mixer.music.load(main.active_directory + f"Sounds/tracks/{main.rooms[main.selected_room].track}"); pygame.mixer.music.play(-1, 0.0); main.track = main.rooms[main.selected_room].track
  except: pass
  clear_game()

def stop_playtest(none):
  global FPS; main.gamestate = 0; FPS = 240; main.selected_room = main.current_room; pygame.mixer.music.stop()
  clear_game()

def clear_game(none=None):
  global k_a, k_b, k_x, k_y, k_right, k_left, k_up, k_down, k_r, k_l, k_z, k_select, k_start, k_back
  for player in main.players: player.clear(); player.hidden = not player.spawn_as_visible; player.rect.x, player.rect.y = player.spawn_location[0], player.spawn_location[1]
  main.selected_key = 0; main.frame_timer.reset(); main.selected_cutscene = 0; main.last_frame_active = 0; main.display_text_timer.reset()
  main.camera.rect.x, main.camera.rect.y = 0, 0; main.camera.cs_speed = [0, 0]; main.camera.scroll = [0, 0]; main.camera.key_frame_rect.x, main.camera.key_frame_rect.y = main.camera.rect.x, main.camera.rect.y
  main.camera.follow_player = main.camera.spawn_follow_player; main.game_stats_range = main.spawn_game_stats_range
  for ui in main.ui.instances: main.ui.instances[ui]["Hidden"] = False
  for room in main.rooms:
    room.hm, room.vm, room.borders, room.selected_item = room.spawn_hm, room.spawn_vm, room.spawn_borders.copy(), [0, 0]
    if "active" in room.menu["flags"]: room.menu_active = True
    for button in room.menu["items"]: button["Timer"].reset(); button["Timer2"].reset(); button["Clicked"] = False
    for zone in room.zones: zone.passed = False; zone.left = False
    for layer in room.layers:
      for coin in layer.collectibles:
        coin.regenerate_values(); coin.cs_speed = [0, 0]; coin.cs_dest = [0, 0]; coin.cs_speed_dest = 0; coin.rect.x, coin.rect.y = coin.spawn_location[0], coin.spawn_location[1]; coin.alive = True; coin.active_debt = False; coin.hidden = not coin.spawn_as_visible; coin.speed = coin.spawn_speed
        if coin.anim_speed == -1: coin.frame = random.randrange(0, len(coin.images))
      for actor in layer.actors: actor.cs_speed = [0, 0]; actor.cs_dest = [0, 0]; actor.cs_speed_dest = 0; actor.clear(); actor.hidden = not actor.spawn_as_visible
      for tile in layer.tiles:
        tile.regenerate_values(); tile.alive = True; tile.destroyed = False; tile.broken_others = False; tile.hp = tile.spawn_hp; tile.rect.x, tile.rect.y = tile.spawn_location[0], tile.spawn_location[1]; tile.cs_speed = [0, 0]; tile.cs_dest = [0, 0]; tile.cs_speed_dest = 0; tile.hidden = not tile.spawn_as_visible; tile.crumbs.clear(); tile.timer.reset(); tile.disperse_timer.reset(); tile.chain_timer.reset()
        if not tile.instigator: tile.chain_speed = 0; tile.speed = tile.spawn_speed
      for text in layer.texts: text.rect.x = text.spawn_location[0]; text.rect.y = text.spawn_location[1]; text.cs_speed = [0, 0]; text.cs_dest = [0, 0]; text.cs_speed_dest = 0; text.regenerate(); text.hidden = not text.spawn_as_visible; text.timer.reset(); text.deceives = [0, 0]
    for door in room.doors: door.passable = door.spawn_passable; door.t_playing, door.t_over, door.tfi, door.cutscene_transport = False, False, 0, False; door.t_timer.reset(); door.alive = True; door.rect.x, door.rect.y = door.spawn_location[0], door.spawn_location[1]; door.cs_speed = [0, 0]; door.cs_dest = [0, 0]; door.cs_speed_dest = 0; door.hidden = not door.spawn_as_visible
    for bg in room.backgrounds: bg.rect.x, bg.rect.y = bg.spawn_location[0], bg.spawn_location[1]; bg.cs_speed = [0, 0]; bg.cs_dest = [0, 0]; bg.cs_speed_dest = 0; bg.hidden = not bg.spawn_as_visible; bg.timer.reset()
    for cs in room.cutscenes: cs.passed = False
    if room.shader:
      try:
        with open(main.active_directory + "Shaders/" + room.shader, "r", encoding="utf-8") as file: shader_code = file.read()
        room.shader_prog = ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=shader_code)
        room.shader_vao = ctx.vertex_array(room.shader_prog, [shader_buffer])
      except Exception as e: console.log("Shader " + room.shader + " not found or contains an error. Using default shader instead."); console.log("GLSL Error: " + str(e)[:-2], "Red"); room.shader = ""; room.shader_prog = 0; room.shader_vao = 0
  try:
    for cs in main.rooms[main.current_room].cutscenes:
      if "Start of Room" in cs.conditions and not main.players: main.play_cutscene(cs); break
  except: pass
  for ui in main.ui.instances:
    if main.ui.instances[ui]["SM"] in main.rooms[main.current_room].show_ui: main.ui.instances[ui]["Hidden"] = False
    if main.ui.instances[ui]["SM"] in main.rooms[main.current_room].hide_ui: main.ui.instances[ui]["Hidden"] = True
  for chr in main.character_types:
    if "wallslide" in main.character_types[chr]["flags"]: main.character_types[chr]["object"].wall_slider = True
    else: main.character_types[chr]["object"].wall_slider = False
  main.random_const = random.randrange(0, 100)
  main.time_since_start = time()
  k_a = False; k_b = False; k_x = False; k_y = False
  k_right = False; k_left = False; k_up = False; k_down = False
  k_r = False; k_l = False
  k_z = False; k_select = False; k_start = False; k_back = False
  for controller in main.ports: controller.disable()














class Main:
  def __init__(self, editor_mode=True):
    self.reset()
    self.ports = [Controller(i, device="Default" if i == 1 else None) for i in range(1, 5)]
    self.editor_mode = editor_mode
    self.game_paused = False
    self.display_text_timer = Timer()
    self.display_text = ""
    self.track = ""
    self.render_filter = {"Linear": moderngl.LINEAR, "Nearest": moderngl.NEAREST}[config["Render Filter"]]
    self.color_swizzle = config["Color Swizzle"]
    self.load_additional_packages = False
    
    self.server_host = ""
    self.debug = False
    self.marine_snow_timer = Timer()
    self.marine_snow = []
    for i in range(70): self.marine_snow.append(MarineSnow(True))
    self.buttons = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []] #this is the buttons list, as you can see, there are many lists in this
    self.launcher_buttons = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]


    self.rename_text_username = ""
    self.rename_text_password = ""
    self.join_text_username = ""
    self.room_host = ""#and he receives from ui in that set_to_room function remember?
    self.room_players = []#
    self.client_instance = Client()
    self.packet = {}#that
    #self.client = Client("", "", self) Here

    if self.client_instance.online:
      console.log("Server link success", "Green")
    else:
      console.log("Server link failed. Switching to offline mode.", "Red")
      self.set_display_text("Server link failed. Switching to offline mode.")



    self.refresh_buttons()

     

  def reset(self, active_directory=""):
    global song, metadata
    self.gamestate = 0
    self.rooms = [] #that's because the first list will be filled with the buttons that will appear in the 1st gamestate
    self.players = [] #right here we have a list of players
    self.teams = []
    self.active_directory = active_directory
    self.tileset = os.listdir(self.active_directory + "Assets/tiles/")
    self.backgrounds = os.listdir(self.active_directory + "Assets/backgrounds/")
    self.images = compress_to_ind_suffix(os.listdir(self.active_directory + "Assets/images/"))
    self.collectibles = os.listdir(self.active_directory + "Assets/collectibles/")
    self.characters = os.listdir(self.active_directory + "Assets/characters/")
    self.tracks = os.listdir(self.active_directory + "Sounds/tracks/")
    self.sfx = compress_to_rnd_suffix(os.listdir(self.active_directory + "Sounds/sfx/"))
    self.fonts = os.listdir(self.active_directory + "Fonts/")
    self.shapes = os.listdir("Assets/editor/shapes/")
    self.shaders = os.listdir(self.active_directory + "Shaders/")
    self.saves = os.listdir("Saves/games/")
    self.tile_types = {}
    self.character_types = {}
    self.collectible_types = {}

    if hasattr(self, "buttons"):
      for button in self.buttons[0]:
        if "Access Layer" in button.text: self.buttons[0].remove(button)
      for button in self.buttons[0]:
        if button.button_type == "Background Layer": self.buttons[0].remove(button)
    
    for index, tex in enumerate(self.tileset):
      if os.path.isdir(self.active_directory + "Assets/tiles/" + tex): img = pygame.image.load(self.active_directory + "Assets/tiles/" + tex + "/1.png").convert_alpha(); self.tile_types[str(index)] = {"img": tex, "size": [img.get_width(), img.get_height()], "off": [0, 0], "ramp": 0, "hp": -1, "team": 0, "anim_s": 1, "destr_delay": 0, "step_sfx": "", "destr_sfx": "", "destr_anim": "Disappear", "flags": ["anim", "solid"]}
      else: img = pygame.image.load(self.active_directory + "Assets/tiles/" + tex).convert_alpha(); self.tile_types[str(index)] = {"img": tex, "size": [img.get_width(), img.get_height()], "off": [0, 0], "ramp": 0, "hp": -1, "team": 0, "anim_s": 1, "destr_delay": 0, "step_sfx": "", "destr_sfx": "", "destr_anim": "Disappear", "flags": ["solid"]}
    for index, col in enumerate(self.collectibles):
      img = pygame.image.load(self.active_directory + "Assets/collectibles/" + col + "/1.png").convert_alpha(); self.collectible_types[str(index)] = {"img": col, "size": [img.get_width(), img.get_height()], "off": [0, 0], "anim_s": 1, "stat": "", "value": 0, "sfx": "", "debt_sfx": "", "blocked_sfx": "", "cs": "", "anim": "Disappear", "ps": "", "pv": "", "ptm": "Do not show", "ptp": "Below", "font": "None", "font_size": 20, "flags": []}
    for index, chr in enumerate(self.characters):
      if os.listdir(self.active_directory + "Assets/characters/" + chr + "/") == ["down", "left", "right", "up"]: img = pygame.image.load(self.active_directory + "Assets/characters/" + chr + "/down/idle/1.png").convert_alpha(); self.character_types[str(index)] = {"type": chr, "object": Character(chr, self), "flags": ["td"]}
      else: img = pygame.image.load(self.active_directory + "Assets/characters/" + chr + "/idle/1.png").convert_alpha(); self.character_types[str(index)] = {"type": chr, "object": Character(chr, self), "flags": []}
    self.chr_frames = []
    self.chr_projectiles = os.listdir(self.active_directory + "Assets/projectiles/")
    self.projectiles = []

    #self.shader_programs = {}
    #for shader in self.shaders:
    #  program = ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)
    #  render_object = ctx.vertex_array(program, [shader_buffer])
       
    #for proj in self.chr_projectiles: self.projectiles.append(ProjectileType(proj, self))

    #list of devices connected
    self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

    if len(self.tracks) > 0: song = pygame.mixer.Sound(self.active_directory + "Sounds/tracks/" + self.tracks[0]); pygame.mixer_music.load(self.active_directory + "Sounds/tracks/" + self.tracks[0]); metadata = pygame.mixer_music.get_metadata()

    self.width, self.height = WIDTH, HEIGHT
    self.fps = 60
    self.game_name = ""
    self.publisher = ""
    self.mouse_state = ""
    self.undo_state = 0

    self.remember_gs = 0
    self.target_object = ""
    self.instance_target = None
    self.rename_target = ""
    self.rename_text = ""
    self.selected_rename_attrib = ""
    self.rooms.append(Room(main=self))
    self.selection_rect = pygame.Rect((0, 0), (0, 0))
    self.sr_release = True
    self.y_scroll = 0
    self.selected_room = 0
    self.selected_itemy = 0
    self.selected_itemx = 0
    self.selected_track = ""
    self.selected_layer = 0
    self.selected_tile = ()
    self.selected_tile_type = "0" #tile type index
    self.selected_character_type = "0" #entity type index
    self.selected_collectible_type = "0" #collectible type index
    self.selected_entity_type = "0" #entity type index
    self.selected_value = 1
    self.selected_bool = "True"
    self.selected_stat = ""
    self.selected_sfx = ""
    self.selected_sfx2 = ""
    self.selected_sfx3 = ""
    self.selected_sfx4 = ""
    self.selected_sfx5 = ""
    self.selected_speed = [0, 0]
    self.selected_background = 0
    self.selected_object = None
    self.selected_cutscene = 0
    self.selected_key = 0
    self.selected_range = 0
    self.selected_behaviors = []
    self.selected_animation = ""
    self.selected_drops = []
    self.selected_hp = 1
    self.selected_button = ""
    self.selected_state = ""
    self.selected_frame = 1
    self.selected_direction = "right"
    self.selected_dl = 0
    self.selected_cutscene_attrib = {}
    self.selected_cutscene_attrib_index = 0
    self.selected_ui = None
    self.selected_ui_mode = "1"
    self.selected_image_index = 1
    self.selected_player = 0
    self.selected_projectile = 1
    self.selected_ui_sm = 0
    self.selected_ui_mode_for_tm = 0
    self.selected_menu_item_index = 0
    self.selected_menu_item_mode = False
    self.selected_both_selected_and_unselected_menu_item = True
    self.selected_menu_item_outline_color_index = 0
    self.choosing_sfx = 1
    self.selecting_first_track = True
    self.tiles = []
    self.entity_types = {}
    self.top_tiles = []
    self.top_collectibles = []
    self.top_actors = []
    self.entity_behaviors = ["walk", "oscillate1", "oscillate2", "ledge_jump", "casual", "retaliator", "chase", "hop", "fly", "buzz", "slow buzz", "roll", "trap", "manuever", "strike", "shoot", "circular_range", "pbtc", "controlled", "in_frame_motion", "detrimental", "stompable_head", "solid", "invincible"]
    self.text_behaviors = ["shake h", "shake v", "tremble", "float v", "float v slow", "float v fast", "float h", "float h slow", "float h fast", "hover v", "hover v slow", "hover v fast", "hover h", "hover h slow", "hover h fast", "oscillate h", "oscillate v", "oscillate h slow", "oscillate v slow", "oscillate h fast", "oscillate v fast", "get h", "get v", "get h fast", "get v fast", "hop up slow", "hop right slow", "hop left slow", "hop down slow", "hop up fast", "hop right fast", "hop left fast", "hop down fast", "freak out", "central far up", "central up", "central", "central down", "central far down", "front", "type", "type fast", "type slow"]
    self.destroy_anims = ["Disappear", "Crumble", "Poof", "Disperse", "Fade Away", "S Descend", "Descend", "F Descend", "Zip Up", "Zip Right", "Zip Down", "Zip Left", "Tumble", "Q Tumble"]
    #self.destroy_anims = ["Disappear", "Crumble", "Poof", "Disperse", "S Descend", "Descend", "F Descend"]
    self.transitions = ["Fade to Room", "Fade to Color", "Cut to Color", "Gaussian Blur", "Box Blur", "Pixelate", "Rotate", "Wipe", "Shrink to Shape"]
    self.conditions = ["Start of Room", "Zone", "Collectible", "Stat", "Story Progress"]
    self.display_buttons = True
    self.hover_on_button = False
    self.user_certainty = False
    self.tiles_size = 32
    self.snap_tile_image = False
    self.snap_tile_rect = False
    self.text_cursor = 0
    self.on_page = 1
    self.page_amount = 1
    self.dir_preview_mode = "down"
    self.clipboard = None
    self.clipboard_text = ""
    self.clipboard_text_data = ["None", 30, [], "A B C", "White", "Transparent", "Black", False, False, False, False, False, "Left", 0, "LTR", 0, [0, 0], 255, 0, [False, False], "Default", False, ["", ""], 0, False]
    self.clipboard_image_path = ""
    self.clipboard_anim_rate = 0
    self.bg_frame_timer = Timer()
    self.animated_bg_images = []
    self.frame_timer = Timer()
    self.long_text_timer = Timer()
    self.long_text2_timer = Timer()
    self.playback_on = False
    self.key_frame_rect = pygame.Rect((0, 0), (0, 0))
    self.last_frame_active = 0
    #self.game_stats = {"Score": int, "Liras": int, "Arrows": int, "Hearts": float, "Red_Renk_Gem": bool, "Yellow_Renk_Gem": bool, "Green_Renk_Gem": bool, "Blue_Renk_Gem": bool, "Name": str}
    
    # self.game_stats = {"Score": int, "Hearts": int}
    # self.game_stats_initpoint = {"Score": 0, "Hearts": 3}
    # self.game_stats_effect = {"Score": "main score", "Hearts": "hp"}
    # self.game_stats_range = {"Score": [0, 0], "Hearts": [0, 5]}
    # self.spawn_game_stats_range = {"Score": [0, 0], "Hearts": [0, 5]}
    self.game_stats = {}
    self.game_stats_initpoint = {}
    self.game_stats_effect = {}
    self.game_stats_range = {}
    self.spawn_game_stats_range = {}
    #self.input_hold = {"A": False, "B": False, "X": False, "Y": False, "Right": True, "Left": True, "Up": True, "Down": True, "Shoulder_L": False, "Shoulder_R": False, "Z": False, "SELECT": False, "START": False}
    self.current_room = 0
    self.camera = Camera(main=self)
    self.playtest_on = False
    self.ui = UI(self)
    self.use_dt = True
    self.current_button_text = "           "
    self.current_button_has_image = False
    self.button_class = Button
    self.buttons_for_dragging_load = [access_cutscene, rename, delete_cutscene, access_layer, background_options]

    self.error_sfx = error_sfx
#self, x, y, width, height, character, main <---
    #self.rooms[0].actors.append(Entity(100, 100, "Keshya", self))

    self.prev_time = time()
    self.now = time()
    self.dt = self.now - self.prev_time
    self.prev_time = self.now
    self.time_since_start = time()
    self.random_const = random.randrange(0, 100)

    if True:
      self.fonts.append("Default")
      self.fonts.append("Agency FB")
      self.fonts.append("Algerian")
      self.fonts.append("Arabic Type Setting")
      self.fonts.append("Arial")
      self.fonts.append("Arial Black")
      self.fonts.append("Arial Rounded")
      self.fonts.append("Aldhabi")
      self.fonts.append("Andalus")
      self.fonts.append("Bahnschrift")
      self.fonts.append("Baskerville Oldface")
      self.fonts.append("Bauhaus 93")
      self.fonts.append("Bell")
      self.fonts.append("Berlin Sans FB")
      self.fonts.append("Berlin Sans FB Demi")
      self.fonts.append("Bernard Condensed")
      self.fonts.append("Bizud Gothic")
      self.fonts.append("Bizud Mincho Medium")
      self.fonts.append("Black Adder ITC")
      self.fonts.append("Bodoni")
      self.fonts.append("Bodoni Black")
      self.fonts.append("Bodoni Poster Compressed")
      self.fonts.append("Bookman Oldstyle")
      self.fonts.append("Book Antiqua")
      self.fonts.append("Bradley Hand ITC")
      self.fonts.append("Britannic")
      self.fonts.append("Broadway")
      self.fonts.append("Brush Script")
      self.fonts.append("Calibri")
      self.fonts.append("Californian FB")
      self.fonts.append("Calisto")
      self.fonts.append("Cambria")
      self.fonts.append("Cambria Math")
      self.fonts.append("Candara")
      self.fonts.append("Cascadi Amono Regular")
      self.fonts.append("Castellar")
      self.fonts.append("Centaur")
      self.fonts.append("Century")
      self.fonts.append("Century Gothic")
      self.fonts.append("Century School Book")
      self.fonts.append("Chiller")
      self.fonts.append("Colonna")
      self.fonts.append("Comic Sans MS")
      self.fonts.append("Consolas")
      self.fonts.append("Constantia")
      self.fonts.append("Cooperblack")
      self.fonts.append("Copperplate Gothic")
      self.fonts.append("Corbel")
      self.fonts.append("Courier New")
      self.fonts.append("Curlz")
      self.fonts.append("Dubai")
      self.fonts.append("Dubai Medium")
      self.fonts.append("Dubai Regular")
      self.fonts.append("Ebrima")
      self.fonts.append("Elephant")
      self.fonts.append("Engravers")
      self.fonts.append("Eras ITC")
      self.fonts.append("Eras Demi ITC")
      self.fonts.append("Eras Medium ITC")
      self.fonts.append("Extra")
      self.fonts.append("Felix Titling")
      self.fonts.append("Footlight")
      self.fonts.append("Forte")
      self.fonts.append("Franklin Gothic Book")
      self.fonts.append("Franklin Gothic Demi")
      self.fonts.append("Franklin Gothic Demicond")
      self.fonts.append("Franklin Gothic Heavy")
      self.fonts.append("Franklin Gothic Medium")
      self.fonts.append("Franklin Gothic Mediumcond")
      self.fonts.append("Free Sans Bold")
      self.fonts.append("Freestyle Script")
      self.fonts.append("French Script")
      self.fonts.append("Gabriola")
      self.fonts.append("Gadugi")
      self.fonts.append("Garamond")
      self.fonts.append("Georgia")
      self.fonts.append("Gigi")
      self.fonts.append("Gill Sans")
      self.fonts.append("Gill Sans Extcondensed")
      self.fonts.append("Gill Sans Ultra")
      self.fonts.append("Gloucester Extra Condensed")
      self.fonts.append("Goudystout")
      self.fonts.append("Goudy Old Style")
      self.fonts.append("Haetten Schweiler")
      self.fonts.append("Harlow Solid")
      self.fonts.append("Harrington")
      self.fonts.append("High Tower Text")
      self.fonts.append("Holomdl2assets")
      self.fonts.append("Informal Roman")
      self.fonts.append("Impact")
      self.fonts.append("Imprint Shadow")
      self.fonts.append("Inkfree")
      self.fonts.append("Javanese Text")
      self.fonts.append("Jokerman")
      self.fonts.append("Juice ITC")
      self.fonts.append("Kristen ITC")
      self.fonts.append("Kunstler Script")
      self.fonts.append("Leelawadee UI")
      self.fonts.append("Lucida Bright")
      self.fonts.append("Lucida Calligraphy")
      self.fonts.append("Lucida Console")
      self.fonts.append("Lucida Fax")
      self.fonts.append("Lucida Fax Regular")
      self.fonts.append("Lucida Sans")
      self.fonts.append("Lucida Sans Regular")
      self.fonts.append("Lucida Sans Roman")
      self.fonts.append("Lucida Sans Typewriter Oblique")
      self.fonts.append("Magneto")
      self.fonts.append("Mai and Ragd")
      self.fonts.append("Matura Script Capitals")
      self.fonts.append("Malgun Gothic")
      self.fonts.append("Malgun Gothic Semilight")
      self.fonts.append("Meiryo")
      self.fonts.append("Meiryo UI")
      self.fonts.append("Microsoft Himalaya")
      self.fonts.append("Microsoft Jhenghei")
      self.fonts.append("Microsoft New Tailue")
      self.fonts.append("Microsoft Phagspa")
      self.fonts.append("Microsoft Sans Serif")
      self.fonts.append("Microsoft Taile")
      self.fonts.append("Microsoft Uighur")
      self.fonts.append("Microsoft Yahei")
      self.fonts.append("Microsoft Yibaiti")
      self.fonts.append("Mingliuextb")
      self.fonts.append("Mistral")
      self.fonts.append("Modernno 20")
      self.fonts.append("Mongolian Baiti")
      self.fonts.append("Monotype Corsiva")
      self.fonts.append("MS Gothic")
      self.fonts.append("MS Mincho")
      self.fonts.append("MS Outlook")
      self.fonts.append("MS Reference Sans Serif")
      self.fonts.append("MS Reference Specialty")
      self.fonts.append("MV Boli")
      self.fonts.append("Myanmar Text")
      self.fonts.append("Niagara Engraved")
      self.fonts.append("Niagara Solid")
      self.fonts.append("Nirmala UI")
      self.fonts.append("Nirmala UI Semilight")
      self.fonts.append("NSimsun")
      self.fonts.append("Palace Script")
      self.fonts.append("Palatinolino Type")
      self.fonts.append("Papyrus")
      self.fonts.append("Parchment")
      self.fonts.append("Perpetua")
      self.fonts.append("Perpetua Titling")
      self.fonts.append("Playbill")
      self.fonts.append("Poor Richard")
      self.fonts.append("Pristina")
      self.fonts.append("Ocra Extended")
      self.fonts.append("Old English Text")
      self.fonts.append("Onyx")
      self.fonts.append("Rage")
      self.fonts.append("Ravie")
      self.fonts.append("Retroville NC")
      self.fonts.append("Rockwell")
      self.fonts.append("Rockwell Condensed")
      self.fonts.append("Rockwell Extra")
      self.fonts.append("Sakkalmajalla")
      self.fonts.append("Sans Serif Collection")
      self.fonts.append("Script")
      self.fonts.append("Segoe Fluent Icons")
      self.fonts.append("Segoe UI")
      self.fonts.append("Segoe UI Black")
      self.fonts.append("Segoe UI Emoji")
      self.fonts.append("Segoe UI Fluent Icons")
      self.fonts.append("Segoe UI Historic")
      self.fonts.append("Segoe UI Semibold")
      self.fonts.append("Segoe UI Semilight")
      self.fonts.append("Segoe UI Symbol")
      self.fonts.append("Segoe UI Variable")
      self.fonts.append("Serif")
      self.fonts.append("Showcard Gothic")
      self.fonts.append("Simplified Arabic")
      self.fonts.append("Simplified Arabic Fixed")
      self.fonts.append("Simsun")
      self.fonts.append("Simsun EXTB")
      self.fonts.append("Sitkatext")
      self.fonts.append("Snap ITC")
      self.fonts.append("Stencil")
      self.fonts.append("Sylfaen")
      self.fonts.append("Symbol")
      self.fonts.append("Tahoma")
      self.fonts.append("Tempus Sans ITC")
      self.fonts.append("Times New Roman")
      self.fonts.append("Traditional Arabic")
      self.fonts.append("Trebuchet MS")
      self.fonts.append("Twcen")
      self.fonts.append("Twcen Condensed")
      self.fonts.append("Uddigi Kyokashonb")
      self.fonts.append("Uddigi Kyokashonkb")
      self.fonts.append("Uddigi Kyokashonpb")
      self.fonts.append("Uddigi Kyokashonpr")
      self.fonts.append("Uddigi Kyokashonr")
      self.fonts.append("Urdu Type Setting")
      self.fonts.append("Vera Serif")
      self.fonts.append("Verdana")
      self.fonts.append("Vinerhand Itc")
      self.fonts.append("Vivaldi")
      self.fonts.append("Vladimir Script")
      self.fonts.append("Webdings")
      self.fonts.append("Wide Latin")
      self.fonts.append("Wingdings")
      self.fonts.append("Wingdings 2")
      self.fonts.append("Wingdings 3")
      self.fonts.append("Yu Gothic")
      self.fonts.append("Yu Gothic Medium")
      self.fonts.append("Yu Gothic Regular")
      self.fonts.append("Yu Gothic UI")
      self.fonts.append("Yu Gothic UI Semibold")
      self.fonts.append("Yu Gothic UI Semilight")
      self.fonts.append("Yu Gothic UI Regular")
      self.fonts.append("Yumincho")

  def refresh_buttons(self):
    self.buttons = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []] #this is the buttons list, as you can see, there are many lists in this
    self.launcher_buttons = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    # ROOM EDİTOR
    for x, button in enumerate([(l[lg]["Add Instance"], "add", add_object), (l[lg]["Delete Object"], "delete", delete_object), (l[lg]["Edit Object"], "cog", edit), (l[lg]["Manage Rooms"], "rooms", room), (l[lg]["Add Cutscene"], "cutscene", add_cutscene)]):
      self.buttons[0].append(Button(3 + (x * 34), 32, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    self.buttons[0].append(Button(180, 32, 32, 32, l[lg]["General Game Settings"], "Assets/editor/joystick.png", go_to, 2))
    self.buttons[0].append(Button(220, 32, 32, 32, l[lg]["Playtest"], "Assets/editor/play.png", playtest))
    self.buttons[0].append(Button(260, 32, 32, 32, l[lg]["Save Game"], "Assets/editor/save.png", save_game_file))
    self.buttons[0].append(Button(294, 32, 32, 32, l[lg]["Load Game"], "Assets/editor/load.png", go_to, target=45))
    # ADD OBJECT
    for x, button in enumerate([(l[lg]["New Player"], l[lg]["Select Instance"], add_player), (l[lg]["New Layer"], l[lg]["Select Instance"], add_layer), (l[lg]["New Background Layer"], l[lg]["Select Background Layer"], add_background), (l[lg]["New Zone"], l[lg]["Select Instance"], add_zone), (l[lg]["New Text"], l[lg]["Select Instance"], add_text)]): #(l[lg]["New Entity Type"], l[lg]["Select Instance Type"], add_entity_type), (l[lg]["New Collectible Type"], l[lg]["Select Instance Type"], add_collectible_type), 
      self.buttons[1].append(Button(64, 150 + (x * 32), 256, 18, button[1], button[0], button[2], color=(0, 25, 25), font=fontmedium))
    # GAME SETTİNGS
    for x, button in enumerate([(l[lg]["Game Statistics"], l[lg]["Statistics and İnventory"], go_to, 15), (l[lg]["Set Game Style"], l[lg]["Set Game Style"], go_to, 28), (l[lg]["Application Settings"], l[lg]["Control the Resolution and FPS"], go_to, 30)]): #(l[lg]["Ports and Devices"], l[lg]["Customize Controls for Inputs and Events"], go_to, 29), 
      self.buttons[2].append(Button(64, 150 + (x * 32), 256, 18, button[1], button[0], button[2], target=button[3], color=(0, 25, 25), font=fontmedium))
    self.buttons[2].append(Button(216, 322, 128, 18, "Set Up Tile Size", "Tiles' Size", change_tiles_size, target=self.tiles_size, target_object="Tile Size", target_gs=2))
    self.buttons[2].append(Button(392, 312, 32, 32, "Snap Tile Image to Tile Size", "Assets/editor/solid.png", snap_tiles_image_size))
    self.buttons[2].append(Button(426, 312, 32, 32, "Snap Tile Rect to Tile Size", "Assets/editor/tiles.png", snap_tiles_rect_size))
    for x, button in enumerate([("tile", "Manage Tiles", manage_tiles), ("stick figure", "Manage Entities", manage_entities), ("coin", "Manage Collectible", manage_collectibles), ("projectile", "Manage Projectiles", manage_projectiles)]):
      self.buttons[2].append(Button(54 + (x * 34), 312, 32, 32, button[1], "Assets/editor/" + button[0] + ".png", button[2], target=2))
    # ROOMS MANAGER
    for x, button in enumerate([(l[lg]["Go Back"], "back", go_to), (l[lg]["Add Room"], "add", add_room)]):
      self.buttons[3].append(Button(165 + (x * 34), 6, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=0))
    for x, button in enumerate([(l[lg]["Edit Room's Menu"], "multiple", edit_menu), (l[lg]["Edit Room"], "cog", edit_room), (l[lg]["Rename Room"], "pencil", rename), (l[lg]["Delete Room"], "delete", delete_room)]):
      self.buttons[3].append(Button((WIDTH - 136) + (x * 34), HEIGHT - 32, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target_gs=3, target_object="Room"))
    self.buttons[3].append(Button((WIDTH - 246), HEIGHT - 32, 32, 32, l[lg]["Create Door to This Room"], "Assets/editor/door.png", create_door))
    for x, button in enumerate([(l[lg]["Move Up"], "sort up", move_room_up), (l[lg]["Move Down"], "sort down", move_room_down)]):
      self.buttons[3].append(Button(WIDTH - 34, 250 + (x * 34), 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=0))
    # LETTERS
    for x, button in enumerate([("Copy Text", "copy text", copy_text), ("Delete All and Paste Text", "paste text", paste_text), ("Paste Text at Selection", "paste text", partial_paste_text)]):
      self.buttons[4].append(Button(WIDTH - (85 + (34 * x)), HEIGHT - 236, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], button_type="Text Edit"))
    
    for x, button in enumerate(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "!",   "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "?",   "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", ",",   "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", ".",   "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "_", "Backspace"]):
      if button != "Backspace": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=1))
      else: self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=1))
    for x, button in enumerate([",", ".", "!", "?", "<", ">", ":", ";", "\'", "\"", "[", "]", "{", "}",   "/", "\\", "|", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "=",   "_", "+", "×", "¡", "²", "³", "¤", "¼", "½", "¾", "‘", "’", "`", "~",   "€", "₺", "£", "¥", "₹", "₩", "₱", "₲", "®", "©", "♯", "⁂", "Space", "0",  "÷", "•", "✓", "✘", "´", "⊗", "⨷", "«", "»", "¬", "¶", "_", "Backspace"]):
      if button != "Space" and button != "Backspace" and button != "0": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=2))
      elif button == "Backspace": self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=2))
      elif button == "Space": self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "Space", add_space, page=2))
    
    for x, button in enumerate(["Á", "À", "Ä", "Å", "Â", "Ã", "Æ", "Ӑ", "Ą", "Ā", "ß", "Ç", "Č", "Ć",   "Ċ", "Ð", "É", "È", "Ë", "Ê", "Ę", "Ė", "Ē", "Ə", "Ğ", "Ǵ", "Ġ", "Ĥ",   "á", "à", "ä", "å", "â", "ã", "æ", "ӑ", "ą", "ā", "ß", "ç", "č", "ć",   "ċ", "ð", "é", "è", "ë", "ê", "ę", "ė", "ē", "ə", "ğ", "ǵ", "ġ", "ĥ",   "Í", "Ì", "Ï", "Î", "İ", "í", "ì", "ï", "î", "ı", "Ƒ", "ƒ", "_", "Backspace"]):
      if button != "Backspace": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=3))
      else: self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 185) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=3))
    for x, button in enumerate(["Ĵ", "Ķ", "Ḱ", "Ł", "M̃", "Ñ", "Ń", "Ǹ", "Ṅ", "Ó", "Ò", "Ö", "Ô", "Õ",   "Ø", "Œ", "Ō", "Ř", "Ş", "Ŝ", "Ś", "Þ", "Ţ", "Ú", "Ù", "Ü", "Û", "Ū",   "ĵ", "ķ", "ḱ", "ł", "m̃", "ñ", "ń", "ǹ", "ṅ", "ó", "ò", "ö", "ô", "õ",   "ø", "œ", "ō", "ř", "ş", "ŝ", "ś", "þ", "ţ", "ú", "ù", "ü", "û", "ū",   "Ṿ", "ṿ", "Ẃ", "ẃ", "X̂", "x̂", "Ý", "ý", "Ÿ", "ÿ", "Ž", "ž", "Ź", "ź"]):
      self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 185) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=4))
    
    for x, button in enumerate(["Α", "Β", "Γ", "Δ", "Ε", "Ζ", "Η", "Θ", "Ι", "Κ", "Λ", "Μ", "Ν", "Ξ",   "Ο", "Π", "Ρ", "Σ", "Τ", "Υ", "Φ", "Χ", "Ψ", "Ω", "Ἀ", "Ἐ", "Ἠ", "Ἰ",   "α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "ι", "κ", "λ", "μ", "ν", "ξ",   "ο", "π", "ρ", "σ", "ς", "τ", "υ", "φ", "χ", "ψ", "ω", "ἀ", "ἐ", "ἠ",   "ί", "ό", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "_", "Backspace"]):
      if button != "Backspace": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=5))
      else: self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=5))
    for x, button in enumerate(["А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И", "Й", "К", "Л", "М",   "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Ъ",   "а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м",   "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ",   "Ы", "Ь", "Э", "Ю", "Я", "ы", "ь", "э", "ю", "я", "_", "Backspace"]):
      if button != "Backspace": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=6))
      else: self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=6))
    for x, button in enumerate(["ا", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص",   "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "و", "ه", "ي",   "ى", "ة", "ء", "أ", "إ", "آ", "ۀ", "ؤ", "ئ", "پ", "چ", "ژ", "گ", "0", "َ", "ِ", "ُ", "ْ", "ّ", "ً", "ٍ", "ٌ", "ٰ", "ٴ", "0", "0", "Space", "0",   "١", "٢", "٣", "٤", "٥", "٦", "٧", "٨", "٩", "٠", "،", "؟", "_", "Backspace"]):
      if button != "Space" and button != "Backspace" and button != "0": self.buttons[4].append(Button((WIDTH - 28) - (20 + ((x % 14) * 34)), (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=7))
      elif button == "Backspace": self.buttons[4].append(Button((WIDTH - 28) - (12 + ((x % 14) * 34)) - 22, (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, "<", remove_letter, page=7))
      elif button == "Space": self.buttons[4].append(Button((WIDTH - 60) - (12 + ((x % 14) * 34)), (HEIGHT - 170) + math.floor(x / 14) * 34, 72, 32, button, "Space", add_space, page=7, shift_x_hitbox=20))
    
    for x, button in enumerate(["ـ", "ٵ", "ٶ", "ٷ", "ٹ", "ٺ", "ٻ", "ټ", "ٽ", "ٿ", "ڀ", "ځ", "ڂ", "ڃ",   "ڄ", "څ", "ڇ", "ڈ", "ډ", "ف", "ڊ", "ڋ", "ڌ", "ڍ", "ڎ", "ڏ", "ڐ", "ڑ",   "ڒ", "ړ", "ڔ", "ڕ", "ږ", "ڗ", "ڙ", "ښ", "ڛ", "ڜ", "ڝ", "ڞ", "ڟ",   "ڠ", "ڡ", "ڢ", "ڣ", "ڤ", "ڥ", "ڦ", "ڧ", "ڨ", "ک", "ڪ", "ګ", "ڬ", "ڭ", "ڮ",   "ڰ", "ڱ", "ڲ", "ڳ", "ڴ", "ڵ", "ڶ", "ڷ", "ڸ", "ڹ", "ں", "ڻ", "ڼ", "ڽ",   "ھ", "ڿ", "ۀ", "ہ", "ۂ", "ۃ", "ۄ", "ۅ", "ۆ", "ۇ", "ۈ", "ۉ", "ۊ", "ۋ", "ۏ", "ی", "Backspace"]):
      if button != "Backspace" and button != "ٵ": self.buttons[4].append(Button((WIDTH - 28) - (20 + ((x % 14) * 34)), (HEIGHT - 204) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=8))
      elif button == "Backspace": self.buttons[4].append(Button((WIDTH - 28) - (12 + ((x % 14) * 34)), (HEIGHT - 204) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=8))
      elif button == "ٵ": self.buttons[4].append(Button((WIDTH - 28) - (12 + ((x % 14) * 34)), (HEIGHT - 204) + math.floor(x / 14) * 34, 32, 32, button, "لا", add_alif_hamza, page=8))

    for x, button in enumerate(["ۍ", "ێ", "ې", "ۑ", "ے", "ۓ", "۔", "ە", "ۖ", "ۗ", "ۘ", "ۙ", "ۚ", "ۛ", "ۜ", "۟", "۠", "ۡ", "ۢ", "ۣ", "ۤ", "ۥ", "ۦ", "ۧ", "ۨ", "۪", "۫", "۬",   "ۭ", "۝", "۞", "۩", "ۺ", "ۻ", "ۼ", "۽", "۾", "ﷲ", "ﷺ", "ﷻ", "ﷰ",   "ﷱ", "ﷳ", "ﷴ", "ﷵ", "ﷶ", "ﷷ", "ﷸ", "ﷹ", "٭", "٪", "ٮ", "ٯ", "٬", "٫", "ٴ",  "Backspace", "_", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "Space"]):
      if button != "Space" and button != "Backspace" and button != "0": self.buttons[4].append(Button((WIDTH - 28) - (20 + ((x % 14) * 34)), (HEIGHT - 180) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=9))
      elif button == "Backspace": self.buttons[4].append(Button((WIDTH - 28) - (12 + ((x % 14) * 34)), (HEIGHT - 180) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=9))
      elif button == "Space": self.buttons[4].append(Button((WIDTH - 60) - (12 + ((x % 14) * 34)), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "Space", add_space, page=9))

    for x, button in enumerate(["ɶ", "ɑ", "ɒ", "ɐ", "ɛ", "ɜ", "ɞ", "ʌ", "ɔ", "ɘ", "ɵ", "ɤ", "ɪ", "ʏ",   "ʊ", "ɨ", "ʉ", "ɯ", "ə", "ɚ", "ɝ", "ʙ", "ɸ", "β", "ɱ", "ⱱ", "ʋ", "ɬ",   "ʃ", "ʒ", "ɮ", "ɹ", "ʈ", "ɖ", "ɳ", "ɽ", "ʂ", "ʐ", "ɻ", "ɭ", "ɟ", "ɲ", "ʝ",   "ʎ", "ŋ", "ɣ", "ɰ", "ʟ", "ɢ", "ɴ", "ʀ", "χ",   "ʁ", "ħ", "ʕ", "ʔ", "ɦ", "ɾ", "ʘ", "ǀ", "ǃ", "ǂ", "ǁ", "ɓ", "ɗ", "ʄ", "ɠ",   "ʛ", "ʼ", "ʍ", "ɥ", "ʜ", "ʢ", "ʡ", "ɕ", "ʑ", "ɺ", "ɧ", "͡", "ː", "ɪ̯", "ʰ", "ʲ", "◌"]):
      if button != "t͡" and button != "ʈ͡" and button != "d͡" and button != "ɖ͡" and button != "ɪ̯": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 204) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=10))
      elif button == "ɪ̯": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 204) + math.floor(x / 14) * 34, 32, 32, button, button, add_near_close_near_front_unrounded_vowel_with_breve_below, page=10))
    for x, button in enumerate(["あ", "い", "う", "え", "お", "か", "き", "く", "け", "こ", "さ", "し", "す", "せ",   "そ", "た", "ち", "つ", "て", "と", "な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ",   "へ", "ほ", "ま", "み", "む", "め", "も", "や", "ゆ", "よ", "ら", "り", "る", "れ",   "ろ", "わ", "を", "ん", "っ", "。", "、", "＜", "＞", "？", "！", "「", "」", "～",   "１", "２", "３", "４", "５", "６", "７", "８", "９", "０", "　", "Backspace"]):
      if button != "Backspace": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=11))
      else: self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=11))
    for x, button in enumerate(["ア", "イ", "ウ", "エ", "オ", "カ", "キ", "ク", "ケ", "コ", "サ", "シ", "ス", "セ",   "ソ", "タ", "チ", "ツ", "テ", "ト", "ナ", "ニ", "ヌ", "ネ", "ノ", "ハ", "ヒ", "フ",   "ヘ", "ホ", "マ", "ミ", "ム", "メ", "モ", "ヤ", "ユ", "ヨ", "ラ", "リ", "ル", "レ",   "ロ", "ワ", "ヲ", "ン", "ッ", "ッ", "…", "《", "》", "【", "】", "『", "』", "Backspace",   "１", "２", "３", "４", "５", "６", "７", "８", "９", "０", "ー", "Space"]):
      if button != "Backspace" and button != "Space": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=12))
      elif button == "Backspace": self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=12))
      elif button == "Space": self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "Space", add_space, page=12))
    for x, button in enumerate(["ぁ", "ぃ", "ぅ", "ぇ", "ぉ", "が", "ぎ", "ぐ", "げ", "ご", "ざ", "じ", "ず", "ぜ",   "ぞ", "だ", "ぢ", "づ", "で", "ど", "ば", "び", "ぶ", "べ", "ぼ", "ぱ", "ぴ", "ぷ",   "ぺ", "ぽ", "ゃ", "ゅ", "ょ", "ヴ", "ァ", "ィ", "ゥ", "ェ", "ォ", "ガ", "ギ", "グ",   "ゲ", "ゴ", "ザ", "ジ", "ズ", "ゼ", "ゾ", "ダ", "ヂ", "ヅ", "デ", "ド", "バ", "ビ",   "ブ", "ベ", "ボ", "パ", "ピ", "プ", "ペ", "ポ", "ャ", "ュ", "ョ", "・", "Backspace"]):
      if button != "Backspace": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=13))
      else: self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=13))
    for x, button in enumerate(["人", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "百", "千", "万",   "億", "兆", "京", "日", "月", "見", "目", "明", "暗", "前", "後", "本", "今", "入",   "出", "発", "早", "木", "山", "森", "川", "石", "空", "草", "花", "葉", "曇", "惑",   "星", "金", "当", "気", "中", "水", "火", "風", "雷", "土", "地", "訓", "音", "声",   "大", "小", "少", "来", "洗", "田", "伝", "公", "王", "主", "文", "門", "問", "Backspace"]):
      if button != "Backspace": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=14))
      else: self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=14))
    for x, button in enumerate(["開", "間", "聞", "引", "光", "闇", "影", "道", "々", "多", "力", "夢", "言", "話",   "笑", "立", "歩", "走", "逃", "行", "会", "変", "買", "書", "読", "学", "忘", "覚",   "思", "考", "知", "信", "分", "語", "私", "僕", "君", "彼", "我", "男", "女", "子",   "夫", "妻", "同", "愛", "遊", "楽", "幸", "嬉", "悲", "優", "弱", "強", "怖", "特",   "待", "持", "時", "動", "物", "朝", "夜", "必", "久", "恋", "向", "何", "誰", "Backspace"]):
      if button != "Backspace": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=15))
      else: self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=15))
    for x, button in enumerate(["曜", "曜", "虫", "犬", "鳥", "魚", "和", "終", "完", "事", "約", "生", "命", "死",   "殺", "激", "不", "止", "左", "右", "上", "下", "部", "東", "南", "西", "北", "毎",   "体", "頭", "顔", "口", "手", "指", "足", "腕", "鼻", "耳", "方", "形", "図", "食",   "飲", "味", "辞", "咳", "井", "良", "悪", "無", "由", "昔", "元", "確", "実", "了",   "可", "苦", "甘", "亡", "失", "欠", "解", "全", "意", "汚", "頼", "欲", "願", "Backspace"]):
      if button != "Backspace": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=16))
      else: self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=16))
    for x, button in enumerate(["礼", "術", "術", "燃", "暑", "寒", "冷", "要", "惜", "慣", "回", "廻", "色", "黒",   "白", "黄", "緑", "青", "留 ","告", "仕", "社", "自", "束", "感", "触", "恥", "困",   "救", "助", "守", "導", "隠", "様", "逆", "迷", "果", "画", "面", "疲", "寝", "区",   "別", "近", "場", "所", "国", "英", "屋", "店", "員", "眠", "起", "押", "送", "起",   "過", "品", "電", "工", "在", "相", "戸", "扉", "席", "哀", "暇", "翻", "訳", "Backspace"]):
      if button != "Backspace": self.buttons[4].append(Button(20 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 32, 32, button, button, add_letter, page=17))
      else: self.buttons[4].append(Button(12 + ((x % 14) * 34), (HEIGHT - 170) + math.floor(x / 14) * 34, 128, 32, button, "<", remove_letter, page=17))
    #機 者 哀 床 消 現 痛 預 吠 叫 歌 唄 曲 伸 縮 屈 諦 頑 共 有 張 種 家 財 船 長 金 布 服 収 内 定 秘 与 返 密 机 椅 敬 先 世 界 線 年 存 在 天 神
    # EDİT ROOM
    self.buttons[5].append(Button(376, 28, 32, 32, l[lg]["Go Back"], "Assets/editor/back.png", go_to, target_gs=3))
    for x, button in enumerate([(l[lg]["Play Track (First)"], "play", play_track2), (l[lg]["Browse Tracks (First)"], "note", select_track2)]):
      self.buttons[5].append(Button(103 + (x * 34), HEIGHT - 128, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target_gs=5))
    for x, button in enumerate([(l[lg]["Play Track (Loop)"], "play", play_track), (l[lg]["Stop Track"], "stop", stop_track)]):
      self.buttons[5].append(Button(103 + (x * 34), HEIGHT - 60, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    self.buttons[5].append(Button(376, HEIGHT - 60, 32, 32, l[lg]["Browse Tracks (Loop)"], "Assets/editor/note.png", select_track, target_gs=5))
    for x, button in enumerate([(l[lg]["No Scrolling"], "scroll", "No Scroll"), (l[lg]["Default Scrolling"], "focus scroll", "Default Scroll"), (l[lg]["Rounded Scrolling"], "rounded scroll", "Snapped Scroll"), (l[lg]["Focus on Center"], "focus on center", "Central Focus")]):
      self.buttons[5].append(Button(103 + (x * 34), 90, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", set_scrolling_mode, target=button[2]))
    self.buttons[5].append(Button(103, 234, 32, 32, l[lg]["Hide Players in This Room"], "Assets/editor/prohibit.png", hide_player_for_room, page=1))
    self.buttons[5].append(Button(342, 90, 32, 32, l[lg]["Horizontal Mirror"], "Assets/editor/horizontal mirror.png", allow_hm))
    self.buttons[5].append(Button(376, 90, 32, 32, l[lg]["Vertical Mirror"], "Assets/editor/vertical mirror.png", allow_vm))
    self.buttons[5].append(Button(250, 90, 32, 32, l[lg]["Platformer"], "Assets/editor/platformer.png", set_room_mode, target="Platformer"))
    self.buttons[5].append(Button(290, 90, 32, 32, l[lg]["Top-Down"], "Assets/editor/top-down.png", set_room_mode, target="Topdown"))
    for x, button in enumerate([(l[lg]["Decrease Gravity"], "less", -0.1), (l[lg]["İncrease Gravity"], "more", 0.1)]):
      self.buttons[5].append(Button(105 + (x * 128), 200, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_room_gravity, target=button[2], page=1))
    for x, button in enumerate([(l[lg]["Decrease Uİ Token"], "less", -1), (l[lg]["İncrease Uİ Token"], "more", 1)]):
      self.buttons[5].append(Button(105 + (x * 128), 130, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_selected_sm, target=button[2], page=2))
    for x, button in enumerate([(l[lg]["Decrease Uİ Mode"], "less", -1), (l[lg]["İncrease Uİ Mode"], "more", 1)]):
      self.buttons[5].append(Button(105 + (x * 128), 170, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_selected_ui_mode, target=button[2], page=2))
    for x, button in enumerate([(l[lg]["Add to Show"], "camera show", show_ui_for_room), (l[lg]["Add to Hide"], "camera hide", hide_ui_for_room)]):
      self.buttons[5].append(Button(290, 130 + (x * 40), 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], page=2))
    self.buttons[5].append(Button(330, 130 + (x * 40), 32, 32, l[lg]["Set Mode for Selected Token"], "Assets/editor/camera button.png", set_ui_mode_for_token, page=2))
    self.buttons[5].append(Button(376, HEIGHT - 128, 32, 32, l[lg]["Apply Shader"], "Assets/editor/code.png", add_shader, target=5))
    # TRACK LİBRARY
    for x, button in enumerate([(l[lg]["Go Back"], "back", go_to), (l[lg]["Add Track"], "add", add_track), (l[lg]["Remove Track"], "delete", remove_track)]):
      self.buttons[6].append(Button(160 + (x * 34), 6, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=self.tracks[self.selected_itemy], target_gs=5))
    # BRUSH MODE
    self.buttons[7].append(Button(WIDTH - 21, 100 - 21, 19, 19, l[lg]["Layer Options"], "Assets/editor/cog.png", edit_layer, target=self.selected_layer, target_gs=7))
    self.buttons[7].append(Button(WIDTH - 44, 100 - 21, 19, 19, l[lg]["Collectibles"], "Assets/editor/tiles.png", cac, target=self.selected_layer, target_gs=7))
    self.buttons[7].append(Button(WIDTH - 67, 100 - 21, 19, 19, l[lg]["Actors"], "Assets/editor/tiles.png", ea, target=self.selected_layer, target_gs=7))
    # EDIT LAYER
    self.buttons[8].append(Button(WIDTH - 136, 104, 32, 32, l[lg]["Go Back"], "Assets/editor/back.png", go_to, target=7, target_gs=7))
    self.buttons[8].append(Button(WIDTH - 136, 138, 32, 32, l[lg]["Delete Layer"], "Assets/editor/delete.png", delete_layer))
    self.buttons[8].append(Button(WIDTH - 136, HEIGHT - 236, 32, 32, "Set Label", "Assets/editor/pencil.png", rename, target_gs=8, target_object="Layer"))
    for x, button in enumerate([(l[lg]["Closer"], "less", change_layer_distance, -0.5), (l[lg]["Further"], "more", change_layer_distance, 0.5)]):
      self.buttons[8].append(Button(106 + (x * 132), HEIGHT - 236, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([(l[lg]["Dimmer"], "less", change_layer_shade, -10), (l[lg]["Brighter"], "more", change_layer_shade, 10)]):
      self.buttons[8].append(Button(106 + (x * 132), HEIGHT - 270, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    # NUMBERS
    for x, button in enumerate(["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", ".", "Backspace"]):
      if button != "Backspace": self.buttons[9].append(Button(156 + ((x % 3) * 34), (HEIGHT - 165) + math.floor(x / 3) * 34, 32, 32, button, button, add_letter))
      else: self.buttons[9].append(Button(156 + ((x % 3) * 34), (HEIGHT - 165) + math.floor(x / 3) * 34, 128, 32, button, "<", remove_letter))
    # PLAYTEST
    self.buttons[10].append(Button(5, 5, 32, 32, l[lg]["Stop Playtest"], "Assets/editor/stop.png", stop_playtest))
    # CAC
    #self.buttons[11].append(Button(WIDTH - 21, 100 - 21, 19, 19, l[lg]["Delete Collectible Type Object"], "Assets/editor/delete.png", delete_collectible_type))
    #self.buttons[11].append(Button(WIDTH - 44, 100 - 21, 19, 19, "Entities and NPCs", "Assets/editor/tiles.png", go_to, target=17))
    # NEW ENTİTY TYPE
      #see at add_entity_type
    # NEW COLLECTİBLE TYPE
      #see at line 83
    # GENERAL SETTİNGS
      #see at line 565
    # SFX LİBRARY
    self.buttons[16].append(Button(WIDTH - 34, HEIGHT - 34, 32, 32, l[lg]["Play Sound Effect"], "Assets/editor/play.png", play_sfx))
    for x, button in enumerate([(l[lg]["Go Back"] + ".", "back", go_to), (l[lg]["Add Sound Effect"], "add", add_sfx), (l[lg]["Remove Sound Effect"], "delete", remove_sfx)]):
      self.buttons[16].append(Button(160 + (x * 34), 6, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=self.sfx[self.selected_itemy]))
    # BG LİBRARY
    for x, button in enumerate([(l[lg]["Go Back"], "back", go_to), (l[lg]["Add Background Layer"], "add", add_bg)]):
      self.buttons[17].append(Button(165 + (x * 34), 6, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=self.sfx[self.selected_itemy], target_gs=1))
    for x, button in enumerate([(l[lg]["Closer"], "less", change_value, -0.5), (l[lg]["Further"], "more", change_value, 0.5)]):
      self.buttons[17].append(Button(270 + (x * 132), 320, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([(l[lg]["Decrease X Speed"], "less", change_speedx, -1), (l[lg]["İncrease X Speed"], "more", change_speedx, 1)]):
      self.buttons[17].append(Button(270 + (x * 132), 365, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([(l[lg]["Decrease Y Speed"], "less", change_speedy, -1), (l[lg]["İncrease Y Speed"], "more", change_speedy, 1)]):
      self.buttons[17].append(Button(270 + (x * 132), 410, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    # BG OPTİONS
    self.buttons[18].append(Button(WIDTH - 136, 104, 32, 32, l[lg]["Go Back"], "Assets/editor/back.png", go_to, target=0))
    self.buttons[18].append(Button(WIDTH - 136, 138, 32, 32, l[lg]["Delete Background"], "Assets/editor/delete.png", delete_bg))
    for x, button in enumerate([(l[lg]["Closer"], "less", change_distance_bg, -0.5), (l[lg]["Further"], "more", change_distance_bg, 0.5)]):
      self.buttons[18].append(Button(106 + (x * 132), HEIGHT - 296, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([(l[lg]["Decrease X Speed"], "less", change_speed_x_bg, -1), (l[lg]["İncrease X Speed"], "more", change_speed_x_bg, 1)]):
      self.buttons[18].append(Button(106 + (x * 132), HEIGHT - 266, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([(l[lg]["Decrease Y Speed"], "less", change_speed_y_bg, -1), (l[lg]["İncrease Y Speed"], "more", change_speed_y_bg, 1)]):
      self.buttons[18].append(Button(106 + (x * 132), HEIGHT - 236, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([(l[lg]["Decrease X"], "less", change_x_bg, -10), (l[lg]["İncrease X"], "more", change_x_bg, 10)]):
      self.buttons[18].append(Button(269 + (x * 110), HEIGHT - 266, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([(l[lg]["Decrease Y"], "less", change_y_bg, -10), (l[lg]["İncrease Y"], "more", change_y_bg, 10)]):
      self.buttons[18].append(Button(269 + (x * 110), HEIGHT - 236, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([(l[lg]["Repeat X"], "horizontal", repeat_x_bg), (l[lg]["Repeat Y"], "vertical", repeat_y_bg)]):
      self.buttons[18].append(Button(WIDTH - 170, 104 + (x * 34), 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    for x, button in enumerate([(l[lg]["Toggle X Scroll"], "x", toggle_x_scroll_bg), (l[lg]["Toggle Y Scroll"], "y", toggle_y_scroll_bg)]):
      self.buttons[18].append(Button(WIDTH - 204, 104 + (x * 34), 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    for x, button in enumerate([("Horizontal Mirroring", "horizontal mirror", toggle_hm_bg), ("Vertical Mirroring", "vertical mirror", toggle_vm_bg)]):
      self.buttons[18].append(Button(WIDTH - 238, 104 + (x * 34), 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    for x, button in enumerate([(l[lg]["Move Front"], "move left", change_bg_order_front), (l[lg]["Move Back"], "move right", change_bg_order_back), (l[lg]["Toggle Foreground"], "left arrow point to panel", toggle_foreground), (l[lg]["Set Background to Player Character"], "set bg to chr", set_bg_to_chr), (l[lg]["Copy Image Path of Background"], "copy image", copy_image_path_from_bg)]):
      self.buttons[18].append(Button(104 + (x * 34), HEIGHT - 326, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=18))
      #More in main.bg_options()
    # EDİT PLAYER
      #See in edit
    # EDİT TİLE
      #See in edit
    # EDİT ZONE
      #edit() > #zone
    # EDİT CUTSCENE
    for x, button in enumerate([("Play Movie", "play", playback_start), ("Pause Movie", "pause", playback_pause), ("Reset Playback", "stop", playback_stop)]):
      self.buttons[24].append(Button(3 + (x * 34), 32, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    for x, button in enumerate([("Audio", "volume", scene_audio), ("Action", "stars", scene_action), ("Move Object", "arrows", scene_move), ("Reposition", "motion", scene_repos)]):
      self.buttons[24].append(Button(WIDTH - (34 + (x * 34)), 36, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    self.buttons[24].append(Button(WIDTH - 34, 2, 32, 32, "Set Play Condition", "Assets/editor/play if.png", go_to, 47))
    self.buttons[24].append(Button(WIDTH - 68, 2, 32, 32, "Enable/Disable Input", "Assets/editor/clicking finger.png", immobilize_for_key))
    self.buttons[24].append(Button(WIDTH - 102, 2, 32, 32, "Pause Until Input", "Assets/editor/circle.png", await_input_key))
    self.buttons[24].append(Button(WIDTH - 136, 2, 32, 32, "Delete Components for Selected Object", "Assets/editor/delete.png", delete_components_key))
    # NEW ENTİTY TYPE PAGE 2
    self.buttons[25].append(Button(64, HEIGHT - 190, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx, target=25))
    self.buttons[25].append(Button(64, HEIGHT - 158, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx2, target=25))
    self.buttons[25].append(Button(64, HEIGHT - 126, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx3, target=25))
    self.buttons[25].append(Button(64, HEIGHT - 94, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx4, target=25))
    self.buttons[25].append(Button(64, HEIGHT - 62, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx5, target=25))
    self.buttons[25].append(Button(WIDTH - 90, HEIGHT - 60, 32, 32, "Next Page", "Assets/editor/next.png", go_to, 26))
    for x, button in enumerate([("Decrease Speed", "less", change_speed_x, -0.25), ("İncrease Speed", "more", change_speed_x, 0.25)]):
      self.buttons[25].append(Button(60 + (x * 132), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Jump Force", "less", change_speed_y, -0.5), ("İncrease Jump Force", "more", change_speed_y, 0.5)]):
      self.buttons[25].append(Button(60 + (x * 132), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Closer Detection Range", "less", change_range, -5), ("Further Detection Range", "more", change_range, 5)]):
      self.buttons[25].append(Button(60 + (x * 132), 150, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease HP", "less", change_hp, -1), ("İncrease HP", "more", change_hp, 1)]):
      self.buttons[25].append(Button(60 + (x * 132), 190, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate(["Tumble", "Fall", "Stay", "Hide"]):
      self.buttons[25].append(Button(275, 100 + (x * 20), fontsmall.render(button, True, "White").get_width(), 24, "Pick Defeat Animation", button, pick_defeat_anim, target=button, font=fontsmall))
    # NEW ENTİTY TYPE PAGE 3
      # see at add_entity_type
    # EA
    self.buttons[27].append(Button(WIDTH - 21, 100 - 21, 19, 19, "Delete Actor Type Object", "Assets/editor/delete.png", delete_entity_type))
    # PORT SETTİNGS
    #for x, button in enumerate(self.input_hold):
    #  self.buttons[29].append(Button(52, 128 + (x * 16), 16, 16, "Toggle " + button, "Assets/editor/empty button.png", toggle_press_and_hold, button))
    # PRE-POST TEXT/BACKGROUND OF A CHARACTER
    self.buttons[29].append(Button(31, 64, 32, 32, "Set Before Text", "Assets/editor/text before.png", set_before_text))
    self.buttons[29].append(Button(65, 64, 32, 32, "Set After Text", "Assets/editor/text after.png", set_after_text))
    for x in range(4):
      self.buttons[29].append(Button(99 + (x * 32), 64, 32, 32, "Take from Player Index " + str(x + 1), "Assets/editor/turn into " + str(x + 1) + ".png", take_from_player, target=x))
    self.buttons[29].append(Button(229, 64, 32, 32, "Take Player/Team", "Assets/editor/loop.png", set_take_player_or_team))
    self.buttons[29].append(Button(31, 140, 32, 32, "Take Variable", "Assets/editor/add.png", set_take_variable))
    # DİSPLAY SETTİNGS
    for y, button in enumerate([("Change Display Width", "Width", change_display, self.width), ("Change Display Height", "Height", change_display, self.height), ("Change FPS", "FPS", change_display, self.fps)]):
      self.buttons[30].append(Button(150, 140 + (y * 40), 128, 24, button[0], button[1], button[2], target=button[3], target_object="Display", target_gs=30, font=fontsmall))
    self.buttons[30].append(Button(376, 104, 32, 32, "Toggle DeltaTime", "Assets/editor/dt.png", toggle_dt))
    self.buttons[30].append(Button(110, 320, 128, 24, "Enter Game Publisher", "Publisher:", enter_publisher, target=self.publisher, target_object="Publisher", target_gs=30, button_type="Specifier", font=fontsmall))
    # ACTİON CONTROLS
      # see edit_action_controls
    # EDİT DOOR
    for x, button in enumerate([("Decrease X Destination", "less", -1), ("İncrease X Destination", "more", 1)]):
      self.buttons[32].append(Button(60 + (x * 132), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_door_x_dest, target=button[2]))
    for x, button in enumerate([("Decrease Y Destination", "less", -1), ("İncrease Y Destination", "more", 1)]):
      self.buttons[32].append(Button(60 + (x * 132), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_door_y_dest, target=button[2]))
    for x, button in enumerate([("Decrease X", "less", -1), ("İncrease X", "more", 1)]):
      self.buttons[32].append(Button(225 + (x * 105), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_door_x, target=button[2]))
    for x, button in enumerate([("Decrease Y", "less", -1), ("İncrease Y", "more", 1)]):
      self.buttons[32].append(Button(225 + (x * 105), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_door_y, target=button[2]))
    for x, button in enumerate([("Previous Room", "less", change_door_dest, -1), ("Next Room", "more", change_door_dest, 1)]):
      self.buttons[32].append(Button(365 + (x * 58), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate(self.transitions):
      self.buttons[32].append(Button(55, 150 + (x * 17), 128, 16, "Apply Transition", button, change_transition, target=button, font=fontsmall, button_type="Transition"))
    self.buttons[32].append(Button(230, 173, 32, 32, "Toggle Input Requirement", "Assets/editor/clicking finger.png", change_door_input_requirement))
    self.buttons[32].append(Button(264, 173, 32, 32, "Toggle Passable", "Assets/editor/passable door.png", change_door_passable))
    #self.buttons[32].append(Button(264, 173, 32, 32, "Spawn Door on Other Side", "Assets/editor/spawn door.png", change_door_spawn_on_other_side))
    #self.buttons[32].append(Button(298, 173, 32, 32, "Door on Other Side is Passable", "Assets/editor/passable door.png", change_door_passable_on_other_side))
    #self.buttons[32].append(Button(332, 173, 32, 32, "Door on Other Side is Animated", "Assets/editor/cutscene.png", change_door_play_anim_on_other_side))
    self.buttons[32].append(Button(230, 207, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx, target=32))
    self.buttons[32].append(Button(230, 241, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx2, target=32))
    self.buttons[32].append(Button(230, 275, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx3, target=32))
    # ENTİTY DİALOGUES
      # see at manage_dialogues
    # STAT EFFECT
      # see at set_stat_effect
    # STAT Uİ
      # see at refresh_ui_buttons
    # BOOLEAN
    for x, button in enumerate(["True", "False"]):
      self.buttons[37].append(Button(128 + (x * 128), 300, 96, 96, "Set Boolean as " + button, button, rebool, eval(button)))
    # SCENE REPOS
    self.buttons[38].append(Button(426, 24, 32, 32, l[lg]["Go Back"], "Assets/editor/back.png", go_to, target_gs=24))
    for x, button in enumerate([(l[lg]["Decrease X"], "less", change_x_repos, -1), (l[lg]["İncrease X"], "more", change_x_repos, 1)]):
      self.buttons[38].append(Button(60 + (x * 132), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([(l[lg]["Decrease Y"], "less", change_y_repos, -1), (l[lg]["İncrease Y"], "more", change_y_repos, 1)]):
      self.buttons[38].append(Button(60 + (x * 132), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Neglect Reposition", "neglect", neglect_reposition), ("Add Reposition", "reposition", add_reposition), ("Stay There when Cutscene is Over", "stay on changed rect", stay_on_changed_rect), ("Show/Hide", "hidden", set_hidden_for_key)]):
      self.buttons[38].append(Button(426 - (x * 34), HEIGHT - 58, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    # SCENE MOVE
    for x, button in enumerate([(l[lg]["Decrease X Speed/Destination"], "less", change_x_cs_speed, -0.25), (l[lg]["İncrease X Speed/Destination"], "more", change_x_cs_speed, 0.25)]):
      self.buttons[39].append(Button(60 + (x * 132), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([(l[lg]["Decrease Y Speed/Destination"], "less", change_y_cs_speed, -0.25), (l[lg]["İncrease Y Speed/Destination"], "more", change_y_cs_speed, 0.25)]):
      self.buttons[39].append(Button(60 + (x * 132), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Speed for Destination Mode", "less", change_cs_speed, -1), ("İncrease Speed for Destination Mode", "more", change_cs_speed, 1)]):
      self.buttons[39].append(Button(60 + (x * 132), 170, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    self.buttons[39].append(Button(426, 24, 32, 32, l[lg]["Go Back"], "Assets/editor/back.png", go_to, target_gs=24))
    # SCENE ACTİON
      # see at scene_action
    # SCENE SFX & TRACK
    self.buttons[41].append(Button(376, 29, 32, 32, l[lg]["Go Back"], "Assets/editor/back.png", go_to, target_gs=24))
    self.buttons[41].append(Button(376, HEIGHT - 60, 32, 32, "Browse Tracks", "Assets/editor/note.png", select_track_for_cs, target_gs=42))
    self.buttons[41].append(Button(376, HEIGHT - 94, 32, 32, "Stop Track", "Assets/editor/stop track.png", stop_track_for_cs, target_gs=42))
    for x, button in enumerate([("Play Track", "play", play_track2), ("Browse SFXs", "note", select_track_for_cs2)]):
      self.buttons[41].append(Button(103 + (x * 34), HEIGHT - 128, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], "Sounds/" + " " + ".png"))
    for x, button in enumerate([("Play Track", "play", play_track), ("Stop Track", "stop", stop_track)]):
      self.buttons[41].append(Button(103 + (x * 34), HEIGHT - 60, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], "Sounds/" + " " + ".png"))
    self.buttons[41].append(Button(HEIGHT - 72, 72, 32, 32, "Browse SFXs", "Assets/editor/note.png", select_sfx, target=41))
    # TRACK LİBRARY FOR CUTSCENE
    for x, button in enumerate([(l[lg]["Go Back"], "back", go_to), ("Add Track for this Key", "add", add_track_for_cs), ("Remove Track", "delete", remove_track_for_cs)]):
      self.buttons[42].append(Button(160 + (x * 34), 6, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=self.tracks[self.selected_itemy], target_gs=41))  
    # FONT LİBRARY
    for x, button in enumerate([(l[lg]["Go Back"], "back", go_to_rgs), ("Add Font", "add", add_font)]):
      self.buttons[44].append(Button(165 + (x * 34), 6, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=self.sfx[self.selected_itemy]))
    # GAME SAVES LİBRARY
    for x, button in enumerate([(l[lg]["Go Back"], "back", go_to_main), ("Load Game", "load", load_game_file)]):
      self.buttons[45].append(Button(165 + (x * 34), 6, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    # İMAGE LİBRARY
    for x, button in enumerate([(l[lg]["Go Back"], "back", go_to_rgs), ("Add İmage", "add", add_image), ("Remove İmage", "delete", remove_image)]):
      self.buttons[46].append(Button(160 + (x * 34), 6, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    # CUTSCENE CONDİTİON
    #for x, button in enumerate([("And Gate", ""), ("Or Gate", "gate or")]):
    #  self.buttons[47].append(Button(450 + (x * 34), 28, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", set_cs_condition_gate, target=button[2]))
    for x, button in enumerate([("Start of Room", "event start"), ("Zone", "event zone"), ("Collectible", "event coin"), ("Stat", "event stats"), ("Story Progress", "event story")]):
      self.buttons[47].append(Button(54 + (x * 34), 58, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", add_cs_condition, target=button[0], button_type="Event"))
    for x, button in enumerate([("And Gate", "gate and", "and"), ("Or Gate", "gate or", "or")]):
      self.buttons[47].append(Button(375 + (x * 34), 58, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", set_cs_condition_gate, target=button[2], button_type="Gate"))
    for x, button in enumerate([("And Gate", "gate and", "and"), ("Or Gate", "gate or", "or")]):
      self.buttons[47].append(Button(375 + (x * 34), 276, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", set_cs_condition_stat_gate, target=button[2], button_type="Gate 2"))
    # SHADER LİBRARY
    for x, button in enumerate([("Go Back", "back", go_to_rgs), ("Apply Shader", "add", apply_shader), ("Remove Shader", "delete", remove_shader)]):
      self.buttons[48].append(Button(160 + (x * 34), 6, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    # PROJECTİLES
    for x, button in enumerate([("Go Back", "back", go_to, None, 2), ("Edit Projectile", "cog", go_to, 50, None), ("Delete Projectile", "delete", delete_projectile, None, None), ("Add Projectile", "add", go_to, 51, 51)]):
      self.buttons[49].append(Button(126 + (x * 34), 6, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3], target_gs=button[4]))
    # PROJECTİLE EDİTOR
    for x, button in enumerate([(l[lg]["Decrease X Speed"], "less", change_proj_x_speed, -1), (l[lg]["İncrease X Speed"], "more", change_proj_x_speed, 1)]):
      self.buttons[50].append(Button(28 + (x * 132), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([(l[lg]["Decrease Y Speed"], "less", change_proj_y_speed, -1), (l[lg]["İncrease Y Speed"], "more", change_proj_y_speed, 1)]):
      self.buttons[50].append(Button(28 + (x * 132), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Projectile Lifetime", "less", change_proj_lifetime, -0.01), ("İncrease Projectile Lifetime", "more", change_proj_lifetime, 0.01)]):
      self.buttons[50].append(Button(28 + (x * 132), 150, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Frame Speed", "less", change_proj_frame_speed, -1), ("İncrease Frame Speed", "more", change_proj_frame_speed, 1)]):
      self.buttons[50].append(Button(28 + (x * 132), 190, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease X Spawn Min", "less", change_proj_x_spawn_min, -1), ("İncrease X Spawn Min", "more", change_proj_x_spawn_min, 1)]):
      self.buttons[50].append(Button(28 + (x * 132), 230, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease X Spawn Max", "less", change_proj_x_spawn_max, -1), ("İncrease X Spawn Max", "more", change_proj_x_spawn_max, 1)]):
      self.buttons[50].append(Button(28 + (x * 132), 270, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Y Spawn Min", "less", change_proj_y_spawn_min, -1), ("İncrease Y Spawn Min", "more", change_proj_y_spawn_min, 1)]):
      self.buttons[50].append(Button(28 + (x * 132), 310, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Y Spawn Max", "less", change_proj_y_spawn_max, -1), ("İncrease Y Spawn Max", "more", change_proj_y_spawn_max, 1)]):
      self.buttons[50].append(Button(28 + (x * 132), 350, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Deal Damage Again", "deal again", toggle_proj_deal_again), ("Pierce Opponent", "pierce", toggle_proj_pierce), ("Stoppable", "stoppable", toggle_proj_stoppable), ("Returnable", "returnable", toggle_proj_returnable), ("Stop at Collision", "stop at collision", toggle_proj_stop_at_collision), ("Die at Collision", "die at collision", toggle_proj_die_at_collision), ("Ease Oscillation", "sine wave", toggle_proj_sine), ("Guided", "guided", toggle_proj_guided), ("Beam", "beam", toggle_proj_beam), ("Directional Relative", "right overpower", toggle_proj_dr), ("Bounce", "bounce", toggle_proj_bounce), ("Slide Around Platform", "around platform", toggle_proj_around_platform)]):
      self.buttons[50].append(Button(28 + (x * 34), HEIGHT - 56, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
    for x, button in enumerate([("Decrease Oscillation Wavelength", "less", change_proj_oscillation_speed, -1), ("İncrease Oscillation Wavelength", "more", change_proj_oscillation_speed, 1)]):
      self.buttons[50].append(Button(192 + (x * 132), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Oscillation Frequency", "less", change_proj_frequency, -1), ("İncrease Oscillation Frequency", "more", change_proj_frequency, 1)]):
      self.buttons[50].append(Button(192 + (x * 132), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Vibration", "less", change_proj_vibrate, -1), ("İncrease Vibration", "more", change_proj_vibrate, 1)]):
      self.buttons[50].append(Button(192 + (x * 132), 150, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease X Weight", "less", change_proj_weight_x, -1), ("İncrease X Weight", "more", change_proj_weight_x, 1)]):
      self.buttons[50].append(Button(192 + (x * 132), 190, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("İncrease Y Weight", "less", change_proj_weight_y, -1), ("İncrease Y Weight", "more", change_proj_weight_y, 1)]):
      self.buttons[50].append(Button(192 + (x * 132), 230, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Time for Weight Applied", "less", change_proj_apply_weight_after, -1), ("Decrease Time for Weight Applied", "more", change_proj_apply_weight_after, 1)]):
      self.buttons[50].append(Button(192 + (x * 132), 270, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Stop X Motion After", "less", change_proj_stop_x_after, -1), ("İncrease Stop X Motion After", "more", change_proj_stop_x_after, 1)]):
      self.buttons[50].append(Button(356 + (x * 124), 70, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Stop Y Motion After", "less", change_proj_stop_y_after, -1), ("İncrease Stop Y Motion After", "more", change_proj_stop_y_after, 1)]):
      self.buttons[50].append(Button(356 + (x * 124), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Stop X Motion For", "less", change_proj_stop_x_for, -1), ("İncrease Stop X Motion For", "more", change_proj_stop_x_for, 1)]):
      self.buttons[50].append(Button(356 + (x * 124), 150, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Stop Y Motion For", "less", change_proj_stop_y_for, -1), ("İncrease Stop Y Motion For", "more", change_proj_stop_y_for, 1)]):
      self.buttons[50].append(Button(356 + (x * 124), 190, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for y, button in enumerate(["Player Relative", "Camera Relative", "Raw Position"]):
      self.buttons[50].append(Button(186, 310 + (y * 22), 172, 20, "Set Projectile Position to " + button, button, set_proj_pos_mode, target=button, font=fontmedium, button_type="Position Mode", shift_x_hitbox=12))
    # PROJECTİLE LİBRARY
    for x, button in enumerate([(l[lg]["Go Back"], "back", go_to), ("Add Projectile", "add", add_projectile)]):
      self.buttons[51].append(Button(194 + (x * 34), 6, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target_gs=49))

    #EDİT TİLE TYPES
    #see the tile type selector buttons in manage_tiles
    for x, button in enumerate([("Toggle Solidity", "solid", toggle_solid), ("Toggle Slipperiness", "ice", toggle_slippery), ("Toggle Flatness", "flat", toggle_flatness)]):
      self.buttons[53].append(Button(WIDTH - (36 + (x * 34)), HEIGHT - 36, 32, 32, l[lg][button[0]], "Assets/editor/" + button[1] + ".png", button[2]))
    for x, button in enumerate([("Decrease Tile's X Hitbox", "less", -1), ("İncrease Tile's X Hitbox", "more", 1)]):
      self.buttons[53].append(Button(356 + (x * 120), 30, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_tile_hitbox_x, target=button[2]))
    for x, button in enumerate([("Decrease Tile's Y Hitbox", "less", -1), ("İncrease Tile's Y Hitbox", "more", 1)]):
      self.buttons[53].append(Button(356 + (x * 120), 64, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_tile_hitbox_y, target=button[2]))
    for x, button in enumerate([("Decrease Tile's Hitbox Width", "less", -1), ("İncrease Tile's Hitbox Width", "more", 1)]):
      self.buttons[53].append(Button(356 + (x * 120), 98, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_tile_hitbox_width, target=button[2]))
    for x, button in enumerate([("Decrease Tile's Hitbox Height", "less", -1), ("İncrease Tile's Hitbox Height", "more", 1)]):
      self.buttons[53].append(Button(356 + (x * 120), 132, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_tile_hitbox_height, target=button[2]))
    for x, button in enumerate([("Decrease HP", "less", -1), ("İncrease HP", "more", 1)]):
      self.buttons[53].append(Button(270 + (x * 124), 174, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_tile_type_hp, target=button[2]))
    for x, button in enumerate([("Decrease Team", "less", -1), ("İncrease Team", "more", 1)]):
      self.buttons[53].append(Button(270 + (x * 124), 204, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_tile_type_team, target=button[2]))
    self.buttons[53].append(Button(274, HEIGHT - 208, 32, 32, "Destroy İf Head Bump", "Assets/editor/bump on.png", change_tile_type_destroy_if_head_bump))
    self.buttons[53].append(Button(312, HEIGHT - 208, 32, 32, "Destroy İf Stood On", "Assets/editor/stand on.png", change_tile_type_destroy_if_stood_on))
    self.buttons[53].append(Button(274, HEIGHT - 174, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx, target=53))
    self.buttons[53].append(Button(274, HEIGHT - 142, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx2, target=53))
    for x, button in enumerate([("Decrease Frame Rate", "less", -1), ("İncrease Frame Rate", "more", 1)]):
      self.buttons[53].append(Button(270 + (x * 124), HEIGHT - 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_tile_type_anim_rate, target=button[2]))
    for x, button in enumerate(self.destroy_anims):
      self.buttons[53].append(Button(415, 175 + (x * 15), 96, 14, "Set Destruct Animation", button, change_tile_type_destroy_anim, target=button, font=fontlittle, button_type="Destroy Animation"))

    #EDİT CHARACTER TYPES
    #for x, button in enumerate([("Decrease HP", "less", -1), ("İncrease HP", "more", 1)]):
    #  self.buttons[54].append(Button(270 + (x * 124), 174, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_entity_type_hp, target=button[2]))
    self.buttons[54].append(Button(WIDTH - 36, 110, 32, 32, "Set Wall Slider", "Assets/editor/wall slide.png", set_character_able_to_wall_slide))
    self.buttons[54].append(Button(WIDTH - 36, HEIGHT - 36, 32, 32, "Action Controls", "Assets/editor/controller.png", edit_action_controls, target=31))
    self.buttons[54].append(Button(WIDTH - 36, HEIGHT - 70, 32, 32, "Edit Entities", "Assets/editor/entity.png", edit_entities, target=56))
    self.buttons[54].append(Button(WIDTH - 36, HEIGHT - 104, 32, 32, "Add Entity", "Assets/editor/entity add.png", add_entity, target=56))
    for x, button in enumerate([("Decrease Speed", "less", change_character_speed, -0.25), ("İncrease Speed", "more", change_character_speed, 0.25)]):
      self.buttons[54].append(Button(274 + (x * 132), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    for x, button in enumerate([("Decrease Jump Force", "less", change_character_leap, 0.25), ("İncrease Jump Force", "more", change_character_leap, -0.25)]):
      self.buttons[54].append(Button(274 + (x * 132), 150, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    temp = [select_sfx6, select_sfx5, select_sfx4, select_sfx3, select_sfx2, select_sfx]
    for x in range(5): self.buttons[54].append(Button(274, HEIGHT - (122 + (x * 32)), 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", temp[x + 1], target=54))
    for x, button in enumerate(["Tumble", "Fall", "Stay", "Hide"]):
      self.buttons[54].append(Button(274, 370 + (x * 15), 96, 14, "Set Defeat Animation", button, change_character_type_defeat_anim, target=button, font=fontlittle, button_type="Defeat Animation"))
    
    #EDİT COLLECTİBLE TYPES
    for x, button in enumerate([("Decrease Animation Speed", "less", change_collectible_anim_speed, -1), ("İncrease Animation Speed", "more", change_collectible_anim_speed, 1)]):
      self.buttons[55].append(Button(274 + (x * 132), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
    self.buttons[55].append(Button(270, HEIGHT - 102, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx, target=55))
    self.buttons[55].append(Button(270, HEIGHT - 68, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx2, target=55))
    self.buttons[55].append(Button(270, HEIGHT - 34, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx3, target=55))

    #EDİT ENTİTY TYPES
    for x, button in enumerate([("Decrease HP", "less", -1), ("İncrease HP", "more", 1)]):
      self.buttons[56].append(Button(274 + (x * 86), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_entity_hp, target=button[2]))
    for x, button in enumerate([("Decrease Team", "less", -1), ("İncrease Team", "more", 1)]):
      self.buttons[56].append(Button(388 + (x * 90), 110, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", change_entity_team, target=button[2]))
    self.buttons[56].append(Button(WIDTH - 34, HEIGHT - 34, 32, 32, "Edit Behaviors", "Assets/editor/guided.png", go_to, 57))
    
    #EDİT ENTİTY BEHAVİORS
    self.buttons[57].append(Button(WIDTH - 36, 24, 32, 32, l[lg]["Go Back"], "Assets/editor/back.png", go_to, 56, target_gs=56))
    width = 0; height = 0
    for behavior in self.entity_behaviors:
      text = fontsmall.render(behavior + ",", True, "White")
      if width + 19 + text.get_width() > WIDTH - 90: height += 25; width = 0
      width += text.get_width() + 10
      self.buttons[57].append(Button(35 + width - text.get_width(), 100 + height, text.get_width() + 7, 25, l[lg]["Toggle Behavior"], behavior, select_behavior, target=behavior, target_object="Behavior", text_color="White", font=fontsmall))

    #EDİT MENU
    self.buttons[58].append(Button(10, 30, 32, 32, "Add Menu Item", "Assets/editor/add.png", add_menu_item))
    self.buttons[58].append(Button(44, 30, 32, 32, "Delete Menu Item", "Assets/editor/delete.png", remove_menu_item))
    self.buttons[58].append(Button(78, 30, 32, 16, "Previous Item", "Assets/editor/up.png", change_selected_menu_item_index, target=-1))
    self.buttons[58].append(Button(78, 46, 32, 16, "Next Item", "Assets/editor/down.png", change_selected_menu_item_index, target=1))
    self.buttons[58].append(Button(112, 30, 32, 16, "Move Item Up", "Assets/editor/up.png", move_selected_menu_item_index_up))
    self.buttons[58].append(Button(112, 46, 32, 16, "Move Item Down", "Assets/editor/down.png", move_selected_menu_item_index_down))
    self.buttons[58].append(Button(146, 30, 32, 32, "Switch Between Selected and Unselected", "Assets/editor/loop.png", switch_menu_item_mode))
    self.buttons[58].append(Button(180, 30, 32, 32, "Edit Both Selected and Unselected", "Assets/editor/loop.png", switch_menu_item_mode_edit_both))
    self.buttons[58].append(Button(214, 30, 32, 32, "Active Menu on Start", "Assets/editor/left arrow point to panel.png", toggle_menu_start_appear))
    self.buttons[58].append(Button(248, 30, 32, 32, "Reset Selected Item on Return", "Assets/editor/retry.png", toggle_reset_menu))
    self.buttons[58].append(Button(282, 30, 32, 32, "Make Menu Joinable", "Assets/editor/load.png", toggle_make_menu_joinable))
    self.buttons[58].append(Button(10, 103, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx, target=58))
    self.buttons[58].append(Button(170, 103, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx2, target=58))

    #EDİT MENU 2 [59] at action and outline/border settings function

    #SET TEXT BEHAVİORS
    width = 0; height = 0
    for behavior in self.text_behaviors:
      text = fontsmall.render(behavior + ",", True, "White")
      if width + 19 + text.get_width() > WIDTH - 90: height += 25; width = 0
      width += text.get_width() + 10
      self.buttons[60].append(Button(35 + width - text.get_width(), 100 + height, text.get_width() + 7, 25, l[lg]["Toggle Behavior"], behavior, select_text_behavior, target=behavior, target_object="Behavior", text_color="White", font=fontsmall))

    # LAUNCHER
    self.launcher_buttons[0].append(Button(2, 18, 86, 32, "", "Assets/editor/LAUNCHER file.png", set_page, target=2, with_sound=False))
    self.launcher_buttons[0].append(Button(90, 18, 124, 32, "", "Assets/editor/LAUNCHER config.png", set_page, target=3, with_sound=False))
    self.launcher_buttons[0].append(Button(216, 18, 152, 32, "", "Assets/editor/LAUNCHER network.png", set_page, target=4, with_sound=False))
    self.launcher_buttons[0].append(Button(370, 18, 106, 32, "", "Assets/editor/LAUNCHER about.png", set_page, target=5, with_sound=False))
    self.launcher_buttons[0].append(Button(478, 18, 32, 32, "", "Assets/editor/power off.png", quit, with_sound=False))
    for x, button in enumerate([(l[lg]["Load Game"], set_page, 6), (l[lg]["Save Game State"], set_page, 7), (l[lg]["Load Game State"], set_page, 8), (l[lg]["Restart Game"], restart_game, 0), (l[lg]["Eject"], eject, 0), (l[lg]["Switch to Editor"], switch_to_editor, 0), (l[lg]["Power Off"], quit, 0)]):
      self.launcher_buttons[0].append(Button(-14, 55 + (32 * x), 230, 26, "", button[0], button[1], target=button[2], font=launcherfontlittle, page=2, with_sound=False, shift_x_hitbox=16))
    for x, button in enumerate([(l[lg]["Configure..."], set_page, 9), (l[lg]["Settings"], set_page, 16), (l[lg]["Miscellaneous"], set_page, 12), (l[lg]["Open Terminal"], open_console, 0), (l[lg]["Toggle Debug Mode"], toggle_debug, 0)]):
      self.launcher_buttons[0].append(Button(74, 55 + (32 * x), 230, 26, "", button[0], button[1], target=button[2], font=launcherfontlittle, page=3, with_sound=False, shift_x_hitbox=16))
    for x, button in enumerate([(l[lg]["Profile"], set_page, 17), (l[lg]["Host Server"], set_page, 13), (l[lg]["Connect to Server"], set_page, 14), (l[lg]["Performance"], set_page, 15)]):
      self.launcher_buttons[0].append(Button(200, 55 + (32 * x), 230, 26, "", button[0], button[1], target=button[2], font=launcherfontlittle, page=4, with_sound=False, shift_x_hitbox=16))

    for x, button in enumerate(self.saves):
      self.launcher_buttons[0].append(Button(40, 100 + (32 * x), WIDTH - 110, 22, "", button, load_game_from_launcher, target=[button, self], font=launcherfontlittle, page=6, with_sound=False, shift_x_hitbox=16, hide_above_y=100, hide_below_y=385, button_type="Game"))
    #self.launcher_buttons[0].append(Button(100, 408, 32, 32, l[lg]["Load Additional Packages"], l[lg]["Load Additional Packages"], load_additional_packages, with_sound=False, page=6))
    self.launcher_buttons[0].append(Button(420, 408, 32, 32, l[lg]["Refresh"], "Assets/editor/ccw.png", refresh_games, with_sound=False, page=6))
    for button in range(20):
      self.launcher_buttons[0].append(Button(30 + ((button % 10) * 45), 150 + math.floor(button / 10) * 64, 16 + (int(len(str(button + 1)) > 1) * 12), 22, "", button + 1, save_game_state_from_launcher, target=[button, self], font=launcherfontlittle, page=7, with_sound=False, shift_x_hitbox=16, shift_y_hitbox=6))
    for button in range(20):
      self.launcher_buttons[0].append(Button(30 + ((button % 10) * 45), 150 + math.floor(button / 10) * 64, 16 + (int(len(str(button + 1)) > 1) * 12), 22, "", button + 1, load_game_state_from_launcher, target=[button, self], font=launcherfontlittle, page=8, with_sound=False, shift_x_hitbox=16, shift_y_hitbox=6))
    for i in range(9, 12):
      for x, button in enumerate([(l[lg]["Input"], 9), (l[lg]["Video"], 10), (l[lg]["Audio"], 11)]):
        self.launcher_buttons[0].append(Button(48 + (166 * x), 80, 56, 26, "", button[0], set_page, target=button[1], font=launcherfontlittle, page=i, with_sound=False, shift_x_hitbox=16))
    for x, button in enumerate(["Player 1", "Player 2", "Player 3", "Player 4"]):
      self.launcher_buttons[0].append(Button(6 + (128 * x), 120, 86, 26, "", button, select_player_index, target=x, font=launcherfontlittle, page=9, button_type="Player Indices", with_sound=False, shift_x_hitbox=16))
    for x, joystick in enumerate([None, "Default"] + self.joysticks):
      if joystick == None: self.launcher_buttons[0].append(Button(16, 190 + (24 * x), launcherfontsmaller.render("None", False, "White").get_width(), 20, "", None, plug_gamepad, target=joystick, font=launcherfontsmaller, page=9, button_type="Device", with_sound=False, shift_x_hitbox=16))
      elif joystick == "Default": self.launcher_buttons[0].append(Button(16, 190 + (24 * x), launcherfontsmaller.render("Default", False, "White").get_width(), 20, "", "Default", plug_gamepad, target=joystick, font=launcherfontsmaller, page=9, button_type="Device", with_sound=False, shift_x_hitbox=16))
      else: self.launcher_buttons[0].append(Button(16, 190 + (24 * x), launcherfontsmaller.render(joystick.get_name(), False, "White").get_width(), 20, "", joystick.get_name(), plug_gamepad, target=joystick, font=launcherfontsmaller, page=9, button_type="Device", with_sound=False, shift_x_hitbox=16))
    for x, button in enumerate([("<", change_deadzone, -0.1), (">", change_deadzone, 0.1)]):
      self.launcher_buttons[0].append(Button(343 + (x * 96), 190, 32, 32, "", button[0], button[1], target=button[2], font=launcherfontsmall, page=9, shift_x_hitbox=16))
    self.launcher_buttons[0].append(Button(340, 270, 120, 32, "", l[lg]["Rumble: "], toggle_rumble, font=launcherfontlittle, page=9, shift_x_hitbox=16))
    self.launcher_buttons[0].append(Button(319, 166, 32, 32, l[lg]["Refresh Connections"], "Assets/editor/ccw.png", refresh_joysticks, font=launcherfontlittle, with_sound=False, page=9))
    
    for x, button in enumerate([("Linear", moderngl.LINEAR), ("Nearest", moderngl.NEAREST)]):
      self.launcher_buttons[0].append(Button(6 + (84 * x), 150, 75, 26, "", button[0], select_render_filter, target=button[1], font=launcherfontlittle, page=10, button_type="Filter", with_sound=False, shift_x_hitbox=16))
    for x, button in enumerate(["ARGB", "ARBG", "AGRB", "AGBR", "ABRG", "ABGR", "RAGB", "RABG", "RGAB", "RGBA", "RBAG", "RBGA", "GARB", "GABR", "GRAB", "GRBA", "GBAR", "GBRA", "BARG", "BAGR", "BRAG", "BRGA", "BGAR", "BGRA"]):
      self.launcher_buttons[0].append(Button(200 + ((x % 6) * 45), 150 + math.floor(x / 6) * 24, 44, 26, "", button, select_color_swizzle, target=button, font=launcherfontlittle, page=10, button_type="Color Swizzle", with_sound=False, shift_x_hitbox=16))
    for button in [("Pygame", [192, 54], 0), ("SDL", [110, 54], 7), ("OpenGL", [128, 54], 11)]:
      self.launcher_buttons[0].append(Button(24 + (30 * button[2]), 340, button[1][0], button[1][1], "", "Assets/editor/LAUNCHER " + button[0] + " logo.png", print, font=launcherfontlittle, page=10, with_sound=False))
    #for button in range(11):
    #  self.launcher_buttons[0].append(Button(30 + (button * 32), 150, 16 + (int(len(str(button + 1)) > 1) * 12), 22, "", button + 1, toggle_layer, target=button + 1, font=launcherfontlittle, page=9, with_sound=False, shift_x_hitbox=16, shift_y_hitbox=6))

    for y, button in enumerate(languages):
      self.launcher_buttons[0].append(Button(300, 80 + (y * 24), 128, 26, "", button[0], set_language, target=button[1], font=launcherfontlittle, page=16, button_type="Language", with_sound=False, shift_x_hitbox=16))
    
    #
    if not self.client_instance.logged: #do you see terminal? ey
      for x, button in enumerate([("Log into Account", 18), ("Create Account", 21)]): #Ohh that's because main isn't defined, do self.
        self.launcher_buttons[0].append(Button(30 + (x * 265), 280, launcherfontlittle.render(button[0], "Black", False).get_width() + 5, 26, "", button[0], set_page, target=button[1], font=launcherfontlittle, page=17, button_type="Account Entry", with_sound=False, shift_x_hitbox=16, shift_y_hitbox=-2))
    else:
      self.launcher_buttons[0].append(Button(370, HEIGHT - 70, 100, 32, "", "Log out", exit_account, page=17, font=launcherfontsmall, with_sound=False, shift_x_hitbox=16))

    self.launcher_buttons[0].append(Button(410, 270, 32, 32, l[lg]["Retry"], "Assets/editor/ccw.png", retry_server_link, page=24, with_sound=False, button_type="Network Retry"))
    
    for y in (18, 19, 20):
      for x, button in enumerate([19, 20]):
        self.launcher_buttons[0].append(Button(24, 160 + (x * 70), 160, 20, "", "", set_page, target=button, page=y, with_sound=False))
    
    for y in (21, 22, 23):
      for x, button in enumerate([22, 23]):
        self.launcher_buttons[0].append(Button(24, 160 + (x * 70), 160, 20, "", "", set_page, target=button, page=y, with_sound=False))
    
    for y in (19, 22):
      for x, button in enumerate(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "!", "'",   "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "?", "-",   "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", ",", "`",   "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", ".", "~",   "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "_", "Backspace"]):
        if button != "Backspace": self.launcher_buttons[0].append(Button(((x % 15) * 34) - 15, (HEIGHT - 170) + math.floor(x / 15) * 34, 32, 32, "", button, add_letter_on_username if y == 19 else add_letter_on_create_username, target=button, page=y, font=launcherfontsmall, with_sound=False, shift_x_hitbox=16))
        else: self.launcher_buttons[0].append(Button(((x % 15) * 34) - 15, (HEIGHT - 170) + math.floor(x / 15) * 34, 128, 32, "", button, remove_letter_on_username if y == 19 else remove_letter_on_create_username, target=button, page=y, font=launcherfontsmall, with_sound=False, shift_x_hitbox=16))

    for y in (20, 23):
      for x, button in enumerate(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "!", "'",   "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "?", "-",   "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", ",", "`",   "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", ".", "~",   "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "_", "Backspace"]):
        if button != "Backspace": self.launcher_buttons[0].append(Button(((x % 15) * 34) - 15, (HEIGHT - 170) + math.floor(x / 15) * 34, 32, 32, "", button, add_letter_on_password if y == 20 else add_letter_on_create_password, target=button, page=y, font=launcherfontsmall, with_sound=False, shift_x_hitbox=16))
        else: self.launcher_buttons[0].append(Button(((x % 15) * 34) - 15, (HEIGHT - 170) + math.floor(x / 15) * 34, 128, 32, "", button, remove_letter_on_password if y == 20 else remove_letter_on_create_password, target=button, page=y, font=launcherfontsmall, with_sound=False, shift_x_hitbox=16))

    for y in (18, 21):
      self.launcher_buttons[0].append(Button(370, HEIGHT - 70, 100, 32, "", "Confirm", confirm_account, page=y, font=launcherfontsmall, with_sound=False, shift_x_hitbox=16))
    
    for x in (19, 20): self.launcher_buttons[0].append(Button(463, HEIGHT - 200, 25, 25, "", "×", set_page, target=18, page=x, color=(0, 0, 120), font=launcherfontsmall, with_sound=False, shift_x_hitbox=24, shift_y_hitbox=0))
    for x in (22, 23): self.launcher_buttons[0].append(Button(463, HEIGHT - 200, 25, 25, "", "×", set_page, target=21, page=x, color=(0, 0, 120), font=launcherfontsmall, with_sound=False, shift_x_hitbox=24, shift_y_hitbox=0))

    for x, button in enumerate(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "!", "'",   "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "?", "-",   "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", ",", "`",   "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", ".", "~",   "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "_", "Backspace"]):
      if button != "Backspace": self.launcher_buttons[0].append(Button(((x % 15) * 34) - 15, (HEIGHT - 170) + math.floor(x / 15) * 34, 32, 32, "", button, add_letter_on_join_username, target=button, page=14, font=launcherfontsmall, with_sound=False, shift_x_hitbox=16))
      else: self.launcher_buttons[0].append(Button(((x % 15) * 34) - 15, (HEIGHT - 170) + math.floor(x / 15) * 34, 128, 32, "", button, remove_letter_on_join_username, target=button, page=14, font=launcherfontsmall, with_sound=False, shift_x_hitbox=16))
    self.launcher_buttons[0].append(Button(340, 175, 120, 32, "", "Join Room", join_game_room, page=14, font=launcherfontsmall, with_sound=False, shift_x_hitbox=20, button_type="Join Room"))

    self.launcher_buttons[0].append(Button(320, 375, 150, 32, "", "Delete Room", delete_game_room, page=13, font=launcherfontsmall, with_sound=False, shift_x_hitbox=20, button_type="Join Deletion"))

  def update(self): #constant calling of the methods of the corresponding gamestates | İ
    global k_down, k_up, k_right, k_left, k_a, k_b, k_x, k_y, k_z, k_l, k_r, k_select, k_start, k_back
    self.now = time()
    self.dt = self.now - self.prev_time
    self.prev_time = self.now
    buttons = button_handler(self)
    k_a = buttons["A"]; k_b = buttons["B"]; k_x = buttons["X"]; k_y = buttons["Y"]
    k_right = buttons["Right"]; k_left = buttons["Left"]; k_up = buttons["Up"]; k_down = buttons["Down"]
    k_r = buttons["R"]; k_l = buttons["L"]
    k_z = buttons["Z"]; k_select = buttons["Select"]; k_start = buttons["Start"]; k_back = buttons["Back"]
    if self.editor_mode:
      #keyboard = pygame.key.get_pressed()
      #if (keyboard[pygame.K_LCTRL] or keyboard[pygame.K_RCTRL]) and keyboard[pygame.K_z]:
      #  self.undo_state -= 1
      #  self = undo_history[self.undo_state]
      #if (keyboard[pygame.K_LCTRL] or keyboard[pygame.K_RCTRL]) and keyboard[pygame.K_y]:
      #  if self.undo_state < len(undo_history):
      #    self.undo_state += 1
      #    self = undo_history[self.undo_state]
      if self.gamestate == 0: self.main_editor()
      if self.gamestate == 1: self.add_object()
      if self.gamestate == 2: self.game_settings()
      if self.gamestate == 3: self.room_manager()
      if self.gamestate == 4: self.rename() # Typing (keyboard)
      if self.gamestate == 5: self.edit_room()
      if self.gamestate == 6: self.track_library()
      if self.gamestate == 7: self.brush_mode() # Tile editor
      if self.gamestate == 8: self.layer_options()
      if self.gamestate == 9: self.renumber() # Typing numbers (keypad)
      if self.gamestate == 10: self.playtest(self.dt)
      if self.gamestate == 11: self.brush_mode_cc() # Tile editor for collectibles
      if self.gamestate == 12: self.new_entity_type()
      if self.gamestate == 13: self.new_collectible_type()
      if self.gamestate == 14: self.new_container_type()
      if self.gamestate == 15: self.stat_settings()
      if self.gamestate == 16: self.sfx_library()
      if self.gamestate == 17: self.bg_library()
      if self.gamestate == 18: self.bg_options() # Background settings
      if self.gamestate == 19: self.edit_player() # Player settings
      if self.gamestate == 20: self.edit_tile()#But the thing is, how can we know which corner should be appended?
      if self.gamestate == 21: self.edit_collectible()
      if self.gamestate == 22: self.edit_zone() #Not just dirt, any tile type
      if self.gamestate == 23: self.edit_entity()
      if self.gamestate == 24: self.edit_cutscene(self.dt)
      if self.gamestate == 25: self.new_entity_type_2()
      if self.gamestate == 26: self.new_entity_type_3()
      if self.gamestate == 27: self.brush_mode_ea()
      if self.gamestate == 28: self.game_style()
      if self.gamestate == 29: self.set_background_to()
      if self.gamestate == 30: self.application_settings()
      if self.gamestate == 31: self.action_customizations()
      if self.gamestate == 32: self.edit_door()
      if self.gamestate == 33: self.entity_dialogue()
      if self.gamestate == 34: self.stat_effects()
      if self.gamestate == 35: self.stat_ui()
      if self.gamestate == 36: self.set_collectible_price()
      if self.gamestate == 37: self.rebool()
      if self.gamestate == 38: self.scene_repos()
      if self.gamestate == 39: self.scene_move()
      if self.gamestate == 40: self.scene_action()
      if self.gamestate == 41: self.scene_audio()
      if self.gamestate == 42: self.track_library()
      if self.gamestate == 43: self.edit_text()
      if self.gamestate == 44: self.font_library()
      if self.gamestate == 45: self.save_manager()
      if self.gamestate == 46: self.image_library()
      if self.gamestate == 47: self.cs_condition()
      if self.gamestate == 48: self.shader_library()
      if self.gamestate == 49: self.projectile_library()
      if self.gamestate == 50: self.projectile_editor()
      if self.gamestate == 51: self.projectile_image_library()
      if self.gamestate == 52: self.edit_bossfight()
      if self.gamestate == 53: self.edit_tile_types()
      if self.gamestate == 54: self.edit_character_types()
      if self.gamestate == 55: self.edit_collectible_types()
      if self.gamestate == 56: self.edit_entities()
      if self.gamestate == 57: self.edit_entity_behaviors()
      if self.gamestate == 58: self.edit_menu()
      if self.gamestate == 59: self.edit_menu2()
      if self.gamestate == 60: self.edit_text_behaviors()
      if self.gamestate == 61: self.edit_ui_behaviors()
      if (self.gamestate != 0 and self.gamestate != 24) and self.display_buttons: self.manage_buttons(self.buttons) #here, if you don't call this function the buttons don't appear and are not clickable
    else:
      if self.gamestate == 0: self.launcher(self.dt)
      if self.gamestate == 1: self.playtest(self.dt)
      if self.display_buttons: self.manage_buttons(self.launcher_buttons) #here, if you don't call this function the buttons don't appear and are not clickable
      #undo_history.clear()
    console.update(screen)
    run()
    if self.on_page == 0: self.on_page = 1
    main.hover_on_button = False

  def manage_buttons(self, buttons): # if you don't call this
    if type(self.gamestate) == str: self.gamestate = 0
    for button in [button for button in buttons[self.gamestate] if button.page == self.on_page or button.page == 0]:
      render = True
      if (button.button_type == "Layer" and button.room != self.selected_room) or (button.button_type == "Background Layer" and button.room != self.selected_room) or (self.gamestate == 53 and not self.tile_types) or (self.gamestate == 54 and not self.character_types) or (self.gamestate == 55 and not self.collectible_types) or (self.gamestate == 56 and not self.entity_types): render = False
      if render: button.update()
    if self.gamestate == 0 and self.editor_mode:
      for index, cutscene in enumerate(self.rooms[self.selected_room].cutscenes):
        pygame.draw.rect(screen, (0, 0, 75), (((WIDTH - cutscene_margin) + 4, 2 + (index * 50)), (cutscene_margin - 6, 48))); pygame.draw.rect(screen, "Dark Blue", (((WIDTH - cutscene_margin) + 4, 2 + (index * 50)), (cutscene_margin - 6, 48)), width=2); screen.blit(fontsmaller.render(cutscene.name, True, "White"), ((WIDTH - cutscene_margin) + 6, 4 + (index * 50)))
        for button in cutscene.buttons: button.update(index * 50)
    for button in [button for button in buttons[self.gamestate] if button.page == self.on_page or button.page == 0]:
      render = True
      if (button.button_type == "Layer" and button.room != self.selected_room) or (button.button_type == "Background Layer" and button.room != self.selected_room) or (self.gamestate == 53 and not self.tile_types) or (self.gamestate == 54 and not self.character_types) or (self.gamestate == 55 and not self.collectible_types) or (self.gamestate == 56 and not self.entity_types): render = False
      if render: button.render_border()
    if self.gamestate == 0 and self.editor_mode:
      for index, cutscene in enumerate(self.rooms[self.selected_room].cutscenes):
        for button in cutscene.buttons: button.on_hover(index * 50)
    for button in [button for button in buttons[self.gamestate] if button.page == self.on_page or button.page == 0]:
      render = True
      if (button.button_type == "Layer" and button.room != self.selected_room) or (button.button_type == "Background Layer" and button.room != self.selected_room) or (self.gamestate == 53 and not self.tile_types) or (self.gamestate == 54 and not self.character_types) or (self.gamestate == 55 and not self.collectible_types) or (self.gamestate == 56 and not self.entity_types): render = False
      if render: button.on_hover()

  def main_editor(self):
    global k_x
    #IT WORK
    # RENDER OBJECTS
    self.rooms[self.selected_room].render_backgrounds(screen, fg=False)
    for layer in self.rooms[self.selected_room].layers[::-1]: layer.render_tiles(screen); layer.render_collectibles(screen); layer.render_entities(screen); layer.render_texts(screen) #renders the tiles and coins for every layer (::-1 means reverse)
    for door in self.rooms[self.selected_room].doors: door.update(screen)
    for player in self.players: player.display(screen)
    for zone in self.rooms[self.selected_room].zones: zone.draw(screen)
    self.rooms[self.selected_room].render_backgrounds(screen, bg=False)
    for layer in self.rooms[self.selected_room].layers[::-1]: layer.render_texts(screen, self.playback_on, front=True)

    if self.width != WIDTH or self.height != HEIGHT: pygame.draw.rect(screen, "Yellow", ((0 - ((k_l or (not k_z)) * self.camera.scroll[0]), 0 - ((k_r or (not k_z)) * self.camera.scroll[1])), (self.width, self.height)), 1)

    # DİSPLAY SELECTİON
    if self.selected_object != None: pygame.draw.rect(screen, "Green", ((self.selected_object.rect.x - self.camera.scroll[0], self.selected_object.rect.y - self.camera.scroll[1]), (self.selected_object.rect.width, self.selected_object.rect.height)), 1)

    # CUTSCENE TAB
    pygame.draw.rect(screen, (0, 0, 50), ((WIDTH - cutscene_margin, 0), (cutscene_margin, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((WIDTH - cutscene_margin, 0), (2, HEIGHT)))
    if len(self.rooms[self.selected_room].cutscenes) == 0: screen.blit(fontsmaller.render(l[lg]["No cutscenes in this room"], True, "White"), (WIDTH - (cutscene_margin - 5), 20))

    # LAYER TAB
    for x, layer in enumerate(self.rooms[self.selected_room].layers):
      pygame.draw.rect(screen, (50, 0, 0), ((1 + (x * 33), HEIGHT - 33), (32, 32)))
      pygame.draw.rect(screen, "Dark Red", ((1 + (x * 33), HEIGHT - 33), (32, 32)), width=2)
      screen.blit(fontmedium.render(layer.label, True, "White"), ((6 - (int(x >= 9) * 3)) + (x * 33), HEIGHT - (26 - (int(layer.name != "") * 6))))
      screen.blit(fontsmaller.render(layer.name, True, "White"), (1 + (x * 33), HEIGHT - 30))

    # BG TAB
    for x, bg in enumerate(self.rooms[self.selected_room].backgrounds):
      pygame.draw.rect(screen, (0, 50, 50), ((1 + (x * 33), HEIGHT - 50), (32, 16)))
      pygame.draw.rect(screen, "Dark Cyan", ((1 + (x * 33), HEIGHT - 50), (32, 16)), width=2)
      screen.blit(fontlittle.render(str(x + 1), True, "White"), ((6 - (int(x >= 9) * 3)) + (x * 33), HEIGHT - 48))

    # EXTRA İNFO
    if type(self.selected_object).__name__ != "NoneType": so = l[lg]["Selected Object: "] + type(self.selected_object).__name__
    else: so = l[lg]["No object selected"]
    screen.blit(fontsmaller.render(l[lg]["Scroll X: "] + str(self.camera.scroll[0]) + " | " + l[lg]["Scroll Y: "] + str(self.camera.scroll[1]) + " | X: " + str(snapint((pygame.mouse.get_pos()[0] + self.camera.scroll[0]) - (self.tiles_size / 2), main.tiles_size)) + " | Y: " + str(snapint((pygame.mouse.get_pos()[1] + self.camera.scroll[1]) - (self.tiles_size / 2), main.tiles_size)), True, "White"), (2, 16))
    screen.blit(fontsmaller.render(l[lg]["Tunaditor"] + " " + str(TUNADİTOR_VERSİON) + " | " + l[lg]["İn Room: "] + self.rooms[self.selected_room].name + " | " + so, True, "White"), (2, 2))
    
    # Let's see if the user REALLY wanted to quit -_-
    if self.user_certainty:
      pygame.draw.rect(screen, (0, 0, 50), ((30, 100), (WIDTH - 200, HEIGHT - 300)))
      pygame.draw.rect(screen, "Dark Blue", ((30, 100), (WIDTH - 200, HEIGHT - 300)), width=2)
      screen.blit(fontsmall.render(l[lg]["Are you sure you want to leave?"], True, "White"), (58, 110))
      for x, button in enumerate([(l[lg]["Back to Editing"], "back", go_to), (l[lg]["Save and Quit"], "floppy disk", save_quit), (l[lg]["Quit without Saving"], "rooms", quit_without_save)]):
        self.buttons[0].append(Button(34 + (x * 34), HEIGHT - 236, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], 0))

    if type(self.selected_object) == Entity or type(self.selected_object) == Player or type(self.selected_object) == Tile or type(self.selected_object) == Door or type(self.selected_object) == Collectible or type(self.selected_object) == Text or type(self.selected_object) == Background:
      if not self.selected_object.spawn_as_visible: screen.blit(fontmedium.render("O", True, "White"), (338, 40))

    self.manage_buttons(self.buttons)
    for button in self.buttons[0]:
      if button.text == l[lg]["Back to Editing"] or button.text == l[lg]["Save and Quit"] or button.text == l[lg]["Quit without Saving"] or button.button_type == "Exclusive if Selected Object": self.buttons[0].remove(button)

    # OBJECT SELECTİON
    texts = []
    for layer in self.rooms[self.selected_room].layers:
      for text in layer.texts: texts.append(text)
    if not main.hover_on_button:
      if len(self.rooms[self.selected_room].layers) > 0: self.top_tiles = self.rooms[self.selected_room].layers[0].tiles; self.top_collectibles = self.rooms[self.selected_room].layers[0].collectibles; self.top_actors = self.rooms[self.selected_room].layers[0].actors
      else: self.top_tiles = []; self.top_collectibles = []; self.top_actors = []
      combined = self.players + self.rooms[self.selected_room].zones + texts + self.top_tiles + self.top_collectibles + self.top_actors + self.rooms[self.selected_room].doors + self.rooms[self.selected_room].backgrounds
      if self.selected_object != None:
        if self.selected_object in combined: combined.remove(self.selected_object)
      for object in combined:
        if pygame.mouse.get_pos()[0] > object.rect.left - self.camera.scroll[0] and pygame.mouse.get_pos()[0] < object.rect.right - self.camera.scroll[0] and pygame.mouse.get_pos()[1] > object.rect.top - self.camera.scroll[1] and pygame.mouse.get_pos()[1] < object.rect.bottom - self.camera.scroll[1]:
          if k_a: self.selected_object = object; selection_sfx.play(); break
        elif k_a: self.selected_object = None
      if k_b: self.selected_object = None

    if type(self.selected_object) == Entity or type(self.selected_object) == Player or type(self.selected_object) == Tile or type(self.selected_object) == Door or type(self.selected_object) == Collectible or type(self.selected_object) == Text or type(self.selected_object) == Background:
      self.buttons[0].append(Button(330, 32, 32, 32, l[lg]["Toggle Show/Hide"], "Assets/editor/toggle 2.png", toggle_show_hide, button_type="Exclusive if Selected Object"))

    if k_left: self.camera.scroll[0] -= 2 + (int(k_y) * 6)
    if k_right: self.camera.scroll[0] += 2 + (int(k_y) * 6)
    if k_up: self.camera.scroll[1] -= 2 + (int(k_y) * 6)
    if k_down: self.camera.scroll[1] += 2 + (int(k_y) * 6)
    if k_x: self.gamestate = 58; k_x = False
  
  def add_object(self): #add object screen
    screen.blit(fontsmall.render(l[lg]["ESC to Cancel"], True, "White"), (2, 2))
    pygame.draw.rect(screen, (0, 0, 50), ((50, 100), (WIDTH - 100, HEIGHT - 170)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 100), (WIDTH - 100, HEIGHT - 170)), width=2)
    screen.blit(fontmedium.render(l[lg]["Create Object"], True, "White"), (55, 105))
    if k_back: self.gamestate = 0

  def game_settings(self): #add object screen
    screen.blit(fontsmall.render(l[lg]["ESC to Cancel"], True, "White"), (2, 2))
    pygame.draw.rect(screen, (0, 0, 50), ((50, 100), (WIDTH - 100, HEIGHT - 200)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 100), (WIDTH - 100, HEIGHT - 200)), width=2)
    screen.blit(fontmedium.render(l[lg]["General Settings"], True, "White"), (55, 105))
    screen.blit(fontmedium.render(f": {main.tiles_size}", True, "White"), (337, 322))
    screen.blit(fontsmaller.render({True: "On", False: "Off"}[self.snap_tile_image] + "      " + {True: "On", False: "Off"}[not self.snap_tile_rect], True, "White"), (392, 300))
    if k_back: self.gamestate = 0

  def room_manager(self):
    for index in range(30):
      if index % 2 == 0: pygame.draw.rect(screen, (0, 0, 50), ((0, 45 + (index * 26)), (WIDTH, 26)))
      else: pygame.draw.rect(screen, (0, 0, 20), ((0, 45 + (index * 26)), (WIDTH, 26)))
    for index, room in enumerate(self.rooms[minint(self.selected_room - 10, 0):]):
      try:
        if self.rooms[self.selected_room].name == room.name: screen.blit(fontsmall.render(room.name, True, "Yellow"), (1, 50 + (index * 26)))
        else: screen.blit(fontsmall.render(room.name, True, "White"), (1, 50 + (index * 26)))
      except: self.selected_room = 0

    try: actor_count = len(self.rooms[self.selected_room].layers[0].actors)
    except: actor_count = 0

    room_margin = 250
    pygame.draw.rect(screen, (0, 0, 50), ((WIDTH - room_margin, 0), (room_margin, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((WIDTH - room_margin, 0), (2, HEIGHT)))
    screen.blit(fontmedium.render(f"{self.rooms[self.selected_room].name}", True, "White"), (room_margin + 30, 16))
    if self.rooms[self.selected_room].track: track = self.rooms[self.selected_room].track
    elif self.rooms[self.selected_room].first_track: track = self.rooms[self.selected_room].first_track
    else: track = ""
    screen.blit(fontsmall.render(l[lg]["Borders"] + ":\n  " + l[lg]["Right: "] + str(self.rooms[self.selected_room].borders['right']) + "\n  " + l[lg]["Left: "] + str(self.rooms[self.selected_room].borders['left']) + "\n  " + l[lg]["Top: "] + str(self.rooms[self.selected_room].borders['top']) + "\n  " + l[lg]["Bottom: "] + str(self.rooms[self.selected_room].borders['bottom']) + "\n\n" + l[lg]["Total Cutscenes: "] + str(len(self.rooms[self.selected_room].cutscenes)) + "\n" + l[lg]["Total Actors: "] + str(actor_count) + "\n" + l[lg]["Total Layers: "] + str(len(self.rooms[self.selected_room].layers)) + "\n" + l[lg]["Track: "] + track, True, "White"), (room_margin + 30, 220))

    screen.blit(pygame.transform.scale(pygame.image.load("Assets/editor/room.png").convert_alpha(), (128, 128)), (room_margin + 32, 64))
    screen.blit(fontmedium.render(l[lg]["Room Manager"], True, "White"), (0, 16))
    
    if k_down: self.selected_room += 1; scrolldown_sfx.play()
    if k_up: self.selected_room -= 1; scrollup_sfx.play()
    if self.selected_room < 0: self.selected_room = len(self.rooms) - 1
    if self.selected_room > len(self.rooms) - 1: self.selected_room = 0
    if k_back: self.gamestate = 0; self.current_room = self.selected_room

  def rename(self):
    global k_back, kfont
    screen.fill("Black")# - (int(self.remember_gs == 35 or self.remember_gs == 43) * 50) | - (int(self.remember_gs == 35 or self.remember_gs == 43) * 100)
    pygame.draw.rect(screen, (0, 0, 50), ((50, 100), (WIDTH - 100, HEIGHT - 300)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 100), (WIDTH - 100, HEIGHT - 300)), width=2)
    if self.remember_gs != 0 and self.remember_gs != 15 and self.remember_gs != 29 and self.remember_gs != 30 and self.remember_gs != 33 and self.remember_gs != 35 and self.remember_gs != 43: screen.blit(fontsmall.render(f"Rename {self.target_object} Object, {main.rename_target.name}", True, "White"), (105, 105))
    elif self.remember_gs == 35 or self.remember_gs == 43: screen.blit(fontsmall.render(f"Rename {self.target_object} Object", True, "White"), (105, 105))
    else: screen.blit(fontsmall.render(f"Rename {self.target_object} Object, {self.rename_target}", True, "White"), (105, 105))
    if self.remember_gs == 0 and self.target_object == "Title":
      if os.path.isfile("Saves/games/" + self.rename_text + "/" + self.rename_text) and self.active_directory: screen.blit(fontlittle.render("By pressing ENTER, you will overwrite another game with the same name!", True, "Yellow"), (2, 68))
      elif os.path.isfile("Saves/games/" + self.rename_text) and not self.active_directory: screen.blit(fontlittle.render("By pressing ENTER, you will overwrite another game with the same name!", True, "Yellow"), (2, 68))
    if self.remember_gs == 35 or self.remember_gs == 43:
      if self.remember_gs != 35:
        try: kfont = pygame.Font(self.selected_object.font_str, 30)
        except: kfont = pygame.font.SysFont(self.selected_object.font_str, 30)
      else:
        try: kfont = pygame.Font(self.ui.instances[self.selected_ui][self.selected_ui_mode]["Font STR"], 30)
        except: kfont = pygame.font.SysFont(self.ui.instances[self.selected_ui][self.selected_ui_mode]["Font STR"], 30)
      kfont.set_script("Arab")
      if k_y or self.on_page == 7 or self.on_page == 8 or self.on_page == 9: kfont.set_direction(pygame.DIRECTION_RTL)
      screen.blit(kfont.render(self.rename_text[:self.text_cursor] + "_" + self.rename_text[self.text_cursor:], True, "White"), (80, 150))
      if self.remember_gs != 35:
        try: kfont = pygame.Font(self.selected_object.font_str, 30)
        except: kfont = pygame.font.SysFont(self.selected_object.font_str, 30)
      else:
        try: kfont = pygame.Font(self.ui.instances[self.selected_ui][self.selected_ui_mode]["Font STR"], 30)
        except: kfont = pygame.font.SysFont(self.ui.instances[self.selected_ui][self.selected_ui_mode]["Font STR"], 30)
    else: screen.blit(fontmedium.render(self.rename_text[:self.text_cursor] + "_" + self.rename_text[self.text_cursor:], True, "White"), (80, 150))
    screen.blit(fontsmall.render(l[lg]["Press L (-) and R (+) to Access More Glyphs:"] + "\n" + l[lg]["Page"] + " " + str(self.on_page) + " | " + glyph_pages[self.on_page], True, "White"), (2, 27))
    screen.blit(fontmedium.render(l[lg]["Press ENTER to Confirm, ESC to Cancel"], True, "Yellow"), (2, 2))
    screen.blit(fontmedium.render(l[lg]["Press ENTER to Confirm, ESC to Cancel"], True, "Blue"), (2, 4))
    screen.blit(fontmedium.render(l[lg]["Press ENTER to Confirm, ESC to Cancel"], True, "White"), (2, 3))
    self.page_amount = 17
    if k_b:
      if main.text_cursor > 0: text = str(main.rename_text); main.rename_text = text[:main.text_cursor - 1] + text[main.text_cursor:]; main.text_cursor -= 1
    if k_x: text = str(main.rename_text); main.rename_text = text[:main.text_cursor] + " " + text[main.text_cursor:]; main.text_cursor += 1
    if k_r:
      self.on_page += 1; switch_page_sfx.play()
      if self.on_page > self.page_amount: self.on_page = 1
    if k_l:
      self.on_page -= 1; switch_page_sfx.play()
      if self.on_page <= 0: self.on_page = self.page_amount
    if k_back: self.gamestate = self.remember_gs; self.rename_target = ""; self.rename_text = ""; k_back = False; self.on_page = 1
    if k_y or self.on_page == 7 or self.on_page == 8 or self.on_page == 9:
      if k_right:
        if self.text_cursor > 0: self.text_cursor -= 1
      if k_left:
        if self.text_cursor < len(self.rename_text): self.text_cursor += 1
    else:
      if k_left:
        if self.text_cursor > 0: self.text_cursor -= 1
      if k_right:
        if self.text_cursor < len(self.rename_text): self.text_cursor += 1
    if k_up: self.text_cursor = 0
    if k_down: self.text_cursor = len(self.rename_text)
    if k_start and (len(str(self.rename_text)) or not (self.remember_gs == 0 or self.remember_gs == 43)):
      self.gamestate = self.remember_gs
      self.rename_target = self.rename_text
      if (self.remember_gs != 0 or self.target_object != "Title") and self.remember_gs != 15 and self.remember_gs != 29 and self.remember_gs != 30 and self.remember_gs != 33 and self.remember_gs != 35 and self.remember_gs != 43: self.instance_target.name = self.rename_target
      elif self.remember_gs == 0 and self.target_object == "Title":
        self.game_name = self.rename_text
        if self.active_directory:
          try: os.mkdir("Saves/games/" + self.rename_target + "/")
          except FileExistsError: pass
          save_game(self.rename_target + "/" + self.rename_target, main)
        else: save_game(self.rename_target, main)
        main.saves = os.listdir("Saves/games/")
        if self.user_certainty: self.editor_mode = False; self.user_certainty = False; self.reset("")
      elif self.remember_gs == 15:
        for index, ui in enumerate(self.ui.instances.values()):
          if self.ui.instances[main.selected_stat][str(index + 1)]["Stat"] == self.selected_stat:
            self.ui.instances[self.rename_target] = self.ui.instances[self.selected_stat]
            self.ui.instances[main.selected_stat][str(index + 1)]["Stat"] = self.rename_target
            self.ui.instances.pop(self.selected_stat)
            break
        vartype = self.game_stats[self.instance_target]
        self.game_stats_initpoint[self.rename_target] = self.game_stats_initpoint[self.instance_target]
        self.game_stats_effect[self.rename_target] = self.game_stats_effect[self.instance_target]
        if vartype == int or vartype == float: self.game_stats_range[self.rename_target] = self.game_stats_range[self.instance_target]
        del self.game_stats[self.instance_target]
        del self.game_stats_initpoint[self.instance_target]
        del self.game_stats_effect[self.instance_target]
        if vartype == int or vartype == float: del self.game_stats_range[self.instance_target]
        self.game_stats[self.rename_target] = vartype
      elif self.remember_gs == 29: self.selected_object.character_string[self.selected_value] = self.rename_target
      elif self.remember_gs == 30: self.publisher = self.rename_target
      elif self.remember_gs == 33: self.selected_object.dialogue[self.selected_dl] = self.rename_target; manage_dialogues(None)
      elif self.remember_gs == 35: self.ui.instances[self.selected_ui][self.selected_ui_mode]["Text"] = self.rename_target; self.ui.regenerate(self.selected_ui)
      elif self.remember_gs == 43: self.instance_target.text = self.rename_target; self.selected_object.regenerate()
      self.rename_text = ""

  def renumber(self):
    global k_back
    pygame.draw.rect(screen, (0, 0, 50), ((100, 100), (WIDTH - 200, HEIGHT - 300)))
    pygame.draw.rect(screen, "Dark Blue", ((100, 100), (WIDTH - 200, HEIGHT - 300)), width=2)
    screen.blit(fontsmall.render(f"Set value {self.target_object} as", True, "White"), (105, 105))
    screen.blit(fontmedium.render(str(str(self.rename_text) + "  ")[:self.text_cursor] + "_" + str(str(self.rename_text) + "  ")[self.text_cursor:], True, "White"), (150, 150))
    screen.blit(fontsmall.render("Press ENTER to Apply, ESC to Cancel", True, "White"), (2, 2))
    if k_b:
      if main.text_cursor > 0: text = str(main.rename_text); main.rename_text = text[:main.text_cursor - 1] + text[main.text_cursor:]; main.text_cursor -= 1
    if k_left:
      if self.text_cursor > 0: self.text_cursor -= 1
    if k_right:
      if self.text_cursor < len(str(self.rename_text)): self.text_cursor += 1
    if k_up: self.text_cursor = 0
    if k_down: self.text_cursor = len(str(self.rename_text))
    if k_back: self.gamestate = self.remember_gs; self.rename_target = ""; self.rename_text = ""; k_back = False
    if k_start and len(str(self.rename_text)):
      self.gamestate = self.remember_gs
      if self.gamestate == 2: self.tiles_size = int(self.rename_text)
      if self.gamestate == 5: self.rename_target = int(self.rename_text); self.rooms[self.selected_room].borders[self.selected_rename_attrib] = self.rename_target; self.rooms[self.selected_room].spawn_borders[self.selected_rename_attrib] = self.rooms[self.selected_room].borders[self.selected_rename_attrib]
      if self.gamestate == 15:
        try:
          if self.target_object == "Stat":
            if self.game_stats[self.selected_stat] == int: self.rename_target = int(self.rename_text); self.game_stats_initpoint[self.selected_stat] = int(self.rename_target)
            elif self.game_stats[self.selected_stat] == float: self.rename_target = float(self.rename_text); self.game_stats_initpoint[self.selected_stat] = float(self.rename_target)
          elif self.target_object == "Stat (Max)":
            if self.game_stats[self.selected_stat] == int: self.rename_target = int(self.rename_text); self.game_stats_range[self.selected_stat][1] = int(self.rename_target)
            elif self.game_stats[self.selected_stat] == float: self.rename_target = float(self.rename_text); self.game_stats_range[self.selected_stat][1] = float(self.rename_target)
          elif self.target_object == "Stat (Min)":
            if self.game_stats[self.selected_stat] == int: self.rename_target = int(self.rename_text); self.game_stats_range[self.selected_stat][0] = int(self.rename_target)
            elif self.game_stats[self.selected_stat] == float: self.rename_target = float(self.rename_text); self.game_stats_range[self.selected_stat][0] = float(self.rename_target)
        except: pass
      if self.gamestate == 30:
        if self.selected_rename_attrib == "Width": self.width = int(self.rename_text)
        if self.selected_rename_attrib == "Height": self.height = int(self.rename_text)
        if self.selected_rename_attrib == "FPS": self.fps = int(self.rename_text)
        self.camera.rect.width, self.camera.rect.height = self.width, self.height
      if self.gamestate == 40:
        self.rename_target = int(self.rename_text)
        if self.target_object == "top": main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['I1'] = self.rename_target
        if self.target_object == "right": main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['I2'] = self.rename_target
        if self.target_object == "bottom": main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['I3'] = self.rename_target
        if self.target_object == "left": main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['I4'] = self.rename_target

  def brush_mode(self):
    global k_left, k_right, k_down, k_up
    if k_back:
      self.gamestate = 0; self.on_page = 1
      for tile in self.rooms[self.selected_room].layers[self.selected_layer].tiles: tile.selected = False
    if k_r:
      self.on_page += 1; switch_page_sfx.play()
      if self.on_page > self.page_amount: self.on_page = 1
    if k_l:
      self.on_page -= 1; switch_page_sfx.play()
      if self.on_page <= 0: self.on_page = self.page_amount
    render_grid()
    try: self.rooms[self.selected_room].layers[self.selected_layer].render_tiles(screen)
    except: pass
    
    mouse_pos = [pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]]
    xp, yp = snapint((mouse_pos[0] + self.camera.scroll[0]) - (main.tiles_size / 2), main.tiles_size), snapint((mouse_pos[1] + self.camera.scroll[1]) - (main.tiles_size / 2), main.tiles_size)
    try:
      #if self.snap_tile_rect:
      #  if type(self.selected_tile[1]) == list: size = [self.selected_tile[1][0].get_width(), self.selected_tile[1][0].get_height()]
      #  else: size = [self.selected_tile[1].get_width(), self.selected_tile[1].get_height()]
      #else: size = [self.tiles_size, self.tiles_size]
      if (k_a and not k_b) and mouse_pos[1] > 100 and self.selected_tile != ():
        place_possible = True
        for tile in self.rooms[self.selected_room].layers[self.selected_layer].tiles:
          if self.selected_tile[0] == tile.type and not (tile.rect.x != xp or tile.rect.y != yp): place_possible = False
        if place_possible: self.rooms[self.selected_room].layers[self.selected_layer].tiles.append(Tile(xp, yp, self.selected_tile[0], main=main))
      elif mouse_pos[1] < 100 and k_a:
        for tile in self.rooms[self.selected_room].layers[self.selected_layer].tiles: tile.selected = False
    except: pass
    if (k_b and not k_a) and mouse_pos[1] > 100:
      eraser_rect = pygame.Rect(((mouse_pos[0] - (self.tiles_size / 2), mouse_pos[1] - (self.tiles_size / 2)), (self.tiles_size / 1.5, self.tiles_size / 1.5)))
      pygame.draw.rect(screen, "Dark Red", eraser_rect, border_radius=self.tiles_size // 4)
      for tile in [tile for tile in self.rooms[self.selected_room].layers[self.selected_layer].tiles if pygame.Rect((tile.rect.x - self.camera.scroll[0], tile.rect.y - self.camera.scroll[1]), (tile.rect.width, tile.rect.height)).colliderect(eraser_rect)]: self.rooms[self.selected_room].layers[self.selected_layer].tiles.remove(tile)

    if k_x or (k_a and k_b):
      if self.sr_release: self.selection_rect = pygame.Rect((mouse_pos[0], mouse_pos[1]), (0, 0))
      else:
        self.selection_rect.width = mouse_pos[0] - self.selection_rect.x
        self.selection_rect.height = mouse_pos[1] - self.selection_rect.y
      self.sr_release = False
      pygame.draw.rect(screen, "Green", self.selection_rect, 1)
      for tile in self.rooms[self.selected_room].layers[self.selected_layer].tiles:
        if self.selection_rect.colliderect((tile.rect.x - self.camera.scroll[0], tile.rect.y - self.camera.scroll[1]), (tile.rect.width, tile.rect.height)):
          tile.selected = True
          if k_left: tile.rect.x -= self.tiles_size; tile.spawn_location[0] = tile.rect.x
          if k_right: tile.rect.x += self.tiles_size; tile.spawn_location[0] = tile.rect.x
          if k_up: tile.rect.y -= self.tiles_size; tile.spawn_location[1] = tile.rect.y
          if k_down: tile.rect.y += self.tiles_size; tile.spawn_location[1] = tile.rect.y
      if k_left: self.selection_rect.x -= self.tiles_size; self.selection_rect.width -= self.tiles_size
      if k_right: self.selection_rect.x += self.tiles_size; self.selection_rect.width += (self.tiles_size * 2)
      if k_up: self.selection_rect.y -= self.tiles_size; self.selection_rect.height -= self.tiles_size
      if k_down: self.selection_rect.y += self.tiles_size; self.selection_rect.height += (self.tiles_size * 2)
      k_right, k_left, k_up, k_down = False, False, False, False
    else:
      self.sr_release = True
      self.selection_rect = pygame.Rect(mouse_pos, (0, 0))
      if k_left: self.camera.scroll[0] -= 3 + (int(k_y) * 15)
      if k_right: self.camera.scroll[0] += 3 + (int(k_y) * 15)
      if k_up: self.camera.scroll[1] -= 3 + (int(k_y) * 15)
      if k_down: self.camera.scroll[1] += 3 + (int(k_y) * 15)
    
    #Auto-tiling
    if k_x:
      try:
        for tile in [tile for tile in self.rooms[self.selected_room].layers[self.selected_layer].tiles if tile.selected]:
          tile.form = []
          for tile2 in self.rooms[self.selected_room].layers[self.selected_layer].tiles:
            if tile.rect.x == tile2.rect.x - self.tiles_size and tile.rect.y == tile2.rect.y: tile.form.append("right")
            elif tile.rect.x == tile2.rect.x + self.tiles_size and tile.rect.y == tile2.rect.y: tile.form.append("left")#Blud.... Yes and there will be a tile on our left
            elif tile.rect.y == tile2.rect.y - self.tiles_size and tile.rect.x == tile2.rect.x: tile.form.append("upper")#Look at this
            elif tile.rect.y == tile2.rect.y + self.tiles_size and tile.rect.x == tile2.rect.x: tile.form.append("lower")
          
          tile_type_name = get_material_name(self.selected_tile[0])
          
          #Block
          if tile.form == []: tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{'mw - stripped steel'} block.png").convert_alpha()
          #Row
          if "right" in tile.form and not ("upper" in tile.form and "lower" in tile.form): tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} row left.png").convert_alpha(); tile.type = f"{tile_type_name} row left.png"; tile.name = tile.type
          if "left" in tile.form and not ("upper" in tile.form and "lower" in tile.form): tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} row right.png").convert_alpha(); tile.type = f"{tile_type_name} row right.png"; tile.name = tile.type
          if "right" in tile.form and "left" in tile.form and not ("upper" in tile.form and "lower" in tile.form): tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} row.png").convert_alpha(); tile.type = f"{tile_type_name} row.png"; tile.name = tile.type
          #Column
          if "upper" in tile.form and not ("right" in tile.form and "left" in tile.form): tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} column upper.png").convert_alpha(); tile.type = f"{tile_type_name} column upper.png"; tile.name = tile.type
          if "lower" in tile.form and not ("right" in tile.form and "left" in tile.form): tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} column lower.png").convert_alpha(); tile.type = f"{tile_type_name} column lower.png"; tile.name = tile.type
          if "upper" in tile.form and "lower" in tile.form and not ("right" in tile.form and "left" in tile.form): tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} column.png").convert_alpha(); tile.type = f"{tile_type_name} column.png"; tile.name = tile.type
          #Terrain Upper
          if "upper" in tile.form and "left" in tile.form and "right" in tile.form and not "lower" in tile.form: tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} terrain upper.png").convert_alpha(); tile.type = f"{tile_type_name} terrain upper.png"; tile.name = tile.type
          elif "upper" in tile.form and "left" in tile.form and not ("right" in tile.form and "lower" in tile.form): tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} terrain upper right.png").convert_alpha(); tile.type = f"{tile_type_name} terrain upper right.png"; tile.name = tile.type
          elif "upper" in tile.form and "right" in tile.form and not ("left" in tile.form and "lower" in tile.form): tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} terrain upper left.png").convert_alpha(); tile.type = f"{tile_type_name} terrain upper left.png"; tile.name = tile.type
          #Terrain
          if "upper" in tile.form and "lower" in tile.form and "left" in tile.form and "right" in tile.form: tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} terrain.png").convert_alpha(); tile.type = f"{tile_type_name} terrain.png"; tile.name = tile.type
          elif "upper" in tile.form and "lower" in tile.form and "left" in tile.form and not "right" in tile.form: tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} terrain right.png").convert_alpha(); tile.type = f"{tile_type_name} terrain right.png"; tile.name = tile.type
          elif "upper" in tile.form and "lower" in tile.form and "right" in tile.form and not "left" in tile.form: tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} terrain left.png").convert_alpha(); tile.type = f"{tile_type_name} terrain left.png"; tile.name = tile.type
          #Terrain Lower
          if "lower" in tile.form and "left" in tile.form and "right" in tile.form and not "upper" in tile.form: tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} terrain lower.png").convert_alpha(); tile.type = f"{tile_type_name} terrain lower.png"; tile.name = tile.type
          elif "lower" in tile.form and "left" in tile.form and not ("right" in tile.form or "upper" in tile.form): tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} terrain lower right.png").convert_alpha(); tile.type = f"{tile_type_name} terrain lower right.png"; tile.name = tile.type
          elif "lower" in tile.form and "right" in tile.form and not ("left" in tile.form or "upper" in tile.form): tile.image = pygame.image.load(main.active_directory + f"Assets/tiles/{tile_type_name} terrain lower left.png").convert_alpha(); tile.type = f"{tile_type_name} terrain lower left.png"; tile.name = tile.type
        
      except: pass
    pygame.draw.rect(screen, (0, 0, 50), ((0, 0), (WIDTH, 100)))
    pygame.draw.rect(screen, "Dark Blue", ((0, 0), (WIDTH, 100)), width=2)
    screen.blit(fontsmall.render(f"Editing Layer {self.rooms[self.selected_room].layers[self.selected_layer].label} {self.rooms[self.selected_room].layers[self.selected_layer].name}   Room {self.rooms[self.selected_room].name}", True, "White"), (3, 3))
    screen.blit(fonttiny.render(f"Tile page {self.on_page}", True, "White"), (3, 16))
    if len(self.selected_tile):
      text = fontsmall.render(f"Selected Tile {self.selected_tile[0]}, index {self.selected_tile[2]}", True, "White")
      if text.get_width() < WIDTH - 75: screen.blit(text, (3, 80))
      else:
        text = fontlittle.render(f"Selected Tile {self.selected_tile[0]}, index {self.selected_tile[2]}", True, "White")
        if text.get_width() < WIDTH - 75: screen.blit(text, (3, 81))
        else:
          text = fontlittle.render(f"Selected Tile {self.selected_tile[0]}, index {self.selected_tile[2]}", True, "White")
          if text.get_width() < WIDTH - 75: screen.blit(text, (3, 82))
          else:
            text = fonttiny.render(f"Selected Tile {self.selected_tile[0]}, index {self.selected_tile[2]}", True, "White")
            screen.blit(text, (3, 83))
    else: screen.blit(fontsmall.render(f"No Tile Selected...", True, "White"), (3, 80))

  def brush_mode_cc(self):
    if k_back: self.gamestate = 7
    render_grid()
    for layer in self.rooms[self.selected_room].layers[::-1]: layer.render_tiles(screen)
    for layer in self.rooms[self.selected_room].layers[::-1]: layer.render_collectibles(screen)
    
    mouse_pos = [pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]]
    try:
      xp, yp = snapint((mouse_pos[0] + self.camera.scroll[0]) - (main.tiles_size / 2), main.tiles_size), snapint((mouse_pos[1] + self.camera.scroll[1]) - (main.tiles_size / 2), main.tiles_size)
      xp, yp = snapint((mouse_pos[0] + self.camera.scroll[0]) - (main.tiles_size / 2), main.tiles_size), snapint((mouse_pos[1] + self.camera.scroll[1]) - (main.tiles_size / 2), main.tiles_size)
      xp += (main.tiles_size - main.collectible_types[self.selected_tile[3]]["size"][0]) // 2
      yp += (main.tiles_size - main.collectible_types[self.selected_tile[3]]["size"][0]) // 2
      if k_a and mouse_pos[1] > 100 and self.selected_tile != ():
        place_possible = True
        for coin in self.rooms[self.selected_room].layers[self.selected_layer].collectibles:
          if self.selected_tile[0] == coin.name and not (coin.rect.x != xp or coin.rect.y != yp): place_possible = False
        if place_possible: self.rooms[self.selected_room].layers[self.selected_layer].collectibles.append(Collectible(xp, yp, self.selected_tile[0], main=main))
    except: pass
    if k_b and mouse_pos[1] > 100:
      eraser_rect = pygame.Rect(((mouse_pos[0] - (self.tiles_size / 2), mouse_pos[1] - (self.tiles_size / 2)), (self.tiles_size / 1.5, self.tiles_size / 1.5)))
      pygame.draw.rect(screen, "Dark Red", eraser_rect, border_radius=self.tiles_size // 4)
      for coin in [coin for coin in self.rooms[self.selected_room].layers[self.selected_layer].collectibles if pygame.Rect((coin.rect.x - self.camera.scroll[0], coin.rect.y - self.camera.scroll[1]), (coin.rect.width, coin.rect.height)).colliderect(eraser_rect)]: self.rooms[self.selected_room].layers[self.selected_layer].collectibles.remove(coin)

    if k_left: self.camera.scroll[0] -= 4 + (int(k_y) * 5)
    if k_right: self.camera.scroll[0] += 4 + (int(k_y) * 5)
    if k_up: self.camera.scroll[1] -= 4 + (int(k_y) * 5)
    if k_down: self.camera.scroll[1] += 4 + (int(k_y) * 5)

    pygame.draw.rect(screen, (0, 0, 50), ((0, 0), (WIDTH, 100)))
    pygame.draw.rect(screen, "Dark Blue", ((0, 0), (WIDTH, 100)), width=2)
    screen.blit(fontsmall.render(f"Editing Layer {self.rooms[self.selected_room].layers[self.selected_layer].label} {self.rooms[self.selected_room].layers[self.selected_layer].name}   Room {self.rooms[self.selected_room].name}, Collectibe Mode", True, "White"), (3, 3))
    try: screen.blit(fontsmall.render(f"Selected Coin {self.selected_tile[0]}, index {self.selected_tile[2]}", True, "White"), (3, 80))
    except: screen.blit(fontsmall.render(f"No Coin Selected...", True, "White"), (3, 80))

  def layer_options(self):
    if k_back: self.gamestate = 7
    pygame.draw.rect(screen, (0, 0, 50), ((100, 100), (WIDTH - 200, HEIGHT - 300)))
    pygame.draw.rect(screen, "Dark Blue", ((100, 100), (WIDTH - 200, HEIGHT - 300)), width=2)
    screen.blit(fontsmall.render(f"Layer  {self.rooms[self.selected_room].layers[self.selected_layer].label} {self.rooms[self.selected_room].layers[self.selected_layer].name} Options", True, "White"), (102, 102))
    screen.blit(fontsmall.render(f"Distance {self.rooms[self.selected_room].layers[self.selected_layer].distance}", True, "White"), (140, 220))
    screen.blit(fontsmall.render(f"Shade {self.rooms[self.selected_room].layers[self.selected_layer].shade}", True, "White"), (140, 186))

  def edit_room(self):
    pygame.draw.rect(screen, (0, 0, 50), ((100, 25), (WIDTH - 200, HEIGHT - 50)))
    pygame.draw.rect(screen, "Dark Blue", ((100, 25), (WIDTH - 200, HEIGHT - 50)), width=2)
    screen.blit(fontmedium.render(l[lg]["Room: "] + self.rooms[self.selected_room].name, True, "White"), (103, 32))
    screen.blit(fontsmaller.render(l[lg]["Gameplay Mode: "] + self.rooms[self.selected_room].mode, True, "White"), (103, 53))
    screen.blit(fontsmaller.render(l[lg]["Shader: "] + self.rooms[self.selected_room].shader, True, "White"), (103, 66))
    screen.blit(fontsmaller.render(l[lg]["Scrolling Mode: "] + self.rooms[self.selected_room].scroll_mode, True, "White"), (103, 78))
    screen.blit(fontsmaller.render("HM: " + {True: "On", False: "Off"}[self.rooms[self.selected_room].hm], True, "White"), (364, 64))
    screen.blit(fontsmaller.render("VM: " + {True: "On", False: "Off"}[self.rooms[self.selected_room].vm], True, "White"), (364, 78))
    
    screen.blit(fontsmaller.render(l[lg]["Press L (-) and R (+) to Access More Settings:"] + "\n" + l[lg]["Page"] + " " + str(self.on_page) + " | " + room_pages[self.on_page], True, "White"), (2, 2))

    if self.on_page == 1:
      screen.blit(fontsmall.render(l[lg]["Gravity"] + " " + str(round(self.rooms[self.selected_room].gravity, 1)), True, "White"), (138, 208))
      screen.blit(fontsmaller.render({True: "On", False: "Off"}[not self.rooms[self.selected_room].show_player], True, "White"), (103, 270))
      for button in [button for button in self.buttons[5] if button.button_type == "Room Borders"]: self.buttons[5].remove(button)
      for y, button in enumerate([(l[lg]["Right Border"], change_borders, "right"), (l[lg]["Left Border"], change_borders, "left")]):
        self.buttons[5].append(Button(95, 134 + (y * 34), 128, 32, l[lg]["Change Border"], button[0], button[1], target=str(self.rooms[self.selected_room].borders[button[2]]), target_object=button[2], target_gs=5, font=fontmedium, button_type="Room Borders", page=1))
      for y, button in enumerate([(l[lg]["Top Border"], change_borders, "top"), (l[lg]["Bottom Border"], change_borders, "bottom")]):
        self.buttons[5].append(Button(248, 134 + (y * 34), 128, 32, l[lg]["Change Border"], button[0], button[1], target=str(self.rooms[self.selected_room].borders[button[2]]), target_object=button[2], target_gs=5, font=fontmedium, button_type="Room Borders", page=1))
    
    if self.on_page == 2:
      screen.blit(fontsmall.render(l[lg]["Token"] + " " + str(self.selected_ui_sm), True, "White"), (138, 138))
      screen.blit(fontsmall.render(l[lg]["Mode"] + " " + str(self.selected_ui_mode_for_tm), True, "White"), (138, 178))
      screen.blit(fontlittle.render(l[lg]["Uİ Tokens to Show: "] + str(self.rooms[self.selected_room].show_ui), True, "Green"), (105, 210))
      screen.blit(fontlittle.render(l[lg]["Uİ Tokens to Hide: "] + str(self.rooms[self.selected_room].hide_ui), True, "Red"), (105, 228))
      screen.blit(fontlittle.render(l[lg]["Tokens Set to Mode (T, M): "] + str(self.rooms[self.selected_room].ui_modes), True, "White"), (105, 246))

    self.page_amount = 2
    if k_r:
      self.on_page += 1; switch_page_sfx.play()
      if self.on_page > self.page_amount: self.on_page = 1
    if k_l:
      self.on_page -= 1; switch_page_sfx.play()
      if self.on_page <= 0: self.on_page = self.page_amount

    pygame.draw.line(screen, "Dark Blue", (180, HEIGHT - 45), (350, HEIGHT - 45), width=7)
    # Inside your main loop or update function:
    if pygame.mixer_music.get_busy():
      pygame.draw.line(screen, "Dark Blue", (180, HEIGHT - 45), (350, HEIGHT - 45), width=7)
      try:
        current_position = pygame.mixer_music.get_pos()
        
        total_duration = song.get_length()
        current_position_seconds = current_position / 1000
        normalized_position = (current_position_seconds / total_duration) * 170

        # Draw the dark blue progress bar background

        #if HEIGHT - 50 <= pygame.mouse.get_pos()[1] <= HEIGHT - 40 and (pygame.mouse.get_pressed()[0] or k_a):
        #  clicked_position = pygame.mouse.get_pos()[0] - 180
        #  jump_time = (clicked_position / 170) * song.get_length()
        #  pygame.mixer_music.set_pos(jump_time)
        #  x_coordinate = clicked_position + 180
        
        #try: x_coordinate = normalized_position + clicked_position + 180
        #except: x_coordinate = normalized_position + 180

        # Ensure x_coordinate does not exceed the maximum value
        x_coordinate = normalized_position + 180
        if x_coordinate > 350: x_coordinate = 350

        # Draw the blue progress bar based on the calculated x_coordinate
        pygame.draw.line(screen, "Blue", (180, HEIGHT - 45), (x_coordinate, HEIGHT - 45), width=7)
      except: pass

    screen.blit(fontsmall.render(self.rooms[self.selected_room].track, True, "White"), (110, HEIGHT - 85))
    screen.blit(fontsmall.render(self.rooms[self.selected_room].first_track, True, "White"), (110, HEIGHT - 153))
    if k_back: self.gamestate = 3; self.on_page = 1

  def track_library(self):
    global song, metadata
    if k_back: self.gamestate = 5
    if k_down:
      self.selected_itemy += 1 + (int(k_y) * 4); scrolldown_sfx.play()
      if self.selected_itemy < len(self.tracks): song = pygame.mixer.Sound(self.active_directory + "Sounds/tracks/" + self.tracks[self.selected_itemy]); pygame.mixer_music.load(self.active_directory + "Sounds/tracks/" + self.tracks[self.selected_itemy]); metadata = pygame.mixer_music.get_metadata()
    if k_up:
      self.selected_itemy -= 1 + (int(k_y) * 4); scrollup_sfx.play()
      if self.selected_itemy < len(self.tracks): song = pygame.mixer.Sound(self.active_directory + "Sounds/tracks/" + self.tracks[self.selected_itemy]); pygame.mixer_music.load(self.active_directory + "Sounds/tracks/" + self.tracks[self.selected_itemy]); metadata = pygame.mixer_music.get_metadata()
    if self.selected_itemy < 0: self.selected_itemy = len(self.tracks) - 1; song = pygame.mixer.Sound(self.active_directory + "Sounds/tracks/" + self.tracks[self.selected_itemy]); pygame.mixer_music.load(self.active_directory + "Sounds/tracks/" + self.tracks[self.selected_itemy]); metadata = pygame.mixer_music.get_metadata()
    if self.selected_itemy > len(self.tracks) - 1: self.selected_itemy = 0; song = pygame.mixer.Sound(self.active_directory + "Sounds/tracks/" + self.tracks[self.selected_itemy]); pygame.mixer_music.load(self.active_directory + "Sounds/tracks/" + self.tracks[self.selected_itemy]); metadata = pygame.mixer_music.get_metadata()

    for index in range(30):
      if index % 2 == 0: pygame.draw.rect(screen, (0, 0, 50), ((0, 45 + (index * 26)), (WIDTH, 26)))
      else: pygame.draw.rect(screen, (0, 0, 20), ((0, 45 + (index * 26)), (WIDTH, 26)))
    for index, track in enumerate(self.tracks[minint(self.selected_itemy - 10, 0):]):
      try:
        if self.tracks[self.selected_itemy] == track: screen.blit(fontsmall.render(track, True, "Yellow"), (1, 50 + (index * 26)))
        else: screen.blit(fontsmall.render(track, True, "White"), (1, 50 + (index * 26)))
      except: self.selected_itemy = 0

    room_margin = 250
    pygame.draw.rect(screen, (0, 0, 50), ((WIDTH - room_margin, 0), (room_margin, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((WIDTH - room_margin, 0), (2, HEIGHT)))
    if len(self.tracks):
      try:
        if len(self.tracks[self.selected_itemy]) < 20: screen.blit(fontmedium.render(f"{self.tracks[self.selected_itemy]}", True, "White"), (room_margin + 30, 16))
        elif len(self.tracks[self.selected_itemy]) < 28: screen.blit(fontsmall.render(f"{self.tracks[self.selected_itemy]}", True, "White"), (room_margin + 30, 18))
        elif len(self.tracks[self.selected_itemy]) < 37: screen.blit(fontlittle.render(f"{self.tracks[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
        else: screen.blit(fontsmaller.render(f"{self.tracks[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
        total_seconds = round(song.get_length())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        screen.blit(fontsmall.render(f"Length: {minutes}:{seconds:02}", True, "White"), (room_margin + 20, 205))
        screen.blit(fontsmall.render("Metadata:", True, "White"), (room_margin + 20, 230))
        index = 0
        for key, value in metadata.items():
          text = fontsmall.render(f"{key.capitalize()}:\n  {value}", True, "White")
          if text.get_width() > WIDTH - (room_margin + 25): text = fontlittle.render(f"{key.capitalize()}:\n  {value}", True, "White")
          screen.blit(text, (room_margin + 25, 260 + (index * 48))); index += 1
        screen.blit(pygame.transform.scale(pygame.image.load("Assets/editor/track.png").convert_alpha(), (128, 128)), (room_margin + 32, 64))
      except: screen.blit(fontmedium.render("Select an audio file", True, "White"), (room_margin + 30, 16))
    else: screen.blit(fontmedium.render("No tracks imported", True, "White"), (room_margin + 30, 16))

    screen.blit(fontmedium.render("Track Library", True, "White"), (0, 16))


  def new_entity_type(self):
    if k_back: self.gamestate = 1; self.selected_range = 0; self.selected_drops = []; self.selected_value = 1; self.selected_animation = ""; self.selected_stat = ""; self.selected_hp = 1; self.selected_tile = (); self.selected_behaviors = []; self.selected_speed = [0, 0]; self.selected_sfx = ""; self.selected_sfx2 = ""; self.selected_sfx3 = ""; self.selected_sfx4 = ""; self.selected_sfx5 = ""
    pygame.draw.rect(screen, (0, 0, 50), ((50, 25), (WIDTH - 100, HEIGHT - 50)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 25), (WIDTH - 100, HEIGHT - 50)), width=2)
    screen.blit(fontmedium.render("New Entity Page 1", True, "White"), (56, 32))
    screen.blit(fontsmall.render("Behaviors", True, "White"), (70, 200))
    pygame.draw.rect(screen, (0, 0, 20), ((55, 220), (WIDTH - 110, 150)))
    for button in (button for button in self.buttons[12] if "Next Page" in button.text): self.buttons[12].remove(button)
    if self.selected_tile != (): main.buttons[12].append(Button(WIDTH - 90, HEIGHT - 60, 32, 32, "Next Page", "Assets/editor/next.png", go_to, 25))

  def new_collectible_type(self):
    if k_back: self.gamestate = 1; self.selected_tile = (); self.selected_stat = ""; self.selected_value = 1; self.selected_sfx = ""
    pygame.draw.rect(screen, (0, 0, 50), ((100, 25), (WIDTH - 200, HEIGHT - 50)))
    pygame.draw.rect(screen, "Dark Blue", ((100, 25), (WIDTH - 200, HEIGHT - 50)), width=2)
    screen.blit(fontmedium.render(f"New Collectible", True, "White"), (103, 32))
    try:
      screen.blit(fontsmaller.render(f"Selected Coin {self.selected_tile[0]}, index {self.selected_tile[2]}", True, "White"), (104, 60))
    except: screen.blit(fontsmaller.render(f"No Coin Selected...", True, "White"), (104, 60))
    screen.blit(fontsmall.render("Collectible Value", True, "White"), (110, 160))
    try:
      if main.game_stats[main.selected_stat] == int or main.game_stats[main.selected_stat] == float: text = fontbig.render(str(self.selected_value), True, "White")
      else: text = fontbig.render(" ", True, "White")
    except: text = fontbig.render("Select a stat", True, "White")
    screen.blit(text, ((WIDTH / 2) - (text.get_width() / 2) - 43, 185))
    screen.blit(fontsmall.render("Sound Effect", True, "White"), (110, 345))
    if self.selected_sfx == "": screen.blit(fontlittle.render("No SFX Used", True, "White"), (110, 365))
    else: screen.blit(fontlittle.render("SFX: " + self.selected_sfx, True, "White"), (110, 365))

    for button in [button for button in self.buttons[13] if button.text == "Finish Collectible Type"]: self.buttons[13].remove(button)
    if len(main.selected_tile) and main.selected_stat: main.buttons[13].append(Button(374, HEIGHT - 62, 32, 32, "Finish Collectible Type", "Assets/editor/check mark.png", make_collectible_type))
  
  def new_container_type(self):
    if k_back: self.gamestate = 1
    pygame.draw.rect(screen, (0, 0, 50), ((100, 25), (WIDTH - 200, HEIGHT - 50)))
    pygame.draw.rect(screen, "Dark Blue", ((100, 25), (WIDTH - 200, HEIGHT - 50)), width=2)
    screen.blit(fontmedium.render(f"New Container", True, "White"), (103, 32))

  def stat_settings(self):
    self.buttons[15].clear()
    width = 0; height = 0
    for stat in self.game_stats:
      text = fontmedium.render(stat + ",", True, "White")
      if width + 19 + text.get_width() > WIDTH - 90: height += 30; width = 0
      width += text.get_width() + 10
      self.buttons[15].append(Button(35 + width - text.get_width(), 100 + height, text.get_width() + 7, 30, "Select Stat", stat, select_statistic, target=stat, target_object="Stat", text_color={int: "Light blue", bool: "Light Yellow", str: "Pink", float: "Light Green"}[self.game_stats[stat]], button_type="Stat"))
    if self.selected_stat:
      self.buttons[15].append(Button(280, 60, 32, 32, "Rename Stat", "Assets/editor/pencil.png", rename, target=self.selected_stat, target_gs=15, button_type="Specifier")); self.buttons[15].append(Button(314, 60, 32, 32, "Set Initial Mode", "Assets/editor/pencil.png", set_stat_init, target=self.selected_stat, target_gs=15, button_type="Specifier")); self.buttons[15].append(Button(348, 60, 32, 32, "Apply Effect", "Assets/editor/effect.png", set_stat_effect, button_type="Specifier")); self.buttons[15].append(Button(382, 60, 32, 32, "Set Uİ", "Assets/editor/ui.png", set_stat_ui, button_type="Specifier"))
      try:
        if self.game_stats[self.selected_stat] == int or self.game_stats[self.selected_stat] == float: self.buttons[15].append(Button(416, 60, 32, 16, "Set Stat Maximum Range", "Assets/editor/up.png", set_stat_max, button_type="Specifier")); self.buttons[15].append(Button(416, 76, 32, 16, "Set Stat Minimum Range", "Assets/editor/down.png", set_stat_min, button_type="Specifier"))
      except: self.selected_stat = None
    for x, button in enumerate([("Add Integer Stat", "add", add_int_stat), ("Add Boolean Stat", "add", add_bool_stat), ("Add String Stat", "add", add_str_stat), ("Add Float Stat", "add", add_float_stat), ("Delete Stat", "delete", delete_stat)]):
      self.buttons[15].append(Button(60 + (x * 34) + (int(button[1] == "delete") * 50), 60, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2]))
      
    if k_back: self.gamestate = 2
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render(f"General Settings, Player Statistics", True, "White"), (53, 32))
    pygame.draw.rect(screen, (0, 0, 20), ((55, 97), (WIDTH - 110, 325)))
    try:
      screen.blit(fontsmall.render("Begins as " + str(self.game_stats_initpoint[self.selected_stat]) + " | Effect: " + str(self.game_stats_effect[self.selected_stat]), True, "White"), (50, HEIGHT - 20))
      if self.game_stats[self.selected_stat] == int or self.game_stats[self.selected_stat] == float:
        if self.game_stats_range[self.selected_stat][0] < self.game_stats_range[self.selected_stat][1]: screen.blit(fontsmall.render("+ " + str(self.game_stats_range[self.selected_stat][1]) + "   - " + str(self.game_stats_range[self.selected_stat][0]), True, "White"), (400, HEIGHT - 20))
        else: screen.blit(fontsmall.render("+ " + str(self.game_stats_range[self.selected_stat][1]) + "   - " + str(self.game_stats_range[self.selected_stat][0]), True, "Red"), (400, HEIGHT - 20))
    except: pass

  def sfx_library(self):
    global k_back
    if k_back: self.gamestate = self.remember_gs; k_back = False
    for index in range(30):
      if index % 2 == 0: pygame.draw.rect(screen, (0, 0, 50), ((0, 45 + (index * 26)), (WIDTH, 26)))
      else: pygame.draw.rect(screen, (0, 0, 20), ((0, 45 + (index * 26)), (WIDTH, 26)))
    for index, sfx in enumerate(self.sfx[minint(self.selected_itemy - 10, 0):]):
      try:
        if type(sfx) == list:
          if self.sfx[self.selected_itemy] == sfx: screen.blit(fontsmall.render(sfx[0][:-5], True, "Yellow"), (1, 50 + (index * 26)))
          else: screen.blit(fontsmall.render(sfx[0][:-5], True, "White"), (1, 50 + (index * 26)))
        else:
          if self.sfx[self.selected_itemy] == sfx: screen.blit(fontsmall.render(sfx, True, "Yellow"), (1, 50 + (index * 26)))
          else: screen.blit(fontsmall.render(sfx, True, "White"), (1, 50 + (index * 26)))
      except Exception as e: print(e); self.selected_itemy = 0

    room_margin = 250
    pygame.draw.rect(screen, (0, 0, 50), ((WIDTH - room_margin, 0), (room_margin, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((WIDTH - room_margin, 0), (2, HEIGHT)))
    if len(self.sfx):
      try:
        if type(self.sfx[self.selected_itemy]) == list:
          pygame.mixer_music.load(self.active_directory + "Sounds/sfx/" + self.sfx[self.selected_itemy][0])
          song = pygame.mixer.Sound(self.active_directory + "Sounds/sfx/" + self.sfx[self.selected_itemy][0])
          if len(self.sfx[self.selected_itemy][0][:-1]) < 20: screen.blit(fontmedium.render(f"{self.sfx[self.selected_itemy][0][:-5]}", True, "White"), (room_margin + 30, 16))
          elif len(self.sfx[self.selected_itemy][0][:-1]) < 28: screen.blit(fontsmall.render(f"{self.sfx[self.selected_itemy][0][:-5]}", True, "White"), (room_margin + 30, 18))
          elif len(self.sfx[self.selected_itemy][0][:-1]) < 37: screen.blit(fontlittle.render(f"{self.sfx[self.selected_itemy][0][:-5]}", True, "White"), (room_margin + 30, 20))
          else: screen.blit(fontsmaller.render(f"{self.sfx[self.selected_itemy][0][:-1]}", True, "White"), (room_margin + 30, 20))
        else:
          pygame.mixer_music.load(self.active_directory + "Sounds/sfx/" + self.sfx[self.selected_itemy])
          song = pygame.mixer.Sound(self.active_directory + "Sounds/sfx/" + self.sfx[self.selected_itemy])
          if len(self.sfx[self.selected_itemy]) < 20: screen.blit(fontmedium.render(f"{self.sfx[self.selected_itemy]}", True, "White"), (room_margin + 30, 16))
          elif len(self.sfx[self.selected_itemy]) < 28: screen.blit(fontsmall.render(f"{self.sfx[self.selected_itemy]}", True, "White"), (room_margin + 30, 18))
          elif len(self.sfx[self.selected_itemy]) < 37: screen.blit(fontlittle.render(f"{self.sfx[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
          else: screen.blit(fontsmaller.render(f"{self.sfx[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
        total_seconds = round(song.get_length())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        screen.blit(fontsmall.render(f"Length: {minutes}:{seconds:02}", True, "White"), (room_margin + 20, 205))
        screen.blit(pygame.transform.scale(pygame.image.load("Assets/editor/track.png").convert_alpha(), (128, 128)), (room_margin + 32, 64))
      except: screen.blit(fontmedium.render("Select a sound file", True, "White"), (room_margin + 30, 16))
    else: screen.blit(fontmedium.render("No SFXs imported", True, "White"), (room_margin + 30, 16))

    screen.blit(fontmedium.render("SFX Library", True, "White"), (0, 16))
    
    if k_down: self.selected_itemy += 1 + (int(k_y) * 4); scrolldown_sfx.play()
    if k_up: self.selected_itemy -= 1 + (int(k_y) * 4); scrollup_sfx.play()
    if self.selected_itemy < 0: self.selected_itemy = len(self.sfx) - 1
    if self.selected_itemy > len(self.sfx) - 1: self.selected_itemy = 0

  def bg_library(self):
    for index in range(30):
      if index % 2 == 0: pygame.draw.rect(screen, (0, 0, 50), ((0, 45 + (index * 26)), (WIDTH, 26)))
      else: pygame.draw.rect(screen, (0, 0, 20), ((0, 45 + (index * 26)), (WIDTH, 26)))
    for index, background in enumerate(self.backgrounds[minint(self.selected_itemy - 10, 0):]):
      try:
        if self.backgrounds[self.selected_itemy] == background: screen.blit(fontsmall.render(background, True, "Yellow"), (1, 50 + (index * 26)))
        else: screen.blit(fontsmall.render(background, True, "White"), (1, 50 + (index * 26)))
      except: self.selected_itemy = 0

    room_margin = 250
    pygame.draw.rect(screen, (0, 0, 50), ((WIDTH - room_margin, 0), (room_margin, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((WIDTH - room_margin, 0), (2, HEIGHT)))
    if len(self.backgrounds):
      try:
        if os.path.isdir(main.active_directory + "Assets/backgrounds/" + self.backgrounds[self.selected_itemy]):
          self.animated_bg_images = sorted(os.listdir(main.active_directory + "Assets/backgrounds/" + self.backgrounds[self.selected_itemy] + "/"), key=extract_number)
          try: img = pygame.image.load(main.active_directory + "Assets/backgrounds/" + self.backgrounds[self.selected_itemy] + "/" + self.animated_bg_images[self.bg_frame_timer.keep_count(1 + (int(k_y) * 3), len(self.animated_bg_images), 0)]).convert_alpha()
          except IndexError: self.bg_frame_timer.tally = 0; img = pygame.image.load(main.active_directory + "Assets/backgrounds/" + self.backgrounds[self.selected_itemy] + "/" + self.animated_bg_images[0]).convert_alpha()
          if len(self.backgrounds[self.selected_itemy]) < 20: screen.blit(fontmedium.render(f"{self.backgrounds[self.selected_itemy]}", True, "White"), (room_margin + 30, 16))
          elif len(self.backgrounds[self.selected_itemy]) < 28: screen.blit(fontsmall.render(f"{self.backgrounds[self.selected_itemy]}", True, "White"), (room_margin + 30, 18))
          elif len(self.backgrounds[self.selected_itemy]) < 37: screen.blit(fontlittle.render(f"{self.backgrounds[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
          else: screen.blit(fontsmaller.render(f"{self.backgrounds[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
          screen.blit(fontsmall.render(f"Scale: {img.get_width()}:{img.get_height()}", True, "White"), (room_margin + 20, 265))
          screen.blit(fontsmall.render(f"Pitch: {img.get_pitch()}", True, "White"), (room_margin + 20, 295))
          #screen.blit(fontsmall.render(f"Metadata: {img}", True, "White"), (room_margin + 20, 230))
          screen.blit(pygame.transform.scale(img, (WIDTH / 2.42, HEIGHT / 2.42)), (room_margin + 32, 64))
        else:
          img = pygame.image.load(main.active_directory + "Assets/backgrounds/" + self.backgrounds[self.selected_itemy]).convert_alpha()
          if len(self.backgrounds[self.selected_itemy]) < 20: screen.blit(fontmedium.render(f"{self.backgrounds[self.selected_itemy]}", True, "White"), (room_margin + 30, 16))
          elif len(self.backgrounds[self.selected_itemy]) < 28: screen.blit(fontsmall.render(f"{self.backgrounds[self.selected_itemy]}", True, "White"), (room_margin + 30, 18))
          elif len(self.backgrounds[self.selected_itemy]) < 37: screen.blit(fontlittle.render(f"{self.backgrounds[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
          else: screen.blit(fontsmaller.render(f"{self.backgrounds[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
          screen.blit(fontsmall.render(f"Scale: {img.get_width()}:{img.get_height()}", True, "White"), (room_margin + 20, 265))
          screen.blit(fontsmall.render(f"Pitch: {img.get_pitch()}", True, "White"), (room_margin + 20, 295))
          #screen.blit(fontsmall.render(f"Metadata: {img}", True, "White"), (room_margin + 20, 230))
          screen.blit(pygame.transform.scale(img, (WIDTH / 2.42, HEIGHT / 2.42)), (room_margin + 32, 64))
      except Exception as e: screen.blit(fontmedium.render("Select a image file", True, "White"), (room_margin + 30, 16)); print(e)
    else: screen.blit(fontmedium.render("No images imported", True, "White"), (room_margin + 30, 16))

    screen.blit(fontmedium.render("Image Library", True, "White"), (0, 16))

    screen.blit(fontsmall.render(f"Distance {self.selected_value}", True, "White"), (302, 330))
    screen.blit(fontsmall.render(f"X Speed {self.selected_speed[0]}", True, "White"), (302, 375))
    screen.blit(fontsmall.render(f"Y Speed {self.selected_speed[1]}", True, "White"), (302, 420))
    
    if k_down: self.selected_itemy += 1 + (int(k_y) * 4); scrolldown_sfx.play()
    if k_up: self.selected_itemy -= 1 + (int(k_y) * 4); scrollup_sfx.play()
    if self.selected_itemy < 0: self.selected_itemy = len(self.backgrounds) - 1
    if self.selected_itemy > len(self.backgrounds) - 1: self.selected_itemy = 0
    if k_back: self.gamestate = 1

  def bg_options(self):
    if k_back: self.gamestate = 0
    try:
      pygame.draw.rect(screen, (0, 0, 50), ((100, 100), (WIDTH - 200, HEIGHT - 300)))
      pygame.draw.rect(screen, "Dark Blue", ((100, 100), (WIDTH - 200, HEIGHT - 300)), width=2)
      screen.blit(pygame.transform.scale(self.rooms[self.selected_room].backgrounds[self.selected_background].image, (128, 128)), (4, HEIGHT - 132))
      screen.blit(fontsmall.render("İmage File: " + self.rooms[self.selected_room].backgrounds[self.selected_background].image_file, True, "White"), (2, 2))
      screen.blit(fontsmall.render("Background Options", True, "White"), (102, 102))
      screen.blit(fontsmall.render(f"Distance {self.rooms[self.selected_room].backgrounds[self.selected_background].distance}", True, "White"), (140, 160))
      screen.blit(fontsmall.render(f"X Speed {self.rooms[self.selected_room].backgrounds[self.selected_background].speed[0]}", True, "White"), (140, 190))
      screen.blit(fontsmall.render(f"Y Speed {self.rooms[self.selected_room].backgrounds[self.selected_background].speed[1]}", True, "White"), (140, 220))
      screen.blit(fontsmall.render(f"X Pos {self.rooms[self.selected_room].backgrounds[self.selected_background].rect.x}", True, "White"), (302, 190))
      screen.blit(fontsmall.render(f"Y Pos {self.rooms[self.selected_room].backgrounds[self.selected_background].rect.y}", True, "White"), (302, 220))
      screen.blit(fontsmaller.render("X Scroll: " + {True: 'On', False: 'Off'}[self.rooms[self.selected_room].backgrounds[self.selected_background].x_scroll] + ", Y Scroll: " + {True: 'On', False: 'Off'}[self.rooms[self.selected_room].backgrounds[self.selected_background].y_scroll], True, "White"), (100, 80))
      screen.blit(fontsmaller.render("Foreground: " + {True: 'On', False: 'Off'}[self.rooms[self.selected_room].backgrounds[self.selected_background].foreground] + ", HM: " + {True: 'On', False: 'Off'}[self.rooms[self.selected_room].backgrounds[self.selected_background].hm_for_move] + ", VM: " + {True: 'On', False: 'Off'}[self.rooms[self.selected_room].backgrounds[self.selected_background].vm_for_move], True, "White"), (100, 90))
      for button in (button for button in self.buttons[18] if "Marge" in button.text or "Animation" in button.text): self.buttons[18].remove(button)
      if self.rooms[self.selected_room].backgrounds[self.selected_background].repeat_x:
        for x, button in enumerate([("Decrease X Marge", "less", change_x_marge_bg, -5), ("İncrease X Marge", "more", change_x_marge_bg, 5)]):
          self.buttons[18].append(Button(106 + (x * 132), HEIGHT - 186, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
        screen.blit(fontsmall.render(f"X Marge {self.rooms[self.selected_room].backgrounds[self.selected_background].marges[0]}", True, "White"), (140, 270))
      if self.rooms[self.selected_room].backgrounds[self.selected_background].repeat_y:
        for x, button in enumerate([("Decrease Y Marge", "less", change_y_marge_bg, -5), ("İncrease Y Marge", "more", change_y_marge_bg, 5)]):
          self.buttons[18].append(Button(269 + (x * 132), HEIGHT - 186, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
        screen.blit(fontsmall.render(f"Y Marge {self.rooms[self.selected_room].backgrounds[self.selected_background].marges[1]}", True, "White"), (302, 270))
      if self.rooms[self.selected_room].backgrounds[self.selected_background].is_animating:
        for x, button in enumerate([("Decrease Animation Speed", "less", change_animation_speed, -0.5), ("İncrease Animation Speed", "more", change_animation_speed, 0.5)]):
          self.buttons[18].append(Button(269 + (x * 132), HEIGHT - 154, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3]))
        screen.blit(fontlittle.render(f"Frame Rate {main.rooms[main.selected_room].backgrounds[main.selected_background].anim_speed}", True, "White"), (302, 302))
      
      x_poses = []
      for button in (button for button in self.buttons[18] if "Marge" in button.text):
        if round(button.rect.x / 4) in x_poses: self.buttons[18].remove(button)
        x_poses.append(round(button.rect.x / 4))
    except: self.gamestate = 0

  def edit_player(self):
    if k_back: self.gamestate = 0
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render("Player " + str(main.selected_object.player_index + 1) + " Customizations", True, "White"), (53, 32))
    screen.blit(fontsmall.render("X Spawn " + str(self.selected_object.spawn_location[0]), True, "White"), (98, 75))
    screen.blit(fontsmall.render("Y Spawn " + str(self.selected_object.spawn_location[1]), True, "White"), (98, 115))
    screen.blit(fontsmall.render("Team " + str(self.selected_object.team), True, "White"), (98, 155))
    screen.blit(fontsmaller.render({True: "On", False: "Off"}[self.selected_object.in_spawn], True, "White"), (56, HEIGHT - 66))
    screen.blit(fontsmaller.render({True: "On", False: "Off"}[self.selected_object.hide_if_out], True, "White"), (90, HEIGHT - 66))
    screen.blit(fontsmaller.render({True: "On", False: "Off"}[self.selected_object.bump_cancel_momentum], True, "White"), (WIDTH - 118, HEIGHT - 66))
    screen.blit(fontsmaller.render({True: "On", False: "Off"}[self.selected_object.accelerated_travel], True, "White"), (WIDTH - 84, HEIGHT - 66))

  def edit_tile(self):
    if k_back: self.gamestate = 0
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render(f"Tile Customizations", True, "White"), (53, 32))
    #if self.selected_object.is_animating: screen.blit(fontsmall.render(f"Frame Rate {self.selected_object.anim_speed}", True, "White"), ((WIDTH / 2) + 42, 35))
    screen.blit(fontsmall.render(f"X {self.selected_object.rect.x}", True, "White"), (98, 75))
    screen.blit(fontsmall.render(f"Y {self.selected_object.rect.y}", True, "White"), (98, 115))
    screen.blit(fontsmall.render(f"X Speed {self.selected_object.speed[0]}", True, "White"), (98, 155))
    screen.blit(fontsmall.render(f"Y Speed {self.selected_object.speed[1]}", True, "White"), (98, 195))
    if self.selected_object.chain_speed != 0: screen.blit(fontlittle.render(f"Chain Speed {self.selected_object.chain_speed}", True, "White"), (95, 238))
    else: screen.blit(fontsmall.render(f" No Chain", True, "White"), (98, 235))
    screen.blit(fontsmaller.render({True: "On", False: "Off"}[self.selected_object.zones_can_move], True, "White"), (260, 74))
    screen.blit(fontsmaller.render({True: "On", False: "Off"}[self.selected_object.zones_can_rotate], True, "White"), (260, 114))
    for y, text in enumerate(({True: "Only Breakable by Chain Break", False: "Breakable (Depending on Tile Type's Settings)"}[self.selected_object.only_breakable_by_chains], {True: "Solidity is Set to its Tile Type", False: "Solidity is Different from its Tile Type"}[not "s" in self.selected_object.deviating_modes], {True: "Flatness is Set to its Tile Type", False: "Flatness is Different from its Tile Type"}[not "f" in self.selected_object.deviating_modes], {True: "Slipperiness is Set to its Tile Type", False: "Slipperiness is Different from its Tile Type"}[not "sl" in self.selected_object.deviating_modes])): screen.blit(fontsmaller.render(text, True, "White"), (98, 275 + (y * 34)))

  def edit_collectible(self):
    if k_back: self.gamestate = 0
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render("Collectible Customizations", True, "White"), (53, 32))
    screen.blit(fontsmall.render(f"X {self.selected_object.rect.x}", True, "White"), (98, 75))
    screen.blit(fontsmall.render(f"Y {self.selected_object.rect.y}", True, "White"), (98, 115))
    screen.blit(fontsmall.render(f"X Speed {self.selected_object.speed[0]}", True, "White"), (98, 155))
    screen.blit(fontsmall.render(f"Y Speed {self.selected_object.speed[1]}", True, "White"), (98, 195))
    screen.blit(fontsmaller.render({True: "On", False: "Off"}[self.selected_object.zones_can_move], True, "White"), (260, 74))
    screen.blit(fontsmaller.render({True: "On", False: "Off"}[self.selected_object.zones_can_rotate], True, "White"), (260, 114))
  
  def edit_zone(self):
    if k_back: self.gamestate = 0
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render(f"Zone Customizations", True, "White"), (53, 32))
    screen.blit(fontsmall.render(f"X {self.selected_object.rect.x}", True, "White"), (98, 65))
    screen.blit(fontsmall.render(f"Y {self.selected_object.rect.y}", True, "White"), (98, 105))
    screen.blit(fontsmall.render(f"Width {self.selected_object.rect.width}", True, "White"), (98, 145))
    screen.blit(fontsmall.render(f"Height {self.selected_object.rect.height}", True, "White"), (98, 185))
    screen.blit(fontsmall.render("Volume " + "{:.1f}".format(self.selected_object.track_volume), True, "White"), (92, 228))
    screen.blit(fontsmall.render(f"Tile X Speed {self.selected_object.tile_speed[0]}", True, "White"), (288, 65))
    screen.blit(fontsmall.render(f"Tile Y Speed {self.selected_object.tile_speed[1]}", True, "White"), (288, 105))
    screen.blit(fontsmall.render(f"Tile Rotation {self.selected_object.tile_rotation}", True, "White"), (288, 145))
    screen.blit(fontsmaller.render({True: "On", False: "Off"}[self.selected_object.ease_motion], True, "White"), (258, 215))
    screen.blit(fontsmall.render(f"Gravity {round(self.selected_object.gravity, 1)}", True, "White"), (335, 189))
    if type(self.selected_object.enter_sound) == list: screen.blit(fontsmall.render("Enter SFX " + self.selected_object.enter_sound[0][:-5], True, "White"), (106, HEIGHT - 94))
    else: screen.blit(fontsmall.render("Enter SFX " + self.selected_object.enter_sound, True, "White"), (106, HEIGHT - 94))
    if type(self.selected_object.exit_sound) == list: screen.blit(fontsmall.render("Exit SFX " + self.selected_object.exit_sound[0][:-5], True, "White"), (106, HEIGHT - 62))
    else: screen.blit(fontsmall.render("Exit SFX " + self.selected_object.exit_sound, True, "White"), (106, HEIGHT - 62))
    screen.blit(fontsmall.render("Multi-Active: " + {True: "On", False: "Off"}[self.selected_object.multi_active], True, "White"), (106, HEIGHT - 126))
    screen.blit(fontsmall.render("Actor Friendly: " + {True: "On", False: "Off"}[self.selected_object.entity_active], True, "White"), (106, HEIGHT - 158))
    screen.blit(fontsmall.render("Void: " + {True: "On", False: "Off"}[self.selected_object.void], True, "White"), (106, HEIGHT - 190))
    if self.selected_object.multi_active and self.selected_object.entity_active: screen.blit(fontsmaller.render("Both Multi-Active and Actor Friendly or multiple subjects (multiplayer) on ON causes issues", True, "Red"), (2, HEIGHT - 15))
  
  def edit_entity(self):
    if k_back: self.gamestate = 0
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render(f"Entity Customizations", True, "White"), (53, 32))
    # if type(self.selected_object.jump_sound) == list: screen.blit(fontsmall.render("Jump SFX " + self.selected_object.jump_sound[0][:-5], True, "White"), (106, HEIGHT - 222))
    # else: screen.blit(fontsmall.render("Jump SFX " + self.selected_object.jump_sound, True, "White"), (106, HEIGHT - 222))
    # if type(self.selected_object.land_sound) == list: screen.blit(fontsmall.render("Land SFX " + self.selected_object.land_sound[0][:-5], True, "White"), (106, HEIGHT - 190))
    # else: screen.blit(fontsmall.render("Land SFX " + self.selected_object.land_sound, True, "White"), (106, HEIGHT - 190))
    # if type(self.selected_object.defeat_sound) == list: screen.blit(fontsmall.render("Defeat SFX " + self.selected_object.defeat_sound[0][:-5], True, "White"), (106, HEIGHT - 158))
    # else: screen.blit(fontsmall.render("Defeat SFX " + self.selected_object.defeat_sound, True, "White"), (106, HEIGHT - 158))
    # if type(self.selected_object.trap_sound) == list: screen.blit(fontsmall.render("Trap SFX " + self.selected_object.trap_sound[0][:-5], True, "White"), (106, HEIGHT - 126))
    # else: screen.blit(fontsmall.render("Trap SFX " + self.selected_object.trap_sound, True, "White"), (106, HEIGHT - 126))
    # if type(self.selected_object.notice_sound) == list: screen.blit(fontsmall.render("Notice SFX " + self.selected_object.notice_sound[0][:-5], True, "White"), (106, HEIGHT - 92))
    # screen.blit(fontsmall.render("Notice SFX " + self.selected_object.notice_sound, True, "White"), (106, HEIGHT - 92))
    # if type(self.selected_object.speech_sound) == list: screen.blit(fontsmall.render("Speech SFX " + self.selected_object.speech_sound[0][:-5], True, "White"), (106, HEIGHT - 62))
    # screen.blit(fontsmall.render("Speech SFX " + self.selected_object.speech_sound, True, "White"), (106, HEIGHT - 62))

  
  def edit_cutscene(self, dt=1):
    dt *= 60
    if k_back: self.gamestate = 0; self.selected_object = None; stop_playtest(None)
    if k_r: self.selected_key += 1 + (int(k_y) * 20); switch_key_sfx.play()
    if k_l: self.selected_key -= 1 + (int(k_y) * 20); switch_key_sfx.play()
    if self.selected_key < 0: self.selected_key = 4999
    if self.selected_key > 4999: self.selected_key = 0
    self.current_room = self.selected_room
    if self.playback_on:
      self.camera.camera_scene(dt)
      delay = 10
      for key in self.rooms[self.selected_room].cutscenes[self.selected_cutscene].animations:
        if key["Frame"] == self.selected_key and self.frame_timer.time == 1:
          if key["Object"] == "Main":
            if key["Track"] and key["Track"] != "Stop": pygame.mixer.music.load(self.active_directory + "Sounds/tracks/" + key["Track"]); pygame.mixer.music.play(-1, 0.0)
            elif key["Track"] == "Stop": pygame.mixer.music.stop()
            try:
              if key["Dir"]: pygame.mixer.music.load(self.active_directory + "Sounds/tracks/" + key["Dir"]); pygame.mixer.music.play(1, 0.0); self.track = key["Dir"]
            except FileNotFoundError: pass
            if key["SFX"]:
              if type(key["SFX"]) == list: pygame.mixer.Sound(self.active_directory + "Sounds/sfx/" + key["SFX"][random.randrange(0, len(key["SFX"]))]).play()
              else: pygame.mixer.Sound(self.active_directory + "Sounds/sfx/" + key["SFX"]).play()
        if key["Frame"] == self.selected_key:
          if key["Object"] == "Main": delay = key["Rotate"]
      if delay != 0:
        if self.frame_timer.timer(delay * dt): self.selected_key += 1

    self.rooms[self.selected_room].render_backgrounds(screen, cutscene=True)
    for layer in self.rooms[self.selected_room].layers[::-1]: layer.render_tiles(screen, cutscene=True); layer.render_texts(screen, cutscene=True); layer.render_collectibles(screen, cutscene=True); layer.render_entities(screen, cutscene=True) #renders the tiles and coins for every layer (::-1 means reverse)
    for door in self.rooms[self.selected_room].doors: door.update(screen)
    for player in self.players: player.display(screen, cutscene=True)
    for zone in self.rooms[self.selected_room].zones: zone.draw(screen)
    self.rooms[self.selected_room].render_backgrounds(screen, bg=False)
    for layer in self.rooms[self.selected_room].layers[::-1]: layer.render_texts(screen, self.playback_on, front=True)
    self.camera.render_preview(screen)

    #for key_object in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].keys[main.selected_key].animations:
    #  if key_object["Frame"] <= main.selected_key and type(key_object["Object"]).__name__ != "Camera": print(key_object)

    # DİSPLAY SELECTİON
    if type(self.selected_object) == Zone: self.selected_object = None
    if self.selected_object != None: pygame.draw.rect(screen, "Green", ((self.selected_object.key_frame_rect.x - self.camera.scroll[0], self.selected_object.key_frame_rect.y - self.camera.scroll[1]), (self.selected_object.key_frame_rect.width, self.selected_object.key_frame_rect.height)), 1)

    self.manage_buttons(self.buttons)
    try: self.top_tiles = self.rooms[self.selected_room].layers[0].tiles
    except: self.top_tiles = []
    try: self.top_collectibles = self.rooms[self.selected_room].layers[0].collectibles
    except: self.top_collectibles = []
    try: self.top_actors = self.rooms[self.selected_room].layers[0].actors
    except: self.top_actors = []
    texts = []
    for layer in self.rooms[self.selected_room].layers:
      for text in layer.texts: texts.append(text)
    if not self.hover_on_button:
      combined = self.players + self.rooms[self.selected_room].zones + texts + self.top_tiles + self.top_collectibles + self.top_actors + self.rooms[self.selected_room].doors + self.rooms[self.selected_room].backgrounds + [self.camera]
      if self.selected_object != None and self.selected_object in combined: combined.remove(self.selected_object)
      for object in combined:
        if pygame.mouse.get_pos()[0] > object.key_frame_rect.left - self.camera.scroll[0] and pygame.mouse.get_pos()[0] < object.key_frame_rect.right - self.camera.scroll[0] and pygame.mouse.get_pos()[1] > object.key_frame_rect.top - self.camera.scroll[1] and pygame.mouse.get_pos()[1] < object.key_frame_rect.bottom - self.camera.scroll[1]:
          if k_a: self.selected_object = object; break
        elif k_a: self.selected_object = None
    if k_b: self.selected_object = None
    
    for anim in self.rooms[self.selected_room].cutscenes[self.selected_cutscene].animations:
      if anim["Frame"] >= self.last_frame_active: self.last_frame_active = anim["Frame"]
    
    if type(self.selected_object).__name__ != "NoneType":
      so = f"Selected Object: {type(self.selected_object).__name__}"
      if k_left: self.camera.scroll[0] -= 2
      if k_right: self.camera.scroll[0] += 2
      if k_up: self.camera.scroll[1] -= 2
      if k_down: self.camera.scroll[1] += 2 #for scrolling controls
    else:
      self.display_buttons = True
      if k_left: self.camera.scroll[0] -= 3
      if k_right: self.camera.scroll[0] += 3
      if k_up: self.camera.scroll[1] -= 3
      if k_down: self.camera.scroll[1] += 3 #for scrolling controls
      so = "No object selected"
    screen.blit(fontsmaller.render(f"Current Room: {self.rooms[self.selected_room].name} | Scroll X: {self.camera.scroll[0]} | Scroll Y: {self.camera.scroll[1]} | At Key {self.selected_key}", True, "White"), (2, 16))
    screen.blit(fontsmaller.render(f"Current Cutscene: {self.rooms[self.selected_room].cutscenes[self.selected_cutscene].name} | {so}", True, "White"), (2, 2))

    for object in self.players + self.rooms[self.selected_room].zones + texts + self.top_tiles + self.top_collectibles + self.top_actors + self.rooms[self.selected_room].doors + self.rooms[self.selected_room].backgrounds + [self.camera]:
      for anim in self.rooms[self.selected_room].cutscenes[self.selected_cutscene].animations:
        if anim["Frame"] == self.selected_key and isinstance(anim["Object"], Camera) and anim["Object"] == object and anim["I1"] != -1: pygame.draw.rect(screen, "Green", ((object.key_frame_rect.x - self.camera.scroll[0], object.key_frame_rect.y - self.camera.scroll[1] - -5), (object.key_frame_rect.width, 4)), border_radius=2)
        if anim["Frame"] == self.selected_key and isinstance(anim["Object"], Camera) and anim["Object"] == object and anim["I2"] != -1: pygame.draw.rect(screen, "Green", ((object.key_frame_rect.right - self.camera.scroll[0] - 9, object.key_frame_rect.y - self.camera.scroll[1]), (4, object.key_frame_rect.height)), border_radius=2)
        if anim["Frame"] == self.selected_key and isinstance(anim["Object"], Camera) and anim["Object"] == object and anim["I3"] != -1: pygame.draw.rect(screen, "Green", ((object.key_frame_rect.x - self.camera.scroll[0], object.key_frame_rect.bottom - self.camera.scroll[1] - 9), (object.key_frame_rect.width, 4)), border_radius=2)
        if anim["Frame"] == self.selected_key and isinstance(anim["Object"], Camera) and anim["Object"] == object and anim["I4"] != -1: pygame.draw.rect(screen, "Green", ((object.key_frame_rect.x - self.camera.scroll[0] - -5, object.key_frame_rect.y - self.camera.scroll[1]), (4, object.key_frame_rect.height)), border_radius=2)
        if anim["Frame"] == self.selected_key and isinstance(anim["Object"], Camera) and anim["Object"] == object and anim["B1"]: pygame.draw.rect(screen, "Cyan", ((object.key_frame_rect.right - self.camera.scroll[0], object.key_frame_rect.y - self.camera.scroll[1]), (2, object.key_frame_rect.height))); pygame.draw.rect(screen, "Cyan", ((object.key_frame_rect.x - self.camera.scroll[0], object.key_frame_rect.y - self.camera.scroll[1]), (2, object.key_frame_rect.height)))
        if anim["Frame"] == self.selected_key and isinstance(anim["Object"], Camera) and anim["Object"] == object and anim["B2"]: pygame.draw.rect(screen, "Cyan", ((object.key_frame_rect.x - self.camera.scroll[0], object.key_frame_rect.y - self.camera.scroll[1]), (object.key_frame_rect.width, 2))); pygame.draw.rect(screen, "Cyan", ((object.key_frame_rect.x - self.camera.scroll[0], object.key_frame_rect.bottom - self.camera.scroll[1]), (object.key_frame_rect.width, 2)))
        if anim["Frame"] == self.selected_key and isinstance(anim["Object"], Camera) and anim["Object"] == object and anim["Hidden"]:
          pygame.draw.rect(screen, "Red", ((object.key_frame_rect.x - self.camera.scroll[0] - -15, object.key_frame_rect.y - self.camera.scroll[1] - -15), (25, 2)))
          pygame.draw.rect(screen, "Red", ((object.key_frame_rect.x - self.camera.scroll[0] - -15, object.key_frame_rect.y - self.camera.scroll[1] - -15), (2, 25)))
          pygame.draw.rect(screen, "Red", ((object.key_frame_rect.right - self.camera.scroll[0] - 40, object.key_frame_rect.y - self.camera.scroll[1] - -15), (25, 2)))
          pygame.draw.rect(screen, "Red", ((object.key_frame_rect.right - self.camera.scroll[0] - 15, object.key_frame_rect.y - self.camera.scroll[1] - -15), (2, 25)))
          pygame.draw.rect(screen, "Red", ((object.key_frame_rect.right - self.camera.scroll[0] - 40, object.key_frame_rect.bottom - self.camera.scroll[1] - 15), (25, 2)))
          pygame.draw.rect(screen, "Red", ((object.key_frame_rect.right - self.camera.scroll[0] - 15, object.key_frame_rect.bottom - self.camera.scroll[1] - 40), (2, 27)))
          pygame.draw.rect(screen, "Red", ((object.key_frame_rect.x - self.camera.scroll[0] - -15, object.key_frame_rect.bottom - self.camera.scroll[1] - 15), (25, 2)))
          pygame.draw.rect(screen, "Red", ((object.key_frame_rect.x - self.camera.scroll[0] - -15, object.key_frame_rect.bottom - self.camera.scroll[1] - 40), (2, 27)))
        if anim["Frame"] == self.selected_key and anim["Object"] == object and anim["Rect"] != None:
          pygame.draw.rect(screen, "Yellow", ((object.key_frame_rect.x - self.camera.scroll[0] - 4, object.key_frame_rect.y - self.camera.scroll[1] - 4), (8, 8)), border_radius=4)
          #if anim["Hidden"]: pygame.draw.rect(screen, "Red", ((object.key_frame_rect.x - self.camera.scroll[0] - 4, object.key_frame_rect.y - self.camera.scroll[1] - 4), (4, 4)), border_radius=2)
          #else: pygame.draw.rect(screen, "Green", ((object.key_frame_rect.x - self.camera.scroll[0] - 4, object.key_frame_rect.y - self.camera.scroll[1] - 4), (4, 4)), border_radius=2)
        if anim["Frame"] == self.selected_key and anim["Object"] == object and (anim["X Speed"] != 0 or anim["Y Speed"] != 0): pygame.draw.rect(screen, "Yellow", (((object.key_frame_rect.x + object.key_frame_rect.width) - self.camera.scroll[0] - 4, object.key_frame_rect.y - self.camera.scroll[1] - 4), (8, 8)), border_radius=4)
        if anim["Frame"] == self.selected_key and anim["Object"] == object and anim["Action"] != "": pygame.draw.rect(screen, "Yellow", ((object.key_frame_rect.x - self.camera.scroll[0] - 4, (object.key_frame_rect.y + object.rect.height) - self.camera.scroll[1] - 4), (8, 8)), border_radius=4)

    for index, key in enumerate(self.rooms[self.selected_room].cutscenes[self.selected_cutscene].keys[minint(self.selected_key - 20, 0):][:32]):
      if self.selected_key == key.frame:
        pygame.draw.rect(screen, (0, 0, 100), ((index * 16, HEIGHT - 16), (16, 16)))
        pygame.draw.rect(screen, "Blue", ((index * 16, HEIGHT - 16), (16, 16)), 1)
        pygame.draw.rect(screen, (50, 50, 255), ((index * 16, HEIGHT - 16), (16, 16)), 1, 8)
        pygame.draw.rect(screen, (100, 100, 255), (((index * 16) + 4, (HEIGHT - 16) + 4), (16 - 8, 16 - 8)), border_radius=4)
      else:
        pygame.draw.rect(screen, (0, 0, 50), ((index * 16, HEIGHT - 16), (16, 16)))
        pygame.draw.rect(screen, "Blue", ((index * 16, HEIGHT - 16), (16, 16)), 1)
        if self.last_frame_active >= key.frame: pygame.draw.rect(screen, "Blue", ((index * 16, HEIGHT - 16), (16, 16)), 1, 8)
      for anim in self.rooms[self.selected_room].cutscenes[self.selected_cutscene].animations:
        if anim["Frame"] == key.frame and anim["Object"] == "Main" and anim["SFX"]: pygame.draw.rect(screen, "Yellow", ((index * 16, HEIGHT - 2), (8, 2)), 1)
        if anim["Frame"] == key.frame and anim["Object"] == "Main" and anim["Track"]: pygame.draw.rect(screen, "Yellow", (((index * 16) + 8, HEIGHT - 2), (8, 2)), 1)
        if anim["Frame"] == key.frame and anim["Object"] == "Main" and not anim["Hidden"]: pygame.draw.rect(screen, "Green", ((index * 16, HEIGHT - 16), (2, 8)))
        if anim["Frame"] == key.frame and anim["Object"] == "Main" and anim["Hidden"]: pygame.draw.rect(screen, "Red", ((index * 16, HEIGHT - 16), (2, 8)))
        if anim["Frame"] == key.frame and anim["Object"] == "Main" and anim["SOCR"]: pygame.draw.rect(screen, "White", (((index * 16) + 5, HEIGHT - 11), (6, 6)), border_radius=3)
      if key.frame % 5 == 0: screen.blit(fontsmaller.render(str(key.frame), True, "White"), (index * 16, HEIGHT - 28))


  def new_entity_type_2(self):
    if k_back: self.gamestate = 12
    pygame.draw.rect(screen, (0, 0, 50), ((50, 25), (WIDTH - 100, HEIGHT - 50)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 25), (WIDTH - 100, HEIGHT - 50)), width=2)
    screen.blit(fontmedium.render("New Entity Page 2", True, "White"), (56, 32))
    screen.blit(fontsmall.render(f"Speed {self.selected_speed[0]}", True, "White"), (98, 75))
    screen.blit(fontsmall.render(f"Leap {self.selected_speed[1]}", True, "White"), (98, 115))
    screen.blit(fontsmall.render(f"Range {self.selected_range}", True, "White"), (98, 155))
    screen.blit(fontsmall.render(f"Health {self.selected_hp}", True, "White"), (98, 195))
    screen.blit(fontmedium.render("Defeat Animation", True, "White"), (270, 70))
    screen.blit(fontmedium.render("Sound Effects", True, "White"), (56, 234))
    if type(self.selected_sfx) == list: screen.blit(fontsmall.render("Jump SFX " + self.selected_sfx[0][:-5], True, "White"), (106, HEIGHT - 190))
    else: screen.blit(fontsmall.render("Jump SFX " + self.selected_sfx, True, "White"), (106, HEIGHT - 190))
    if type(self.selected_sfx2) == list: screen.blit(fontsmall.render("Land SFX " + self.selected_sfx2[0][:-5], True, "White"), (106, HEIGHT - 158))
    else: screen.blit(fontsmall.render("Land SFX " + self.selected_sfx2, True, "White"), (106, HEIGHT - 158))
    if type(self.selected_sfx3) == list: screen.blit(fontsmall.render("Defeat SFX " + self.selected_sfx3[0][:-5], True, "White"), (106, HEIGHT - 126))
    else: screen.blit(fontsmall.render("Defeat SFX " + self.selected_sfx3, True, "White"), (106, HEIGHT - 126))
    if type(self.selected_sfx4) == list: screen.blit(fontsmall.render("Trap SFX " + self.selected_sfx4[0][:-5], True, "White"), (106, HEIGHT - 94))
    else: screen.blit(fontsmall.render("Trap SFX " + self.selected_sfx4, True, "White"), (106, HEIGHT - 94))
    if type(self.selected_sfx5) == list: screen.blit(fontsmall.render("Notice SFX " + self.selected_sfx5[0][:-5], True, "White"), (106, HEIGHT - 62))
    else: screen.blit(fontsmall.render("Notice SFX " + self.selected_sfx5, True, "White"), (106, HEIGHT - 62))

  def new_entity_type_3(self):
    if k_back: self.gamestate = 25
    pygame.draw.rect(screen, (0, 0, 50), ((50, 25), (WIDTH - 100, HEIGHT - 50)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 25), (WIDTH - 100, HEIGHT - 50)), width=2)
    screen.blit(fontmedium.render("New Entity Page 3", True, "White"), (56, 32))
    screen.blit(fontmedium.render("On Defeat, Grant", True, "White"), (60, 85))
    screen.blit(fontsmall.render(f"Value {self.selected_value}", True, "White"), (130, 118))
    screen.blit(fontmedium.render("Drops", True, "White"), (56, 300))

  def brush_mode_ea(self):
    if k_back: self.gamestate = 7
    render_grid()
    for layer in self.rooms[self.selected_room].layers[::-1]: layer.render_tiles(screen)
    for layer in self.rooms[self.selected_room].layers[::-1]: layer.render_collectibles(screen)
    for layer in self.rooms[self.selected_room].layers[::-1]: layer.render_entities(screen)
    
    mouse_pos = [pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]]
    xp, yp = snapint((mouse_pos[0] + self.camera.scroll[0]) - (main.tiles_size / 2), main.tiles_size), snapint((mouse_pos[1] + self.camera.scroll[1]) - (main.tiles_size / 2), main.tiles_size)
    try:
      if k_a and mouse_pos[1] > 100 and self.selected_tile != ():
        place_possible = True
        for actor in self.rooms[self.selected_room].layers[self.selected_layer].actors:
          if self.selected_tile[0] == actor.name and not (actor.rect.x != xp or actor.rect.y != yp): place_possible = False
        if place_possible:
          try: self.rooms[self.selected_room].layers[self.selected_layer].actors.append(Entity(xp, yp, self.selected_tile[3], main, fontsmall, 24))
          except: pass
    except: pass
    if k_b and mouse_pos[1] > 100:
      eraser_rect = pygame.Rect(((mouse_pos[0] - (self.tiles_size / 2), mouse_pos[1] - (self.tiles_size / 2)), (self.tiles_size / 1.5, self.tiles_size / 1.5)))
      pygame.draw.rect(screen, "Dark Red", eraser_rect, border_radius=self.tiles_size // 4)
      for actor in [actor for actor in self.rooms[self.selected_room].layers[self.selected_layer].actors if pygame.Rect((actor.rect.x - self.camera.scroll[0], actor.rect.y - self.camera.scroll[1]), (actor.rect.width, actor.rect.height)).colliderect(eraser_rect)]: self.rooms[self.selected_room].layers[self.selected_layer].actors.remove(actor)

    if k_left: self.camera.scroll[0] -= 4 + (int(k_y) * 5)
    if k_right: self.camera.scroll[0] += 4 + (int(k_y) * 5)
    if k_up: self.camera.scroll[1] -= 4 + (int(k_y) * 5)
    if k_down: self.camera.scroll[1] += 4 + (int(k_y) * 5)

    pygame.draw.rect(screen, (0, 0, 50), ((0, 0), (WIDTH, 100)))
    pygame.draw.rect(screen, "Dark Blue", ((0, 0), (WIDTH, 100)), width=2)
    screen.blit(fontsmall.render(f"Editing Layer {self.rooms[self.selected_room].layers[self.selected_layer].label} {self.rooms[self.selected_room].layers[self.selected_layer].name}   Room {self.rooms[self.selected_room].name}, Actor Mode", True, "White"), (3, 3))
    try:
      screen.blit(fontsmall.render(f"Selected Actor {self.selected_tile[0]}, index {self.selected_tile[2]}", True, "White"), (3, 80))
    except: screen.blit(fontsmall.render(f"No Actor Selected...", True, "White"), (3, 80))

  def game_style(self):
    if k_back: self.gamestate = 2
    pygame.draw.rect(screen, (0, 0, 50), ((100, 100), (WIDTH - 200, HEIGHT - 300)))
    pygame.draw.rect(screen, "Dark Blue", ((100, 100), (WIDTH - 200, HEIGHT - 300)), width=2)
    screen.blit(fontsmall.render(l[lg]["Set Game Style"], True, "White"), (102, 102))
    screen.blit(fontsmall.render(f"Smoothness", True, "White"), (140, 220))
    
  def set_background_to(self):
    global k_back
    if k_back:
      if type(self.selected_object) == Background: self.gamestate = 18; k_back = False
      if type(self.selected_object) == Text: self.gamestate = 43; k_back = False
    pygame.draw.rect(screen, (0, 0, 50), ((25, 25), (WIDTH - 50, HEIGHT - 50)))
    pygame.draw.rect(screen, "Dark Blue", ((25, 25), (WIDTH - 50, HEIGHT - 50)), width=2)
    if type(self.selected_object) == Background:
      screen.blit(fontmedium.render("Set Background To", True, "White"), (30, 30))
    if type(self.selected_object) == Text:
      screen.blit(fontmedium.render("Set Text To", True, "White"), (30, 30))
    screen.blit(fontsmaller.render({False: "Player ", True: "Team "}[self.selected_object.player_or_team] + str(self.selected_object.take_index + 1), True, "White"), (225, 52))
    screen.blit(fontsmall.render("Before Character String: " + self.selected_object.character_string[0], True, "White"), (30, 100))
    screen.blit(fontsmall.render("After Character String: " + self.selected_object.character_string[1], True, "White"), (30, 120))
    screen.blit(fontsmaller.render({False: "Off", True: "On"}[self.selected_object.take_variable], True, "White"), (38, 173))

  def application_settings(self):
    if k_back: self.gamestate = 2
    pygame.draw.rect(screen, (0, 0, 50), ((100, 100), (WIDTH - 200, HEIGHT - 185)))
    pygame.draw.rect(screen, "Dark Blue", ((100, 100), (WIDTH - 200, HEIGHT - 185)), width=2)
    screen.blit(fontsmall.render("Display Settings", True, "White"), (102, 102))
    screen.blit(fontlittle.render(l[lg]["Use DT: "] + {False: "Off", True: "On"}[self.use_dt], True, "White"), (300, 106))
    screen.blit(fontsmall.render(str(main.width), True, "White"), (275, 140))
    screen.blit(fontsmall.render(str(main.height), True, "White"), (275, 180))
    screen.blit(fontsmall.render(str(main.fps), True, "White"), (275, 220))
    screen.blit(fontsmall.render(main.publisher, True, "White"), (203, 320)) #-40
    screen.blit(fontsmall.render("Title: " + main.game_name, True, "Dark Gray"), (118, 280))

  def save_manager(self):
    for index in range(30):
      if index % 2 == 0: pygame.draw.rect(screen, (0, 0, 50), ((0, 45 + (index * 26)), (WIDTH, 26)))
      else: pygame.draw.rect(screen, (0, 0, 20), ((0, 45 + (index * 26)), (WIDTH, 26)))
    for index, save in enumerate(self.saves[minint(self.selected_itemy - 10, 0):]):
      try:
        if save == self.saves[self.selected_itemy]: screen.blit(fontsmall.render(save, True, "Yellow"), (1, 50 + (index * 26)))
        else: screen.blit(fontsmall.render(save, True, "White"), (1, 50 + (index * 26)))
      except: self.selected_itemy = 0

    #try: actor_count = len(self.saves[self.selected_itemy].layers[0].actors)
    #except: actor_count = 0

    room_margin = 250
    pygame.draw.rect(screen, (0, 0, 50), ((WIDTH - room_margin, 0), (room_margin, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((WIDTH - room_margin, 0), (2, HEIGHT))); pygame
    try:
      if len(self.saves[self.selected_itemy]) < 20: screen.blit(fontmedium.render(f"{self.saves[self.selected_itemy]}", True, "White"), (room_margin + 30, 16))
      elif len(self.saves[self.selected_itemy]) < 28: screen.blit(fontsmall.render(f"{self.saves[self.selected_itemy]}", True, "White"), (room_margin + 30, 18))
      elif len(self.saves[self.selected_itemy]) < 37: screen.blit(fontlittle.render(f"{self.saves[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
      else: screen.blit(fontsmaller.render(f"{self.saves[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
      if os.path.isdir(f"Saves/games/{self.saves[self.selected_itemy]}"): screen.blit(fontsmall.render("Size: " + str(os.path.getsize(f"Saves/games/{self.saves[self.selected_itemy]}/{self.saves[self.selected_itemy]}") / 1000000) + " megabytes", True, "White"), (room_margin + 30, 220))
      else: screen.blit(fontsmall.render("Size: " + str(os.path.getsize(f"Saves/games/{self.saves[self.selected_itemy]}") / 1000000) + " megabytes", True, "White"), (room_margin + 30, 220))
      screen.blit(fontsmall.render("Last Accessed:\n  " + str(last_access_time(os.stat(f"Saves/games/{self.saves[self.selected_itemy]}").st_atime)), True, "White"), (room_margin + 30, 250))
      screen.blit(fontsmall.render("Last Modified:\n  " + str(last_access_time(os.stat(f"Saves/games/{self.saves[self.selected_itemy]}").st_mtime)), True, "White"), (room_margin + 30, 300))
      screen.blit(fontsmall.render("Hardlinks Pointing to This: " + str(os.stat(f"Saves/games/{self.saves[self.selected_itemy]}").st_nlink), True, "White"), (room_margin + 30, 350))
      if k_y: screen.blit(fontsmall.render("Protagonist: " + load_game_attributes(self.saves[self.selected_itemy])["Protagonist"].upper(), True, "White"), (room_margin + 30, 390))
    except: screen.blit(fontmedium.render(f"File not Found", True, "White"), (room_margin + 30, 20))

    screen.blit(pygame.transform.scale(pygame.image.load("Assets/editor/floppy disc.png").convert_alpha(), (128, 128)), (room_margin + 32, 64))
    screen.blit(fontmedium.render("Save Manager", True, "White"), (0, 16))
    
    if k_down: self.selected_itemy += 1; scrolldown_sfx.play()
    if k_up: self.selected_itemy -= 1; scrollup_sfx.play()
    if self.selected_itemy < 0: self.selected_itemy = len(self.saves) - 1
    if self.selected_itemy > len(self.saves) - 1: self.selected_itemy = 0
    if k_back: self.gamestate = 0; self.current_room = self.selected_itemy

  def action_customizations(self):
    global k_back
    if k_back: self.gamestate = 54; k_back = False; self.selected_button = ""; self.selected_state = ""
    pygame.draw.rect(screen, (0, 0, 50), ((50, 5), (WIDTH - 100, HEIGHT - 10)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 5), (WIDTH - 100, HEIGHT - 10)), width=2)
    screen.blit(fontmedium.render(f"Control Character Actions", True, "White"), (53, 17))
    try:
      screen.blit(fontsmall.render(f"Flip Rate: {self.character_types[self.selected_character_type]['object'].actions[main.selected_state].rate}", True, "White"), (92, 58))
      screen.blit(fontsmaller.render("Does Loop? " + {True: "On", False: "Off"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].loop], True, "White"), (160, 40))
      screen.blit(fontsmaller2.render({True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].prioritize_action], True, "White"), (WIDTH - 140, 25))
      screen.blit(fontsmaller2.render({True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].allow_travel] + "\n\n\n" + {True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].allow_jump] + "\n\n\n" + {True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].allow_flip] + "\n\n\n" + {True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].apply_gravity] + "\n\n\n" + {True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].aerial] + "\n\n\n" + {True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].terrestial] + "\n\n\n" + {True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].subaqueous] + "\n\n\n" + {True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].cancel_on_walk] + "\n\n\n" + {True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].cancel_on_ground] + "\n\n\n" + {True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].cancel_on_jump] + "\n\n\n" + {True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].cancel_on_hit] + "\n\n\n" + {True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].directional_relative] + "\n\n\n" + {True: "Yes", False: "No"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].continue_until_cancel], True, "White"), (WIDTH - 50, 25))
      screen.blit(fontsmaller2.render({True: "On", False: "Off"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].hold], True, "White"), (124, HEIGHT - 132))
      screen.blit(fontsmaller2.render({True: "On", False: "Off"}[self.character_types[self.selected_character_type]["object"].actions[main.selected_state].double_click], True, "White"), (156, HEIGHT - 132))
    except: pass
    screen.blit(joypad_surf, (( (WIDTH / 4) - 10) - (joypad_surf.get_width() / 2), 365))

    if self.selected_button and self.selected_state:
      #try:
      #  for button in self.selected_object.state_controls: self.selected_object.state_controls.pop(get_key_from_value(self.selected_object.state_controls, self.selected_state))
      #except Exception: pass
      if self.selected_state in self.character_types[self.selected_character_type]["object"].state_controls[self.selected_button]: self.character_types[self.selected_character_type]["object"].state_controls[self.selected_button].remove(self.selected_state)
      else: self.character_types[self.selected_character_type]["object"].state_controls[self.selected_button].append(self.selected_state)
      self.selected_button = ""; self.selected_state = ""
      edit_action_controls(None)

    for x, action in enumerate(self.character_types[self.selected_character_type]["object"].actions):
      buttons = ""
      for index, button in enumerate(self.character_types[self.selected_character_type]["object"].state_controls):
        if action in self.character_types[self.selected_character_type]["object"].state_controls[button]:
          buttons += {"A Button": "A", "B Button": "B", "X Button": "X", "Y Button": "Y", "D-Pad Right": "Right", "D-Pad Left": "Left", "D-Pad Up": "Up", "D-Pad Down": "Down", "R Shoulder": "R", "L Shoulder": "L", "Start": "START", "Select": "SELECT"}[button] + " / "
      text = fontsmaller.render(buttons[:-3], True, "White"); screen.blit(text, (368 - (text.get_width()), 59 + (x * 24)))

    #get_key_from_value(self.selected_object.state_controls, action)
    #for button in self.selected_object.state_controls:
    #  try:
    #    text = fontsmaller.render({"A Button": "A", "B Button": "B", "X Button": "X", "Y Button": "Y", "D-Pad Right": "Right", "D-Pad Left": "Left", "D-Pad Up": "Up", "D-Pad Down": "Down", "R Shoulder": "R", "L Shoulder": "L", "Start": "START", "Select": "SELECT"}[button], True, "White")
    #    screen.blit(text, (368 - (text.get_width()), 78 + (self.states.index(self.selected_object.state_controls[button]) * 28)))
    #  except: pass

    #print(self.selected_object.state_controls)

    if self.selected_state == "away":
      text = fontlittle.render("Away " + str(self.character_types[self.selected_character_type]["object"].away_delay), True, "White")
      screen.blit(text, (70, HEIGHT - 146))
      text = fontlittle.render("Wake " + str(self.character_types[self.selected_character_type]["object"].wake_up_delay), True, "White")
      screen.blit(text, (165, HEIGHT - 146))

    if self.selected_state:
      if self.on_page == 1:
        text = fontlittle.render("Move X " + str(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].move_x), True, "White")
        screen.blit(text, (80, 95))
        text = fontlittle.render("Move Y " + str(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].move_y), True, "White")
        screen.blit(text, (175, 95))
        text = fontlittle.render("Gain X vel " + str(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].gain_x), True, "White")
        screen.blit(text, (80, 115))
        text = fontlittle.render("Gain Y vel " + str(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].gain_y), True, "White")
        screen.blit(text, (193, 115))
        text = fontlittle.render("Damage " + str(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].damage), True, "White")
        screen.blit(text, (80, 135))
        text = fontlittle.render("Self Destruct " + str(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].self_destruct), True, "White")
        screen.blit(text, (185, 135))
        text = fontlittle.render("KX " + str(round(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].knockback_x, 1)), True, "White")
        screen.blit(text, (80, 155))
        text = fontlittle.render("KY " + str(round(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].knockback_y, 1)), True, "White")
        screen.blit(text, (80, 175))
        text = fontlittle.render("L Base " + str(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].loop_to), True, "White")
        screen.blit(text, (155, 155))
        text = fontlittle.render("L " + str(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].loops), True, "White")
        screen.blit(text, (250, 155))
        text = fontlittle.render("Combo Unit " + str(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].combo_unit), True, "White")
        screen.blit(text, (155, 175))
        if type(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].sound) != list: text = fontsmaller.render("SFX: " + str(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].sound), True, "White")
        else: text = fontsmaller.render("SFX: " + str(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].sound[0][:-5]), True, "White")
        screen.blit(text, (80, 191))
      elif self.on_page == 2:
        if len(self.projectiles):
          try: text = fontlittle.render("Projectile " + str(self.selected_projectile) + "        " + str(self.selected_projectile) + ". " + str(self.projectiles[self.selected_projectile - 1]), True, "White")
          except IndexError: text = fontlittle.render("uhh... error", True, "White")
          screen.blit(text, (80, 96))
        else:
          text = fontlittle.render("No Projectiles Created", True, "White")
          screen.blit(text, (110, 110))
        for index, proj in enumerate(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].projectiles):
          try: text = fonttiny.render(str(proj) + ". " + str(self.projectiles[proj - 1]), True, "White")
          except IndexError: self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].projectiles.remove(proj); continue
          screen.blit(text, (60, 130 + (index * 10)))
      elif self.on_page == 3:
        pygame.draw.rect(screen, "Black", ((60, 90), (110, 110)))
        if self.character_types[self.selected_character_type]["object"].mode == "platformer": surface = self.character_types[self.selected_character_type]["object"].images_dict[self.selected_state][self.selected_frame - 1]
        elif self.character_types[self.selected_character_type]["object"].mode == "topdown": surface = self.character_types[self.selected_character_type]["object"].images_dict[self.selected_direction][self.selected_state][self.selected_frame - 1]
        else: surface = self.character_types[self.selected_character_type]["object"].images_dict[self.selected_state][self.selected_frame - 1]
        x = 60 + ((110 / 2) - (surface.get_width() / 2))
        y = 90 + ((110 / 2) - (surface.get_height() / 2))
        screen.blit(surface, (x, y))
        pygame.draw.line(screen, "White", (60, 90 + ((110 / 2) + (surface.get_height() / 2))), (170, 90 + ((110 / 2) + (surface.get_height() / 2))), 1)
        rect = self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].rect
        attack_rect = self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].attack_rect
        pygame.draw.rect(screen, "red", ((x + rect.x, y + rect.y), (rect.width, rect.height)), 1)
        pygame.draw.rect(screen, "blue", ((x + attack_rect.x, y + attack_rect.y), (attack_rect.width, attack_rect.height)), 1)
        text = fontlittle.render("X " + str(round(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].rect.x)), True, "White")
        screen.blit(text, (187, 95))
        text = fontlittle.render("Y " + str(round(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].rect.y)), True, "White")
        screen.blit(text, (187, 115))
        text = fontlittle.render("W " + str(round(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].rect.width)), True, "White")
        screen.blit(text, (187, 135))
        text = fontlittle.render("H " + str(round(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].rect.height)), True, "White")
        screen.blit(text, (187, 155))
        text = fontlittle.render("AX " + str(round(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].attack_rect.x)), True, "White")
        screen.blit(text, (250, 95))
        text = fontlittle.render("AY " + str(round(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].attack_rect.y)), True, "White")
        screen.blit(text, (250, 115))
        text = fontlittle.render("AW " + str(round(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].attack_rect.width)), True, "White")
        screen.blit(text, (250, 135))
        text = fontlittle.render("AH " + str(round(self.character_types[self.selected_character_type]["object"].actions[self.selected_state].frants[self.selected_frame - 1].attack_rect.height)), True, "White")
        screen.blit(text, (250, 155))
        
      if k_r:
        self.on_page += 1; switch_page_sfx.play()
        if self.on_page > self.page_amount: self.on_page = 1
      if k_l:
        self.on_page -= 1; switch_page_sfx.play()
        if self.on_page <= 0: self.on_page = self.page_amount
    self.page_amount = 3

  def edit_door(self):
    if k_back: self.gamestate = 0
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render(f"Door Customizations", True, "White"), (53, 32))
    screen.blit(fontsmall.render(f"X Dest {self.selected_object.led_pos[0]}", True, "White"), (92, 75))
    screen.blit(fontsmall.render(f"Y Dest {self.selected_object.led_pos[1]}", True, "White"), (92, 115))
    screen.blit(fontsmall.render(f"X {self.selected_object.rect.x}", True, "White"), (258, 75))
    screen.blit(fontsmall.render(f"Y {self.selected_object.rect.y}", True, "White"), (258, 115))
    screen.blit(fontsmall.render(f"Lead to Room {self.selected_object.led_room}\n{self.rooms[self.selected_object.led_room].name}", True, "White"), (330, 150))
    if type(self.selected_object.hover_sound) == list: screen.blit(fontsmall.render("Hover SFX " + self.selected_object.hover_sound[0][:-5], True, "White"), (266, 211))
    else: screen.blit(fontsmall.render("Hover SFX " + self.selected_object.hover_sound, True, "White"), (266, 211))
    if type(self.selected_object.enter_sound) == list: screen.blit(fontsmall.render("Enter SFX " + self.selected_object.enter_sound[0][:-5], True, "White"), (266, 245))
    else: screen.blit(fontsmall.render("Enter SFX " + self.selected_object.enter_sound, True, "White"), (266, 245))
    if type(self.selected_object.exit_sound) == list: screen.blit(fontsmall.render("Exit SFX " + self.selected_object.exit_sound[0][:-5], True, "White"), (266, 279))
    else: screen.blit(fontsmall.render("Exit SFX " + self.selected_object.exit_sound, True, "White"), (266, 279))
    screen.blit(fontlittle.render({True: "On", False: "Off"}[self.selected_object.requires_input], True, "White"), (230, 162))
    screen.blit(fontlittle.render({True: "On", False: "Off"}[self.selected_object.passable], True, "White"), (264, 162))
    #screen.blit(fontlittle.render({True: "On", False: "Off"}[self.selected_object.spawn_door_on_other_side], True, "White"), (264, 162))
    #screen.blit(fontlittle.render({True: "On", False: "Off"}[self.selected_object.door_on_other_side_is_passable], True, "White"), (298, 162))
    #screen.blit(fontlittle.render({True: "On", False: "Off"}[self.selected_object.play_anim_on_other_side], True, "White"), (332, 162))
    for button in [button for button in self.buttons[32] if "Transition Setting" in button.button_type]: self.buttons[32].remove(button)
    if self.selected_object.transition:
      for x, button in enumerate([("Decrease Pretransition Speed", "less", change_door_prets, -1), ("İncrease Pretransition Speed", "more", change_door_prets, 1)]):
        self.buttons[32].append(Button(60 + (x * 230), 350, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3], button_type="Transition Setting"))
      for x, button in enumerate([("Decrease Posttransition Speed", "less", change_door_postts, -1), ("İncrease Posttransition Speed", "more", change_door_postts, 1)]):
        self.buttons[32].append(Button(60 + (x * 230), 390, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3], button_type="Transition Setting"))
      screen.blit(fontsmall.render(f"Pretransition Speed: {self.selected_object.transition_speed_pre}", True, "White"), (92, 357))
      screen.blit(fontsmall.render(f"Posttransition Speed: {self.selected_object.transition_speed_post}", True, "White"), (92, 397))
      if "Fade to Color" in self.selected_object.transition or "Cut to Color" in self.selected_object.transition or "Shrink to Shape" in self.selected_object.transition:
        for x, color in enumerate(basic_colors):
          main.buttons[32].append(Button((WIDTH - 134) + math.floor(x / 4) * 16, 360 + ((x % 4) * 16), 16, 16, color, "", change_transition_color, target=basic_colors[color], color=basic_colors[color], button_type="Transition Setting Color"))
      if "Shrink to Shape" in self.selected_object.transition:
        for x, shape in enumerate(self.shapes):
          main.buttons[32].append(Button((WIDTH - 134) + ((x % 5) * 16), 306 + math.floor(x / 5) * 16, 16, 16, shape, f"Assets/editor/shapes/{shape}", change_transition_shape, target=shape, button_type="Transition Setting Shape"))
      main.buttons[32].append(Button(230, 316, 32, 32, "Toggle Door and Player Animation", "Assets/editor/cutscene.png", change_transition_play_door_and_player_animation, button_type="Transition Setting"))
      main.buttons[32].append(Button(264, 316, 32, 32, "İmmobilize Player in Pretransition", "Assets/editor/lock.png", change_transition_pre_immobilize_player, button_type="Transition Setting"))
      main.buttons[32].append(Button(298, 316, 32, 32, "İmmobilize Player in Posttransition", "Assets/editor/lock.png", change_transition_post_immobilize_player, button_type="Transition Setting"))
      main.buttons[32].append(Button(332, 316, 32, 32, "Override Uİ During Transition", "Assets/editor/ui 2.png", change_transition_override_ui, button_type="Transition Setting"))
      main.buttons[32].append(Button(332, 352, 32, 32, "Toggle Flag 1", "Assets/editor/flag 1.png", change_transition_f1, button_type="Transition Setting"))
      main.buttons[32].append(Button(332, 388, 32, 32, "Toggle Flag 2", "Assets/editor/flag 2.png", change_transition_f2, button_type="Transition Setting"))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.selected_object.transition_play_door_and_player_animation], True, "White"), (228, 305))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.selected_object.transition_pre_immobilize_player], True, "White"), (264, 305))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.selected_object.transition_post_immobilize_player], True, "White"), (298, 305))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.selected_object.transition_override_ui], True, "White"), (332, 305))
      screen.blit(fontlittle.render("Transition Flag 1: " + {True: "On", False: "Off"}[self.selected_object.transition_flag_1] + ", Transition Flag 2: " + {True: "On", False: "Off"}[self.selected_object.transition_flag_2], True, "White"), (5, HEIGHT - 15))

  def entity_dialogue(self):
    if k_back: self.gamestate = 23
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render("Dialogues", True, "White"), (53, 32))
    try: screen.blit(fontmedium.render(str(self.selected_object.letter_delay[self.selected_dl]), True, "White"), (WIDTH - 216, 38))
    except: pass 
    #for index, dialogue in enumerate(self.selected_object.dialogue):
    #  screen.blit(fontsmall.render(dialogue, True, "White"), (53, 50 + (index * 15)))

  def stat_effects(self):
    if k_back: self.gamestate = 15
    pygame.draw.rect(screen, (0, 0, 50), ((100, 100), (WIDTH - 200, HEIGHT - 300)))
    pygame.draw.rect(screen, "Dark Blue", ((100, 100), (WIDTH - 200, HEIGHT - 300)), width=2)
    screen.blit(fontsmall.render("Set Effect for Stat", True, "White"), (102, 102))

  def stat_ui(self):
    if k_back: self.gamestate = 15
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render("Customize Stat Uİ", True, "White"), (53, 32))
    screen.blit(display_surf, (56, 320))
    screen.blit(fontsmall.render(f"X Margin: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['X Margin']}", True, "White"), (98, 78))
    screen.blit(fontsmall.render(f"Y Margin: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['Y Margin']}", True, "White"), (98, 108))
    screen.blit(fontsmall.render(f"Rotate: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['Rotate']}", True, "White"), (98, 138))
    screen.blit(fontsmall.render(f"Scale: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['Font Size']}", True, "White"), (98, 168))
    screen.blit(fontsmall.render(f"Outline: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['TOL']}", True, "White"), (98, 198))
    screen.blit(fontsmall.render(f"Offset: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['MAO']}", True, "White"), (172, 360))
    if self.ui.instances[self.selected_ui][self.selected_ui_mode]["I"]:
      screen.blit(fontsmall.render(f"X Pos: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['I X']}", True, "White"), (298, 75))
      screen.blit(fontsmall.render(f"Y Pos: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['I Y']}", True, "White"), (298, 105))
      screen.blit(fontsmall.render(f"Offset: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['I Offset']}", True, "White"), (298, 135))
      screen.blit(fontsmall.render(f"Wrap: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['I WL']}", True, "White"), (298, 165))
      screen.blit(fontsmall.render(f"Angle: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['I Angle']}", True, "White"), (298, 195))
      screen.blit(fontsmall.render(f"Frame Speed: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['I FS']}", True, "White"), (298, 225))
    elif self.ui.instances[self.selected_ui][self.selected_ui_mode]["Bar"]:
      screen.blit(fontsmall.render(f"X Pos: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['B X']}", True, "White"), (298, 75))
      screen.blit(fontsmall.render(f"Y Pos: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['B Y']}", True, "White"), (298, 105))
      screen.blit(fontsmall.render(f"Length: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['B Len']}", True, "White"), (298, 135))
      screen.blit(fontsmall.render(f"Width: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['B Thi']}", True, "White"), (298, 165))
      screen.blit(fontsmall.render(f"Outline: {self.ui.instances[self.selected_ui][self.selected_ui_mode]['B OL']}", True, "White"), (298, 195))
      screen.blit(fontlittle.render({False: "Horizontal", True: "Vertical"}[self.ui.instances[self.selected_ui][self.selected_ui_mode]['B V']] + " Bar", True, "White"), (400, HEIGHT - 17))
    screen.blit(fontlittle.render(f"Token: {self.ui.instances[self.selected_ui]['SM']}", True, "White"), (374, 358))
    screen.blit(fontlittle.render(f"Mode: {self.selected_ui_mode}", True, "White"), (374, 324))
    try:
      if self.ui.instances[self.selected_ui][self.selected_ui_mode]["TCBG"] == "Transparent": self.ui.instances[self.selected_ui][self.selected_ui_mode]["Text Surface"] = self.ui.instances[self.selected_ui][self.selected_ui_mode]["Font"].render(self.ui.instances[self.selected_ui][self.selected_ui_mode]["Text"], self.ui.instances[self.selected_ui][self.selected_ui_mode]["AA"], self.ui.instances[self.selected_ui][self.selected_ui_mode]["TC"])
      else: self.ui.instances[self.selected_ui][self.selected_ui_mode]["Text Surface"] = self.ui.instances[self.selected_ui][self.selected_ui_mode]["Font"].render(self.ui.instances[self.selected_ui][self.selected_ui_mode]["Text"], self.ui.instances[self.selected_ui][self.selected_ui_mode]["AA"], self.ui.instances[self.selected_ui][self.selected_ui_mode]["TC"], self.ui.instances[self.selected_ui][self.selected_ui_mode]["TCBG"])
    except:
      for mode in self.ui.instances[self.selected_ui]["Modes"]:
        try:
          try:
            if type(self.ui.instances[self.selected_ui][mode]["Font STR"]) == pygame.Font: self.ui.instances[self.selected_ui][mode]["Font"] = self.ui.instances[self.selected_ui][mode]["Font STR"]
            elif self.ui.instances[self.selected_ui][mode]["Font STR"] != None: self.ui.instances[self.selected_ui][mode]["Font"] = self.ui.instances[self.selected_ui][mode]["Font STR"]; self.ui.instances[self.selected_ui][mode]["Font"] = pygame.Font(self.ui.instances[self.selected_ui][mode]["Font STR"], self.ui.instances[self.selected_ui][mode]["Font Size"])
            else: self.ui.instances[self.selected_ui][mode]["Font"] = pygame.Font(None, self.ui.instances[self.selected_ui]["Font Size"])
          except: self.ui.instances[self.selected_ui][mode]["Font"] = pygame.Font(self.main.active_directory + "Fonts/" + self.ui.instances[self.selected_ui][mode]["Font STR"], self.ui.instances[self.selected_ui][mode]["Font Size"]); self.ui.instances[self.selected_ui][mode]["Font STR"] = self.ui.instances[self.selected_ui][mode]["Font"]
        except: self.ui.instances[self.selected_ui][mode]["Font"] = pygame.font.SysFont(self.ui.instances[self.selected_ui][mode]["Font"], self.ui.instances[self.selected_ui][mode]["Font Size"])
    if self.ui.instances[self.selected_ui][self.selected_ui_mode]["TOL"]:
      ol_image = self.ui.instances[self.selected_ui][self.selected_ui_mode]["Text Surface"]
      self.ui.instances[self.selected_ui][self.selected_ui_mode]["Text Surface"] = pygame.mask.from_surface(self.ui.instances[self.selected_ui][self.selected_ui_mode]["Text Surface"]).convolve(pygame.mask.Mask((self.ui.instances[self.selected_ui][self.selected_ui_mode]["TOL"], self.ui.instances[self.selected_ui][self.selected_ui_mode]["TOL"]), fill=True)).to_surface(setcolor=self.ui.instances[self.selected_ui][self.selected_ui_mode]["TCOL"], unsetcolor=self.ui.instances[self.selected_ui][self.selected_ui_mode]["Text Surface"].get_colorkey()).convert_alpha()
      self.ui.instances[self.selected_ui][self.selected_ui_mode]["Text Surface"].blit(ol_image, (self.ui.instances[self.selected_ui][self.selected_ui_mode]["TOL"] / 2, self.ui.instances[self.selected_ui][self.selected_ui_mode]["TOL"] / 2))
    screen.blit(self.ui.instances[self.selected_ui][self.selected_ui_mode]["Text Surface"], (160, HEIGHT - 60))
    screen.blit(fontlittle.render("Multiplayer Alignment: " + self.ui.instances[self.selected_ui][self.selected_ui_mode]['MA']  + "  Font: " + str(self.ui.instances[self.selected_ui][self.selected_ui_mode]['Font STR']), True, "White"), (20, 2))
    screen.blit(fontlittle.render("Align: " + self.ui.instances[self.selected_ui][self.selected_ui_mode]['I Align'], True, "White"), (20, HEIGHT - 17))

  def set_collectible_price(self):
    if k_back: self.gamestate = 21
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render("Collectible Price", True, "White"), (53, 32))
    screen.blit(fontlittle.render("Exchange: " + {True: "On", False: "Off"}[self.selected_object.price_exchange] + "\nDynamic Drop: " + {True: "On", False: "Off"}[self.selected_object.price_decrement], True, "White"), (WIDTH / 2, 28))
    screen.blit(fontmedium.render("Price Stat", True, "White"), (53, 156))
    screen.blit(fontmedium.render("Price Value", True, "White"), (53, 306))
    screen.blit(fontsmall.render("Value: " + str(self.selected_object.price_value), True, "White"), (112, 334))
    screen.blit(fontsmall.render("Price Text Position", True, "White"), (280, 70))

  def rebool(self):
    global k_back
    pygame.draw.rect(screen, (0, 0, 50), ((100, 100), (WIDTH - 200, HEIGHT - 300)))
    pygame.draw.rect(screen, "Dark Blue", ((100, 100), (WIDTH - 200, HEIGHT - 300)), width=2)
    screen.blit(fontsmall.render(f"Set boolean {self.target_object} as", True, "White"), (105, 105))
    screen.blit(fontmedium.render(f"{main.rename_text}", True, "White"), (150, 150))
    screen.blit(fontsmall.render("Press ENTER to Apply, ESC to Cancel", True, "White"), (2, 2))
    if k_back: self.gamestate = self.remember_gs; self.rename_target = ""; self.rename_text = ""; k_back = False
    if k_start and len(str(self.rename_text)):
      self.gamestate = self.remember_gs
      if self.remember_gs == 15: self.rename_target = eval(str(self.rename_text)); self.game_stats_initpoint[self.selected_stat] = self.rename_target
  
  def scene_repos(self):
    if k_back: self.gamestate = 24
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render(f"Reposition {type(self.selected_object).__name__}", True, "White"), (53, 32))
    if main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Rect'] != None:
      screen.blit(fontsmall.render(f"to X {main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Rect'][0]}", True, "White"), (98, 75))
      screen.blit(fontsmall.render(f"to Y {main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Rect'][1]}", True, "White"), (98, 115))
      screen.blit(fontsmaller.render({True: f"When the cutscene is over, this {type(self.selected_object).__name__} will stay on X {main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Rect'][0]} and y {main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Rect'][1]}", False: f"When the cutscene is over, this {type(self.selected_object).__name__} will go back to where it was before the cutscene"}[main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['SOCR']], True, "White"), (2, HEIGHT - 15))
    else:
      screen.blit(fontsmall.render("X Not Set!", True, "White"), (98, 75))
      screen.blit(fontsmall.render("Y Not Set!", True, "White"), (98, 115))
    screen.blit(fontsmaller.render("Set on " + {True: "Hidden", False: "Shown"}[main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Hidden']] + " for Key " + str(self.selected_key), True, "White"), (300, HEIGHT - 70))
    
  def scene_move(self):
    if k_back: self.gamestate = 24
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render(f"Move {type(self.selected_object).__name__}", True, "White"), (53, 32))
    if main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Speed"]:
      screen.blit(fontsmall.render(f"Speed {main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Speed']}", True, "White"), (98, 175))
      screen.blit(fontsmall.render(f"X Dest {main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['X Speed']}", True, "White"), (98, 75))
      screen.blit(fontsmall.render(f"Y Dest {main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Y Speed']}", True, "White"), (98, 115))
    else:
      screen.blit(fontlittle.render("No Destination", True, "White"), (95, 178))
      screen.blit(fontsmall.render(f"X Speed {main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['X Speed']}", True, "White"), (98, 75))
      screen.blit(fontsmall.render(f"Y Speed {main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Y Speed']}", True, "White"), (98, 115))
    screen.blit(fontlittle.render("Setting at No Destination will only result in a change in speed.\n\nUsing destination will move the object to X Dest and Y Dest,\nthen Speed will configure how fast it moves to the destination.\n\n\nAll of this won't work in the 0th frame", True, "White"), (54, 220))

  def scene_action(self):
    if k_back: self.gamestate = 24
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    if self.selected_object == None:
      screen.blit(fontmedium.render(f"Main Cutscene Options", True, "White"), (53, 32))
      screen.blit(fontsmall.render(f"Key Rate {main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Rotate']}", True, "White"), (86, 92))
      screen.blit(fontlittle.render(f"At 0, the key will not progress at all from time.\nAt 1, the key lasts a frame.\nAt {self.fps} (game FPS), the key lasts one second.", True, "White"), (54, 130))
      screen.blit(fontsmall.render(f"Scene Mode {main.selected_ui_sm}", True, "White"), (184, 258))
      screen.blit(fontlittle.render(l[lg]["Uİ Tokens to Show: "] + str(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Show UI']), True, "Green"), (54, 320))
      screen.blit(fontlittle.render(l[lg]["Uİ Tokens to Hide: "] + str(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Hide UI']), True, "Red"), (54, 360))
    else:
      screen.blit(fontmedium.render(f"Set Action for {type(self.selected_object).__name__}", True, "White"), (53, 32))
      if type(main.selected_object) == Player: screen.blit(fontsmaller.render("These only work when player's inputs are disabled", True, "White"), (2, HEIGHT - 15))
      if type(main.selected_object) == Entity: screen.blit(fontsmaller.render("These only work when entity's behaviors aren't in motion", True, "White"), (2, HEIGHT - 15))
      if type(main.selected_object) == Camera:
        screen.blit(fontlittle.render("Follow player: " + {True: "On", False: "Off"}[main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Hidden']], True, "White"), (285, HEIGHT - 40))
        screen.blit(fontlittle.render("Horizontal Mirror: " + {True: "On", False: "Off"}[main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['B1']], True, "White"), (285, HEIGHT - 74))
        screen.blit(fontlittle.render("Vertical Mirror: " + {True: "On", False: "Off"}[main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['B2']], True, "White"), (285, HEIGHT - 107))
        screen.blit(fontlittle.render("Leave on -1 for no changes to borders.", True, "White"), (54, 130))
        screen.blit(fontlittle.render(str(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["I2"]), True, "White"), (220, 155))
        screen.blit(fontlittle.render(str(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["I4"]), True, "White"), (220, 188))
        screen.blit(fontlittle.render(str(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["I1"]), True, "White"), (220, 219))
        screen.blit(fontlittle.render(str(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["I3"]), True, "White"), (220, 254))
      if type(main.selected_object) == Tile:
        screen.blit(fontlittle.render(f"Tile action: {main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Action']}", True, "White"), (54, 130))
      if type(main.selected_object) == Door:
        screen.blit(fontlittle.render(f"Door action: {main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Action']}", True, "White"), (54, 130))
      if type(main.selected_object) == Background:
        if main.selected_object.is_animating:
          screen.blit(fontlittle.render(f"Background action: {main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Action']}", True, "White"), (54, 130))
          screen.blit(fontlittle.render({True: "Once the animated background loops again, it will\njump to the next key", False: "The animated background won't jump to next key\nonce it has looped"}[main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['B1']], True, "White"), (54, HEIGHT - 60))

  def scene_audio(self):
    if k_back: self.gamestate = 24
    pygame.draw.rect(screen, (0, 0, 50), ((100, 25), (WIDTH - 200, HEIGHT - 50)))
    pygame.draw.rect(screen, "Dark Blue", ((100, 25), (WIDTH - 200, HEIGHT - 50)), width=2)
    screen.blit(fontmedium.render(f"Key {self.selected_key} Audio", True, "White"), (103, 32))
    if type(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["SFX"]) == list: screen.blit(fontsmall.render("Key SFX: " + main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["SFX"][0][:-5], True, "White"), (105, 60))
    else: screen.blit(fontsmall.render("Key SFX: " + main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["SFX"], True, "White"), (105, 60))

    pygame.draw.line(screen, "Dark Blue", (180, HEIGHT - 45), (350, HEIGHT - 45), width=7)
    # Inside your main loop or update function:
    if pygame.mixer_music.get_busy():
      pygame.draw.line(screen, "Dark Blue", (180, HEIGHT - 45), (350, HEIGHT - 45), width=7)
      try:
        current_position = pygame.mixer_music.get_pos()
        total_duration = song.get_length()
        current_position_seconds = current_position / 1000
        normalized_position = (current_position_seconds / total_duration) * 170
        x_coordinate = normalized_position + 180
        if x_coordinate > 350: x_coordinate = 350
        pygame.draw.line(screen, "Blue", (180, HEIGHT - 45), (x_coordinate, HEIGHT - 45), width=7)
      except: pass

    screen.blit(fontsmall.render(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Track"], True, "White"), (110, HEIGHT - 85))
    screen.blit(fontsmall.render(main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Dir"], True, "White"), (110, HEIGHT - 153))
  
  def edit_text(self):
    if k_back: self.gamestate = 0
    self.remember_gs = 43
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render("Edit Text", True, "White"), (53, 32))
    screen.blit(fontsmall.render(f"X {self.selected_object.rect.x}", True, "White"), (98, 75))
    screen.blit(fontsmall.render(f"Y {self.selected_object.rect.y}", True, "White"), (98, 115))
    screen.blit(fontsmall.render(f"Font Size {self.selected_object.size}", True, "White"), (94, 155))
    if self.selected_object.scale[0] > 0: screen.blit(fontsmall.render(f"X Scale {self.selected_object.scale[0]}", True, "White"), (98, 195))
    else: screen.blit(fontsmaller.render(f"X Scale on Default", True, "White"), (92, 200))
    if self.selected_object.scale[1] > 0: screen.blit(fontsmall.render(f"Y Scale {self.selected_object.scale[1]}", True, "White"), (98, 235))
    else: screen.blit(fontsmaller.render(f"Y Scale on Default", True, "White"), (92, 240))
    if self.selected_object.margin > 0: screen.blit(fontsmall.render(f"Margin {self.selected_object.margin}", True, "White"), (98, 275))
    else: screen.blit(fontsmall.render(f"No Margins", True, "White"), (98, 275))
    screen.blit(fontsmall.render(f"Rotate {self.selected_object.rotation}", True, "White"), (98, 315))
    screen.blit(fontsmall.render(f"Alpha {self.selected_object.opacity}", True, "White"), (98, 355))
    screen.blit(fontsmall.render(f"Layer {self.selected_object.layer}", True, "White"), (98, 395))
    screen.blit(fontsmall.render(f"Outline {self.selected_object.outline_thickness}", True, "White"), (260, 395))
    screen.blit(fontlittle.render("Bold: " + {True: "On", False: "Off"}[self.selected_object.bold] + ", İtalic: " + {True: "On", False: "Off"}[self.selected_object.italic] + ", Underline: " + {True: "On", False: "Off"}[self.selected_object.underline] + ", Strikethrough: " + {True: "On", False: "Off"}[self.selected_object.strikethrough] + ", Anti-Alias: " + {True: "On", False: "Off"}[self.selected_object.anti_aliasing], True, "White"), (20, 5))
    screen.blit(fontlittle.render("Align: " + self.selected_object.align + ", Cap: " + self.selected_object.capitalization_mode + ", Text Direction: " + self.selected_object.direction + ", Flip X: " + {True: "On", False: "Off"}[self.selected_object.flip[0]] + ", Flip Y: " + {True: "On", False: "Off"}[self.selected_object.flip[1]], True, "White"), (20, HEIGHT - 17))
    screen.blit(pygame.transform.rotate(fontlittle.render("Font: " + str(self.selected_object.font_str), True, "White"), 90), (2, 20))

  def font_library(self):
    for index in range(30):
      if index % 2 == 0: pygame.draw.rect(screen, (0, 0, 50), ((0, 45 + (index * 26)), (WIDTH, 26)))
      else: pygame.draw.rect(screen, (0, 0, 20), ((0, 45 + (index * 26)), (WIDTH, 26)))
    for index, font in enumerate(self.fonts[minint(self.selected_itemy - 10, 0):]):
      try:
        if self.fonts[self.selected_itemy] == font: screen.blit(fontsmall.render(font, True, "Yellow"), (1, 50 + (index * 26)))
        else: screen.blit(fontsmall.render(font, True, "White"), (1, 50 + (index * 26)))
        if not ".ttf" in font and not ".otf" in font:
          try:
            for lang_index, lang in enumerate(font_lang_support[self.fonts[minint((index + minint(self.selected_itemy, 10)) - 10, 0)]]): screen.blit(fonttiny.render(lang, True, {"LA": "Red", "GR": (0, 128, 255), "CY": (196, 196, 255), "AR": "Dark green", "JP": (255, 128, 196), "KO": (255, 255, 128), "??": "White", "": "White"}[lang]), (2 + (lang_index * 25), 65 + (index * 26)))
          except: pass
      except: self.selected_itemy = 0

    room_margin = 250
    pygame.draw.rect(screen, (0, 0, 50), ((WIDTH - room_margin, 0), (room_margin, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((WIDTH - room_margin, 0), (2, HEIGHT)))
    if len(self.fonts):
      try:
        try: tfont = pygame.Font("Fonts/" + self.fonts[self.selected_itemy], 20)
        except: tfont = pygame.font.SysFont(self.fonts[self.selected_itemy], 20)
        screen.blit(fontmedium.render(self.fonts[self.selected_itemy], True, "White"), (room_margin + 20, 10))
        screen.blit(tfont.render(self.fonts[self.selected_itemy], True, "White"), (room_margin + 20, 30))
        tfont.set_script("Arab")
        if self.on_page == 1: screen.blit(tfont.render("\"The quick brown fox, jumps over the lazy dog.\"\n1 2 3 4 5 6 7 8 9 0 ! ? () [] {} : ; ' \" / \\ < > @ # $ % ^ & * _ - + = ~ `\nÁ á É é Í í Ó ó Ú ú À à È è Ì ì Ò ò Ù ù Ä ä Ë ë Ï ï Ö ö Ü ü Â â Ê ê Î î Ô ô Û û Ç ç Ñ ñ", True, "White", wraplength=WIDTH - (room_margin + 20)), (room_margin + 20, 60))
        if self.on_page == 2: screen.blit(tfont.render("διαφυλάξτε γενικά τη ζωή σας από βαθειά ψυχικά τραύματα\nРазъяренный чтец эгоистично бьёт пятью жердями шустрого фехтовальщика", True, "White", wraplength=WIDTH - (room_margin + 20)), (room_margin + 20, 60))
        if self.on_page == 3: screen.blit(tfont.render("~ ١ ٢ ٣ ٤ ٥ ٦ ٧ ٨ ٩ ٠ نص حكيم له سر قاطع وذو شأن عظيم مكتوب على ثوب أخضر ومغلف بجلد أزرق\n ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن و ه لا ى ي ة ء  َ ِ ُ ْ ّ ً ٍ ٌ أ إ آ ؤ لأ لإ لآ ئ ، ؟", True, "White", wraplength=WIDTH - (room_margin + 20)), (room_margin + 20, 60)); tfont.set_direction(pygame.DIRECTION_RTL)
        else: tfont.set_direction(pygame.DIRECTION_LTR)
        if self.on_page == 4: screen.blit(tfont.render("あ い う え お か き く け こ さ し す せ そ た ち つ て と な に ぬ ね の は ひ ふ へ ほ ま み む め も や ゆ よ ら り る れ ろ わ を ん が ぎ ぐ げ ご ざ じ ず ぜ ぞ だ ぢ づ で ど ば び ぶ べ ぼ ぱ ぴ ぷ ぺ ぽ っ ぁ ぃ ぅ ぇ ぉ ゃ ゅ ょ ～ １ ２ ３ ４ ５ ６ ７ ８ ９ ０ 。 、 ・ ！ ？ ： ； （ ）「 」 『 』 【 】‘ 　", True, "White", wraplength=WIDTH - (room_margin + 20)), (room_margin + 20, 60))
        if self.on_page == 5: screen.blit(tfont.render("ア イ ウ エ オ カ キ ク ケ コ サ シ ス セ ソ タ チ ツ テ ト ナ ニ ヌ ネ ノ ハ ヒ フ ヘ ホ マ ミ ム メ モ ヤ ユ ヨ ラ リ ル レ ロ ワ ヲ ガ ギ グ ゲ ゴ ザ ジ ズ ゼ ゾ ダ ヂ ヅ デ ド バ ビ ブ ベ ボ パ ピ プ ペ ポ ッ ァ ィ ゥ ェ ォ ー １ ２ ３ ４ ５ ６ ７ ８ ９ ０ 。 、 ・ ！ ？ ： ； （ ）「 」 『 』 【 】‘ 　", True, "White", wraplength=WIDTH - (room_margin + 20)), (room_margin + 20, 60))
        if self.on_page == 6: screen.blit(tfont.render("人 一 二 三 四 五 六 七 八 九 十 百 千 万 億 兆 京 日 月 見 目 明 暗 前 後 本 今 入 出 発 早 木 山 森 川 石 空 草 花 葉 曇 惑 星 金 当 気 中 水 火 風 雷 土 地 訓 音 声 大 小 少 来 洗 田 伝 公 王 主 文 門 問 開 間 聞 引 光 闇 影 道 々 多 力 夢 言 話 笑 立 歩 走 逃 行 会 変 買 書 読 学 忘 覚 思 考 知 信 分 語 私", True, "White", wraplength=WIDTH - (room_margin + 20)), (room_margin + 20, 60))
        if self.on_page == 7: screen.blit(tfont.render("僕 君 彼 我 男 女 子 夫 妻 同 愛 遊 楽 幸 嬉 悲 優 弱 強 怖 特 待 持 時 動 物 朝 夜 必 久 恋 向 何 誰 曜 離 虫 独 猫 犬 鳥 魚 和 終 完 事 約 生 命 死 殺 激 不 止 左 右 上 下 部 東 南 西 北 毎 体 頭 顔 口 手 指 足 腕 鼻 耳 方 形 図 食 飲 味 辞 咳 井 良 悪 無 由 昔 元 確 実 了 可 苦 甘 亡 失 欠 解 全 意 汚 頼 欲", True, "White", wraplength=WIDTH - (room_margin + 20)), (room_margin + 20, 60))
        if self.on_page == 8: screen.blit(tfont.render("願 礼 術 燃 暑 寒 冷 要 惜 慣 回 廻 色 黒 白 赤 黄 緑 青 留 告 仕 社 自 束 感 触 恥 困 救 助 守 導 隠 様 逆 迷 果 画 面 疲 寝 区 別 近 場 所 国 英 屋 店 員 眠 起 押 送 起 過 品 電 工 在 相 戸 扉 席 哀 暇 翻 訳 機 者 哀 床 消 現 痛 預 吠 叫 歌 唄 曲 伸 縮 屈 諦 頑 共 有 張 種 家 財 船 長 金 布 服 収 内 定 秘 与", True, "White", wraplength=WIDTH - (room_margin + 20)), (room_margin + 20, 60))
        if self.on_page == 9: screen.blit(tfont.render("返 密 机 椅 敬 先 世 界 線 年 存 在 天 神", True, "White", wraplength=WIDTH - (room_margin + 20)), (room_margin + 20, 60))
        if self.on_page == 10: screen.blit(tfont.render("ㅏㅐㅑㅓㅔㅕㅗㅛㅜㅠㅡㅣ\nㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ", True, "White", wraplength=WIDTH - (room_margin + 20)), (room_margin + 20, 60))
      except: screen.blit(fontmedium.render("Select a font file", True, "White"), (room_margin + 30, 16))
    else: screen.blit(fontmedium.render("No fonts imported", True, "White"), (room_margin + 30, 16))

    screen.blit(fontmedium.render("Font Library", True, "White"), (0, 16))
    self.page_amount = 10
    if k_down: self.selected_itemy += 1 + (int(k_y) * 4); scrolldown_sfx.play()
    if k_up: self.selected_itemy -= 1 + (int(k_y) * 4); scrollup_sfx.play()
    if self.selected_itemy < 0: self.selected_itemy = len(self.fonts) - 1
    if self.selected_itemy > len(self.fonts) - 1: self.selected_itemy = 0
    if k_r:
      self.on_page += 1; switch_page_sfx.play()
      if self.on_page > self.page_amount: self.on_page = 1
    if k_l:
      self.on_page -= 1; switch_page_sfx.play()
      if self.on_page <= 0: self.on_page = self.page_amount
    if k_back: self.gamestate = self.remember_gs

  def image_library(self):
    for index in range(30):
      if index % 2 == 0: pygame.draw.rect(screen, (0, 0, 50), ((0, 45 + (index * 26)), (WIDTH, 26)))
      else: pygame.draw.rect(screen, (0, 0, 20), ((0, 45 + (index * 26)), (WIDTH, 26)))
    for index, image in enumerate(self.images[minint(self.selected_itemy - 10, 0):]):
      try:
        if type(image) == list:
          if self.images[self.selected_itemy] == image: screen.blit(fontsmall.render(image[0][:-5], True, "Yellow"), (1, 50 + (index * 26)))
          else: screen.blit(fontsmall.render(image[0][:-5], True, "White"), (1, 50 + (index * 26)))
        else:
          if self.images[self.selected_itemy] == image: screen.blit(fontsmall.render(image, True, "Yellow"), (1, 50 + (index * 26)))
          else: screen.blit(fontsmall.render(image, True, "White"), (1, 50 + (index * 26)))
      except: self.selected_itemy = 0      

    room_margin = 250
    pygame.draw.rect(screen, (0, 0, 50), ((WIDTH - room_margin, 0), (room_margin, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((WIDTH - room_margin, 0), (2, HEIGHT)))
    if len(self.images):
      try:
        if type(self.images[self.selected_itemy]) != list:
          if os.path.isdir(main.active_directory + "Assets/images/" + self.images[self.selected_itemy]):
            self.animated_bg_images = sorted(os.listdir(main.active_directory + "Assets/images/" + self.images[self.selected_itemy] + "/"), key=extract_number)
            try: img = pygame.image.load(main.active_directory + "Assets/images/" + self.images[self.selected_itemy] + "/" + self.animated_bg_images[self.bg_frame_timer.keep_count(1 + (int(k_y) * 3), len(self.animated_bg_images), 0)]).convert_alpha()
            except IndexError: self.bg_frame_timer.tally = 0; img = pygame.image.load(main.active_directory + "Assets/images/" + self.images[self.selected_itemy] + "/" + self.animated_bg_images[0]).convert_alpha()
            if len(self.images[self.selected_itemy]) < 20: screen.blit(fontmedium.render(f"{self.images[self.selected_itemy]}", True, "White"), (room_margin + 30, 16))
            elif len(self.images[self.selected_itemy]) < 28: screen.blit(fontsmall.render(f"{self.images[self.selected_itemy]}", True, "White"), (room_margin + 30, 18))
            elif len(self.images[self.selected_itemy]) < 37: screen.blit(fontlittle.render(f"{self.images[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
            else: screen.blit(fontsmaller.render(f"{self.images[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
            screen.blit(fontsmall.render(f"Scale: {img.get_width()}:{img.get_height()}", True, "White"), (room_margin + 20, 265))
            screen.blit(fontsmall.render(f"Pitch: {img.get_pitch()}", True, "White"), (room_margin + 20, 295))
            #screen.blit(fontsmall.render(f"Metadata: {img}", True, "White"), (room_margin + 20, 230))
            screen.blit(pygame.transform.scale(img, (WIDTH / 2.42, HEIGHT / 2.42)), (room_margin + 32, 64))
          else:
            img = pygame.image.load(main.active_directory + "Assets/images/" + self.images[self.selected_itemy]).convert_alpha()
            if len(self.images[self.selected_itemy]) < 20: screen.blit(fontmedium.render(f"{self.images[self.selected_itemy]}", True, "White"), (room_margin + 30, 16))
            elif len(self.images[self.selected_itemy]) < 28: screen.blit(fontsmall.render(f"{self.images[self.selected_itemy]}", True, "White"), (room_margin + 30, 18))
            elif len(self.images[self.selected_itemy]) < 37: screen.blit(fontlittle.render(f"{self.images[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
            else: screen.blit(fontsmaller.render(f"{self.images[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
            screen.blit(fontsmall.render(f"Scale: {img.get_width()}:{img.get_height()}", True, "White"), (room_margin + 20, 265))
            screen.blit(fontsmall.render(f"Pitch: {img.get_pitch()}", True, "White"), (room_margin + 20, 295))
            #screen.blit(fontsmall.render(f"Metadata: {img}", True, "White"), (room_margin + 20, 230))
            screen.blit(pygame.transform.scale(img, (WIDTH / 2.42, HEIGHT / 2.42)), (room_margin + 32, 64))
        else:
          if len(self.images[self.selected_itemy][0][:-1]) < 20: screen.blit(fontmedium.render(f"{self.images[self.selected_itemy][0][:-5]}", True, "White"), (room_margin + 30, 16))
          elif len(self.images[self.selected_itemy][0][:-1]) < 28: screen.blit(fontsmall.render(f"{self.images[self.selected_itemy][0][:-5]}", True, "White"), (room_margin + 30, 18))
          elif len(self.images[self.selected_itemy][0][:-1]) < 37: screen.blit(fontlittle.render(f"{self.images[self.selected_itemy][0][:-5]}", True, "White"), (room_margin + 30, 20))
          else: screen.blit(fontsmaller.render(f"{self.images[self.selected_itemy][0][:-1]}", True, "White"), (room_margin + 30, 20))
          width, height = pygame.image.load(main.active_directory + "Assets/images/" + self.images[self.selected_itemy][0]).convert_alpha().get_width(), pygame.image.load(main.active_directory + "Assets/images/" + self.images[self.selected_itemy][0]).convert_alpha().get_height()
          screen.blit(fontsmall.render(f"Scale: {width}:{height}", True, "White"), (room_margin + 20, 265))
          screen.blit(fontsmall.render(f"Pitch: {pygame.image.load(main.active_directory + 'Assets/images/' + self.images[self.selected_itemy][0]).convert_alpha().get_pitch()}", True, "White"), (room_margin + 20, 295))
          screen.blit(fontsmall.render(f"Set Amount: {len(self.images[self.selected_itemy])}", True, "White"), (room_margin + 20, 325))
          for index, image in enumerate(self.images[self.selected_itemy]): screen.blit(pygame.image.load(main.active_directory + "Assets/images/" + image).convert_alpha(), (room_margin + 32 + (index * width), 64))
      except Exception as e: screen.blit(fontmedium.render("Select a image file", True, "White"), (room_margin + 30, 16)); print(e)
    else: screen.blit(fontmedium.render("No images imported", True, "White"), (room_margin + 30, 16))

    screen.blit(fontmedium.render("Image Library", True, "White"), (0, 16))

    #screen.blit(fontsmall.render(f"Distance {self.selected_value}", True, "White"), (302, 330))
    #screen.blit(fontsmall.render(f"X Speed {self.selected_speed[0]}", True, "White"), (302, 375))
    #screen.blit(fontsmall.render(f"Y Speed {self.selected_speed[1]}", True, "White"), (302, 420))
    
    if k_down: self.selected_itemy += 1 + (int(k_y) * 4); scrolldown_sfx.play()
    if k_up: self.selected_itemy -= 1 + (int(k_y) * 4); scrollup_sfx.play()
    if self.selected_itemy < 0: self.selected_itemy = len(self.images) - 1
    if self.selected_itemy > len(self.images) - 1: self.selected_itemy = 0
    if k_back: self.gamestate = self.remember_gs

  def cs_condition(self):
    if k_back: self.gamestate = 24
    pygame.draw.rect(screen, (0, 0, 50), ((50, 20), (WIDTH - 100, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((50, 20), (WIDTH - 100, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render("Set Up Condition", True, "White"), (53, 32))
    
    main.buttons[47] = [button for button in main.buttons[47] if button.button_type != "Boolean"]

    if "Stat" in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].conditions:
      width, height = 0, 0
      for stat in (stat for stat in main.game_stats if main.game_stats[stat] == bool):
        text = fontsmaller.render(stat + ",", True, "White")
        if width + text.get_width() > WIDTH / 1.3: height += 16; width = 0
        width += text.get_width() + 10
        main.buttons[47].append(Button(45 + width - text.get_width(), 320 + height, text.get_width() + 7, 16, "Set Action for a Condition", stat, select_scene_bool_condition, target=stat, text_color="Light Yellow", font=fontsmaller, button_type="Boolean"))

  def shader_library(self):
    for index in range(30):
      if index % 2 == 0: pygame.draw.rect(screen, (0, 0, 50), ((0, 45 + (index * 26)), (WIDTH, 26)))
      else: pygame.draw.rect(screen, (0, 0, 20), ((0, 45 + (index * 26)), (WIDTH, 26)))
    for index, shader in enumerate(self.shaders[minint(self.selected_itemy - 10, 0):]):
      try:
        if self.shaders[self.selected_itemy] == shader: screen.blit(fontsmall.render(shader, True, "Yellow"), (1, 50 + (index * 26)))
        else: screen.blit(fontsmall.render(shader, True, "White"), (1, 50 + (index * 26)))
      except: self.selected_itemy = 0

    room_margin = 250
    pygame.draw.rect(screen, (0, 0, 50), ((WIDTH - room_margin, 0), (room_margin, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((WIDTH - room_margin, 0), (2, HEIGHT)))
    if len(self.shaders):
      try:
        screen.blit(fontmedium.render(self.shaders[self.selected_itemy], True, "White"), (room_margin + 30, 16))
        screen.blit(pygame.transform.scale(pygame.image.load("Assets/editor/text file.png").convert_alpha(), (128, 128)), (room_margin + 32, 64))

        uniforms = "Uniforms:\n"
        with open(main.active_directory + "Shaders/" + main.shaders[main.selected_itemy], "r", encoding="utf-8") as file: shader_code = file.read()
        if "uniform float time;" in shader_code: uniforms += "  time (float)\n"
        if "uniform vec2 resolution;" in shader_code: uniforms += "  resolution (vec2)\n"
        if "uniform vec2 mouse;" in shader_code: uniforms += "  mouse (vec2)\n"
        if "uniform vec2 cam_pos;" in shader_code: uniforms += "  cam_pos (vec2)\n"
        if "uniform float random;" in shader_code: uniforms += "  random (float)\n"
        if "uniform float random_const;" in shader_code: uniforms += "  random_const (float)\n"
        if "uniform int player_amount;" in shader_code: uniforms += "  player_amount (int)\n"
        if "uniform int player_in_amount;" in shader_code: uniforms += "  player_in_amount (int)\n"
        if "uniform int menu_item;" in shader_code: uniforms += "  menu_item (int)\n"
        screen.blit(fontsmall.render(uniforms, True, "White"), (room_margin + 30, 200))

      except: screen.blit(fontmedium.render("Select a glsl, frag or\ntxt file", True, "White"), (room_margin + 30, 16))
    else: screen.blit(fontmedium.render("No shaders imported", True, "White"), (room_margin + 30, 16))

    screen.blit(fontmedium.render("Shader Library", True, "White"), (0, 16))
    self.page_amount = 1
    if k_down: self.selected_itemy += 1 + (int(k_y) * 4); scrolldown_sfx.play()
    if k_up: self.selected_itemy -= 1 + (int(k_y) * 4); scrollup_sfx.play()
    if self.selected_itemy < 0: self.selected_itemy = len(self.shaders) - 1
    if self.selected_itemy > len(self.shaders) - 1: self.selected_itemy = 0
    if k_back: self.gamestate = self.remember_gs
  
  def projectile_library(self):
    for index in range(30):
      if index % 2 == 0: pygame.draw.rect(screen, (0, 0, 50), ((0, 45 + (index * 26)), (WIDTH, 26)))
      else: pygame.draw.rect(screen, (0, 0, 20), ((0, 45 + (index * 26)), (WIDTH, 26)))
    for index, proj in enumerate(self.projectiles[minint(self.selected_itemy - 10, 0):]):
      try:
        if len(self.projectiles[self.selected_itemy].images):
          if self.projectiles[self.selected_itemy] == proj: screen.blit(fontsmall.render(proj.name, True, "Yellow"), (1, 50 + (index * 26)))
          else: screen.blit(fontsmall.render(proj.name, True, "White"), (1, 50 + (index * 26)))
        else:
          if self.projectiles[self.selected_itemy] == proj: screen.blit(fontsmall.render(proj.name, True, "Yellow"), (1, 50 + (index * 26)))
          else: screen.blit(fontsmall.render(proj.name, True, "White"), (1, 50 + (index * 26)))
      except: self.selected_itemy = 0

    room_margin = 250
    pygame.draw.rect(screen, (0, 0, 50), ((WIDTH - room_margin, 0), (room_margin, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((WIDTH - room_margin, 0), (2, HEIGHT)))
    if len(self.projectiles):
      try:
        if len(self.projectiles[self.selected_itemy].images) and type(self.projectiles[self.selected_itemy].images) == tuple:
          if len(self.projectiles[self.selected_itemy].images) and type(self.projectiles[self.selected_itemy].images) == list:
            try: img = self.projectiles[self.selected_itemy].images[self.bg_frame_timer.keep_count(3 + (int(k_y) * 30), len(self.projectiles[self.selected_itemy].images), 0)]
            except IndexError: self.bg_frame_timer.tally = 0; img = self.projectiles[self.selected_itemy].images[0]
            if len(self.chr_projectiles[self.selected_itemy]) < 20: screen.blit(fontmedium.render(f"{self.chr_projectiles[self.selected_itemy]}", True, "White"), (room_margin + 30, 16))
            elif len(self.chr_projectiles[self.selected_itemy]) < 28: screen.blit(fontsmall.render(f"{self.chr_projectiles[self.selected_itemy]}", True, "White"), (room_margin + 30, 18))
            elif len(self.chr_projectiles[self.selected_itemy]) < 37: screen.blit(fontlittle.render(f"{self.chr_projectiles[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
            else: screen.blit(fontsmaller.render(f"{self.chr_projectiles[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
            screen.blit(fontsmall.render(f"Scale: {img.get_width()}:{img.get_height()}", True, "White"), (room_margin + 20, 265))
            screen.blit(fontsmall.render(f"Pitch: {img.get_pitch()}", True, "White"), (room_margin + 20, 295))
            screen.blit(fontsmall.render(f"Total Frames: {len(self.chr_projectiles[self.selected_itemy])}", True, "White"), (room_margin + 20, 325))
            #screen.blit(fontsmall.render(f"Metadata: {img}", True, "White"), (room_margin + 20, 230))
            screen.blit(pygame.transform.scale(img, (WIDTH / 2.42, HEIGHT / 2.42)), (room_margin + 32, 64))
          else:
            if len(self.projectiles[self.selected_itemy].name) < 20: screen.blit(fontmedium.render(f"{self.projectiles[self.selected_itemy].name}", True, "White"), (room_margin + 30, 16))
            elif len(self.projectiles[self.selected_itemy].name) < 28: screen.blit(fontsmall.render(f"{self.projectiles[self.selected_itemy].name}", True, "White"), (room_margin + 30, 18))
            elif len(self.projectiles[self.selected_itemy].name) < 37: screen.blit(fontlittle.render(f"{self.projectiles[self.selected_itemy].name}", True, "White"), (room_margin + 30, 20))
            else: screen.blit(fontsmaller.render(f"{self.projectiles[self.selected_itemy].name}", True, "White"), (room_margin + 30, 20))
            width, height = self.projectiles[self.selected_itemy].images[0].get_width(), self.projectiles[self.selected_itemy].images[0].get_height()
            screen.blit(fontsmall.render(f"Scale: {width}:{height}", True, "White"), (room_margin + 20, 265))
            screen.blit(fontsmall.render(f"Pitch: {self.projectiles[self.selected_itemy].images[0].get_pitch()}", True, "White"), (room_margin + 20, 295))
            screen.blit(fontsmall.render(f"Set Amount: {len(self.projectiles[self.selected_itemy])}", True, "White"), (room_margin + 20, 325))
            for index, image in enumerate(self.projectiles[self.selected_itemy].images): screen.blit(pygame.image.load(self.active_directory + "Assets/projectiles/" + image).convert_alpha(), (room_margin + 32 + (index * width), 64))
        else:
          if len(self.projectiles[self.selected_itemy].name) < 20: screen.blit(fontmedium.render(f"{self.projectiles[self.selected_itemy].name}", True, "White"), (room_margin + 30, 16))
          elif len(self.projectiles[self.selected_itemy].name) < 28: screen.blit(fontsmall.render(f"{self.projectiles[self.selected_itemy].name}", True, "White"), (room_margin + 30, 18))
          elif len(self.projectiles[self.selected_itemy].name) < 37: screen.blit(fontlittle.render(f"{self.projectiles[self.selected_itemy].name}", True, "White"), (room_margin + 30, 20))
          else: screen.blit(fontsmaller.render(f"{self.projectiles[self.selected_itemy].name}", True, "White"), (room_margin + 30, 20))
          screen.blit(fontsmall.render(f"Scale: {self.projectiles[self.selected_itemy].image.get_width()}:{self.projectiles[self.selected_itemy].image.get_height()}", True, "White"), (room_margin + 20, 265))
          screen.blit(fontsmall.render(f"Pitch: {self.projectiles[self.selected_itemy].image.get_pitch()}", True, "White"), (room_margin + 20, 295))
          #screen.blit(fontsmall.render(f"Metadata: {img}", True, "White"), (room_margin + 20, 230))
          screen.blit(pygame.transform.scale(self.projectiles[self.selected_itemy].image, (WIDTH / 2.42, HEIGHT / 2.42)), (room_margin + 32, 64))
      except Exception as e: screen.blit(fontsmall.render("Something went wrong,\nCheck the console for info", True, "White"), (room_margin + 30, 16)); print(e)
    else: screen.blit(fontmedium.render("No Projectiles Created", True, "White"), (room_margin + 30, 16))

    screen.blit(fontmedium.render("Projectiles", True, "White"), (0, 16))

    #screen.blit(fontsmall.render(f"Distance {self.selected_value}", True, "White"), (302, 330))
    #screen.blit(fontsmall.render(f"X Speed {self.selected_speed[0]}", True, "White"), (302, 375))
    #screen.blit(fontsmall.render(f"Y Speed {self.selected_speed[1]}", True, "White"), (302, 420))
    
    if k_down: self.selected_itemy += 1 + (int(k_y) * 4); scrolldown_sfx.play()
    if k_up: self.selected_itemy -= 1 + (int(k_y) * 4); scrollup_sfx.play()
    if self.selected_itemy < 0: self.selected_itemy = len(self.projectiles) - 1
    if self.selected_itemy > len(self.projectiles) - 1: self.selected_itemy = 0
    if k_back: self.gamestate = self.remember_gs

  def projectile_editor(self):
    if k_back: self.gamestate = 49
    if len(self.projectiles):
      pygame.draw.rect(screen, (0, 0, 50), ((25, 20), (WIDTH - 25, HEIGHT - 40)))
      pygame.draw.rect(screen, "Dark Blue", ((25, 20), (WIDTH - 25, HEIGHT - 40)), width=2)
      screen.blit(fontmedium.render(f"Edit Projectile", True, "White"), (53, 32))
      screen.blit(fontsmall.render(f"X Speed {self.projectiles[self.selected_itemy].speed[0]}", True, "White"), (66, 75))
      screen.blit(fontsmall.render(f"Y Speed {self.projectiles[self.selected_itemy].speed[1]}", True, "White"), (66, 115))
      screen.blit(fontsmall.render(f"Lifespan {self.projectiles[self.selected_itemy].lifespan}", True, "White"), (66, 155))
      screen.blit(fontsmall.render(f"Frame {self.projectiles[self.selected_itemy].anim_speed}", True, "White"), (66, 195))
      screen.blit(fontlittle.render(f"X Min Spawn {self.projectiles[self.selected_itemy].set_pos_min_range[0]}", True, "White"), (60, 239))
      screen.blit(fontlittle.render(f"X Max Spawn {self.projectiles[self.selected_itemy].set_pos_max_range[0]}", True, "White"), (60, 279))
      screen.blit(fontlittle.render(f"Y Min Spawn {self.projectiles[self.selected_itemy].set_pos_min_range[1]}", True, "White"), (60, 319))
      screen.blit(fontlittle.render(f"Y Max Spawn {self.projectiles[self.selected_itemy].set_pos_max_range[1]}", True, "White"), (60, 359))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.projectiles[self.selected_itemy].deal_again], True, "White"), (30, HEIGHT - 70))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.projectiles[self.selected_itemy].pierce], True, "White"), (64, HEIGHT - 70))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.projectiles[self.selected_itemy].stoppable], True, "White"), (98, HEIGHT - 70))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.projectiles[self.selected_itemy].returnable], True, "White"), (132, HEIGHT - 70))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.projectiles[self.selected_itemy].stop_at_collision], True, "White"), (166, HEIGHT - 70))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.projectiles[self.selected_itemy].die_at_collision], True, "White"), (200, HEIGHT - 70))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.projectiles[self.selected_itemy].oscil_ease], True, "White"), (234, HEIGHT - 70))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.projectiles[self.selected_itemy].guided], True, "White"), (268, HEIGHT - 70))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.projectiles[self.selected_itemy].beam], True, "White"), (302, HEIGHT - 70))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.projectiles[self.selected_itemy].directional_relative], True, "White"), (336, HEIGHT - 70))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.projectiles[self.selected_itemy].bounce], True, "White"), (370, HEIGHT - 70))
      screen.blit(fontlittle.render({True: "On", False: "Off"}[self.projectiles[self.selected_itemy].around_platform], True, "White"), (404, HEIGHT - 70))
      screen.blit(fontsmall.render(f"Oscillation {self.projectiles[self.selected_itemy].oscil_speed}", True, "White"), (222, 75))
      screen.blit(fontsmall.render(f"Frequency {self.projectiles[self.selected_itemy].frequency}", True, "White"), (222, 115))
      screen.blit(fontsmall.render(f"Vibrate {self.projectiles[self.selected_itemy].vibrate}", True, "White"), (222, 155))
      screen.blit(fontsmall.render(f"Weight X {self.projectiles[self.selected_itemy].weight[0]}", True, "White"), (222, 195))
      screen.blit(fontsmall.render(f"Weight Y {self.projectiles[self.selected_itemy].weight[1]}", True, "White"), (222, 235))
      if self.projectiles[self.selected_itemy].apply_weight_after > 0: screen.blit(fontlittle.render(f"Apply After {self.projectiles[self.selected_itemy].apply_weight_after}", True, "White"), (222, 276))
      else: screen.blit(fontlittle.render(f"Always Apply", True, "White"), (222, 276))
      screen.blit(fontlittle.render(f"Stop X After {self.projectiles[self.selected_itemy].stop_motion_after[0]}", True, "White"), (386, 79))
      screen.blit(fontlittle.render(f"Stop Y After {self.projectiles[self.selected_itemy].stop_motion_after[1]}", True, "White"), (386, 119))
      screen.blit(fontlittle.render(f"Stop X For {self.projectiles[self.selected_itemy].stop_motion_for[0]}", True, "White"), (386, 159))
      screen.blit(fontlittle.render(f"Stop Y For {self.projectiles[self.selected_itemy].stop_motion_for[1]}", True, "White"), (386, 199))
    else: self.gamestate = 49

  def projectile_image_library(self):
    for index in range(30):
      if index % 2 == 0: pygame.draw.rect(screen, (0, 0, 50), ((0, 45 + (index * 26)), (WIDTH, 26)))
      else: pygame.draw.rect(screen, (0, 0, 20), ((0, 45 + (index * 26)), (WIDTH, 26)))
    for index, image in enumerate(self.chr_projectiles[minint(self.selected_itemy - 10, 0):]):
      try:
        if type(image) == list:
          if self.chr_projectiles[self.selected_itemy] == image: screen.blit(fontsmall.render(image[0][:-5], True, "Yellow"), (1, 50 + (index * 26)))
          else: screen.blit(fontsmall.render(image[0][:-5], True, "White"), (1, 50 + (index * 26)))
        else:
          if self.chr_projectiles[self.selected_itemy] == image: screen.blit(fontsmall.render(image, True, "Yellow"), (1, 50 + (index * 26)))
          else: screen.blit(fontsmall.render(image, True, "White"), (1, 50 + (index * 26)))
      except: self.selected_itemy = 0      

    room_margin = 250
    pygame.draw.rect(screen, (0, 0, 50), ((WIDTH - room_margin, 0), (room_margin, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((WIDTH - room_margin, 0), (2, HEIGHT)))
    if len(self.chr_projectiles):
      try:
        if type(self.chr_projectiles[self.selected_itemy]) != list:
          if os.path.isdir(self.active_directory + "Assets/projectiles/" + self.chr_projectiles[self.selected_itemy]):
            self.animated_bg_images = sorted(os.listdir(self.active_directory + "Assets/projectiles/" + self.chr_projectiles[self.selected_itemy] + "/"), key=extract_number)
            try: img = pygame.image.load(self.active_directory + "Assets/projectiles/" + self.chr_projectiles[self.selected_itemy] + "/" + self.animated_bg_images[self.bg_frame_timer.keep_count(3 + (int(k_y) * 30), len(self.animated_bg_images), 0)]).convert_alpha()
            except IndexError: self.bg_frame_timer.tally = 0; img = pygame.image.load(self.active_directory + "Assets/projectiles/" + self.chr_projectiles[self.selected_itemy] + "/" + self.animated_bg_images[0]).convert_alpha()
            if len(self.chr_projectiles[self.selected_itemy]) < 20: screen.blit(fontmedium.render(f"{self.chr_projectiles[self.selected_itemy]}", True, "White"), (room_margin + 30, 16))
            elif len(self.chr_projectiles[self.selected_itemy]) < 28: screen.blit(fontsmall.render(f"{self.chr_projectiles[self.selected_itemy]}", True, "White"), (room_margin + 30, 18))
            elif len(self.chr_projectiles[self.selected_itemy]) < 37: screen.blit(fontlittle.render(f"{self.chr_projectiles[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
            else: screen.blit(fontsmaller.render(f"{self.chr_projectiles[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
            screen.blit(fontsmall.render(f"Scale: {img.get_width()}:{img.get_height()}", True, "White"), (room_margin + 20, 265))
            screen.blit(fontsmall.render(f"Pitch: {img.get_pitch()}", True, "White"), (room_margin + 20, 295))
            screen.blit(fontsmall.render(f"Total Frames: {len(self.chr_projectiles[self.selected_itemy])}", True, "White"), (room_margin + 20, 325))
            #screen.blit(fontsmall.render(f"Metadata: {img}", True, "White"), (room_margin + 20, 230))
            screen.blit(pygame.transform.scale(img, (WIDTH / 2.42, HEIGHT / 2.42)), (room_margin + 32, 64))
          else:
            img = pygame.image.load(self.active_directory + "Assets/projectiles/" + self.chr_projectiles[self.selected_itemy]).convert_alpha()
            if len(self.chr_projectiles[self.selected_itemy]) < 20: screen.blit(fontmedium.render(f"{self.chr_projectiles[self.selected_itemy]}", True, "White"), (room_margin + 30, 16))
            elif len(self.chr_projectiles[self.selected_itemy]) < 28: screen.blit(fontsmall.render(f"{self.chr_projectiles[self.selected_itemy]}", True, "White"), (room_margin + 30, 18))
            elif len(self.chr_projectiles[self.selected_itemy]) < 37: screen.blit(fontlittle.render(f"{self.chr_projectiles[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
            else: screen.blit(fontsmaller.render(f"{self.chr_projectiles[self.selected_itemy]}", True, "White"), (room_margin + 30, 20))
            screen.blit(fontsmall.render(f"Scale: {img.get_width()}:{img.get_height()}", True, "White"), (room_margin + 20, 265))
            screen.blit(fontsmall.render(f"Pitch: {img.get_pitch()}", True, "White"), (room_margin + 20, 295))
            #screen.blit(fontsmall.render(f"Metadata: {img}", True, "White"), (room_margin + 20, 230))
            screen.blit(pygame.transform.scale(img, (WIDTH / 2.42, HEIGHT / 2.42)), (room_margin + 32, 64))
        else:
          if len(self.chr_projectiles[self.selected_itemy][0][:-1]) < 20: screen.blit(fontmedium.render(f"{self.chr_projectiles[self.selected_itemy][0][:-5]}", True, "White"), (room_margin + 30, 16))
          elif len(self.chr_projectiles[self.selected_itemy][0][:-1]) < 28: screen.blit(fontsmall.render(f"{self.chr_projectiles[self.selected_itemy][0][:-5]}", True, "White"), (room_margin + 30, 18))
          elif len(self.chr_projectiles[self.selected_itemy][0][:-1]) < 37: screen.blit(fontlittle.render(f"{self.chr_projectiles[self.selected_itemy][0][:-5]}", True, "White"), (room_margin + 30, 20))
          else: screen.blit(fontsmaller.render(f"{self.chr_projectiles[self.selected_itemy][0][:-1]}", True, "White"), (room_margin + 30, 20))
          width, height = pygame.image.load(self.active_directory + "Assets/projectiles/" + self.chr_projectiles[self.selected_itemy][0]).convert_alpha().get_width(), pygame.image.load(self.active_directory + "Assets/projectiles/" + self.chr_projectiles[self.selected_itemy][0]).convert_alpha().get_height()
          screen.blit(fontsmall.render(f"Scale: {width}:{height}", True, "White"), (room_margin + 20, 265))
          screen.blit(fontsmall.render(f"Pitch: {pygame.image.load(self.active_directory + 'Assets/projectiles/' + self.chr_projectiles[self.selected_itemy][0]).convert_alpha().get_pitch()}", True, "White"), (room_margin + 20, 295))
          screen.blit(fontsmall.render(f"Set Amount: {len(self.chr_projectiles[self.selected_itemy])}", True, "White"), (room_margin + 20, 325))
          for index, image in enumerate(self.chr_projectiles[self.selected_itemy]): screen.blit(pygame.image.load(self.active_directory + "Assets/projectiles/" + image).convert_alpha(), (room_margin + 32 + (index * width), 64))
      except Exception as e: screen.blit(fontmedium.render("Select a image file", True, "White"), (room_margin + 30, 16)); print(e)
    else: screen.blit(fontmedium.render("No images imported", True, "White"), (room_margin + 30, 16))

    screen.blit(fontmedium.render("Projectiles Library", True, "White"), (0, 16))

    #screen.blit(fontsmall.render(f"Distance {self.selected_value}", True, "White"), (302, 330))
    #screen.blit(fontsmall.render(f"X Speed {self.selected_speed[0]}", True, "White"), (302, 375))
    #screen.blit(fontsmall.render(f"Y Speed {self.selected_speed[1]}", True, "White"), (302, 420))
    
    if k_down: self.selected_itemy += 1 + (int(k_y) * 4); scrolldown_sfx.play()
    if k_up: self.selected_itemy -= 1 + (int(k_y) * 4); scrollup_sfx.play()
    if self.selected_itemy < 0: self.selected_itemy = len(self.chr_projectiles) - 1
    if self.selected_itemy > len(self.chr_projectiles) - 1: self.selected_itemy = 0
    if k_back: self.gamestate = self.remember_gs

  def edit_bossfight(self):
    if k_back: self.gamestate = 23
    pygame.draw.rect(screen, (0, 0, 50), ((25, 20), (WIDTH - 25, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((25, 20), (WIDTH - 25, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render(f"Edit Bossfight", True, "White"), (30, 32))
    screen.blit(fontsmall.render(f"Wave 1", True, "White"), (30, 60))
    screen.blit(fontsmall.render(f"Wave 2", True, "White"), (30, 150))
    screen.blit(fontsmall.render(f"Wave 3", True, "White"), (30, 240))
    screen.blit(fontsmall.render(f"Wave 4", True, "White"), (30, 330))

  def edit_tile_types(self):
    if k_back: self.gamestate = 2
    screen.fill((0, 0, 50))
    pygame.draw.rect(screen, (0, 0, 75), ((262, 0), (250, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((262, 0), (250, HEIGHT)), width=2)
    if self.tile_types:
      if len(self.tile_types[self.selected_tile_type]["img"]) < 20: screen.blit(fontmedium.render(self.tile_types[self.selected_tile_type]["img"], True, "White"), (265, 4))
      elif len(self.tile_types[self.selected_tile_type]["img"]) < 28: screen.blit(fontsmall.render(self.tile_types[self.selected_tile_type]["img"], True, "White"), (265, 6))
      elif len(self.tile_types[self.selected_tile_type]["img"]) < 37: screen.blit(fontlittle.render(self.tile_types[self.selected_tile_type]["img"], True, "White"), (265, 8))
      else: screen.blit(fontsmaller.render(self.tile_types[self.selected_tile_type]["img"], True, "White"), (265, 8))
      
      if "anim" in self.tile_types[self.selected_tile_type]["flags"]: image = pygame.image.load(self.active_directory + "Assets/tiles/" + self.tile_types[self.selected_tile_type]["img"] + "/" + str(self.frame_timer.keep_count(self.tile_types[self.selected_tile_type]['anim_s'], len(os.listdir(self.active_directory + "Assets/tiles/" + self.tile_types[self.selected_tile_type]["img"])) + 1, 1)) + ".png").convert_alpha()
      else: image = pygame.image.load(self.active_directory + "Assets/tiles/" + self.tile_types[self.selected_tile_type]["img"]).convert_alpha()
      pygame.draw.rect(screen, "Black", ((270, 30), (image.get_width() + 20, image.get_height() + 20)))
      screen.blit(image, (280, 40))
      pygame.draw.rect(screen, "Red", ((280 + self.tile_types[self.selected_tile_type]["off"][0], 40 + self.tile_types[self.selected_tile_type]["off"][1]), (self.tile_types[self.selected_tile_type]["size"][0], self.tile_types[self.selected_tile_type]["size"][1])), width=2)

      screen.blit(fontsmall.render("X Offset " + str(self.tile_types[self.selected_tile_type]["off"][0]), True, "White"), (392, 38))
      screen.blit(fontsmall.render("Y Offset " + str(self.tile_types[self.selected_tile_type]["off"][1]), True, "White"), (392, 72))
      screen.blit(fontsmall.render("Width " + str(self.tile_types[self.selected_tile_type]["size"][0]), True, "White"), (392, 106))
      screen.blit(fontsmall.render("Height " + str(self.tile_types[self.selected_tile_type]["size"][1]), True, "White"), (392, 140))

      if self.tile_types[self.selected_tile_type]["hp"] != -1: screen.blit(fontsmall.render(f"HP {self.tile_types[self.selected_tile_type]['hp']}", True, "White"), (304, 182))
      else: screen.blit(fontlittle.render("Indestructible", True, "White"), (302, 182))
      screen.blit(fontsmall.render(f"Team {self.tile_types[self.selected_tile_type]['team']}", True, "White"), (304, 212))
      screen.blit(fontsmaller.render("Bump on " + {True: "On", False: "Off"}["dihb" in self.tile_types[self.selected_tile_type]["flags"]] + "\n\nStood on " + {True: "On", False: "Off"}["diso" in self.tile_types[self.selected_tile_type]["flags"]], True, "White"), (348, HEIGHT - 200))
      if type(self.tile_types[self.selected_tile_type]["step_sfx"]) == list: screen.blit(fontlittle.render("Footstep SFX " + self.tile_types[self.selected_tile_type]["step_sfx"][0][:-5], True, "White"), (310, HEIGHT - 154))
      else: screen.blit(fontlittle.render("Footstep SFX " + self.tile_types[self.selected_tile_type]["step_sfx"], True, "White"), (310, HEIGHT - 154))
      if type(self.tile_types[self.selected_tile_type]["destr_sfx"]) == list: screen.blit(fontlittle.render("Destroy SFX " + self.tile_types[self.selected_tile_type]["destr_sfx"][0][:-5], True, "White"), (310, HEIGHT - 122))
      else: screen.blit(fontlittle.render("Destroy SFX " + self.tile_types[self.selected_tile_type]["destr_sfx"], True, "White"), (310, HEIGHT - 122))
      screen.blit(fontsmall.render(f"Frame R {self.tile_types[self.selected_tile_type]['anim_s']}", True, "White"), (304, HEIGHT - 103))

      for x, flag in enumerate(("solid", "ice", "flat")):
        screen.blit(fontlittle.render({True: "On", False: "Off"}[flag in self.tile_types[self.selected_tile_type]["flags"]], True, "White"), (WIDTH - (35 + (x * 34)), HEIGHT - 48))
    else: screen.blit(fontsmall.render("No Tiles Imported", True, "White"), (265, 6))

  def edit_character_types(self):
    if k_back: self.gamestate = 2
    screen.fill((0, 0, 50))
    pygame.draw.rect(screen, (0, 0, 75), ((262, 0), (250, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((262, 0), (250, HEIGHT)), width=2)
    if self.character_types:
      if len(self.character_types[self.selected_character_type]["type"]) < 20: screen.blit(fontmedium.render(self.character_types[self.selected_character_type]["type"], True, "White"), (265, 4))
      elif len(self.character_types[self.selected_character_type]["type"]) < 28: screen.blit(fontsmall.render(self.character_types[self.selected_character_type]["type"], True, "White"), (265, 6))
      elif len(self.character_types[self.selected_character_type]["type"]) < 37: screen.blit(fontlittle.render(self.character_types[self.selected_character_type]["type"], True, "White"), (265, 8))
      else: screen.blit(fontsmaller.render(self.character_types[self.selected_character_type]["type"], True, "White"), (265, 8))
    
      if "td" in self.character_types[self.selected_character_type]["flags"]: image = pygame.image.load(self.active_directory + "Assets/characters/" + self.character_types[self.selected_character_type]["type"] + "/" + self.dir_preview_mode + "/idle/1.png").convert_alpha()
      else: image = pygame.image.load(self.active_directory + "Assets/characters/" + self.character_types[self.selected_character_type]["type"] + "/idle/1.png").convert_alpha()
      screen.blit(image, (280, 40))
      
      screen.blit(fontsmall.render(f"Speed {self.character_types[self.selected_character_type]['object'].speed}", True, "White"), (308, 118))
      screen.blit(fontsmall.render(f"Leap {-self.character_types[self.selected_character_type]['object'].jump_force}", True, "White"), (308, 158))
      screen.blit(fontsmaller.render({True: "On", False: "Off"}["wallslide" in self.character_types[self.selected_character_type]["flags"]], True, "White"), (WIDTH - 32, 142))
      if type(self.character_types[self.selected_character_type]["object"].jump_sound) == list: screen.blit(fontlittle.render("Jump SFX " + self.character_types[self.selected_character_type]["object"].jump_sound[0][:-5], True, "White"), (310, HEIGHT - 246))
      else: screen.blit(fontlittle.render("Jump SFX " + self.character_types[self.selected_character_type]["object"].jump_sound, True, "White"), (310, HEIGHT - 246))
      if type(self.character_types[self.selected_character_type]["object"].land_sound) == list: screen.blit(fontlittle.render("Land SFX " + self.character_types[self.selected_character_type]["object"].land_sound[0][:-5], True, "White"), (310, HEIGHT - 214))
      else: screen.blit(fontlittle.render("Land SFX " + self.character_types[self.selected_character_type]["object"].land_sound, True, "White"), (310, HEIGHT - 214))
      if type(self.character_types[self.selected_character_type]["object"].beat_sound) == list: screen.blit(fontlittle.render("Beat SFX " + self.character_types[self.selected_character_type]["object"].beat_sound[0][:-5], True, "White"), (310, HEIGHT - 182))
      else: screen.blit(fontlittle.render("Beat SFX " + self.character_types[self.selected_character_type]["object"].beat_sound, True, "White"), (310, HEIGHT - 182))
      if type(self.character_types[self.selected_character_type]["object"].hurt_sound) == list: screen.blit(fontlittle.render("Hurt SFX " + self.character_types[self.selected_character_type]["object"].hurt_sound[0][:-5], True, "White"), (310, HEIGHT - 150))
      else: screen.blit(fontlittle.render("Hurt SFX " + self.character_types[self.selected_character_type]["object"].hurt_sound, True, "White"), (310, HEIGHT - 150))
      if type(self.character_types[self.selected_character_type]["object"].defeat_sound) == list: screen.blit(fontlittle.render("Defeat SFX " + self.character_types[self.selected_character_type]["object"].defeat_sound[0][:-5], True, "White"), (310, HEIGHT - 118))
      else: screen.blit(fontlittle.render("Defeat SFX " + self.character_types[self.selected_character_type]["object"].defeat_sound, True, "White"), (310, HEIGHT - 118))
    else: screen.blit(fontsmall.render("No Characters Imported", True, "White"), (265, 6))

    #if self.character_types[self.selected_character_type]["hp"] != -1: screen.blit(fontsmall.render(f"HP {self.character_types[self.selected_character_type]['hp']}", True, "White"), (304, 182))
    #else: screen.blit(fontlittle.render(f"Invincible", True, "White"), (302, 182))

  def edit_collectible_types(self):
    if k_back: self.gamestate = 2
    screen.fill((0, 0, 50))
    pygame.draw.rect(screen, (0, 0, 75), ((262, 0), (250, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((262, 0), (250, HEIGHT)), width=2)
    if self.collectible_types:
      if len(self.collectible_types[self.selected_collectible_type]["img"]) < 20: screen.blit(fontmedium.render(self.collectible_types[self.selected_collectible_type]["img"], True, "White"), (265, 4))
      elif len(self.collectible_types[self.selected_collectible_type]["img"]) < 28: screen.blit(fontsmall.render(self.collectible_types[self.selected_collectible_type]["img"], True, "White"), (265, 6))
      elif len(self.collectible_types[self.selected_collectible_type]["img"]) < 37: screen.blit(fontlittle.render(self.collectible_types[self.selected_collectible_type]["img"], True, "White"), (265, 8))
      else: screen.blit(fontsmaller.render(self.collectible_types[self.selected_collectible_type]["img"], True, "White"), (265, 8))
      
      image = pygame.image.load(self.active_directory + "Assets/collectibles/" + self.collectible_types[self.selected_collectible_type]["img"] + "/" + str(self.frame_timer.keep_count(self.collectible_types[self.selected_collectible_type]["anim_s"], len(os.listdir(self.active_directory + "Assets/collectibles/" + self.collectible_types[self.selected_collectible_type]["img"])) + 1, 1)) + ".png").convert_alpha()
      pygame.draw.rect(screen, "Black", ((270, 30), (image.get_width() + 20, image.get_height() + 20)))
      screen.blit(image, (280, 40))
      pygame.draw.rect(screen, "Red", ((280 + self.collectible_types[self.selected_collectible_type]["off"][0], 40 + self.collectible_types[self.selected_collectible_type]["off"][1]), (self.collectible_types[self.selected_collectible_type]["size"][0], self.collectible_types[self.selected_collectible_type]["size"][1])), width=2)

      for button in self.buttons[55]:
        if button.button_type == "Stat" or button.button_type == "Value": self.buttons[55].remove(button)
      for button in self.buttons[55]:
        if button.button_type == "Stat" or button.button_type == "Value": self.buttons[55].remove(button)

      width = 0; height = 0
      if self.collectible_types[self.selected_collectible_type]["stat"]:
        if main.game_stats[self.collectible_types[self.selected_collectible_type]["stat"]] == int or main.game_stats[self.collectible_types[self.selected_collectible_type]["stat"]] == float:
          for x, button in enumerate([(l[lg]["Decrease"], "less", change_collectible_value, -1), (l[lg]["Increase"], "more", change_collectible_value, 1)]):
            main.buttons[55].append(Button(270 + (x * 180), HEIGHT - 296, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3], button_type="Value"))
          screen.blit(fontmedium.render(str(self.collectible_types[self.selected_collectible_type]["value"]), True, "White"), (365, HEIGHT - 292))
        if main.game_stats[self.collectible_types[self.selected_collectible_type]["stat"]] == float:
          for x, button in enumerate([(l[lg]["Decrease Decimal"], "less", change_collectible_value, -0.25), (l[lg]["Increase Decimal"], "more", change_collectible_value, 0.25)]):
            main.buttons[55].append(Button(302 + (x * 132), HEIGHT - 288, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3], button_type="Value"))
        if main.game_stats[self.collectible_types[self.selected_collectible_type]["stat"]] == bool:
          for x, button in enumerate(["True", "False", "Negate"]):
            main.buttons[55].append(Button(270 + (x * 64), HEIGHT - 296, 64, 22, "Set as " + {"True": "True", "False": "False", "Negate": "Negation"}[button], button, change_collectible_bool, button, font=fontsmall, button_type="Value"))
      for stat in main.game_stats:
        text = fontsmaller.render(stat + ",", True, "White")
        if width + 120 + text.get_width() > WIDTH - 150: height += 16; width = 0
        width += text.get_width() + 10
        main.buttons[55].append(Button(260 + width - text.get_width(), (HEIGHT - 255) + height, text.get_width() + 7, 16, l[lg]["Use Stat"], stat, set_collectible_stat, target=stat, text_color={int: "Light blue", bool: "Light Yellow", str: "Pink", float: "Light Green"}[main.game_stats[stat]], font=fontsmaller, button_type="Stat"))

      screen.blit(fontlittle.render("Pickup SFX: " + self.collectible_types[self.selected_collectible_type]["sfx"], True, "White"), (308, HEIGHT - 92))
      screen.blit(fontlittle.render("Debt Drop SFX: " + self.collectible_types[self.selected_collectible_type]["debt_sfx"], True, "White"), (308, HEIGHT - 58))
      screen.blit(fontlittle.render("Insufficient SFX: " + self.collectible_types[self.selected_collectible_type]["blocked_sfx"], True, "White"), (308, HEIGHT - 24))

      if self.collectible_types[self.selected_collectible_type]['anim_s'] > 0: screen.blit(fontlittle.render(f"Frame Speed {self.collectible_types[self.selected_collectible_type]['anim_s']}", True, "White"), (308, 118))
      elif self.collectible_types[self.selected_collectible_type]['anim_s'] == 0: screen.blit(fontlittle.render(f"Don't Animate", True, "White"), (308, 118))
      else: screen.blit(fontlittle.render("Random Frame", True, "White"), (308, 118))

    else: screen.blit(fontsmall.render("No Collectibles Imported", True, "White"), (265, 6))

  def edit_entities(self):
    if k_back: self.gamestate = 54
    screen.fill((0, 0, 50))
    pygame.draw.rect(screen, (0, 0, 75), ((262, 0), (250, HEIGHT)))
    pygame.draw.rect(screen, "Dark Blue", ((262, 0), (250, HEIGHT)), width=2)
    if self.entity_types:
      if len(self.entity_types[self.selected_entity_type]["character"]) < 20: screen.blit(fontmedium.render(self.entity_types[self.selected_entity_type]["character"], True, "White"), (265, 4))
      elif len(self.entity_types[self.selected_entity_type]["character"]) < 28: screen.blit(fontsmall.render(self.entity_types[self.selected_entity_type]["character"], True, "White"), (265, 6))
      elif len(self.entity_types[self.selected_entity_type]["character"]) < 37: screen.blit(fontlittle.render(self.entity_types[self.selected_entity_type]["character"], True, "White"), (265, 8))
      else: screen.blit(fontsmaller.render(self.entity_types[self.selected_entity_type]["character"], True, "White"), (265, 8))
      
      if "td" in self.entity_types[self.selected_entity_type]["flags"]: image = pygame.image.load(self.active_directory + "Assets/characters/" + self.entity_types[self.selected_entity_type]["character"] + "/" + self.dir_preview_mode + "/idle/1.png").convert_alpha()
      else: image = pygame.image.load(self.active_directory + "Assets/characters/" + self.entity_types[self.selected_entity_type]["character"] + "/idle/1.png").convert_alpha()
      screen.blit(image, (280, 40))
      
      screen.blit(fontsmall.render(f"HP {self.entity_types[self.selected_entity_type]['hp']}", True, "White"), (308, 118))
      screen.blit(fontsmall.render(f"Team {self.entity_types[self.selected_entity_type]['team']}", True, "White"), (420, 118))

      for button in self.buttons[56]:
        if button.button_type == "Stat" or button.button_type == "Value": self.buttons[56].remove(button)
      for button in self.buttons[56]:
        if button.button_type == "Stat" or button.button_type == "Value": self.buttons[56].remove(button)

      width = 0; height = 0
      if self.game_stats:
        if self.entity_types[self.selected_entity_type]["stat"]:
          if main.game_stats[self.entity_types[self.selected_entity_type]["stat"]] == int or main.game_stats[self.entity_types[self.selected_entity_type]["stat"]] == float:
            for x, button in enumerate([(l[lg]["Decrease"], "less", change_entity_value, -1), (l[lg]["Increase"], "more", change_entity_value, 1)]):
              main.buttons[56].append(Button(270 + (x * 180), HEIGHT - 296, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3], button_type="Value"))
            screen.blit(fontmedium.render(str(self.entity_types[self.selected_entity_type]["value"]), True, "White"), (365, HEIGHT - 292))
          if main.game_stats[self.entity_types[self.selected_entity_type]["stat"]] == float:
            for x, button in enumerate([(l[lg]["Decrease Decimal"], "less", change_entity_value, -0.25), (l[lg]["Increase Decimal"], "more", change_entity_value, 0.25)]):
              main.buttons[56].append(Button(302 + (x * 132), HEIGHT - 288, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", button[2], target=button[3], button_type="Value"))
          if main.game_stats[self.entity_types[self.selected_entity_type]["stat"]] == bool:
            for x, button in enumerate(["True", "False", "Negate"]):
              main.buttons[56].append(Button(270 + (x * 64), HEIGHT - 296, 64, 22, "Set as " + {"True": "True", "False": "False", "Negate": "Negation"}[button], button, change_entity_bool, button, font=fontsmall, button_type="Value"))
      for stat in main.game_stats:
        text = fontsmaller.render(stat + ",", True, "White")
        if width + 120 + text.get_width() > WIDTH - 150: height += 16; width = 0
        width += text.get_width() + 10
        main.buttons[56].append(Button(260 + width - text.get_width(), (HEIGHT - 255) + height, text.get_width() + 7, 16, l[lg]["Use Stat"], stat, set_entity_stat, target=stat, text_color={int: "Light blue", bool: "Light Yellow", str: "Pink", float: "Light Green"}[main.game_stats[stat]], font=fontsmaller, button_type="Stat"))

    else: screen.blit(fontsmall.render("No Entities to Show", True, "White"), (265, 6))

    #if self.character_types[self.selected_character_type]["hp"] != -1: screen.blit(fontsmall.render(f"HP {self.character_types[self.selected_character_type]['hp']}", True, "White"), (304, 182))
    #else: screen.blit(fontlittle.render(f"Invincible", True, "White"), (302, 182))

  def edit_entity_behaviors(self):
    global k_back
    if k_back: self.gamestate = 56; k_back = False
    pygame.draw.rect(screen, (0, 0, 50), ((25, 20), (WIDTH - 25, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((25, 20), (WIDTH - 25, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render("Edit Behavior for Entity: " + self.entity_types[self.selected_entity_type]["character"], True, "White"), (30, 32))
    pygame.draw.rect(screen, (0, 0, 20), ((55, 100), (WIDTH - 110, 270)))

  def edit_menu(self):
    global k_back, k_down, k_up, k_y, k_x
    if k_back: self.gamestate = 3; k_back = False
    if k_x: self.gamestate = 0; k_x = False
    preview_y = 200
    screen.fill((0, 0, 50))
    screen.blit(fontmedium.render("Edit Menu", True, "White"), (4, 4))
    pygame.draw.rect(screen, "Black", ((10, 150), (WIDTH - 20, HEIGHT - 160)))
    pygame.draw.rect(screen, "Dark Blue", ((10, 150), (WIDTH - 20, HEIGHT - 160)), width=2)
    screen.blit(fontlittle.render("Selected Index: " + str(self.selected_menu_item_index) + "\nEditing the " + {True: "Selected", False: "Unselected"}[self.selected_menu_item_mode] + " mode", True, {True: "Yellow", False: "White"}[self.selected_menu_item_mode]), (320, 3))
    screen.blit(fontlittle.render({True: "On", False: "Off"}[main.selected_both_selected_and_unselected_menu_item], True, "White"), (182, 12))
    screen.blit(fontlittle.render({True: "On", False: "Off"}["active" in main.rooms[main.selected_room].menu["flags"]], True, "White"), (216, 12))
    screen.blit(fontlittle.render({True: "On", False: "Off"}["reset" in main.rooms[main.selected_room].menu["flags"]], True, "White"), (250, 12))
    screen.blit(fontlittle.render({True: "On", False: "Off"}["in" in main.rooms[main.selected_room].menu["flags"]], True, "White"), (284, 12))
    selected = False
    screen.blit(fontlittle.render("Down SFX: " + main.rooms[main.selected_room].menu["down_s"], True, "White"), (10, 137))
    screen.blit(fontlittle.render("Up SFX: " + main.rooms[main.selected_room].menu["up_s"], True, "White"), (170, 137))
    for button in main.rooms[main.selected_room].menu["items"]:
      if button["I"] == main.selected_menu_item_index:
        selected = True
        screen.blit(fontlittle.render("X İndex: " + str(button["X_I"]) + "\nY İndex: " + str(button["Y_I"]), True, "White"), (430, 32))
        screen.blit(fontlittle.render("X Cam: " + str(button["Cam_X"]) + "\nY Cam: " + str(button["Cam_Y"]), True, "White"), (430, 67))
        if self.selected_menu_item_mode: screen.blit(fontlittle.render("X Pos: " + str(button["X_PS"]) + "\nY Pos: " + str(button["Y_PS"]), True, "White"), (162, 67))
        else: screen.blit(fontlittle.render("X Pos: " + str(button["X_P"]) + "\nY Pos: " + str(button["Y_P"]), True, "White"), (162, 67))
        if self.selected_menu_item_mode: screen.blit(fontlittle.render("X Text: " + str(button["TPXS"]) + "\nY Text: " + str(button["TPYS"]), True, "White"), (256, 67))
        else: screen.blit(fontlittle.render("X Text: " + str(button["TPX"]) + "\nY Text: " + str(button["TPY"]), True, "White"), (256, 67))
        if self.selected_menu_item_mode: screen.blit(fontlittle.render("X İmg: " + str(button["IPXS"]) + "\nY İmg: " + str(button["IPYS"]), True, "White"), (342, 67))
        else: screen.blit(fontlittle.render("X İmg: " + str(button["IPX"]) + "\nY İmg: " + str(button["IPY"]), True, "White"), (342, 67))
        screen.blit(fontlittle.render("Press SFX: " + button["S"], True, "White"), (330, 137))
        if self.selected_menu_item_mode:
          if button["Image_SurfaceS"] != None:
            if button["Anim_Rate"] > -1:
              screen.blit(button["Image_SurfaceS"][button["Timer"].keep_count(button["Anim_Rate"], len(button["Image_SurfaceS"]), 0)], (((WIDTH / 2) - (button["Image_SurfaceS"][self.frame_timer.tally].get_width() / 2)) + button["IPXS"], preview_y + button["IPYS"]))
              if button["BCS"]:
                try:
                  if "olai" in button["flags"] and button["BCS"][button["Timer2"].keep_count(button["BDS"], len(button["BCS"]), 0)] != "Transparent": pygame.draw.rect(screen, button["BCS"][button["Timer2"].tally], (((WIDTH / 2) - ((button["Image_SurfaceS"][self.frame_timer.tally].get_width() / 2)) + button["BXS"], preview_y + button["BYS"]), (button["Image_SurfaceS"][self.frame_timer.tally].get_width() + button["BWS"], button["Image_SurfaceS"][self.frame_timer.tally].get_height() + button["BHS"])), button["BTS"], button["BRS"])
                except IndexError: button["Timer2"].reset()
            else:
              screen.blit(button["Image_SurfaceS"], (((WIDTH / 2) - (button["Image_SurfaceS"].get_width() / 2)) + button["IPXS"], preview_y + button["IPYS"]))
              if button["BCS"]:
                try:
                  if "olai" in button["flags"] and button["BCS"][button["Timer2"].keep_count(button["BDS"], len(button["BCS"]), 0)] != "Transparent": pygame.draw.rect(screen, button["BCS"][button["Timer2"].tally], (((WIDTH / 2) - ((button["Image_SurfaceS"].get_width() / 2)) + button["BXS"], preview_y + button["BYS"]), (button["Image_SurfaceS"].get_width() + button["BWS"], button["Image_SurfaceS"].get_height() + button["BHS"])), button["BTS"], button["BRS"])
                except IndexError: button["Timer2"].reset()
          if button["Text_SurfaceS"] != None:
            screen.blit(button["Text_SurfaceS"], (((WIDTH / 2) - (button["Text_SurfaceS"].get_width() / 2)) + button["TPXS"], preview_y + button["TPYS"]))
            if button["BCS"]:
              try:
                if "olat" in button["flags"] and button["BCS"][button["Timer2"].keep_count(button["BDS"], len(button["BCS"]), 0)] != "Transparent": pygame.draw.rect(screen, button["BCS"][button["Timer2"].tally], ((((WIDTH / 2) - (button["Text_SurfaceS"].get_width() / 2)) + button["BXS"], preview_y + button["BYS"]), (button["Text_SurfaceS"].get_width() + button["BWS"], button["Text_SurfaceS"].get_height() + button["BHS"])), button["BTS"], button["BRS"])
              except IndexError: button["Timer2"].reset()
          if button["Text_DataS"][3] == "" and button["Image_SurfaceS"] == None: screen.blit(fontmedium.render("No Display", True, "White"), ((WIDTH / 2) - (fontmedium.render("No Display", True, "White").get_width() / 2), preview_y))
        else:
          if button["Image_Surface"] != None:
            if button["Anim_Rate"] > -1:
              screen.blit(button["Image_Surface"][button["Timer"].keep_count(button["Anim_Rate"], len(button["Image_Surface"]), 0)], (((WIDTH / 2) - (button["Image_Surface"][self.frame_timer.tally].get_width() / 2)) + button["IPX"], preview_y + button["IPY"]))
              if button["BC"]:
                try:
                  if "olai" in button["flags"] and button["BC"][button["Timer2"].keep_count(button["BD"], len(button["BC"]), 0)] != "Transparent": pygame.draw.rect(screen, button["BC"][button["Timer2"].tally], (((WIDTH / 2) - ((button["Image_Surface"][self.frame_timer.tally].get_width() / 2)) + button["BX"], preview_y + button["BY"]), (button["Image_Surface"][self.frame_timer.tally].get_width() + button["BW"], button["Image_Surface"][self.frame_timer.tally].get_height() + button["BH"])), button["BT"], button["BR"])
                except IndexError: button["Timer2"].reset()
            else:
              screen.blit(button["Image_Surface"], (((WIDTH / 2) - (button["Image_Surface"].get_width() / 2)) + button["IPX"], preview_y + button["IPY"]))
              if button["BC"]:
                try:
                  if "olai" in button["flags"] and button["BC"][button["Timer2"].keep_count(button["BD"], len(button["BC"]), 0)] != "Transparent": pygame.draw.rect(screen, button["BC"][button["Timer2"].tally], (((WIDTH / 2) - ((button["Image_Surface"].get_width() / 2)) + button["BX"], preview_y + button["BY"]), (button["Image_Surface"].get_width() + button["BW"], button["Image_Surface"].get_height() + button["BH"])), button["BT"], button["BR"])
                except IndexError: button["Timer2"].reset()
          if button["Text_Surface"] != None:
            screen.blit(button["Text_Surface"], (((WIDTH / 2) - (button["Text_Surface"].get_width() / 2)) + button["TPX"], preview_y + button["TPY"]))
            if button["BC"]:
              try:
                if "olat" in button["flags"] and button["BC"][button["Timer2"].keep_count(button["BD"], len(button["BC"]), 0)] != "Transparent": pygame.draw.rect(screen, button["BC"][button["Timer2"].tally], ((((WIDTH / 2) - (button["Text_Surface"].get_width() / 2)) + button["BX"], preview_y + button["BY"]), (button["Text_Surface"].get_width() + button["BW"], button["Text_Surface"].get_height() + button["BH"])), button["BT"], button["BR"])
              except IndexError: button["Timer2"].reset()
          if button["Text_Data"][3] == "" and button["Image_Surface"] == None: screen.blit(fontmedium.render("No Display", True, "White"), ((WIDTH / 2) - (fontmedium.render("No Display", True, "White").get_width() / 2), preview_y))
    if not len(main.rooms[main.selected_room].menu["items"]): screen.blit(fontmedium.render("No Buttons Selected", True, "White"), ((WIDTH / 2) - (fontmedium.render("Out of Menu Range", True, "White").get_width() / 2), preview_y))

    for button in [button for button in self.buttons[58] if button.button_type == "Menu Item Customization"]: self.buttons[58].remove(button)

    if selected:
      for x, button in enumerate([("Paste Text Data", "paste text data", paste_text_data_to_menu_item), ("Paste Image Path", "paste image", paste_image_to_menu_item), ("Remove Text", "delete", remove_text_data_from_menu_item), ("Remove Image", "delete", remove_image_from_menu_item)]):
        self.buttons[58].append(Button(10 + (x * 34), 66, 32, 32, button[0], "Assets/editor/" + button[1] + ".png", button[2], button_type="Menu Item Customization"))
      for x, button in enumerate([("Decrease İtem X Index", "less", -1), ("İncrease İtem X Index", "more", 1)]):
        self.buttons[58].append(Button(414 + (x * 82), 32, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_menu_item_x_index, target=button[2], button_type="Menu Item Customization"))
      for x, button in enumerate([("Decrease İtem Y Index", "less", -1), ("İncrease İtem Y Index", "more", 1)]):
        self.buttons[58].append(Button(414 + (x * 82), 48, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_menu_item_y_index, target=button[2], button_type="Menu Item Customization"))
      for x, button in enumerate([("Decrease İtem X Pos", "less", -5), ("İncrease İtem X Pos", "more", 5)]):
        self.buttons[58].append(Button(146 + (x * 82), 66, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_menu_item_x_pos, target=button[2], button_type="Menu Item Customization"))
      for x, button in enumerate([("Decrease İtem Y Pos", "less", -5), ("İncrease İtem Y Pos", "more", 5)]):
        self.buttons[58].append(Button(146 + (x * 82), 82, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_menu_item_y_pos, target=button[2], button_type="Menu Item Customization"))
      for x, button in enumerate([("Decrease Text X Mod Pos", "less", -2), ("İncrease Text X Mod Pos", "more", 2)]):
        self.buttons[58].append(Button(242 + (x * 72), 66, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_menu_item_text_x_pos, target=button[2], button_type="Menu Item Customization"))
      for x, button in enumerate([("Decrease Text Y Mod Pos", "less", -2), ("İncrease Text Y Mod Pos", "more", 2)]):
        self.buttons[58].append(Button(242 + (x * 72), 82, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_menu_item_text_y_pos, target=button[2], button_type="Menu Item Customization"))
      for x, button in enumerate([("Decrease İmage X Mod Pos", "less", -2), ("İncrease İmage X Mod Pos", "more", 2)]):
        self.buttons[58].append(Button(328 + (x * 72), 66, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_menu_item_image_x_pos, target=button[2], button_type="Menu Item Customization"))
      for x, button in enumerate([("Decrease İmage Y Mod Pos", "less", -2), ("İncrease İmage Y Mod Pos", "more", 2)]):
        self.buttons[58].append(Button(328 + (x * 72), 82, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_menu_item_image_y_pos, target=button[2], button_type="Menu Item Customization"))
      for x, button in enumerate([("Decrease Camera X Scrolling Susceptibility", "less", -1), ("İncrease Camera X Scrolling Susceptibility", "more", 1)]):
        self.buttons[58].append(Button(414 + (x * 82), 66, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_menu_item_camera_x_susceptibility, target=button[2], button_type="Menu Item Customization"))
      for x, button in enumerate([("Decrease Camera Y Scrolling Susceptibility", "less", -1), ("İncrease Camera Y Scrolling Susceptibility", "more", 1)]):
        self.buttons[58].append(Button(414 + (x * 82), 82, 16, 16, button[0], "Assets/editor/" + button[1] + ".png", change_menu_item_camera_y_susceptibility, target=button[2], button_type="Menu Item Customization"))
      self.buttons[58].append(Button(330, 103, 32, 32, l[lg]["Browse SFXs"], "Assets/editor/note.png", select_sfx3, target=58, button_type="Menu Item Customization"))
      self.buttons[58].append(Button(316, 30, 32, 32, "Action and Outline Settings", "Assets/editor/cog.png", action_and_outline_settings, button_type="Menu Item Customization"))

    if k_l: main.selected_menu_item_index -= 1 + (int(k_y) * 4); scrollup_sfx.play()
    if k_r: main.selected_menu_item_index += 1 + (int(k_y) * 4); scrolldown_sfx.play()
    if main.selected_menu_item_index < 0: main.selected_menu_item_index = 0

  def edit_menu2(self):
    if k_back: self.gamestate = 58
    pygame.draw.rect(screen, (0, 0, 50), ((25, 20), (WIDTH - 25, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((25, 20), (WIDTH - 25, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render("Edit Action and Border", True, "White"), (30, 32))
    
    for button in main.rooms[main.selected_room].menu["items"]:
      if button["I"] == main.selected_menu_item_index:
        screen.blit(fontlittle.render({True: "On", False: "Off"}["olat" in button["flags"]], True, "White"), (420, 37))
        screen.blit(fontlittle.render({True: "On", False: "Off"}["olai" in button["flags"]], True, "White"), (454, 37))
        if self.selected_menu_item_mode:
          screen.blit(fontlittle.render("Outline X " + str(button["BXS"]), True, "White"), (260, 79))
          screen.blit(fontlittle.render("Outline Y " + str(button["BYS"]), True, "White"), (260, 119))
          screen.blit(fontlittle.render("Outline Width " + str(button["BWS"]), True, "White"), (260, 159))
          screen.blit(fontlittle.render("Outline Height " + str(button["BHS"]), True, "White"), (260, 199))
          screen.blit(fontlittle.render("Outline Thick " + str(button["BTS"]), True, "White"), (260, 239))
          screen.blit(fontlittle.render("Outline Radius " + str(button["BRS"]), True, "White"), (260, 279))
          screen.blit(fontlittle.render("Outline CR " + str(button["BDS"]), True, "White"), (260, 319))
          screen.blit(fontlittle.render("Outline Colors " + str(main.selected_menu_item_outline_color_index), True, "White"), (260, 359))
          screen.blit(fontlittle.render("Outline Colors: " + str(button["BCS"]) + "\nSelected Index: " + str(self.selected_menu_item_index), True, "White"), (30, HEIGHT - 55))
        else:
          screen.blit(fontlittle.render("Outline X " + str(button["BX"]), True, "White"), (260, 79))
          screen.blit(fontlittle.render("Outline Y " + str(button["BY"]), True, "White"), (260, 119))
          screen.blit(fontlittle.render("Outline Width " + str(button["BW"]), True, "White"), (260, 159))
          screen.blit(fontlittle.render("Outline Height " + str(button["BH"]), True, "White"), (260, 199))
          screen.blit(fontlittle.render("Outline Thick " + str(button["BT"]), True, "White"), (260, 239))
          screen.blit(fontlittle.render("Outline Radius " + str(button["BR"]), True, "White"), (260, 279))
          screen.blit(fontlittle.render("Outline CR " + str(button["BD"]), True, "White"), (260, 319))
          screen.blit(fontlittle.render("Outline Colors " + str(main.selected_menu_item_outline_color_index), True, "White"), (260, 359))
          screen.blit(fontlittle.render("Outline Colors: " + str(button["BC"]) + "\nSelected Index: " + str(self.selected_menu_item_index), True, "White"), (30, HEIGHT - 55))
    
    if k_l: main.selected_menu_item_index -= 1 + (int(k_y) * 4); scrollup_sfx.play()
    if k_r: main.selected_menu_item_index += 1 + (int(k_y) * 4); scrolldown_sfx.play()
    if main.selected_menu_item_index < 0: main.selected_menu_item_index = 0

  def edit_text_behaviors(self):
    global k_back
    if k_back: self.gamestate = 43; k_back = False
    pygame.draw.rect(screen, (0, 0, 50), ((25, 20), (WIDTH - 25, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((25, 20), (WIDTH - 25, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render("Edit Behavior for Text", True, "White"), (30, 32))
    pygame.draw.rect(screen, (0, 0, 20), ((55, 100), (WIDTH - 110, 270)))

  def edit_ui_behaviors(self):
    global k_back
    if k_back: self.gamestate = 35; k_back = False
    pygame.draw.rect(screen, (0, 0, 50), ((25, 20), (WIDTH - 25, HEIGHT - 40)))
    pygame.draw.rect(screen, "Dark Blue", ((25, 20), (WIDTH - 25, HEIGHT - 40)), width=2)
    screen.blit(fontmedium.render("Edit Behavior for Uİ", True, "White"), (30, 32))
    pygame.draw.rect(screen, (0, 0, 20), ((55, 100), (WIDTH - 110, 270)))

  def playtest(self, dt):
    global screen, k_back, FPS
    dt *= 60
    if not self.use_dt: dt = 1

    if self.playback_on and not self.game_paused:
      await_input = False
      #try:
      for key in self.rooms[self.current_room].cutscenes[self.selected_cutscene].animations:
        if key["Object"] == "Main" and key["Frame"] == self.selected_key and self.frame_timer.time == 1:
          await_input = key["SOCR"]
          for player in self.players:
            if await_input and (player.port.buttons["Press"]["start"] or player.port.buttons["Press"]["a"] or player.port.buttons["Press"]["b"] or player.port.buttons["Press"]["x"] or player.port.buttons["Press"]["y"] or player.port.buttons["Press"]["select"]): await_input = False
      #except IndexError: pass
      self.camera.camera_scene(dt)
      delay = 10
      for key in self.rooms[self.current_room].cutscenes[self.selected_cutscene].animations:
        if key["Frame"] == self.selected_key and self.frame_timer.time == 1:
          if key["Object"] == "Main":
            for player in self.players: player.immobilize = key["Hidden"]
            for ui in self.ui.instances:
              if self.ui.instances[ui]["SM"] in key["Show UI"]: self.ui.instances[ui]["Hidden"] = False
              if self.ui.instances[ui]["SM"] in key["Hide UI"]: self.ui.instances[ui]["Hidden"] = True
            if key["Track"] and key["Track"] != "Stop": pygame.mixer.music.load(self.active_directory + "Sounds/tracks/" + key["Track"]); pygame.mixer.music.play(-1, 0.0); self.track = key["Track"]
            elif key["Track"] == "Stop": pygame.mixer.music.stop()
            try:
              if key["Dir"]: pygame.mixer.music.load(self.active_directory + "Sounds/tracks/" + key["Dir"]); pygame.mixer.music.play(1, 0.0); self.track = key["Dir"]
            except FileNotFoundError: pass
            if key["SFX"]:
              if type(key["SFX"]) == list: pygame.mixer.Sound(self.active_directory + "Sounds/sfx/" + key["SFX"][random.randrange(0, len(key["SFX"]))]).play()
              else: pygame.mixer.Sound(self.active_directory + "Sounds/sfx/" + key["SFX"]).play()
            if key["Object"] == self.camera: self.rooms[self.current_room].hm = key["B1"]
            if key["Object"] == self.camera: self.rooms[self.current_room].vm = key["B2"]
            if key["Object"] == self.camera and key["I1"] != -1: self.rooms[self.current_room].borders["top"] = key["I1"]
            if key["Object"] == self.camera and key["I2"] != -1: self.rooms[self.current_room].borders["right"] = key["I2"]
            if key["Object"] == self.camera and key["I3"] != -1: self.rooms[self.current_room].borders["bottom"] = key["I3"]
            if key["Object"] == self.camera and key["I4"] != -1: self.rooms[self.current_room].borders["left"] = key["I4"]
        if key["Frame"] == self.selected_key:
          if key["Object"] == "Main": delay = key["Rotate"]
      if not await_input:
        if delay != 0:
          if self.frame_timer.timer(delay * dt): self.selected_key += 1
    if self.selected_key > self.last_frame_active: self.playback_on = False; self.selected_key = 0; self.frame_timer.reset(); self.selected_cutscene = 0; main.last_frame_active = 0
    
    self.rooms[self.current_room].render_backgrounds(screen, self.playback_on, dt, fg=False)
    for layer in self.rooms[self.current_room].layers[::-1]: layer.render_tiles(screen, self.playback_on, dt); layer.render_collectibles(screen, self.playback_on, dt); layer.update_entities(screen, dt); layer.render_entities(screen, self.playback_on, dt); layer.render_texts(screen, self.playback_on, dt, False) #Wait an error, there is no scroll[1] and x
    for door in self.rooms[self.current_room].doors: door.update(screen, self.playback_on, dt)
    for player in [player for player in self.players if (not player.hide_if_out) or player.in_]: player.update(screen, self.playback_on, dt)
    for player in self.players: player.display_projectiles(screen, dt)
    for layer in self.rooms[self.current_room].layers[::-1]: layer.update_tiles(screen, self.playback_on, dt); layer.update_collectibles(screen, self.playback_on, dt)
    for layer in self.rooms[self.current_room].layers[::-1]:
      for actor in layer.actors: actor.display_projectiles(screen, dt)

    for room in self.rooms:
      for door in [door for door in room.doors if not door.transition_override_ui]:
        screen = door.play_transition(screen, dt)
        if (door.transition_pre_immobilize_player or door.transition_post_immobilize_player) and not door.t_playing:
          for player in self.players: player.immobilize = False
        if (not door.t_over) and door.t_playing and door.transition_pre_immobilize_player:
          for player in [player for player in self.players if player.rect.colliderect(door.rect)]: player.immobilize = True
        if door.t_over and door.t_playing and door.transition_post_immobilize_player:
          for player in [player for player in self.players if player.rect.colliderect(door.rect)]: player.immobilize = True

    #for player in self.players: player.render_ui(screen, fontsmaller)
    self.rooms[self.current_room].render_backgrounds(screen, self.playback_on, dt, bg=False)
    for layer in self.rooms[self.current_room].layers[::-1]: layer.render_texts(screen, self.playback_on, dt, True)
    self.ui.render(screen, clock)

    for room in self.rooms:
      for door in [door for door in room.doors if door.transition_override_ui]:
        screen = door.play_transition(screen, dt)
        if (door.transition_pre_immobilize_player or door.transition_post_immobilize_player) and not door.t_playing:
          for player in self.players: player.immobilize = False
        if (not door.t_over) and door.t_playing and door.transition_pre_immobilize_player:
          for player in [player for player in self.players if player.rect.colliderect(door.rect)]: player.immobilize = True
        if door.t_over and door.t_playing and door.transition_post_immobilize_player:
          for player in [player for player in self.players if player.rect.colliderect(door.rect)]: player.immobilize = True

    #Draw Game Menu
    if main.rooms[main.current_room].menu_active:
      for player in main.players: player.immobilize = True
      highest_x_index, highest_y_index = 0, 0
      lowest_x_index, lowest_y_index = 0, 0
      for button in main.rooms[main.current_room].menu["items"]:
        if button["X_I"] > highest_x_index: highest_x_index = button["X_I"]
        if button["Y_I"] > highest_y_index: highest_y_index = button["Y_I"]
        if button["X_I"] < lowest_x_index: lowest_x_index = button["X_I"]
        if button["Y_I"] < lowest_y_index: lowest_y_index = button["Y_I"]
      if highest_x_index <= highest_y_index: menu_type = "vertical"
      else: menu_type = "horizontal"
      for index, port in enumerate(main.ports): # Up and down navigation
        if index < len(self.players):
          if not self.players[index].in_spawn:
            if "in" in main.rooms[main.current_room].menu["flags"]:
              if port.buttons["Press"]["start"]: self.players[index].in_ = not self.players[index].in_; port.buttons["Press"]["start"] = False; break
          if self.players[index].in_:
            if port.buttons["Press"]["down"]:
              main.rooms[main.current_room].selected_item[1] += 1; port.buttons["Press"]["down"] = False
              if type(main.rooms[main.current_room].menu["down_s"]) == list: main.rooms[main.current_room].menu["down_sfx"] = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + main.rooms[main.current_room].menu["down_s"][random.randrange(0, len(main.rooms[main.current_room].menu["down_s"]))])
              if main.rooms[main.current_room].menu["down_s"]: main.rooms[main.current_room].menu["down_sfx"].play()
              break
            if port.buttons["Press"]["up"]:
              main.rooms[main.current_room].selected_item[1] -= 1; port.buttons["Press"]["up"] = False
              if type(main.rooms[main.current_room].menu["up_s"]) == list: main.rooms[main.current_room].menu["up_sfx"] = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + main.rooms[main.current_room].menu["up_s"][random.randrange(0, len(main.rooms[main.current_room].menu["down_s"]))])
              if main.rooms[main.current_room].menu["up_s"]: main.rooms[main.current_room].menu["up_sfx"].play()
              break
            if port.buttons["Press"]["right"]:
              main.rooms[main.current_room].selected_item[0] += 1; port.buttons["Press"]["right"] = False
              if type(main.rooms[main.current_room].menu["down_s"]) == list: main.rooms[main.current_room].menu["down_sfx"] = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + main.rooms[main.current_room].menu["down_s"][random.randrange(0, len(main.rooms[main.current_room].menu["down_s"]))])
              if main.rooms[main.current_room].menu["down_s"]: main.rooms[main.current_room].menu["down_sfx"].play()
              break
            if port.buttons["Press"]["left"]:
              main.rooms[main.current_room].selected_item[0] -= 1; port.buttons["Press"]["left"] = False
              if type(main.rooms[main.current_room].menu["up_s"]) == list: main.rooms[main.current_room].menu["up_sfx"] = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + main.rooms[main.current_room].menu["up_s"][random.randrange(0, len(main.rooms[main.current_room].menu["down_s"]))])
              if main.rooms[main.current_room].menu["up_s"]: main.rooms[main.current_room].menu["up_sfx"].play()
              break
      if "noclipback" in main.rooms[main.current_room].menu["flags"]:
        if main.rooms[main.current_room].selected_item[0] < lowest_x_index: main.rooms[main.current_room].selected_item[0] = lowest_x_index
        if main.rooms[main.current_room].selected_item[0] > highest_x_index: main.rooms[main.current_room].selected_item[0] = highest_x_index
        if main.rooms[main.current_room].selected_item[1] < lowest_y_index: main.rooms[main.current_room].selected_item[1] = lowest_y_index
        if main.rooms[main.current_room].selected_item[1] > highest_y_index: main.rooms[main.current_room].selected_item[1] = highest_y_index
      else:
        if main.rooms[main.current_room].selected_item[0] < lowest_x_index: main.rooms[main.current_room].selected_item[0] = highest_x_index
        if main.rooms[main.current_room].selected_item[0] > highest_x_index: main.rooms[main.current_room].selected_item[0] = lowest_x_index
        if main.rooms[main.current_room].selected_item[1] < lowest_y_index: main.rooms[main.current_room].selected_item[1] = highest_y_index
        if main.rooms[main.current_room].selected_item[1] > highest_y_index: main.rooms[main.current_room].selected_item[1] = lowest_y_index
      selected = False
      for button in main.rooms[main.current_room].menu["items"]:
        if [button["X_I"], button["Y_I"]] == main.rooms[main.current_room].selected_item:
          for port in main.ports:
            if port.buttons["Press"]["a"] and not button["Clicked"]: #ON BUTTON CLİCK
              if button["A"]: self.play_cutscene(button["A"])
              port.disable()
              button["Clicked"] = True
              if type(button["S"]) == list: button["SFX"] = pygame.mixer.Sound(self.main.active_directory + "Sounds/sfx/" + button["S"][random.randrange(0, len(button["S"]))])
              if button["S"]: button["SFX"].play()
              break
          selected = True
          main.current_button_text = button["Text_Data"][3]
          main.current_button_has_image = button["Image_Surface"] != None
          if button["Image_SurfaceS"] != None:
            if button["Anim_Rate"] > -1:
              screen.blit(button["Image_SurfaceS"][button["Timer"].keep_count(button["Anim_RateS"], len(button["Image_SurfaceS"]), 0)], (button["X_PS"] + button["IPXS"], button["Y_PS"] + button["IPYS"]))
              if button["BCS"]:
                try:
                  if "olai" in button["flags"] and button["BCS"][button["Timer2"].keep_count(button["BDS"], len(button["BCS"]), 0)] != "Transparent": pygame.draw.rect(screen, button["BCS"][button["Timer2"].tally], ((button["X_P"] + button["BXS"], button["Y_P"] + button["BYS"]), (button["Image_SurfaceS"][self.frame_timer.tally].get_width() + button["BWS"], button["Image_SurfaceS"][self.frame_timer.tally].get_height() + button["BHS"])), button["BTS"], button["BRS"])
                except IndexError: button["Timer2"].reset()
            else:
              screen.blit(button["Image_SurfaceS"], (button["X_PS"] + button["IPXS"], button["Y_PS"] + button["IPYS"]))
              if button["BCS"]:
                try:
                  if "olai" in button["flags"] and button["BCS"][button["Timer2"].keep_count(button["BDS"], len(button["BCS"]), 0)] != "Transparent": pygame.draw.rect(screen, button["BCS"][button["Timer2"].tally], ((button["X_P"] + button["BXS"], button["Y_P"] + button["BYS"]), (button["Image_SurfaceS"].get_width() + button["BWS"], button["Image_SurfaceS"].get_height() + button["BHS"])), button["BTS"], button["BRS"])
                except IndexError: button["Timer2"].reset()
          if button["Text_SurfaceS"] != None:
            x = button["X_PS"]
            if button["Text_DataS"][12] == "Center": x -= button["Text_SurfaceS"].get_width() / 2
            if button["Text_DataS"][12] == "Right": x -= button["Text_SurfaceS"].get_width()
            screen.blit(button["Text_SurfaceS"], (x + button["TPXS"], button["Y_PS"] + button["TPYS"]))
            if button["BCS"]:
              try:
                if "olat" in button["flags"] and button["BCS"][button["Timer2"].keep_count(button["BDS"], len(button["BCS"]), 0)] != "Transparent": pygame.draw.rect(screen, button["BCS"][button["Timer2"].tally], ((x + button["BXS"], button["Y_P"] + button["BYS"]), (button["Text_SurfaceS"].get_width() + button["BWS"], button["Text_SurfaceS"].get_height() + button["BHS"])), button["BTS"], button["BRS"])
              except IndexError: button["Timer2"].reset()
        else:
          if button["Image_Surface"] != None:
            if button["Anim_Rate"] > -1:
              screen.blit(button["Image_Surface"][button["Timer"].keep_count(button["Anim_Rate"], len(button["Image_Surface"]), 0)], (button["X_P"] + button["IPX"], button["Y_P"] + button["IPY"]))
              if button["BC"]:
                try:
                  if "olai" in button["flags"] and button["BC"][button["Timer2"].keep_count(button["BD"], len(button["BC"]), 0)] != "Transparent": pygame.draw.rect(screen, button["BC"][button["Timer2"].tally], ((button["X_P"] + button["BX"], button["Y_P"] + button["BY"]), (button["Image_Surface"][self.frame_timer.tally].get_width() + button["BW"], button["Image_Surface"][self.frame_timer.tally].get_height() + button["BH"])), button["BT"], button["BR"])
                except IndexError: button["Timer2"].reset()
            else:
              screen.blit(button["Image_Surface"], (button["X_P"] + button["IPX"], button["Y_P"] + button["IPY"]))
              if button["BC"]:
                try:
                  if "olai" in button["flags"] and button["BC"][button["Timer2"].keep_count(button["BD"], len(button["BC"]), 0)] != "Transparent": pygame.draw.rect(screen, button["BC"][button["Timer2"].tally], ((button["X_P"] + button["BX"], button["Y_P"] + button["BY"]), (button["Image_Surface"].get_width() + button["BW"], button["Image_Surface"].get_height() + button["BH"])), button["BT"], button["BR"])
                except IndexError: button["Timer2"].reset()
          if button["Text_Surface"] != None:
            x = button["X_P"]
            if button["Text_Data"][12] == "Center": x -= button["Text_Surface"].get_width() / 2
            if button["Text_Data"][12] == "Right": x -= button["Text_Surface"].get_width()
            screen.blit(button["Text_Surface"], (x + button["TPX"], button["Y_P"] + button["TPY"]))
            if button["BC"]:
              try:
                if "olat" in button["flags"] and button["BC"][button["Timer2"].keep_count(button["BD"], len(button["BC"]), 0)] != "Transparent": pygame.draw.rect(screen, button["BC"][button["Timer2"].tally], ((x + button["BX"], button["Y_P"] + button["BY"]), (button["Text_Surface"].get_width() + button["BW"], button["Text_Surface"].get_height() + button["BH"])), button["BT"], button["BR"])
              except IndexError: button["Timer2"].reset()
      if menu_type == "vertical" and not selected: main.rooms[main.current_room].selected_item[1] = 0
      if menu_type == "horizontal" and not selected: main.rooms[main.current_room].selected_item[0] = 0
      
    if self.rooms[self.current_room].track and ((self.gamestate == 10 and self.editor_mode) or (self.gamestate == 1 and not self.editor_mode)) and not pygame.mixer.music.get_busy(): pygame.mixer.music.load(self.active_directory + f"Sounds/tracks/{self.rooms[self.current_room].track}"); pygame.mixer.music.play(-1, 0.0); self.track = self.rooms[self.current_room].track
    if k_back and self.gamestate == 1 and not self.editor_mode: self.game_paused = True; self.gamestate = 0; k_back = False; FPS = 240; pygame.mixer.music.pause()
    
    if self.debug:
      screen.blit(launcherfonttiny.render("FPS: " + str(round(clock.get_fps(), 2)) + "\nCamera Scroll: x " + str(round(self.camera.scroll[0], 2)) + ", y " + str(round(self.camera.scroll[1], 2)) + "\nCutscene Playing? " + str(self.playback_on) + "\nCutscene Key: " + str(self.selected_key) + "\nLayers Count: " + str(len(self.rooms[self.current_room].layers)) + "\nBackgrounds Count: " + str(len(self.rooms[self.current_room].backgrounds)) + "\nCurrent Room: Index " + str(self.current_room) + ", Name: " + str(self.rooms[self.current_room].name), True, "White").convert_alpha(), (0, 0))
      for player in self.players:
        statistics = ""
        for stat in player.stats: statistics += str(stat) + " = " + str(player.stats[stat]) + "\n"
        if player.state in player.character.actions: frame = player.frame + 1
        else: frame = "not defined"
        text = launcherfonttiny.render("x " + str(round(player.rect.x, 2)) + ", y " + str(round(player.rect.y, 2)) + "\naction " + player.state + ", frame " + str(frame) + "\n" + statistics, True, "White").convert_alpha()
        if player.deceives[0] < WIDTH / 2: screen.blit(text, (player.deceives[0] + player.rect.width, player.deceives[1]))
        else: screen.blit(text, (player.deceives[0] - text.get_width(), player.deceives[1]))
        if self.playback_on: pygame.draw.rect(screen, "Green", ((player.key_frame_rect.x - self.camera.scroll[0], player.key_frame_rect.y - self.camera.scroll[1]), (player.key_frame_rect.width, player.key_frame_rect.height)), 1)
        try:
          if player.state in player.character.actions: pygame.draw.rect(screen, "Red", ((player.deceives[0] + player.character.actions[player.state].frants[player.frame - 1].rect.x, player.deceives[1] + player.character.actions[player.state].frants[player.frame - 1].rect.x), (player.character.actions[player.state].frants[player.frame - 1].rect.width, player.character.actions[player.state].frants[player.frame - 1].rect.height)), 1)
        except IndexError: pass
        else: pygame.draw.rect(screen, (150, 0, 0), ((player.deceives[0], player.deceives[1]), (player.rect.width, player.rect.height)), 1)
        try:
          if player.state in player.character.actions: pygame.draw.rect(screen, "Blue", ((player.deceives[0] + player.character.actions[player.state].frants[player.frame - 1].attack_rect.x, player.deceives[1] + player.character.actions[player.state].frants[player.frame - 1].attack_rect.x), (player.character.actions[player.state].frants[player.frame - 1].attack_rect.width, player.character.actions[player.state].frants[player.frame - 1].attack_rect.height)), 1)
        except: pass
      if len(self.rooms[self.current_room].layers):
        for actor in self.rooms[self.current_room].layers[0].actors:
          statistics = ""
          for stat in actor.stats: statistics += str(stat) + " = " + str(actor.stats[stat]) + "\n"
          if actor.state in actor.character.actions: frame = actor.frame + 1
          else: frame = "not defined"
          text = launcherfonttiny.render("x " + str(round(actor.rect.x, 2)) + ", y " + str(round(actor.rect.y, 2)) + "\naction " + actor.state + ", frame " + str(frame) + "\n" + statistics + "HP:" + str(actor.hp), True, "White").convert_alpha()
          if actor.key_frame_rect.x - self.camera.scroll[0] < WIDTH / 2: screen.blit(text, (actor.key_frame_rect.x - self.camera.scroll[0] + actor.rect.width, actor.key_frame_rect.y - self.camera.scroll[1]))
          else: screen.blit(text, (actor.key_frame_rect.x - self.camera.scroll[0] - text.get_width(), actor.key_frame_rect.y - self.camera.scroll[1]))
          if self.playback_on: pygame.draw.rect(screen, "Green", ((actor.key_frame_rect.x - self.camera.scroll[0], actor.key_frame_rect.y - self.camera.scroll[1]), (actor.key_frame_rect.width, actor.key_frame_rect.height)), 1)
          if actor.state in actor.character.actions: pygame.draw.rect(screen, "Red", (((actor.character.actions[actor.state].frants[actor.frame - 1].rect.x + actor.rect.x) - self.camera.scroll[0], (actor.character.actions[actor.state].frants[actor.frame - 1].rect.y + actor.rect.y) - self.camera.scroll[1]), (actor.character.actions[actor.state].frants[actor.frame - 1].rect.width, actor.character.actions[actor.state].frants[actor.frame - 1].rect.height)), 1)
          else: pygame.draw.rect(screen, (150, 0, 0), ((actor.rect.x - self.camera.scroll[0], actor.rect.y - self.camera.scroll[1]), (actor.rect.width, actor.rect.height)), 1)
          if actor.state in actor.character.actions: pygame.draw.rect(screen, "Blue", (((actor.rect.x - self.camera.scroll[0]) + actor.character.actions[actor.state].frants[actor.frame - 1].attack_rect.x, (actor.rect.y - self.camera.scroll[1]) + actor.character.actions[actor.state].frants[actor.frame - 1].attack_rect.x), (actor.character.actions[actor.state].frants[actor.frame - 1].attack_rect.width, actor.character.actions[actor.state].frants[actor.frame - 1].attack_rect.height)), 1)
        for collectible in self.rooms[self.current_room].layers[0].collectibles:
          text = launcherfonttiny.render("x " + str(round(collectible.rect.x, 2)) + ", y " + str(round(collectible.rect.y, 2)), True, "White").convert_alpha()
          if collectible.key_frame_rect.x - self.camera.scroll[0] < WIDTH / 2: screen.blit(text, (collectible.key_frame_rect.x - self.camera.scroll[0] + collectible.rect.width, collectible.key_frame_rect.y - self.camera.scroll[1]))
          else: screen.blit(text, (collectible.key_frame_rect.x - self.camera.scroll[0] - text.get_width(), collectible.key_frame_rect.y - self.camera.scroll[1]))
          if self.playback_on: pygame.draw.rect(screen, "Green", ((collectible.key_frame_rect.x - self.camera.scroll[0], collectible.key_frame_rect.y - self.camera.scroll[1]), (collectible.key_frame_rect.width, collectible.key_frame_rect.height)), 1)
          pygame.draw.rect(screen, "Red", ((collectible.rect.x - self.camera.scroll[0], collectible.rect.y - self.camera.scroll[1]), (collectible.rect.width, collectible.rect.height)), 1)
      
  def play_cutscene(self, scene):
    self.last_frame_active = 0
    self.selected_cutscene = 0
    self.selected_key = -1
    for cs in self.rooms[self.current_room].cutscenes:
      if scene == cs.name: self.selected_cutscene = self.rooms[self.current_room].cutscenes.index(cs)
      for anim in cs.animations:
        if anim["Frame"] >= main.last_frame_active: main.last_frame_active = anim["Frame"] + 1
    self.playback_on = True

  def get_cutscene_from_name(self, scene):
    for cs in self.rooms[self.current_room].cutscenes:
      if scene == cs.name: cutscene = cs
    return cutscene

  def reset_shader(self, program, render_object):
    program.release(); ctx.clear(); program = ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=self.rooms[self.current_room].shader_code); render_object.release(); render_object = ctx.vertex_array(program, [shader_buffer])

  def launcher(self, dt=1):
    global k_back, FPS
    dt *= 60
    #if k_back: self.quit()
    for y in range(HEIGHT): y += 1; pygame.draw.rect(screen, (10, 10, y // 8), ((0, y), (WIDTH, 1)))

    if self.game_paused:
      if k_back: self.gamestate = 1; k_back = False; self.game_paused = False; FPS = main.fps; pygame.mixer.music.unpause()
      else: self.playtest(0); screen.blit(paused_surf, (0, 0))
        #resizer = pygame.transform.scale(screen, (WIDTH, HEIGHT))
        #screen.blit(resizer, (self.camera.shake[0], self.camera.shake[1]))

    if self.marine_snow_timer.timer(5): self.marine_snow.append(MarineSnow())
    for ms in self.marine_snow: ms.update(dt)
    for ms in [ms for ms in self.marine_snow if ms.rect.y < 0]: self.marine_snow.remove(ms)

    pygame.draw.rect(screen, (10, 10, 60), ((0, 0), (WIDTH, 55))); pygame.draw.rect(screen, (15, 15, 80), ((0, 25), (WIDTH, 20))); pygame.draw.rect(screen, (20, 20, 100), ((0, 30), (WIDTH, 10)))
    try: battery_percent = pygame.system.get_power_state().battery_percent; screen.blit(launcherfontsmaller.render(str(battery_percent) + "%", True, "White"), (40, 1)); screen.blit(pygame.image.load(f"Assets/editor/LAUNCHER {battery_mode[str([battery_percent <= 10, battery_percent > 10 and battery_percent <= 20, battery_percent > 20 and battery_percent < 50, battery_percent >= 50 and battery_percent <= 80, battery_percent > 80, pygame.system.get_power_state().plugged_in])]}.png").convert_alpha(), (3, 1))
    except: screen.blit(pygame.image.load(f"Assets/editor/LAUNCHER battery complete.png").convert_alpha(), (3, 1)); screen.blit(launcherfontsmaller.render("...", True, "White"), (40, 1))
    screen.blit(pygame.image.load("Assets/editor/LAUNCHER ram.png").convert_alpha(), (80, 1))
    screen.blit(launcherfontsmaller.render("RAM " + str(pygame.system.get_total_ram()), True, "White"), (100, 1))
    if not main.game_name: screen.blit(launcherfontsmaller.render("No Card Inserted", True, "White"), (190, 1))
    else:
      game_title = main.game_name
      if len(game_title) >= 15: game_title = game_title[:15] + "..."
      screen.blit(launcherfontsmaller.render(game_title, True, "White"), (185, 1))
    time_x = 335
    screen.blit(launcherfontsmaller.render(f"{str(datetime.now().hour).zfill(2)}:{str(datetime.now().minute).zfill(2)}", True, "White"), (time_x + 20, 1))
    screen.blit(launcherfonttiny.render(f":{str(datetime.now().second).zfill(2)}", True, "White"), (time_x + 60, 4))
    screen.blit(pygame.image.load("Assets/editor/LAUNCHER clock.png").convert_alpha(), (time_x, 1))
    screen.blit(pygame.image.load(f"Assets/editor/LAUNCHER clock h2 {round(datetime.now().minute / 7.5) * 7.5}.png").convert_alpha(), (time_x, 1))
    screen.blit(pygame.image.load(f"Assets/editor/LAUNCHER clock h1 {commercial_time(datetime.now().hour)}.png").convert_alpha(), (time_x, 1))
    screen.blit(launcherfontsmaller.render(str(datetime.now().date()), True, "White"), (time_x + 90, 1))

    if self.on_page == 2:
      for y, button in enumerate([button for button in main.launcher_buttons[self.gamestate] if button.page == 2]): pygame.draw.rect(screen, (0, 0, 50), ((2, 50 + (y * 32)), (230, 32))); pygame.draw.line(screen, (0, 0, 150), (2, 50 + (y * 32)), (230, 50 + (y * 32)))
    if self.on_page == 3:
      for y, button in enumerate([button for button in main.launcher_buttons[self.gamestate] if button.page == 3]): pygame.draw.rect(screen, (0, 0, 50), ((90, 50 + (y * 32)), (230, 32))); pygame.draw.line(screen, (0, 0, 150), (90, 50 + (y * 32)), (230 + 90, 50 + (y * 32)))
    if self.on_page == 4:
      for y, button in enumerate([button for button in main.launcher_buttons[self.gamestate] if button.page == 4]): pygame.draw.rect(screen, (0, 0, 50), ((216, 50 + (y * 32)), (230, 32))); pygame.draw.line(screen, (0, 0, 150), (216, 50 + (y * 32)), (230 + 216, 50 + (y * 32)))
    if self.on_page == 5:
      pygame.draw.rect(screen, (0, 0, 50), ((50, 100), (WIDTH - 100, 300))); pygame.draw.rect(screen, (0, 0, 150), ((50, 100), (WIDTH - 100, 300)), width=2)
      screen.blit(launcherfontlittle.render(f"About Tunaditor™ {TUNADİTOR_VERSİON}", True, (240, 240, 240)), (54, 105))
      screen.blit(launcherfontlittle.render("This program is designed for creating,\nplaying and sharing retro video games." +
                              "\n\nThis is a free software and it is free\nto distribute under certain conditions:\n" +
                              "non-commercial use and inclusion of the\noriginal license.\n\n\n\n\n\nDeveloped and licensed by Kaan, Tunari", True, (170, 170, 170)), (54, 135))
      if k_a: self.on_page = 1
    if self.on_page == 6:
      pygame.draw.rect(screen, (0, 0, 15), ((50, 100), (WIDTH - 100, 300))); screen.blit(launcherfontsmall.render("Load ROM", True, "White"), (50, 75))
      if k_down and self.y_scroll > -((len([button2 for button2 in main.launcher_buttons[self.gamestate] if button2.page == 6]) * 32) - 300): self.y_scroll -= 5 * dt
      if k_up and self.y_scroll < 0: self.y_scroll += 5 * dt
      for y, button in enumerate([button for button in main.launcher_buttons[self.gamestate] if button.page == 6 and button.button_type == "Game"]): button.rect.y = (106 + (32 * y)) + self.y_scroll; pygame.draw.rect(screen, (0, 0, 50), ((50, minint((100 + (y * 32)) + self.y_scroll, 100)), (WIDTH - 100, 32))) if y % 2 != 0 else pygame.draw.rect(screen, (0, 0, 20), ((50, minint((100 + (y * 32)) + self.y_scroll, 100)), (WIDTH - 100, 32)))
      pygame.draw.rect(screen, (0, 0, 150), ((50, 100), (WIDTH - 100, 300)), width=2); pygame.draw.rect(screen, (0, 0, 75), ((50, 400), (WIDTH - 100, HEIGHT - 400)))
    if self.on_page == 7 or self.on_page == 8:
      for y, button in enumerate([button for button in main.launcher_buttons[self.gamestate] if button.page == 7 or button.page == 8]): button.target = [self.game_name, self, int(button.path)]
      if self.on_page == 7: screen.blit(launcherfontsmall.render("Save Game Slot", True, "White"), (40, 115))
      if self.on_page == 8: screen.blit(launcherfontsmall.render("Load Game Slot", True, "White"), (40, 115))
      pygame.draw.rect(screen, (0, 0, 50), ((40, 140), (WIDTH - 65, 140)))
      pygame.draw.rect(screen, (0, 0, 150), ((40, 140), (WIDTH - 65, 140)), width=2)
      for button in range(20):
        if os.path.exists("Saves/states/" + self.game_name + " Slot " + str(button + 1)): pygame.draw.rect(screen, "White", ((30 + ((button % 10) * 45) + (22), (150 + math.floor(button / 10) * 64) + 30), (16, 16)), border_radius=8)
        pygame.draw.rect(screen, "Blue", ((30 + ((button % 10) * 45) + (22), (150 + math.floor(button / 10) * 64) + 30), (16, 16)), width=2, border_radius=8)
    if self.on_page >= 9 and self.on_page < 12:
      for x in range(3):
        pygame.draw.rect(screen, (0, 0, 50), ((16 + (166 * x), 70), (150, 48)), border_radius=8)
        pygame.draw.rect(screen, (0, 0, 150), ((16 + (166 * x), 70), (150, 48)), width=2, border_radius=8)
      pygame.draw.rect(screen, (0, 0, 50), ((16, 110), (482, 300)))
      pygame.draw.rect(screen, (0, 0, 150), ((16, 110), (482, 300)), width=2)
      if self.on_page == 9:
        screen.blit(launcherfontlittle.render(l[lg]["Set Device"], True, "White").convert_alpha(), (28, 165))
        screen.blit(launcherfontlittle.render(l[lg]["Set Deadzone"], True, "White").convert_alpha(), (360, 165))
        screen.blit(launcherfontlittle.render({True: "On", False: "Off"}[main.ports[main.selected_player].rumble], True, "White").convert_alpha(), (360 + launcherfontlittle.render(l[lg]["Rumble: "], False, "White").get_width(), 270))
        dz = main.ports[main.selected_player].deadzone; pygame.draw.rect(screen, (0, 0, 100), ((390, 190), (64, 64)), border_radius=32); pygame.draw.rect(screen, (0, 0, 170), ((390 + (64 - round(dz * 64)) / 2, 190 + (64 - round(dz * 64)) / 2,), (round(dz * 64), round(dz * 64))), border_radius=32)
      if self.on_page == 10:
        screen.blit(launcherfontsmall.render(l[lg]["Render Filter"], True, "White").convert_alpha(), (30, 120))
        screen.blit(launcherfontsmall.render(l[lg]["Color Swizzle"], True, "White").convert_alpha(), (220, 120))
        screen.blit(launcherfontsmall.render(l[lg]["Set Render Mode"], True, "White").convert_alpha(), ((WIDTH / 2) - (launcherfontsmall.render("Set Render Mode", True, "White").get_width() / 2), 290))
    if self.on_page == 16:
      pygame.draw.rect(screen, (0, 0, 50), ((16, 70), (482, 350)))
      pygame.draw.rect(screen, (0, 0, 150), ((16, 70), (482, 350)), width=2)
      screen.blit(launcherfontsmall.render(l[lg]["Settings"], True, "White").convert_alpha(), (24, 76))
    if self.on_page == 12:
      pygame.draw.rect(screen, (0, 0, 50), ((16, 70), (482, 350)))
      pygame.draw.rect(screen, (0, 0, 150), ((16, 70), (482, 350)), width=2)
      screen.blit(launcherfontsmall.render(l[lg]["Miscellaneous"], True, "White").convert_alpha(), (24, 76))
      text_surf = pygame.Surface((472, 25)).convert_alpha(); text_surf.fill((0, 0, 50))
      text_surf.blit(launcherfontsmaller.render("  Python Version: " + str(sys.version), True, "White").convert_alpha(), (-maxint(self.long_text_timer.keep_count(5, launcherfontsmaller.render("  Python Version: " + str(sys.version), True, "White").get_width() - 460 + 50, 0), launcherfontsmaller.render("Python Version: " + str(sys.version), True, "White").get_width() - 460), 0))
      screen.blit(text_surf, (24, 105))
      screen.blit(launcherfontsmaller.render("Windows: " + str(sys.getwindowsversion()[0]) + "." + str(sys.getwindowsversion()[1]) + ", Build: " + str(sys.getwindowsversion()[2]) + ", Platform: " + str(sys.platform) + ", API: " + str(sys.api_version), True, "White").convert_alpha(), (24, 130))
      screen.blit(launcherfontsmaller.render("Pygame Version: " + str(pygame.ver) + ", SDL Version: " + str(pygame.get_sdl_version()[0]) + "." + str(pygame.get_sdl_version()[1]) + "." + str(pygame.get_sdl_version()[2]), True, "White").convert_alpha(), (24, 155))
      mem = psutil.virtual_memory()
      screen.blit(launcherfontsmaller.render("Total RAM: " + (str(mem.total / (1024 ** 3)) if k_y else str(round(mem.total / (1024 ** 3), 2))) + " Gigabytes, " + str(mem.percent) + "% used", True, "White").convert_alpha(), (24, 180))
      screen.blit(launcherfontsmaller.render("RAM Usage: " + (str(mem.used / (1024 ** 3)) if k_y else str(round(mem.used / (1024 ** 3), 2))) + " / " + (str(mem.free / (1024 ** 3)) if k_y else str(round(mem.free / (1024 ** 3), 2))) + " Gigabytes", True, "White").convert_alpha(), (24, 205))
      mem = psutil.disk_usage("C:\\")
      screen.blit(launcherfontsmaller.render("Total ROM: " + (str(mem.total / (1024 ** 3)) if k_y else str(round(mem.total / (1024 ** 3), 2))) + " Gigabytes, " + str(mem.percent) + "% used", True, "White").convert_alpha(), (24, 230))
      screen.blit(launcherfontsmaller.render("ROM Usage: " + (str(mem.used / (1024 ** 3)) if k_y else str(round(mem.used / (1024 ** 3), 2))) + " / " + (str(mem.free / (1024 ** 3)) if k_y else str(round(mem.free / (1024 ** 3), 2))) + " Gigabytes", True, "White").convert_alpha(), (24, 255))
      if not k_y:
        screen.blit(launcherfontsmaller.render("Boot Time: " + str(datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')), True, "White").convert_alpha(), (24, 280))
        screen.blit(launcherfontsmaller.render("Logical CPU: " + str(psutil.cpu_count(True)) + ", Physical Cores: " + str(psutil.cpu_count(False)), True, "White").convert_alpha(), (24, 305))
        screen.blit(launcherfontsmaller.render("CPU Frequency (MHz): " + str(psutil.cpu_freq().current), True, "White").convert_alpha(), (24, 330))
      else:
        screen.blit(launcherfontsmaller.render("CPU Context: " + str(psutil.cpu_stats().ctx_switches) + " CTX Switches, " + str(psutil.cpu_stats().interrupts) + " Interrupts,\n" + str(psutil.cpu_stats().soft_interrupts) + " Soft Interrupts, " + str(psutil.cpu_stats().syscalls) + " Syscalls", True, "White").convert_alpha(), (24, 280))
        screen.blit(launcherfontsmaller.render("CPU Times: " + str(psutil.cpu_times().user) + " User,\n" + str(psutil.cpu_times().system) + " System, " + str(psutil.cpu_times().idle) + " Idle", True, "White").convert_alpha(), (24, 315))
      if not k_y:
        screen.blit(launcherfontsmaller.render("CPU: " + cpu, True, "White").convert_alpha(), (24, 355))
        screen.blit(launcherfontsmaller.render("Architecture: " + architecture[0] + ", " + architecture[1], True, "White").convert_alpha(), (24, 380))
      else:
        screen.blit(launcherfontsmaller.render("Platform: " + pf, True, "White").convert_alpha(), (24, 355))
        screen.blit(launcherfontsmaller.render("System: " + pf_system + ", Machine: " + platform.machine(), True, "White").convert_alpha(), (24, 380))
      text_surf = pygame.Surface((472, 18)).convert_alpha(); text_surf.fill((0, 0, 50))
      text_surf.blit(launcherfontsmaller.render("  Path: " + str(sys.argv[0]), True, "White").convert_alpha(), (-maxint(self.long_text2_timer.keep_count(5, launcherfontsmaller.render("  Path: " + str(sys.argv[0]), False, "White").get_width() - 460 + 50, 0), launcherfontsmaller.render("Path: " + str(sys.argv[0]), False, "White").get_width() - 460), 0))
      screen.blit(text_surf, (24, 398))

    if self.on_page == 15:
      pygame.draw.rect(screen, (0, 0, 50), ((16, 70), (482, 350)))
      pygame.draw.rect(screen, (0, 0, 150), ((16, 70), (482, 350)), width=2)
      screen.blit(launcherfontsmall.render(l[lg]["Network Monitor"], True, "White").convert_alpha(), (24, 76))
      net_io = psutil.net_io_counters()
      screen.blit(launcherfontsmaller.render("Bytes Sent: " + str(net_io.bytes_sent) + ", Bytes Received: " + str(net_io.bytes_recv), True, "White").convert_alpha(), (24, 105))
      screen.blit(launcherfontsmaller.render("Packets Sent: " + str(net_io.packets_sent) + ", Packets Received: " + str(net_io.packets_recv), True, "White").convert_alpha(), (24, 130))
      screen.blit(launcherfontsmaller.render("Error In: " + str(net_io.errin) + ", Error Out: " + str(net_io.errout) + ", Dropped In: " + str(net_io.dropin) + ", Dropped Out: " + str(net_io.dropout), True, "White").convert_alpha(), (24, 155))
      screen.blit(launcherfontsmaller.render("Packet Loss: " + str(bool(net_io.dropin) or bool(net_io.dropout)), True, "White").convert_alpha(), (24, 180))
      try: screen.blit(launcherfontsmaller.render("Ping: " + str(verbose_ping(self.server_host) * 1000), True, "White").convert_alpha(), (24, 205))
      except: screen.blit(launcherfontsmaller.render("Ping to host failed", True, "White").convert_alpha(), (24, 205))
    
    if self.on_page == 13:
      """ updated_data = main.client.portal.recv_data(main.client.client, "OBJECT")
      new_lobby = updated_data["MESSAGE"] """
      #is that all of them? let's try
      #console.log(main.client.temporary_packet)
      #print(new_lobby)
      pygame.draw.rect(screen, (0, 0, 50), ((16, 70), (482, 350)))
      pygame.draw.rect(screen, (0, 0, 150), ((16, 70), (482, 350)), width=2)
      screen.blit(launcherfontsmall.render("Host Server", True, "White").convert_alpha(), (24, 76))
      screen.blit(launcherfontsmall.render("Server name: " + self.room_host, True, "White").convert_alpha(), (24, 106))
      screen.blit(launcherfontsmall.render("Participants (" + str(len(self.room_players)) + "/4):", True, "White").convert_alpha(), (24, 136))
      for index, player in enumerate(self.players):
        screen.blit(launcherfontsmaller.render(player, True, "White").convert_alpha(), (120, 150 + (index * 15)))
      
      #if k_y: console.log(updated_lobby)
      

    if self.on_page == 14:
      pygame.draw.rect(screen, (0, 0, 50), ((16, 70), (482, 150)))
      pygame.draw.rect(screen, (0, 0, 150), ((16, 70), (482, 150)), width=2)
      screen.blit(launcherfontsmall.render("Join Server", True, "White").convert_alpha(), (24, 76))
      screen.blit(launcherfontsmall.render("Enter Host's Username: " + self.join_text_username + "_", True, "White").convert_alpha(), (24, 110))
      pygame.draw.rect(screen, (0, 0, 50), ((0, HEIGHT - 175), (WIDTH, 175)))
      pygame.draw.rect(screen, (0, 0, 150), ((0, HEIGHT - 175), (WIDTH, 175)), width=2)#this is all UI
    else: self.join_text_username = "" 
      
    if self.on_page == 17: #Logged in is logged into an account
      if main.client_instance.logged:#Viewing the user's profile
        pygame.draw.rect(screen, (0, 0, 50), ((16, 70), (482, 350)))
        pygame.draw.rect(screen, (0, 0, 150), ((16, 70), (482, 350)), width=2)
        screen.blit(launcherfontsmall.render(l[lg]["Profile"], True, "White").convert_alpha(), (24, 76))
        screen.blit(launcherfontmedium.render("Logged in as: " + main.client_instance.user_data["user"], True, "White").convert_alpha(), (24, 110))
      else:#Not logged in screen
        pygame.draw.rect(screen, (0, 0, 50), ((16, 70), (482, 350)))
        pygame.draw.rect(screen, (0, 0, 150), ((16, 70), (482, 350)), width=2)
        screen.blit(launcherfontsmall.render(l[lg]["Profile"], True, "White").convert_alpha(), (24, 76))
        screen.blit(launcherfontsmall.render("You're not logged in", True, "White").convert_alpha(), ((WIDTH / 2) - (launcherfontsmall.render("You're not logged in", True, "White").get_width() / 2), 150))

    if self.on_page == 18 or self.on_page == 19 or self.on_page == 20: # Did you just rename it?
      pygame.draw.rect(screen, (0, 0, 50), ((16, 70), (482, 350)))
      pygame.draw.rect(screen, (0, 0, 150), ((16, 70), (482, 350)), width=2)
      screen.blit(launcherfontsmall.render("Log In Page", True, "White").convert_alpha(), (24, 76))

      if self.on_page == 19: pygame.draw.rect(screen, "Light blue", ((23, 159), (162, 22)), width=3)
      if self.on_page == 20: pygame.draw.rect(screen, "Light blue", ((23, 229), (162, 22)), width=3)

      screen.blit(launcherfontlittle.render("Username", True, "White").convert_alpha(), (24, 137))
      pygame.draw.rect(screen, (0, 0, 150), ((24, 160), (160, 20)), width=2)

      screen.blit(launcherfontlittle.render(self.rename_text_username, True, "White").convert_alpha(), (26, 160))

      screen.blit(launcherfontlittle.render("Password", True, "White").convert_alpha(), (24, 207))
      pygame.draw.rect(screen, (0, 0, 150), ((24, 230), (160, 20)), width=2)

      screen.blit(launcherfontlittle.render(self.rename_text_password, True, "White").convert_alpha(), (26, 230))

      if self.on_page == 19 or self.on_page == 20:
        pygame.draw.rect(screen, (0, 0, 50), ((0, HEIGHT - 175), (WIDTH, 175)))
        pygame.draw.rect(screen, (0, 0, 150), ((0, HEIGHT - 175), (WIDTH, 175)), width=2)

        if len(self.rename_text_username) > 15: self.rename_text_username = self.rename_text_username[:-1]
        if len(self.rename_text_password) > 15: self.rename_text_password = self.rename_text_password[:-1]

    elif self.on_page == 21 or self.on_page == 22 or self.on_page == 23:
      pygame.draw.rect(screen, (0, 0, 50), ((16, 70), (482, 350)))
      pygame.draw.rect(screen, (0, 0, 150), ((16, 70), (482, 350)), width=2)
      screen.blit(launcherfontsmall.render("Register Page", True, "White").convert_alpha(), (24, 76))
      
      if self.on_page == 22: pygame.draw.rect(screen, "Light blue", ((23, 159), (162, 22)), width=3)
      if self.on_page == 23: pygame.draw.rect(screen, "Light blue", ((23, 229), (162, 22)), width=3)

      screen.blit(launcherfontlittle.render("Create Username", True, "White").convert_alpha(), (24, 137))
      pygame.draw.rect(screen, (0, 0, 150), ((24, 160), (160, 20)), width=2)

      screen.blit(launcherfontlittle.render(self.rename_text_username, True, "White").convert_alpha(), (26, 160))

      screen.blit(launcherfontlittle.render("Create Password", True, "White").convert_alpha(), (24, 207))
      pygame.draw.rect(screen, (0, 0, 150), ((24, 230), (160, 20)), width=2)

      screen.blit(launcherfontlittle.render(self.rename_text_password, True, "White").convert_alpha(), (26, 230))
      
      if self.on_page == 22 or self.on_page == 23:
        pygame.draw.rect(screen, (0, 0, 50), ((0, HEIGHT - 175), (WIDTH, 175)))
        pygame.draw.rect(screen, (0, 0, 150), ((0, HEIGHT - 175), (WIDTH, 175)), width=2)

        if len(self.rename_text_username) > 15: self.rename_text_username = self.rename_text_username[:-1]
        if len(self.rename_text_password) > 15: self.rename_text_password = self.rename_text_password[:-1]
      
    else: self.rename_text_username, self.rename_text_password = "", ""

    if self.on_page == 24: #No connection
      pygame.draw.rect(screen, (0, 0, 50), ((66, 180), (382, 130)))
      pygame.draw.rect(screen, (0, 0, 150), ((66, 180), (382, 130)), width=2)
      screen.blit(launcherfontsmall.render("You're not connected", True, "White").convert_alpha(), (74, 186))

    if self.on_page == 25: #Not logged in
      pygame.draw.rect(screen, (0, 0, 50), ((66, 180), (382, 130)))
      pygame.draw.rect(screen, (0, 0, 150), ((66, 180), (382, 130)), width=2)
      screen.blit(launcherfontsmall.render("You're not logged in", True, "White").convert_alpha(), (74, 186))


    if k_b: self.on_page = 1
  
  def set_display_text(self, text): self.display_text_timer.reset(); self.display_text = text

  def quit(self):
    config = {"Language": lg, "Color Swizzle": self.color_swizzle, "Render Filter": {moderngl.LINEAR: "Linear", moderngl.NEAREST: "Nearest"}[self.render_filter], "Mode": "Pygame"} #"Account": {"username": self.client.username, "password": self.client.password}
    with open("config.json", "w") as file: json.dump(config, file)
    pygame.quit(); sys.exit()
#okay let's goooooo
#Oh wait we don't have keshya files :( one sec follow me


# İ--------------------------------------------------------------------------------------------------------------------------------İ




class Button:
  def __init__(self, x, y, width, height, text, image_path, function, target=None, target_gs=0, target_object=None, color=None, text_color="White", font=fontmedium, page=0, button_type="Button", with_sound=True, shift_x_hitbox=0, shift_y_hitbox=0, hide_below_y=0, hide_above_y=0, room=0):
    self.rect = pygame.Rect((x, y), (width, height))
    self.text = text
    if type(image_path) != list:
      try: self.image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (width, height))
      except Exception as e:
        self.image = font.render("  " + str(image_path), True, text_color)
    else: self.image = image_path
    self.path = image_path
    self.text_color = text_color
    self.function = function
    self.target = target
    self.target_gs = target_gs
    self.target_object = target_object
    self.color = color
    self.page = page
    self.button_type = button_type
    self.timer = Timer()
    self.with_sound = with_sound
    self.rect.x += shift_x_hitbox
    self.shift_x_hitbox = shift_x_hitbox
    self.rect.y += shift_y_hitbox
    self.shift_y_hitbox = shift_y_hitbox
    self.hide_below_y, self.hide_above_y = hide_below_y, hide_above_y
    self.room = room
    if button_type == "Transition Setting Shape": self.image.fill("White", special_flags=pygame.BLEND_RGB_MAX)

  def update(self, y_offset=0):
    if (self.hide_above_y == 0 or self.rect.y > self.hide_above_y) and (self.hide_below_y == 0 or self.rect.y < self.hide_below_y):
      if self.color != None:
        if self.color != "Transparent": pygame.draw.rect(screen, self.color, self.rect)
        else: screen.blit(png_surf, self.rect)
        if not "Color" in self.button_type:
          for c in self.color: color = (maxint(c * 2.5, 255), maxint(c * 2.5, 255), maxint(c * 2.5, 255))
          pygame.draw.rect(screen, color, self.rect, 2)
      if main.gamestate != 10:
        if (main.remember_gs != 43 and main.remember_gs != 35) or main.gamestate != 4:
          if type(self.image) == list:
            screen.blit(pygame.transform.scale(pygame.image.load(self.image[self.timer.keep_count(2 + (15 * int(self.button_type == "Collectible Type")), len(self.image), 0)]).convert_alpha(), (self.rect.width, self.rect.height)), (self.rect.x - self.shift_x_hitbox, (self.rect.y + y_offset) - self.shift_y_hitbox))
          else: screen.blit(self.image, (self.rect.x - self.shift_x_hitbox, (self.rect.y + y_offset) - self.shift_y_hitbox))
        else:
          if (k_y or main.on_page == 7) and self.path != "Space" and self.path != "<": kfont.set_direction(pygame.DIRECTION_RTL)
          elif self.path == "Space" or self.path == "<": kfont.set_direction(pygame.DIRECTION_LTR)
          if not "Text Edit" in self.button_type: screen.blit(kfont.render(" " + self.path, True, self.text_color), (self.rect.x - self.shift_x_hitbox, self.rect.y + y_offset))
          else: screen.blit(self.image, (self.rect.x - self.shift_x_hitbox, (self.rect.y + y_offset) - self.shift_y_hitbox))
  
  def on_hover(self, y_offset=0):
    if (self.hide_above_y == 0 or self.rect.y > self.hide_above_y) and (self.hide_below_y == 0 or self.rect.y < self.hide_below_y):
      if pygame.mouse.get_pos()[0] > self.rect.left and pygame.mouse.get_pos()[0] < self.rect.right and pygame.mouse.get_pos()[1] > self.rect.top + y_offset and pygame.mouse.get_pos()[1] < self.rect.bottom + y_offset:
        main.hover_on_button = True
        if self.text != "Stop Playtest": pygame.draw.rect(screen, "Blue", self.rect, 2)
        if self.text:
          if pygame.mouse.get_pos()[0] < WIDTH / 2: pygame.draw.rect(screen, "Black", (pygame.mouse.get_pos(), (fontsmall.render(self.text, True, "White").get_width() + 5, 24))); screen.blit(fontsmall.render(self.text, True, "White"), (pygame.mouse.get_pos()[0] + 2, pygame.mouse.get_pos()[1] + 4))
          else: pygame.draw.rect(screen, "Black", ((pygame.mouse.get_pos()[0] - (fontsmall.render(self.text, True, "White").get_width() + 5), pygame.mouse.get_pos()[1]), (fontsmall.render(self.text, True, "White").get_width() + 5, 24))); screen.blit(fontsmall.render(self.text, True, "White"), (pygame.mouse.get_pos()[0] - (fontsmall.render(self.text, True, "White").get_width() + 5), pygame.mouse.get_pos()[1] + 4))
        if k_a or ((pygame.key.get_pressed()[pygame.K_SPACE] or pygame.key.get_pressed()[pygame.K_KP_6] or pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_RETURN]) and main.gamestate == 10 and main.editor_mode): self.on_click(self.function)

  def render_border(self):
    if main.gamestate == 10: global program, render_object; program.release(); ctx.clear(); program = ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER); render_object.release(); render_object = ctx.vertex_array(program, [shader_buffer])
    if (self.hide_above_y == 0 or self.rect.y > self.hide_above_y) and (self.hide_below_y == 0 or self.rect.y < self.hide_below_y):
      if self.button_type != "Specifier":
        if main.editor_mode:
          if self.target == main.selected_tile: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 4)), 3)
          if main.gamestate != 55 and (self.target == main.selected_stat and self.button_type == "Stat") or (self.target == main.selected_bool and self.button_type == "Boolean") or (self.target == main.selected_state and self.button_type == "State"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x + 1, self.rect.y - 5), (self.rect.width + 4, self.rect.height + 4)), 3)
          if self.target == main.selected_animation: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x + 2, self.rect.y - 2), (self.rect.width + 8, self.rect.height)), 3)
          if self.target in main.selected_drops: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 4)), 3)
          if self.button_type == "Dialogue" and self.target == main.selected_dl: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x + 2, self.rect.y - 2), (self.rect.width + 11, self.rect.height)), 3)
          if self.button_type == "Tile Type" and self.target == main.selected_tile_type: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 2, self.rect.height + 2)), 3)
          if self.button_type == "Character Type" and self.target == main.selected_character_type: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 2, self.rect.height + 2)), 3)
          if self.button_type == "Collectible Type" and self.target == main.selected_collectible_type: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 2, self.rect.height + 2)), 3)
          if main.gamestate == 55 and self.button_type == "Stat" and self.target == main.collectible_types[main.selected_collectible_type]["stat"]: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 2, self.rect.height + 2)), 3)
          if main.gamestate == 55 and self.button_type == "Value" and self.target == main.collectible_types[main.selected_collectible_type]["value"] and main.game_stats[main.collectible_types[main.selected_collectible_type]["stat"]] == bool: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 2, self.rect.height + 2)), 3)
          if main.gamestate == 56 and self.button_type == "Stat" and self.target == main.entity_types[main.selected_entity_type]["stat"]: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 2, self.rect.height + 2)), 3)
          if main.gamestate == 56 and self.button_type == "Value" and self.target == main.entity_types[main.selected_entity_type]["value"] and main.game_stats[main.entity_types[main.selected_entity_type]["stat"]] == bool: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 2, self.rect.height + 2)), 3)
          if main.gamestate == 57 and self.target in main.entity_types[main.selected_entity_type]["behaviors"]: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 4, self.rect.height)), 3)
          if main.gamestate == 59 and self.button_type == "Cutscene Name":
            for button in main.rooms[main.selected_room].menu["items"]:
              if button["I"] == main.selected_menu_item_index:
                if button["A"] == self.target:
                  pygame.draw.rect(screen, "Dark Blue", ((self.rect.x + 1, self.rect.y - 4), (self.rect.width + 16, self.rect.height + 7)), 3)
          if main.gamestate == 60 and self.target in main.selected_object.behaviors: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 4, self.rect.height)), 3)
          try:
            if self.target == main.selected_frame and self.button_type == "Frame": pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 4)), 3)
          except: pass
          try:
            if self.target == main.selected_object.initial_direction and self.button_type == "Direction": pygame.draw.rect(screen, "Dark Blue", ((self.rect.x + 2, self.rect.y - 2), (self.rect.width + 8, self.rect.height + 4)), 3)
          except: pass
          if self.target == main.selected_button: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x, self.rect.y), (self.rect.width, self.rect.height)), 2, 4)
          try:
            if self.target == main.selected_object.price_stat: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x + 1, self.rect.y - 5), (self.rect.width + 4, self.rect.height + 4)), 3)
          except: pass
          try:
            if self.target == main.selected_object.price_text_position or self.target == main.selected_object.price_text_mode: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x + 1, self.rect.y - 5), (self.rect.width + 16, self.rect.height + 4)), 3)
          except: pass
          try:
            if self.target == main.character_types[main.selected_character_type]["object"].actions[main.selected_state].condition_stat: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x + 1, self.rect.y - 5), (self.rect.width + 16, self.rect.height + 4)), 3)
          except: pass
          try:
            if self.target == main.character_types[main.selected_character_type]["object"].actions[main.selected_state].combo: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 4)), 2)
          except: pass
          try:
            if self.target == main.character_types[main.selected_character_type]["object"].actions[main.selected_state].trigger_mode: pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 4)), 2)
          except: pass
          try:
            if self.target == main.selected_object.trigger_cutscene and self.button_type == "Cutscene Name": pygame.draw.rect(screen, "Dark Blue", ((self.rect.x + 1, self.rect.y - 4), (self.rect.width + 16, self.rect.height + 7)), 3)
          except: pass
          try:
            if self.target == main.projectiles[main.selected_itemy].pos_mode and self.button_type == "Position Mode": pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 4)), 3)
          except: pass
          try:
            if (self.target == main.ui.instances[main.selected_ui][main.selected_ui_mode]["Corner"] and self.button_type == "Uİ Corner"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 6, self.rect.height + 6)), 2)
          except: pass
          try:
            if (self.target == main.game_stats_effect[main.selected_stat] and self.button_type == "Effect"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 6, self.rect.height + 6)), 2)
          except: pass
          try:
            if (main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Frame"] == main.selected_key and main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Object"] == main.selected_object and main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Action"] == self.target and self.button_type == "Action for Frame"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x + 1, self.rect.y - 4), (self.rect.width + 16, self.rect.height + 7)), 3)
          except: pass
          try:
            if (main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Frame"] == main.selected_key and main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Object"] == main.selected_object and main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Dir"] == self.target and self.button_type == "Directions for Frame"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 1, self.rect.y - 4), (self.rect.width + 2, self.rect.height + 7)), 3)
          except: pass
          try:
            if (main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Frame"] == main.selected_key and main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["Object"] == main.selected_object and main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]["SFX"] == self.target and self.button_type == "Character for Frame"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 1, self.rect.y - 4), (self.rect.width + 2, self.rect.height + 7)), 3)
          except: pass
          try:
            if (main.ui.instances[main.selected_ui][main.selected_ui_mode]["TC"] == self.target and self.button_type == "Color") or (main.ui.instances[main.selected_ui][main.selected_ui_mode]["TCOL"] == self.target and self.button_type == "OL Color") or (main.ui.instances[main.selected_ui][main.selected_ui_mode]["TCBG"] == self.target and self.button_type == "BG Color") or (main.ui.instances[main.selected_ui][main.selected_ui_mode]["C1"] == self.target and self.button_type == "B Color") or (main.ui.instances[main.selected_ui][main.selected_ui_mode]["C3"] == self.target and self.button_type == "B OL Color") or (main.ui.instances[main.selected_ui][main.selected_ui_mode]["C2"] == self.target and self.button_type == "B BG Color"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 4)), 2)
          except: pass
          try:
            if (main.tile_types[main.selected_tile_type]["destr_anim"] == self.target and self.button_type == "Destroy Animation"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 2)), 2)
          except: pass
          if main.gamestate == 54 and (main.character_types[main.selected_character_type]["object"].defeat_anim == self.target and self.button_type == "Defeat Animation"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 2)), 2)
          if isinstance(main.selected_object, Door):
            if (self.target in main.selected_object.transition and self.button_type == "Transition"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 2)), 2)
            if (self.target == tuple(main.selected_object.transition_color) and self.button_type == "Transition Setting Color"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 4)), 2)
            if (self.target == main.selected_object.transition_shape and self.button_type == "Transition Setting Shape"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 4)), 2)
          if isinstance(main.selected_object, Text):
            if (self.target == tuple(main.selected_object.color) and self.button_type == "Color") or (self.target == main.selected_object.outline_color and self.button_type == "OL Color")  or (self.target == main.selected_object.bg_color and self.button_type == "BG Color") or (self.target in main.selected_object.behaviors and self.button_type == "Text Behavior"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 4)), 2)
          if isinstance(main.selected_object, Zone):
            if (self.target == tuple(main.selected_object.color) and self.button_type == "Zone Color"): pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 4, self.rect.height + 4)), 2)
          try:
            if self.target in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].conditions and self.button_type == "Event": pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 6, self.rect.height + 6)), 2)
            if self.target == main.rooms[main.selected_room].cutscenes[main.selected_cutscene].condition_gate and self.button_type == "Gate": pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 6, self.rect.height + 6)), 2)
            if self.target == main.rooms[main.selected_room].cutscenes[main.selected_cutscene].condition_stat_gate and self.button_type == "Gate 2": pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 6, self.rect.height + 6)), 2)
            if self.target in main.rooms[main.selected_room].cutscenes[main.selected_cutscene].stat_required and self.button_type == "Boolean": pygame.draw.rect(screen, "Dark Blue", ((self.rect.x - 2, self.rect.y - 2), (self.rect.width + 6, self.rect.height + 6)), 2)
          except: pass
        else:
          if self.button_type == "Player Indices" and self.target == main.selected_player: pygame.draw.rect(screen, "Blue", self.rect, border_radius=4); screen.blit(self.image, (self.rect.x - self.shift_x_hitbox, self.rect.y + 3))
          if self.button_type == "Device" and self.target == main.ports[main.selected_player].device: pygame.draw.rect(screen, "Blue", self.rect, border_radius=4); screen.blit(self.image, (self.rect.x - self.shift_x_hitbox, self.rect.y + 3))
          if self.button_type == "Filter" and self.target == main.render_filter: pygame.draw.rect(screen, "Blue", self.rect, border_radius=4); screen.blit(self.image, (self.rect.x - self.shift_x_hitbox, self.rect.y + 3))
          if self.button_type == "Color Swizzle" and self.target == main.color_swizzle[::-1]: pygame.draw.rect(screen, "Blue", self.rect, border_radius=4); screen.blit(self.image, (self.rect.x - self.shift_x_hitbox, self.rect.y + 3))
          if self.button_type == "Language" and self.target == lg: pygame.draw.rect(screen, "Blue", self.rect, border_radius=4); screen.blit(self.image, (self.rect.x - self.shift_x_hitbox, self.rect.y + 3))

  def on_click(self, event):
    global k_a
    #if event != go_to and event != go_to_main and event != go_to_rgs and event != add_object and event != edit and event != room and event != access_layer and event != edit_room and event != manage_tiles:
    #  main.undo_state = len(undo_history) - 1
    #  undo_history.append(main)
    #if main.gamestate == 0 and not main.editor_mode: main.on_page = 1
    if (self.path == "Assets/editor/more.png" or self.path == "Assets/editor/less.png" or self.path == "Assets/editor/ccw.png" or self.path == "Assets/editor/cw.png") and k_y:
      if type(self.target) == int: self.target *= 10
      if type(self.target) == float: self.target *= 10.0
    if self.with_sound:#let's get back on the network
      if self.path == "Assets/editor/more.png" or self.path == "Assets/editor/cw.png": increase_by_sfx.play()
      elif self.path == "Assets/editor/less.png" or self.path == "Assets/editor/ccw.png": decrease_by_sfx.play()
      elif self.text != "Play Sound Effect" and self.text != "Play Track": button_sfx.play()
    if l["EN"]["Delete Room"] in self.text or l["EN"]["Rename Room"] in self.text or l["EN"]["Edit Room"] in self.text: self.target = main.rooms[main.selected_room]
    if l["EN"]["Play Track"] in self.text:
      if main.gamestate == 5: self.target = main.active_directory + "Sounds/tracks/" + main.rooms[main.selected_room].track
      if main.gamestate == 41: self.target = main.rooms[main.selected_room].cutscenes[main.selected_cutscene].animations[main.selected_cutscene_attrib_index]['Track']
    if l["EN"]["Play Sound Effect"] in self.text:
      if type(main.sfx[main.selected_itemy]) == list: self.target = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.sfx[main.selected_itemy][random.randrange(0, len(main.sfx[main.selected_itemy]))])
      else: self.target = pygame.mixer.Sound(main.active_directory + "Sounds/sfx/" + main.sfx[main.selected_itemy])
    if l["EN"]["Add Sound Effect"] in self.text or l["EN"]["Go Back."] in self.text: self.target = main.remember_gs; self.target_gs = main.remember_gs
    if l["EN"]["Set Label"] in self.text: self.target = main.rooms[main.selected_room].layers[main.selected_layer]; event(self.target_gs, self.target, self.target_object)
    
    elif l["EN"]["Rename"] in self.text or self.text == l["EN"]["Set Dialogue"] or self.text == l["EN"]["Set Text"] or self.text == l["EN"]["Enter Game Publisher"]: event(self.target_gs, self.target, self.target_object)
    elif l["EN"]["Change Border"] in self.text: main.selected_rename_attrib = self.target_object; event(self.target_gs, self.target, self.target_object)
    elif l["EN"]["Change FPS"] in self.text or l["EN"]["Change Display"] in self.text or l["EN"]["Set Up Tile Size"] in self.text: main.selected_rename_attrib = self.path; event(self.target_gs, self.target, self.target_object)
    elif l["EN"]["Go Back"] in self.text: event(self.target_gs)
    elif l["EN"]["Delete Dialogue"] in self.text: event(main.selected_dl)
    elif len(self.text) == 1:
      if main.remember_gs == 43: event(self.text)
      elif len(str(main.rename_text)) < 40 and main.remember_gs != 8: event(self.text)
      if len(str(main.rename_text)) < 5 and main.remember_gs == 8: event(self.text)
    else: event(self.target)
    if (self.path == "Assets/editor/more.png" or self.path == "Assets/editor/less.png" or self.path == "Assets/editor/ccw.png" or self.path == "Assets/editor/cw.png") and k_y:
      if type(self.target) == int: self.target //= 10
      if type(self.target) == float: self.target /= 10.0
    k_a = False





class Console:
  def __init__(self):
    self.rect = pygame.Rect((0, 50), (200, 200))
    self.border_rect = pygame.Rect((0, 50), (200, 200))
    self.console_surface = pygame.Surface((self.rect.width - 4, self.rect.height - 34))
    self.logs = []
    self.colors = []
    self.y = 0
    self.y_scroll = 0
    self.hidden = True

  def update(self, screen):
    if not self.hidden:
      dx = self.rect.x - self.border_rect.x; dy = self.rect.y - self.border_rect.y; distance = math.hypot(dx, dy)
      if distance != 0: move_x = (dx / distance) * 20; move_y = (dy / distance) * 20; self.border_rect.move_ip(move_x, move_y)
      if distance > 20: pygame.draw.rect(screen, (100, 100, 100), self.border_rect, width=1)
      pygame.draw.rect(screen, (0, 0, 50), self.rect)
      pygame.draw.rect(screen, (0, 0, 150), self.rect, width=2)
      screen.blit(launcherfontlittle.render("Console", True, "White").convert_alpha(), (self.rect.x + 4, self.rect.y + 2))
      if main.gamestate == 0 or main.editor_mode:
        if k_a: self.rect.x = pygame.mouse.get_pos()[0]; self.rect.y = pygame.mouse.get_pos()[1]
        if k_up: self.y_scroll -= 4
        if k_down: self.y_scroll += 4
      self.console_surface.fill((0, 0, 20))
      self.y = 0
      for index, log in enumerate(self.logs):
        text = launcherfonttiny.render(str(log), True, self.colors[index], wraplength=self.console_surface.get_width()).convert_alpha()
        text_height = text.get_height()
        self.console_surface.blit(text, (0, self.y - self.y_scroll))
        self.y += text_height
      if self.y_scroll < 0: self.y_scroll = 0
      if self.y_scroll > self.y - self.console_surface.get_height(): self.y_scroll = self.y - self.console_surface.get_height()
      screen.blit(self.console_surface, (self.rect.x + 2, self.rect.y + 30))

  def log(self, event, color="White", catch_up=False):
    self.logs.append(event); self.colors.append(color)
    if catch_up:
      self.y_scroll = self.y - self.console_surface.get_height()




# --------------------------------------------------------------------------------------------------------------------------------

class MarineSnow:
  def __init__(self, spawn=False): self.rect = pygame.FRect((random.randrange(-40, WIDTH + 40), HEIGHT - (int(spawn) * random.randrange(0, HEIGHT))), (1, 1)); self.xspeed = random.randrange(-100, 101) * 0.002#; self.xspeed = random.randrange(-2, 3) * 0.13
  def update(self, dt=1): pygame.draw.rect(screen, "White", self.rect); self.rect.x += self.xspeed * dt; self.rect.y -= 2.5 * dt


class Number:
  def __init__(self, text, x, y, colors=["White"]):
    self.text = text
    self.x = x
    self.y = y
    self.timer = Timer()
    self.flash_timer = Timer()
    self.alive = True
    self.colors = colors

  def update(self):
    screen.blit(fontsmall.render(self.text, True, self.colors[self.flash_timer.keep_count(2, len(self.colors), 0)]), ((self.x - main.camera.scroll[0]) + 75, self.y))
    if self.timer.timer(FPS * 2): self.alive = False


    

k_right, k_left, k_down, k_up, k_a, k_b, k_x, k_y, k_z, k_l, k_r, k_select, k_start, k_back = False, False, False, False, False, False, False, False, False, False, False, False, False, False

def run(ignore_res=False):
  global screen, program, render_object
  if k_down and k_up and pygame.mouse.get_pressed(): pygame.image.save(screen, "screenshot.png")
  mouse = pygame.mouse.get_pos()
  clock.tick(FPS)
  resizer = pygame.Surface((main.width, main.height))
  if ((main.gamestate == 1 and not main.editor_mode) or (main.gamestate == 10 and main.editor_mode)) or ignore_res: screen = pygame.transform.scale(screen, (main.width, main.height)); resizer.blit(screen, (0, 0)); resizer = pygame.transform.scale(screen, (WIDTH, HEIGHT))
  if main.display_text_timer.count(1 * main.dt, 325, 0) < 323 and not main.editor_mode:
    if main.gamestate == 1: resizer.blit(launcherfontsmaller.render(main.display_text, True, "White"), (30, 300))
    else: screen.blit(launcherfontsmaller.render(main.display_text, True, "White"), (30, 300))
  if ((main.gamestate == 1 and not main.editor_mode) or (main.gamestate == 10 and main.editor_mode)) or ignore_res:
    display.blit(resizer, (main.camera.shake[0], main.camera.shake[1]))
    if main.gamestate == 10 and main.editor_mode: display.blit(stop_playtesting_surf, (5, 5))
  else:
    screen = pygame.transform.scale(screen, (WIDTH, HEIGHT))
    display.blit(screen, (main.camera.shake[0], main.camera.shake[1]))
  if not (main.gamestate == 1 and not main.editor_mode) and not (not (pygame.mouse.get_rel()[0] or pygame.mouse.get_rel()[1]) and (main.gamestate == 10 and main.editor_mode)):
    if mouse[0] > WIDTH / 2 and main.hover_on_button: display.blit(cursor_surf, mouse)
    elif not main.hover_on_button: display.blit(cursor_surf, mouse)
    else: display.blit(cursor2_surf, (mouse[0] - 10, mouse[1]))
  if mouse[0] < 0: pygame.mouse.set_pos((0, mouse[1]))
  if mouse[0] > WIDTH - 3: pygame.mouse.set_pos((WIDTH - 3, mouse[1]))
  if mouse[1] > HEIGHT - 3: pygame.mouse.set_pos((mouse[0], HEIGHT - 3))
  texture = ctx.texture(display.get_size(), 4)
  texture.filter = (moderngl.NEAREST, main.render_filter); texture.swizzle = main.color_swizzle; texture.write(display.get_view("1")); texture.use(0); program["tex"] = 0
  if ((main.gamestate == 1 and not main.editor_mode) or (main.gamestate == 10 and main.editor_mode)) and main.rooms[main.current_room].shader != "":
    if "time" in main.rooms[main.current_room].shader_prog._members: main.rooms[main.current_room].shader_prog["time"] = time() - main.time_since_start
    if "resolution" in main.rooms[main.current_room].shader_prog._members: main.rooms[main.current_room].shader_prog["resolution"] = (main.width, main.height)
    if "mouse" in main.rooms[main.current_room].shader_prog._members: main.rooms[main.current_room].shader_prog["mouse"] = (mouse[0], mouse[1])
    if "cam_pos" in main.rooms[main.current_room].shader_prog._members: main.rooms[main.current_room].shader_prog["cam_pos"] = (main.camera.scroll[0], main.camera.scroll[1])
    if "random" in main.rooms[main.current_room].shader_prog._members: main.rooms[main.current_room].shader_prog["random"] = random.randrange(0, 100)
    if "random_const" in main.rooms[main.current_room].shader_prog._members: main.rooms[main.current_room].shader_prog["random_const"] = main.random_const
    if "player_amount" in main.rooms[main.current_room].shader_prog._members: main.rooms[main.current_room].shader_prog["player_amount"] = len(main.players)
    if "player_in_amount" in main.rooms[main.current_room].shader_prog._members: main.rooms[main.current_room].shader_prog["player_in_amount"] = len([player for player in main.players if player.in_])
    if "menu_item" in main.rooms[main.current_room].shader_prog._members: main.rooms[main.current_room].shader_prog["menu_item"] = (main.rooms[main.current_room].selected_item[0], main.rooms[main.current_room].selected_item[1])
    main.rooms[main.current_room].shader_vao.render(mode=moderngl.TRIANGLE_STRIP)
  else: render_object.render(mode=moderngl.TRIANGLE_STRIP)
  pygame.display.flip() #if time is being used then look
  texture.release()
  if not ignore_res: screen.fill("Black")
  if main.gamestate == 1 and main.game_name == "" and not main.editor_mode: screen.blit(launcherfontsmaller.render("enterprise mode", True, "White"), (30, 30))

console = Console()
console.log("Booting up...")
console.log("This is the terminal window. This is where logs are reported.", "Yellow")

#console.log("[TELECOちゃん]: LISTENING")
#console.log("[TELECOちゃん]: 1024 BYTES")

#undo_history = []



if __name__ == "__main__":
  main = Main(False)
  threading.Thread(target=main.client_instance.run_listen, daemon=True).start()
  while True:
    main.update()