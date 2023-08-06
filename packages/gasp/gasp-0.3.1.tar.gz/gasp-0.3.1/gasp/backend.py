#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This program is part of GASP, a toolkit for newbie Python Programmers.
# Copyright (C) 2009, the GASP Development Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import math
import multiprocessing
import threading
import gobject
import time
import gtk
import cairo


# diffrent update_when values
NOTHING = "Nothing"
MOUSE_PRESSED = "Mouse_Pressed"
KEY_PRESSED = "Key_Pressed"
screen = None

#============================= SCREEN FUNCTIONS ================================

def check_screen_atts(screen_obj):

    try:   # checks width attribute
        width = int(screen_obj.width)
        self.width = width
    except:
        raise GaspException("Width is not a viable type. Width = %d "  % screen_obj.width)

    try:  # checks height attribute
        height = int(height)
        self.height = height
    except:
        raise GaspException("Height is not a vaiable type. Height = %d" % screen_obj.height)


def shutdown(type, value, traceback):
    end()
    sys.__excepthook__(type, value, traceback)
    
    
def create_screen(screen_obj): # takes a Screen() objects.
    global screen
    #create the screen obj
    screen = screen_obj

    #create the window and set its size and title
    screen.window = gtk.Window()
    screen.window.set_title(screen.title)
    screen.window.set_default_size(screen.width, screen.height)
    screen.window.set_resizable(False)

    #create the drawing area 
    screen.drawing_area = gtk.DrawingArea()
    screen.window.add(screen.drawing_area)
    screen.drawing_area.set_size_request(screen.width,screen.height)
    screen.drawing_area.show()

    screen.frame_rate = 40
    screen.last_tick = time.time()

    #set up the event handling
    screen.drawing_area.set_events( gtk.gdk.EXPOSURE_MASK
                                | gtk.gdk.BUTTON1_MOTION_MASK
                                | gtk.gdk.BUTTON_PRESS_MASK
                                | gtk.gdk.BUTTON_RELEASE_MASK
                                | gtk.gdk.POINTER_MOTION_MASK
                                | gtk.gdk.POINTER_MOTION_HINT_MASK)
    screen.drawing_area.connect("motion_notify_event", mouse_move)
    screen.drawing_area.connect('button-press-event', mouse_press)
    screen.drawing_area.connect('button-release-event', mouse_release)
    screen.window.connect("key-press-event",key_pressed)
    screen.window.connect("key-release-event",key_released)
    screen.window.connect('delete-event', quit)
    screen.keys_pressed = []
    screen.mouse_pos = (-1,-1)
    screen.mouse_state = {"left":0,"middle":0,"right":0}
    screen.mouse_buttons = ["left","middle","right"]

    #set the window icon and show the window
    pic = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),"images"),"gasp.png")
    screen.window.set_icon_from_file(pic)
    screen.window.show()

    #create the buffer to draw to
    screen.buffer = gtk.gdk.Pixmap(screen.drawing_area.window, screen.width, screen.height)
    screen.gc = gtk.gdk.GC(screen.buffer)
    screen.objects = []
    screen.action_objects = multiprocessing.Queue()
    screen.keys = multiprocessing.Queue()
    screen.process = multiprocessing.current_process()

    screen.mouse = multiprocessing.Queue()

    #start the thread that will update the gui by calling main_iteration
    screen.updater = Updater(screen)
    
    screen.screenshot = False
    screen.filename = ""
    screen.update_when = NOTHING
    screen.update1 = multiprocessing.Queue()
    screen.update2 = multiprocessing.Queue()
    #if this is called to often key and mouse events will be slow
    screen.sprites = 0

    screen.text_entry = None
    screen.entry_done = multiprocessing.Queue()
    screen.updater.daemon = True
    screen.updater.start()

def quit(widget=None, event=None):
    screen.updater.running = False
    os.popen("kill "+str(os.getppid()))
    #screen.process.terminate()

class Updater( multiprocessing.Process ):
    """thread that handles the updateing of the GUI
       This thread does not update the graphics"""
    def __init__(self,screen):
        self.screen = screen
        multiprocessing.Process.__init__(self)
        self.objects = []
        self.sprites = 0

    def killPID(self):
        os.popen("kill -9 "+str(os.getppid()))
        os.popen("kill -9 "+str(os.getpid()))

    def create_obj(self,obj):
        if obj[0] == "circle":
            create_circle(obj[1])
            self.objects.append(obj[1])
        elif obj[0] == "box":
            create_box(obj[1])
            self.objects.append(obj[1])
        elif obj[0] == "plot":
            plot(obj[1])
            self.objects.append(obj[1])
        elif obj[0] == "line":
            create_line(obj[1])
            self.objects.append(obj[1])
        elif obj[0] == "polygon":
            create_polygon(obj[1])
            self.objects.append(obj[1])
        elif obj[0] == "arc":
            create_arc(obj[1])
            self.objects.append(obj[1])
        elif obj[0] == "oval":
            create_oval(obj[1])
            self.objects.append(obj[1])
        elif obj[0] == "image":
            create_image(obj[1])
            self.objects.append(obj[1])
        elif obj[0] == "text":
            create_text(obj[1])
            self.objects.append(obj[1])

    def update(self,widget=None, event=None):
        self.check_queues()
        if not self.running: return False
        context = self.screen.buffer.cairo_create() #create a cairo context the draw to buffer
        #draw background
        context.set_source_rgb(*self.screen.background)
        context.rectangle(0, 0, *self.screen.drawing_area.window.get_size())
        context.fill()
        #draw all of the objects on screen
        if screen.text_entry:
            screen.text_entry.draw(context)
        else:
            for i in self.objects:
                i.draw(context)
        #take a screenshot it must be hear because it requires an active cairo context
        if self.screen.screenshot:
            print "taking screen shot"
            self.screen.screenshot = False
            surf = context.get_target()
            surf.write_to_png(self.screen.filename)
        #draw the buffer onto the actual drawing area
        self.screen.drawing_area.window.draw_drawable(self.screen.gc,self.screen.buffer,0,0,0,0,-1,-1,)
        #return True
        #make sure that the number of sprites on screen hasn't changed
        if self.sprites == len(self.objects):
            return True
        #if the number of sprites has changed it will end this time out
        #and begin a new one with more or less time difference depending
        #on the number of sprites on screen
        #this makes sure it is not updated to often
        if self.sprites != len(self.objects):
            gobject.timeout_add(40+len(self.objects)/10,self.update)
            self.sprites = len(self.objects)
            return False

    def check_queues(self):
        while not self.screen.update1.empty():
            self.screen.update_when = self.screen.update1.get()
        while not self.screen.action_objects.empty():
            obj=screen.action_objects.get()
            if obj[1] =="end_graphics":
                self.running = False
            elif obj[1] == "text entry":
                self.screen.text_entry = obj[0]
            elif obj[1] =="remove_all":
                self.objects = []
            elif obj[1] == "screen shot":
                self.screen.screenshot = True
                self.screen.filename = obj[0]
            elif obj[1] == "new object":
                self.create_obj(obj[0])
            else:
                for i in self.objects:
                    if i.key == obj[0].key:
                        if obj[1] == "remove":
                            self.objects.remove(i)
                        if obj[1] == "move_to":
                            i.move_to(obj[2])
                        if obj[1] == "move_by":
                            i.move_by(obj[2][0],obj[2][1])
                        if obj[1] == "rotate_by":
                            i.rot += obj[2]
                        if obj[1] == "rotate_to":
                            i.rot = obj[2]

    def run(self):
        gobject.timeout_add(40, self.update) #this will call update periodically
        self.running = True
        #while threading.enumerate()[0].isAlive() and self.running:
           #if threading.activeCount() < 2: self.killPID()
        while self.running:
            sleep(1.0/100.0)
            gtk.main_iteration(False)


#============================== EVENT HANDLER FUNCTIONS ===============================

def key_pressed(widget, event):
    if screen.text_entry:
        if event.keyval == 65293:
            screen.entry_done.put(screen.text_entry.entry)
            screen.text_entry = None
        elif event.keyval == 65288:
            screen.text_entry.entry = screen.text_entry.entry[:-1]
        else:
            screen.text_entry.entry += event.string
    else:
        string = ""
        if event.keyval == 65364:string = "down"
        elif event.keyval == 65362:string = "up"
        elif event.keyval == 65361:string = "left"
        elif event.keyval == 65363:string = "right"
        elif event.keyval == 65293:string = "enter"
        elif event.keyval == 65506:string = "shift"
        elif event.keyval == 65289:string = "tab"
        else:string = event.string
        if not string in screen.keys_pressed: screen.keys.put([string,"pressed"])
        if screen.update_when == KEY_PRESSED: screen.update2.put(NOTHING)

def key_released(widget, event):
    string = ""
    if event.keyval == 65364:string = "down"
    elif event.keyval == 65362:string = "up"
    elif event.keyval == 65361:string = "left"
    elif event.keyval == 65363:string = "right"
    elif event.keyval == 65293:string = "enter"
    elif event.keyval == 65506:string = "shift"
    elif event.keyval == 65289:string = "tab"
    else:string = event.string
    screen.keys.put([string,"released"])

def mouse_press(widget, event):
    screen.mouse.put(["press",screen.mouse_buttons[event.button-1],1])
    if screen.update_when == MOUSE_PRESSED:
        screen.update_when = NOTHING


def mouse_release(widget, event):
    screen.mouse.put(["press",screen.mouse_buttons[event.button-1],0])

def mouse_move(widget, event):
    screen.mouse.put(["position",(event.x,event.y)])



def require_screen(func):
    def wrapper(*args):
        if not screen:
            raise GaspException("No graphics window initialized. Please call begin_graphics().")
        return func(*args)

    return wrapper


#============================== SHAPE FUNCTIONS ===============================
@require_screen
def plot(obj): # must be passed a Plot()
    obj.rot = 0
    obj.topleft = (obj.center.x-obj.size,obj.center.y-obj.size)
    obj.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,int(obj.size*2),int(obj.size*2))
    context = cairo.Context(obj.surface)
    context.set_source_rgb(*obj.color)
    context.rectangle(0,0,obj.size*2,obj.size*2)
    context.fill_preserve()
    obj.on_screen = True
    #screen.objects.append(obj)

@require_screen
def create_line(obj): # Must take a line object
    thickness = obj.thickness
    obj.topleft = (min(obj.start.x,obj.end.x)-thickness,min(obj.start.y,obj.end.y)-thickness)
    obj.width = abs(obj.start.x-obj.end.x)+thickness*2
    obj.height = abs(obj.start.y-obj.end.y)+thickness*2
    obj.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(obj.width),int(obj.height))
    context = cairo.Context(obj.surface)
    context.set_source_rgb(*obj.color)
    context.set_line_width(thickness)
    context.move_to(obj.start.x-obj.topleft[0],obj.height - (obj.start.y-obj.topleft[1]))
    context.line_to(obj.end.x-obj.topleft[0],obj.height - (obj.end.y-obj.topleft[1]))
    context.stroke()
    context.arc(obj.start.x-obj.topleft[0],obj.height - (obj.start.y-obj.topleft[1]),thickness/2, 0, 2.0 * math.pi)
    context.fill()
    context.arc(obj.end.x-obj.topleft[0],obj.height - (obj.end.y-obj.topleft[1]),thickness/2, 0, 2.0 * math.pi)
    context.fill()
    obj.thickness = 1
    obj.rot = 0
    obj.on_screen = True
    #screen.objects.append(obj)

@require_screen
def create_box(obj): # Must take a box object
    obj.topleft = (obj.center.x-obj.width/2,obj.center.y-obj.height/2)
    obj.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,int(obj.width+obj.thickness*2),int(obj.height+obj.thickness*2))
    context = cairo.Context(obj.surface)
    context.set_source_rgb(*obj.color)
    context.set_line_width(obj.thickness)
    context.rectangle(obj.thickness,obj.thickness,obj.width,obj.height)
    if obj.filled: context.fill_preserve()
    else: context.stroke()
    obj.on_screen = True
    #screen.objects.append(obj)

@require_screen
def create_polygon(obj): # Must take a polygon object
    obj.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(obj.width),int(obj.height))
    context = cairo.Context(obj.surface)
    context.set_source_rgb(*obj.color)
    context.set_line_width(obj.thickness)
    context.move_to(obj.points[0][0]-obj.topleft[0],obj.height - (obj.points[0][1]-obj.topleft[1]))
    i = 1
    while i < len(obj.points):
        context.line_to(obj.points[i][0]-obj.topleft[0],obj.height-(obj.points[i][1]-obj.topleft[1]))
        i+=1
    context.line_to(obj.points[0][0]-obj.topleft[0],obj.height - (obj.points[0][1]-obj.topleft[1]))
    if obj.filled: context.fill_preserve()
    else: context.stroke()
    obj.on_screen = True
    #screen.objects.append(obj)

@require_screen
def create_circle(obj): # Must take a circle objects
    obj.width = obj.radius*2+2*obj.thickness
    obj.height = obj.width
    obj.topleft = (obj.center.x-obj.width/2,obj.center.y-obj.height/2)
    obj.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,int(obj.width),int(obj.height))
    context = cairo.Context(obj.surface)
    context.set_source_rgb(*obj.color)
    context.set_line_width(obj.thickness)
    context.arc(obj.width/2,obj.height/2, obj.radius, 0, 2.0 * math.pi)
    if obj.filled: context.fill_preserve()
    else: context.stroke()
    obj.on_screen = True
    #screen.updater.add(obj)
    #screen.new_objects.put(obj)
    #screen.objects.append(obj)

@require_screen
def create_arc(obj):
    obj.width = obj.radius*2+2*obj.thickness
    obj.height = obj.width
    obj.topleft = (obj.center.x-obj.width/2,obj.center.y-obj.height/2)
    obj.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,int(obj.width),int(obj.height))
    context = cairo.Context(obj.surface)
    context.set_source_rgb(*obj.color)
    context.set_line_width(obj.thickness)
    context.arc(obj.width/2,obj.height/2, obj.radius, math.radians(obj.end_angle), math.radians(obj.start_angle))
    context.stroke()
    if obj.filled:
        angle = obj.end_angle
        context.set_line_width(3.5)
        context.move_to(obj.width/2,obj.height/2)
        while angle < obj.start_angle:
             context.line_to(obj.width/2+math.cos(math.radians(angle))*obj.radius,obj.height/2+math.sin(math.radians(angle))*obj.radius)
             angle+=4
        angle = obj.start_angle
        context.line_to(obj.width/2+math.cos(math.radians(angle))*obj.radius,obj.height/2+math.sin(math.radians(angle))*obj.radius)
        context.line_to(obj.width/2,obj.height/2)
        context.fill_preserve()
    obj.on_screen = True
    #screen.objects.append(obj)

@require_screen
def create_oval(obj): # Must take an oval object
    radius = obj.width
    obj.topleft = (obj.center.x-(2*obj.width+obj.thickness)/2,obj.center.y-(2*obj.height+obj.thickness)/2)
    obj.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,int(2*obj.width+obj.thickness),int(2*obj.height+obj.thickness))
    context = cairo.Context(obj.surface)
    scale = (1,1.0*obj.height/obj.width)
    context.set_source_rgb(*obj.color)
    context.set_line_width(obj.thickness)
    context.save()
    context.scale(scale[0],scale[1])
    context.arc((2*obj.width+obj.thickness)/(2*scale[0]), (2*obj.height+obj.thickness)/(2*scale[1]), radius, 0, 2 * math.pi)
    context.restore()
    if obj.filled: context.fill()
    else: context.stroke()
    obj.on_screen = True
    #screen.objects.append(obj)

@require_screen
def create_image(obj): # must take an image object
    obj.rot = 0
    try:
        obj.pixbuf = gtk.gdk.pixbuf_new_from_file(obj.path_name)
    except:
        raise GaspException("Image file not found")
    width = obj.pixbuf.get_width()
    height = obj.pixbuf.get_height()
    if obj.width != 0 and obj.height != 0:
        obj.scale = (float(obj.width)/width, float(obj.height)/height)
    else:
        obj.scale = (1,1)
        obj.width = width
        obj.height = height
    obj.topleft = (obj.center.x-obj.width/2,obj.center.y-obj.height/2)
    obj.on_screen = True
    #screen.objects.append(obj)

def create_text(obj):
    temp_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,1,1)
    context = cairo.Context(temp_surface)
    context.set_font_size(obj.size)
    x,y,obj.length,obj.height = context.text_extents(obj.text)[:4]
    obj.topleft = (int(obj.pos[0]),int(obj.pos[1]))
    obj.rot = 0
    obj.on_screen = True

def get_text_length(text):
    temp_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,1,1)
    context = cairo.Context(temp_surface)
    context.set_font_size(text.size)
    x,y,length,height = context.text_extents(text.text)[:4]
    return length

class Entry:
    """
    Allows the creation of text in the graphics window
    """
    def __init__(self, message, pos, color, size):
        self.message = message
        self.color = color_convert(color)
        self.size = size
        self.pos = flip_coords(pos)
        self.entry = ""
        screen.text_entry = self
        screen.action_objects.put([self,"text entry"])
        self.done = False
        while not self.done:
            if not screen.entry_done.empty():
                self.entry = screen.entry_done.get()
                self.done = True
            pass

    def draw(self, context):
        context.save()
        context.move_to(*self.pos)
        context.set_source_rgb(*self.color)
        context.set_font_size(self.size)
        context.show_text(self.message+" "+self.entry)
        context.restore()
    


"""#================================== Sound =====================================

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
    obj.sound.stop()"""


# ============================== Event Functions ==============================


@require_screen
def keys(): #returns all the keys currently being pressed
    while not screen.keys.empty():
        key = screen.keys.get()
        if key[1] == "pressed":
           screen.keys_pressed.append(key[0])
        if key[1] == "released" and key[0] in screen.keys_pressed:
           screen.keys_pressed.remove(key[0])
    return screen.keys_pressed

def mouse_pos():
    while not screen.mouse.empty():
        event = screen.mouse.get()
        if event[0] == "press":
            screen.mouse_state[event[1]]=event[2]
        if event[0] == "position":
            screen.mouse_pos = event[1]
    return screen.mouse_pos

def mouse_state():
    while not screen.mouse.empty():
        event = screen.mouse.get()
        if event[0] == "press":
            screen.mouse_state[event[1]]=event[2]
        if event[0] == "position":
            screen.mouse_pos = event[1]
    return screen.mouse_state

def get_screen_size():
    return (screen.width,screen.height)



# ============================ Exception Handling ============================

class GaspException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# =============================== BACKEND TOOLS ===============================
@require_screen
def screen_picture(file_name):
     screen.action_objects.put([file_name,"screen shot"])
    
@require_screen
def flip_coords(point):
    """
    Changes (0, 0) from topleft bottomleft.
    """
    try:
        return (point[0],screen.height-point[1])
    except: return (point.x,screen.height-point.y)


def color_convert(color):
    """
    convert the colors to the formate the cairo takes
    """
    return (color[0]/255.0,color[1]/255.0,color[2]/255.0)



@require_screen
def end():
    screen.action_objects.put([None, "end_graphics"])
    for queue in [screen.action_objects, screen.keys, screen.mouse, screen.update1, screen.update2, screen.entry_done]:
        while not queue.empty():
             queue.get()
    sys.exit()

@require_screen
def remove(obj):
    screen.objects.remove(obj)
    screen.action_objects.put([obj,"remove"])

@require_screen
def clear_screen():
    screen.action_objects.put([None,"remove_all"])


# ============================== Time ========================================
@require_screen
def update_when(event_type):

    if event_type == "key_pressed":
        screen.update_when = KEY_PRESSED
        screen.update1.put(KEY_PRESSED)
        
    elif event_type == "mouse_pressed":
        screen.update_when = MOUSE_PRESSED

    elif event_type == "next_tick":
        while time.time() < screen.last_tick+1.0/screen.frame_rate:
            pass
        screen.last_tick = time.time()

    if screen.update_when == KEY_PRESSED:
        while True:
            while not screen.update2.empty():
                screen.update_when = screen.update2.get()
            keys_p = keys()
            if len(keys_p) != 0 and screen.update_when == NOTHING:
                screen.update_when = NOTHING
                return keys_p[0]
    old_state = mouse_state()
    while screen.update_when == MOUSE_PRESSED:
        state = mouse_state()
        for key in state.get_keys():
            if state[key] != old_state[key] and state[key] == 1:
                screen.update_when = NOTHING
                    

@require_screen
def set_frame_rate(fps):
    screen.frame_rate = fps


def sleep(duration):
    time.sleep(duration)
