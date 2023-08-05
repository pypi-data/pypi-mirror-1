import os
import sys
import math
import threading

try: import pygame
except ImportError: raise 'Pygame is not installed. Please install it.'
from pygame.locals import *
if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

#============================= SCREEN FUNCTIONS ================================

def check_screen_atts(screen_obj):

    try:   # checks width attribute
        width = int(screen_obj.width)
        self.width = width
    except:
        raise "Width is not a viable type. Width = %d "  %(screen_obj.width)

    try:  # checks height attribute
        height = int(height)
        self.height = height
    except:
        raise "Height is not a vaiable type. Height = %d" %(screen_obj.height)





def create_screen(screen_obj): # takes a Screen() objects.
    global screen, handler
    screen = screen_obj
    screen.clock = pygame.time.Clock()
    screen.FPS = 600
    screen.visible_sprites = pygame.sprite.OrderedUpdates()

    screen.display = pygame.display.set_mode((screen.width, screen.height), pygame.DOUBLEBUF)
    pygame.display.set_caption(screen.title)

    if type(screen.background) is str:
        #screen.image = pygame.image.load(filler).convert()
        screen.color = (0, 0, 0, 255)
    elif type(screen.background) in (tuple, list):
        color = screen.background
        screen.background = pygame.Surface((screen.width, screen.height))
        screen.background.fill(color)
        screen.color = (color)
    else:
        raise 'Unknown data sent to fill the screen'
   
    if screen.color != (0, 0, 0):
        screen.background.set_colorkey((0, 0, 0, 255))
    else:
        screen.background.set_colorkey((255, 255, 255, 255))
    for i in screen.visible_sprites.sprites():
        i.remove(screen.visible_sprites)
    screen.display.blit(screen.background, screen.background.get_rect())
    pygame.display.flip()

    screen.quitting = False

    handler = EventHandler()
    handler.start()

def end():
    screen.quitting = True
    pygame.event.post(pygame.event.Event(2))
    from time import sleep
    sleep(.05)
    pygame.display.quit()

def remove(obj):
    obj.sprite.kill()
    update()

def clear_screen():
    global screen
    screen.visible_sprites.clear(screen.display, screen.background)
    screen.visible_sprites.empty()
    pygame.display.flip()#self.update()

def update():
    check_graphics()
    screen.clock.tick(screen.FPS)
    screen.visible_sprites.clear(screen.display, screen.background)
    rects = screen.visible_sprites.draw(screen.display)
    pygame.display.update(rects)



#============================== SHAPE FUNCTIONS ===============================

#------Automated sprite creation and movement-----
def sprite_create(obj, width, height):
    width = int(math.fabs(width))
    height = int(math.fabs(height))
    obj.sprite = pygame.sprite.Sprite()
    obj.sprite.image = pygame.Surface([width, height])
    obj.sprite.rect = obj.sprite.image.get_rect()
    screen.visible_sprites.add(obj.sprite)

    obj.sprite.image.set_colorkey(screen.color)
    obj.sprite.image.fill(screen.color)
    

def sprite_move(obj, pos):
    check_graphics()
    try: 
        len(pos) == 2
        obj.sprite.rect.center = (pos[0], flip_coords(pos[1]))
    except:
        obj.sprite.rect.center = (pos.x, flip_coords(pos.y))

def rotate_sprite(obj, angle):
    check_graphics()
    center = obj.sprite.rect.center
    obj.sprite.image = pygame.transform.rotate(obj.sprite.image, angle)
    obj.sprite.rect = obj.sprite.image.get_rect(center=center)

def plot(obj): # must be passed a Plot()
    check_graphics()
    obj.sprite = pygame.sprite.Sprite()
    obj.sprite.image = pygame.Surface([obj.size*2, obj.size*2])
    obj.sprite.rect = obj.sprite.image.get_rect()
    screen.visible_sprites.add(obj.sprite)
    obj.sprite.rect.center = (obj.pos.x, flip_coords(obj.pos.y))
    obj.sprite.image.fill(obj.color)
    update()

def create_line(obj): # Must take a line object
    check_graphics()
    obj.width = int(math.fabs(obj.start.run(obj.end)))
    if obj.width == 0 or obj.width == 1:
        obj.width = 2
    
    obj.height = int(math.fabs(obj.start.rise(obj.end)))
    if obj.height == 0 or obj.height == 1:
        obj.height = 2

    dx = min(obj.start.x, obj.end.x)
    dy = min(obj.start.y, obj.end.y)
    start = (obj.start.x - dx, obj.start.y - dy)
    end = (obj.end.x - dx, obj.end.y - dy)
    
    obj.x = min(obj.start.x, obj.end.x)
    obj.y = max(obj.start.y, obj.end.y)
    #sprite_create(obj)
    #-----
    obj.sprite = pygame.sprite.Sprite()
    obj.sprite.image = pygame.Surface([obj.width, obj.height])
    obj.sprite.rect = obj.sprite.image.get_rect()
    screen.visible_sprites.add(obj.sprite)
    obj.sprite.rect.topleft = (obj.x, flip_coords(obj.y))

    obj.sprite.image.set_colorkey(screen.color)
    obj.sprite.image.fill(screen.color)
    #-----
    if int(math.fabs(obj.start.run(obj.end))) == 0:
        pygame.draw.rect(obj.sprite.image, obj.color, [0, 0, 2, obj.height])
    elif int(math.fabs(obj.start.rise(obj.end))) == 0:
        pygame.draw.rect(obj.sprite.image, obj.color, [0, 0, obj.width, 2])
    else:
        pygame.draw.aaline(obj.sprite.image, obj.color, (start[0],flip_coords(start[1], obj.sprite.rect)), 
                  (end[0], flip_coords(end[1], obj.sprite.rect)), False)
    update()

def create_box(obj): # Must take a box object
    check_graphics()
    
    sprite_create(obj, obj.width, obj.height)
    sprite_move(obj, (obj.center.x, obj.center.y))
    if obj.filled:
        obj.thickness = 0
    pygame.draw.rect(obj.sprite.image, obj.color, [0, 0, obj.width, obj.height], obj.thickness)
    update()

def create_polygon(obj): # Must take a polygon object
    check_graphics()
    
    x_values = []
    y_values = []
    for point in obj.points:
        x_values.append(point[0])
        y_values.append(point[1])
    dx = min(x_values)  
    dy = min(y_values)
    sprite_create(obj, obj.width + 1, obj.height + 1)
    relative_points = []
    for point in obj.points:
        relative_points.append((point[0] - dx, flip_coords(point[1] - dy + 1, obj.sprite.rect)))
    sprite_move(obj, (obj.center.x, obj.center.y))
    if obj.filled:
        obj.thickness = 0

    sprite_move(obj, (obj.center.x, obj.center.y))
    pygame.draw.polygon(obj.sprite.image, obj.color, relative_points, obj.thickness)
    update()

def create_circle(obj): # Must take a circle objects
    check_graphics()
    sprite_create(obj, obj.radius*2, obj.radius*2)
    sprite_move(obj, (obj.center.x, obj.center.y))
    if obj.filled:
        obj.thickness = 0
    pygame.draw.circle(obj.sprite.image, obj.color, 
                       (obj.radius, obj.radius), obj.radius, obj.thickness)
    update()

def create_arc(obj):
    check_graphics()
    width = obj.radius*2
    height = obj.radius*2
    sprite_create(obj, width, height)
    sprite_move(obj, (obj.center.x, obj.center.y))
    if obj.filled == True:
        obj.thickness = obj.radius

    pygame.draw.arc(obj.sprite.image, obj.color, [0, 0, width, height], 
                     math.radians(obj.start_angle), math.radians(obj.end_angle), obj.thickness)
    update()

def create_oval(obj): # Must take an oval object
    check_graphics()
    sprite_create(obj, obj.width, obj.height)
    sprite_move(obj, (obj.center.x, obj.center.y))
    if obj.filled == True:
        obj.thickness = 0
    pygame.draw.ellipse(obj.sprite.image, obj.color,
                        [0, 0, obj.width, obj.height], obj.thickness)
    update()

def create_image(obj): # must take an image object
    check_graphics()
    obj.sprite = pygame.sprite.Sprite()
    obj.sprite.image = pygame.image.load(obj.path_name).convert()
    obj.sprite.rect = obj.sprite.image.get_rect()
    obj.width = obj.sprite.rect.width
    obj.height = obj.sprite.rect.height
    screen.visible_sprites.add(obj.sprite)
    obj.sprite.rect.topleft = (obj.pos.x, flip_coords(obj.pos.y + obj.height))
    update()

#------object manipulaters-------
def move_to(obj, pos):
    check_graphics()
    sprite_move(obj, pos)
    update()

def rotate_by(obj, angle):
    check_graphics()
    rotate_sprite(obj, angle)
    update()
    
#================================== Text ======================================

def create_text(obj):
    if not pygame.font.get_init():
        pygame.font.init()
    
    font = pygame.font.Font(None, obj.size)
    obj.sprite = pygame.sprite.Sprite()
    obj.sprite.image= font.render(obj.text, 1, obj.color)
    obj.sprite.rect = obj.sprite.image.get_rect()
    screen.visible_sprites.add(obj.sprite)
    obj.sprite.rect.topleft = (obj.pos.x, flip_coords(obj.pos.y + obj.sprite.rect.height))

    update()

#================================== Sound =====================================

def create_sound(obj): # needs to be a sound object.
    try: 
        pygame.mixer.init()
    except:
        print "sound is all ready init"
        pass
    obj.sound = pygame.mixer.Sound(obj.path)

def play_sound(obj):
    obj.sound.play()

def stop_sound(obj):
    obj.sound.stop()

# ============================== Event Functions ==============================

def mouse_pos():
    pygame.event.pump()
    a = pygame.mouse.get_pos()
    return a[0], flip_coords(a[1])

def mouse_pressed():
    pressed = pygame.mouse.get_pressed()
    return {'left': pressed[0],
            'middle': pressed[1],
            'right': pressed[2]}

def keys(): #returns all the keys currently being pressed
    pressed = pygame.key.get_pressed()
    name=pygame.key.name
    all=[]
    for key in [name(i) for i in xrange(len(pressed)) if pressed[i]]:
        if key[0] == '[' and key[-1] == ']': key = key[1:-1] #numpad key
        if key not in all: #is this 'if' needed?
            all.append(key)
    return all


#=============================== EVENT HANDLER ================================

class EventHandler(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while not screen.quitting:
            check_events()


def check_events(): 
    event = pygame.event.poll()
    if event.type == ACTIVEEVENT: # if the event is an ACTIVEEVENT
        if event.state == 2 and event.gain == 0: # and its state is 2
            #wait = True
            #while wait:
            #    wait_event = pygame.event.wait()
                #if wait_event.type == ACTIVEEVENT:
                #    if wait_event.state == 2 and wait_event.gain == 1:
                #       wait = False
            #    if wait_event.type == QUIT:
            #        pygame.quit()
            #        sys.exit()
            pygame.display.update()
    elif event.type == QUIT:
        pygame.quit()
        sys.exit()
    
    return event

# ============================ Exception Handling ============================

def check_graphics():
    if not pygame.display.get_surface():
        raise "No graphics window initialized. Please call begin_graphics()."

def check_sound():
    if not pygame.mixer.get_init():
        raise "Sound is not initialized"

def check_text():
    if not pygame.font.get_init():
        raise "Font is not initialized"


# =============================== BACKEND TOOLS ===============================
def screen_picture(file_name):
    pygame.image.save(screen.display, file_name)
    

def flip_coords(y, surface=None): #changes topleft from (0,0) to bottomleft being (0,0)
    if not surface:
        surface = screen
   
    try:
        return surface.height - y.y
    except:
        return surface.height - y

