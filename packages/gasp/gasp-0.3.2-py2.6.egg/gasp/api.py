#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""Publicly accessable API of GASP. 

GASP is designed to be imported with `from gasp import *`.

To use any methods in this application, you must first run `begin_graphics()`.

"""

import math
import random
import time

import backend

# diffrent update_when values
NOTHING = "Nothing"
MOUSE_PRESSED = "Mouse_Pressed"
KEY_PRESSED = "Key_Pressed"

#============================ SCREEN FUNCTIONS ==============================

class Screen:
    """
    Defines the graphics window in which objects can be created
    """
    def __init__(self, width=640, height=480,
                 title="Gasp", background=(255,255,255), back_end=None):
        global backend
        backend = back_end
        if isinstance(width,(int,float)) and width > 0:
            self.width = int(width)
        else:
            raise backend.GaspException("invalid screen width, expected int got " + str(type(width)))
        if isinstance(height,(int,float)) and height > 0:
            self.height = int(height)
        else:
            raise backend.GaspException("invalid screen height, expected int got " + str(type(height)))
        if isinstance(title,str):
            self.title = title
        else:
            raise backend.GaspException("Title must be a string")
        try:
            self.background = backend.color_convert(background)
        except:
            raise backend.GaspException("background argument is not a color")

        # backend.check_screen_atts(self)  # checks the variables
        backend.create_screen(self)



def begin_graphics(width=640, height=480, title="Gasp",
                   background=(255,255,255), back_end=backend):
    """
    Initialize a graphics window in GASP
    """
    global screen
    screen = Screen(width, height, title, background, back_end)

def end_graphics():
    """
    Close the graphics window
    """
    backend.end()

def clear_screen():
    """
    Removes all objects from the graphics window
    """
    backend.clear_screen()


def remove_from_screen(obj):
    """
    Removes a specified object from the graphics window
    """
    try:
        backend.remove(obj)
    except:
        raise backend.GaspException("This object is not on screen")
#================================ Point =====================================

class Point:
    """
    Creates a point object with an x and y attribute
    """
    def __init__(self, *args):
        if len(args) == 1:
            self.x, self.y = args[0]
        else:
            self.x, self.y = args
            
    def __str__(self):
        return "A Point instance at (%i, %i) \n" %(self.x, self.y)
    
    def distance(self, other):
        ''' The distance between two points '''
        return math.sqrt(float((other.x - self.x))**2 +
                                (float(other.y - self.y))**2) 
    

def make_it_a_point(point):
    """
    Takes something and makes it into a point if it isn't one already
    """
    if isinstance(point, Point):
        return point
    else:
        return Point(point)



class Shape:
    def __init__(self, center, filled=False, color=(0,0,0), thickness=1):
        try:
            self.center = make_it_a_point(center)
        except: raise backend.GaspException("center is not in (x,y) format")
        if isinstance(filled,bool):
            self.filled = filled
        else: raise backend.GaspException("filled argument must be a boolean")
        try:
            self.color = backend.color_convert(color)
        except: raise backend.GaspException("color argument is not a color")
        if isinstance(thickness,(int,float)):
            self.thickness = thickness
        else:
            raise backend.GaspException("thickness must be an int")
        self.rot = 0
        self.key = time.time()*random.random()

    def move_by(self,x,y):
        if self.on_screen:
            self.topleft = (self.topleft[0]+x,self.topleft[1]+y)
            self.center = Point(self.center.x+x,self.center.y+y)
        else: move_by(self,x,y)

    def move_to(self,pos):
        if self.on_screen:
            x,y = pos[0]-self.center.x,pos[1]-self.center.y
            self.topleft = (self.topleft[0]+x,self.topleft[1]+y)
            self.center = Point(self.center.x+x,self.center.y+y)
        else: move_to(self,pos)

    def draw(self,context):
        context.save()
        x,y = backend.flip_coords(self.topleft)
        context.translate(x,y-self.surface.get_height())
        if self.rot != 0:
            context.translate(self.surface.get_width()/2,self.surface.get_height()/2)
            context.rotate(self.rot)
            context.translate(-1*self.surface.get_width()/2,-1*self.surface.get_height()/2)
        context.set_source_surface(self.surface)
        context.paint()
        context.restore()

class Plot(Shape):
    """
    Allows screen objects to be placed in the graphics window
    """
    def __init__(self, pos, color=(0,0,0), size=1):
        try:
            self.center = make_it_a_point(center)
        except: raise backend.GaspException("center is not in (x,y) format")
        try:
            self.color = backend.color_convert(color)
        except: raise backend.GaspException("color argument is not a color")
        if isinstance(size,(int,float)):
            self.size = size
        else: raise backend.GaspException("size argument is not a number")
        self.key = time.time()*random.random()
        self.on_screen = False
        screen.action_objects.put([["plot",self],"new object"])
        screen.objects.append(self)


class Line(Shape):
    """
    Allows the creation of lines in the graphics window
    """
    def __init__(self, start, end, color=(0,0,0),thickness=1):
        try:
            self.start = make_it_a_point(start)
        except: raise backend.GaspException("start is not is (x,y) format")
        try:
            self.end = make_it_a_point(end)
        except: raise backend.GaspException("end is not is (x,y) format")
        self.center = make_it_a_point(((start[0]+end[0])/2,(start[1]+end[1])/2))
        try:
            self.color = backend.color_convert(color)
        except: raise backend.GaspException("color argument is not a color")
        self.thickness=thickness
        self.key = time.time()*random.random()
        self.on_screen = False
        screen.action_objects.put([["line",self],"new object"])
        screen.objects.append(self)

    def move_by(self,x,y):
        if self.on_screen:
            self.topleft = (self.topleft[0]+x,self.topleft[1]+y)
            self.center = Point(self.center.x+x,self.center.y+y)
        else: move_by(self,x,y)

    def move_to(self,pos):
        if self.on_screen:
            x,y = pos[0]-self.center.x,pos[1]-self.center.y
            self.topleft = (self.topleft[0]+x,self.topleft[1]+y)
            self.center = Point(self.center.x+x,self.center.y+y)
        else: move_to(self,pos)

    def __repr__(self):
        return "A Line instance from (%d, %d) to (%d, %d)" % \
                (self.start.x, self.start.y, self.end.x, self.end.y)

class Box(Shape):
    """
    Allows the creation of squares and rectangles in the graphics window
    """
    def __init__(self, lower_left_corner, width, height,
                 filled=False, color=(0,0,0), thickness=1):
        if isinstance(lower_left_corner,(tuple,list)) and isinstance(width,(int,float)) and isinstance(height,(int,float)):
            center = Point((int(lower_left_corner[0] + width/2.0),
                            int(lower_left_corner[1] + height/2.0)))
            self.height = height
            self.width = width
        else: raise backend.GaspException("improper arguments")
        self.on_screen = False
        Shape.__init__(self, center, filled, color, thickness)
        screen.action_objects.put([["box",self],"new object"])
        screen.objects.append(self)

    def move_to(self,pos):
        if self.on_screen:
            x,y = pos[0]-self.topleft[0],pos[1]-self.topleft[1]
            self.topleft = (self.topleft[0]+x,self.topleft[1]+y)
            self.center = Point(self.center.x+x,self.center.y+y)
        else:
            move_to(self,pos)

    def __repr__(self):
        return "Box instance at (%d, %d) with width %d and height %d" % \
               (self.center.x, self.center.y, self.width, self.height)

class Polygon(Shape):
    """
    Allows the creation of polygons in the graphics window
    """
    def __init__(self, points, filled=False, color=(0,0,0),thickness=1):
        self.thickness = thickness
        if isinstance(points,list):
            self.points = points
        else: raise backend.GaspException("points must be a list")
        x_values = []
        y_values = []    
        for point in self.points:
            if isinstance(point,tuple):
                x_values.append(point[0])
                y_values.append(point[1])
            else: raise backend.GaspException("points for be tuples")
        self.height = (max(y_values) - min(y_values))+self.thickness*2
        self.width = (max(x_values) - min(x_values))+self.thickness*2
        self.topleft = (min(x_values)-self.thickness, min(y_values)-self.thickness)
        self.center = Point(self.width/2 + min(x_values), self.height/2 +
                                                              min(y_values))
        self.on_screen = False
        Shape.__init__(self, self.center, filled, color)
        screen.action_objects.put([["polygon",self],"new object"])
        screen.objects.append(self)
            
    def __repr__(self):
        return "Polygon instance at (%i, %i)" % \
                (self.center.x , self.center.y)

class Circle(Shape):
    """
    Allows the creation of circles in the graphics window
    """
    def __init__(self, center, radius,
                 filled=False, color=(0,0,0), thickness=1):
        Shape.__init__(self, center, filled, color, thickness)
        if isinstance(radius,(int,float)):
            self.radius = radius
        else: raise backend.GaspException("radius must be a int or float")
        self.on_screen = False
        screen.action_objects.put([["circle",self],"new object"])
        screen.objects.append(self)
        #backend.create_circle(self)

    def __repr__(self):
        return "Circle instance at (%d, %d) with radius %d" % \
               (self.center.x, self.center.y, self.radius)

class Arc(Shape):
    """
    Allows the creation of arcs in the graphics window
    """
    def __init__(self, center, radius, start_angle, end_angle,
                 filled=False, color=(0,0,0), thickness=1):
        Shape.__init__(self, center, filled, color, thickness)
        if isinstance(radius,(int,float)):
            self.radius = radius
        else: raise backend.GaspException("radius must be an int or float")
        if isinstance(start_angle,(int,float)):
            self.start_angle = 360-start_angle
        else: raise backend.GaspException("start angle argument must be an int of float")
        if isinstance(end_angle,(int,float)):
            self.end_angle = 360-end_angle
        else: raise backend.GaspException("end angle argument must be an int of float")
        self.on_screen = False        
        screen.action_objects.put([["arc",self],"new object"])
        screen.objects.append(self)

    def __repr__(self):
        return "Arc instance at (%d, %d) with start angle %d and end angle %d" \
             % (self.center.x, self.center.y, self.start_angle, self.end_angle)



class Oval(Shape):
    """
    Allows the creation of circles in the graphics window
    """
    def __init__(self, center, width, height,
                 filled=False, color=(0,0,0), thickness=1):
        Shape.__init__(self, center, filled, color, thickness)
        if isinstance(width,(int,float)):
            self.width = width
        else: raise backend.GaspException("width must be an int or a float")
        if isinstance(height,(int,float)):
            self.height = height
        else: raise backend.GaspException("height must be an int or a float")
        self.on_screen = False
        screen.action_objects.put([["oval",self],"new object"])
        screen.objects.append(self)

    def __repr__(self):
        return "Oval instance at (%d, %d) with width %d and height %d" % \
               (self.center.x, self.center.y, self.width, self.height)

class Image(Shape):
    """
    Allows the placing of images in the graphics window
    """
    def __init__(self, file_path, center, width=0, height=0):
        self.path_name = file_path
        try:
            self.center = Point(backend.flip_coords(center))
        except: raise backend.GaspException("center argument is not in (x,y) format")
        if isinstance(width,(int,float)):
            self.width = width
        else: raise backend.GaspException("width must be an int or a float")
        if isinstance(height,(int,float)):
            self.height = height
        else: raise backend.GaspException("height must be an int or a float")
        self.key = time.time()*random.random()
        self.on_screen = False
        screen.action_objects.put([["image",self],"new object"])
        screen.objects.append(self)

    def draw(self,context):
        context.save()
        context.translate(*self.topleft)
        context.translate(self.width/2,self.height/2)
        context.rotate(self.rot)
        context.translate(-1*self.width/2,-1*self.height/2)
        context.save()
        context.scale(self.scale[0],self.scale[1])
        context.set_source_pixbuf(self.pixbuf,0,0)
        context.paint()
        context.restore()
        context.restore()

    def move_by(self,x,y):
        if self.on_screen:
            self.topleft = (self.topleft[0]+x,self.topleft[1]-y)
            self.center = Point(self.center.x+x,self.center.y-y)
        else:
            move_by(self,x,y)

    def move_to(self,pos):
        if self.on_screen:
            pos = backend.flip_coords(pos)
            x,y = pos[0]-self.center.x,self.center.y-pos[1]
            self.topleft = (self.topleft[0]+x,self.topleft[1]-y)
            self.center = Point(self.center.x+x,self.center.y-y)
        else:
            move_to(self,pos)

    def __repr__(self):
        return "Image instance at (%i, %i) from the file %s" % \
               (self.center.x, self.center.y, self.path_name)

 
def move_to(obj, pos):
    """
    Moves a screen object to a specified location
    """
    try:
        if isinstance(pos,tuple):
            screen.action_objects.put([obj,"move_to",pos])
        else: raise backend.GaspException("position must be a tuple")
    except:
        raise backend.GaspException("this object is not on screen")

def move_by(obj, dx, dy):
    """
    Moves a screen object by specified X and Y amounts
    """
    try:
        if isinstance(dx,(int,float)) and isinstance(dy,(int,float)):
            screen.action_objects.put([obj,"move_by",(dx,dy)])
        else: raise backend.GaspException("improper arguments, must move by int or float")
    except:
        raise backend.GaspException("this object is not on screen")

def get_text_length(text):
    if isinstance(text,Text):
        return backend.get_text_length(text)
    else:
        raise backend.GaspException("argument must be instance of Text")

def rotate_to(obj, angle):
    """
    Rotates a screen object to a specified angle
    """
    if obj in screen.objects:
        if isinstance(angle,(int,float)):
            screen.action_objects.put([obj,"rotate_to",math.radians(angle)])
        else: raise backend.GaspException("angle must fe an int or a float")
    else:
        raise backend.GaspException("this object is not on screen")

def rotate_by(obj, angle):
    """
    Rotates a screen object by a specified angle
    """
    if obj in screen.objects:
        if isinstance(angle,(int,float)):
            screen.action_objects.put([obj,"rotate_by",math.radians(angle)])
        else: raise backend.GaspException("angle must fe an int or a float")
    else:
        raise backend.GaspException("this object is not on screen")


# =============================== Text ======================================

class Text(Shape):
    """
    Allows the creation of text in the graphics window
    """
    def __init__(self, text, pos, color=(0,0,0), size=12):
        if isinstance(text, str):
            self.text = text
        else: raise backend.GaspException("Text must take a string argument")
        try:
            self.color = backend.color_convert(color)
        except: raise backend.GaspException("color argument is not a color")
        if isinstance(size, (int,float)):
            self.size = size
        else: raise backend.GaspException("size argument must be an int or float")
        try: self.pos = backend.flip_coords(pos)
        except: raise backend.GaspException("pos argument is not in the (x,y) format")
        self.key = time.time()*random.random()
        self.on_screen = False
        screen.action_objects.put([["text",self],"new object"])
        screen.objects.append(self)
        #screen.action_objects.put(obj)
        #screen.objects.append(obj)

    def draw(self, context):
        context.save()
        context.move_to(*self.pos)
        if self.rot != 0:
            context.rotate(self.rot)
        context.set_source_rgb(*self.color)
        context.set_font_size(self.size)
        context.show_text(self.text)
        context.restore()


    def move_to(self,pos):
        if self.on_screen:
            self.pos = backend.flip_coords(pos)
        else:
            move_to(self,pos)

    def move_by(self,dx,dy):
        if self.on_screen:
            self.pos = (self.pos[0]+dx,self.pos[1]-dy)
        else:
            move_by(self,dx,dy)

# ============================ Text Entry ==================================

def Text_Entry(message="Enter Text:", pos=(0,0), color=(0,0,0), size=12):
    entry = backend.Entry(message,pos,color,size)
    return entry.entry


"""# =============================== Sound =====================================

class Sound:
    ""
    Allows the creation and playback of sounds
    ""
    def __init__(self, file_path):
        self.path = file_path
        self.filename = ''.join(file_path.split('.')[:-1]).split('/')[-1]

    def play(self):
        backend.play_sound(self)

    def stop(self):
        backend.stop_sound(self)
        

def create_sound(file_path):
    ""
    Creates a sound object from a file
    ""
    return Sound(file_path)
        

def play_sound(sound):
    ""
    Starts to play a specified sound object
    ""
    sound.play()


def stop_sound(sound):
    ""
    Stops the playback of a specified sound object
    ""
    sound.stop()"""

# =========================== Event Functions ==============================

def mouse_position(): 
    """
    Returns a Point() at the mouse's current position
    """
    pos = backend.mouse_pos()
    return backend.flip_coords((int(pos[0]),int(pos[1])))


def mouse_buttons():  
    """
    Returns a dictionary of the current state of the mouse buttons
    """
    return backend.mouse_state()


def keys_pressed(): 
    """
    Returns a list of all of the keys being pressed
    """
    return backend.keys()

def key_pressed(key):
    return key in backend.keys()

def screen_size():
    return backend.get_screen_size()

# ============================= GASP TOOLS ==================================

def screen_shot(filename="screen_shot"):
    """
    Saves a screenshot to a specified file name
    """
    backend.screen_picture(filename)

def random_between(num1, num2):
    if (num1 == num2):
        return num1
    elif (num1 > num2):
        return random.randint(num2, num1)
    else:
        return random.randint(num1, num2)

read_string = raw_input


def read_number(prompt='Please enter a number: '):
    """
    Prompts the user to enter a number
    """
    while True:
        try:
            result = eval(raw_input(prompt))
            if isinstance(result, (float, int)):
                return result
            print "But that wasn't a number!"
        except:
            print "But that wasn't a number!"


def read_yesorno(prompt='Yes or no? '):
    """
    Asks the user to enter yes or no
    """
    while True:
        result = raw_input(prompt)
        result = result.lower()
        if result=='yes' or result=='y': return True
        if result=='no' or result=='n': return False
        print "Please answer yes or no."

# =============================== Time =====================================

def set_speed(speed):
    """
    Sets program frame rate in frames per second 
    """
    if isinstance(speed,(int,float)):
        backend.set_frame_rate(int(speed))
    else: raise backend.GaspException("set_speed must take an int or float")


def update_when(event_type):
    """
    Event Types include 
    'key_pressed' 
    'mouse_clicked'
    'next_tick'
    """
    if event_type == 'key_pressed' or event_type == 'mouse_clicked' or event_type == "next_tick":
        if event_type == "key_pressed":
            return backend.update_when(event_type)
        else: backend.update_when(event_type)
    else: raise backend.GaspException("update_when must take of 'key_pressed', 'mouse_clicked', or 'next_tick'")

def sleep(duration):
    """
    Sleeps for a length of time
    """
    if isinstance(duration,(int,float)):
        backend.sleep(duration)
    else: raise backend.GaspException("sleep takes either int or float")


# ============================== main =====================================

if __name__ == "__main__":
    """
    If api.py is run independently, this runs the test suite
    """
    import doctest
    doctest.testmod()
