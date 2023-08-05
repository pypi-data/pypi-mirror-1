import backend
import math
import random


#============================ SCREEN FUNCTIONS ==============================

class Screen:
    def __init__(self, width=640, height=480, title="Gasp", 
                                      background=(255,255,255)):
        self.width = width
        self.height = height
        self.title = title
        self.background = background

        # backend.check_screen_atts(self)  # checks the variables
        backend.create_screen(self)

    def __str__(self):
        return 'Screen: \n width = %d \n height = %d \n title = %s \n' %(self.width, self.height, self.title)


def begin_graphics(width=640, height=480, title="Gasp",
                                          background=(255,255,255)):
    Screen(width, height, title, background)

def end_graphics():
    backend.end()

def remove_from_screen(obj):
    backend.remove(obj)

def clear_screen():
    backend.clear_screen()

def wait():
    backend.wait()


#================================ Point =====================================

class Point:
    def __init__(self, *args):
        if len(args) == 1:
            self.x, self.y = args[0]
        else:
            self.x, self.y = args
            
    def __str__(self):
        return "A Point instance at (%i, %i) \n" %(self.x, self.y)
    
    def distance(self, otherpoint):
        return math.sqrt(float((otherpoint.x - self.x))**2 + (float(otherpoint.y - self.y))**2) 
    
    def midpoint(self, otherpoint):
        return Point((self.x + otherpoint.x)/2.0, (self.y + otherpoint.y)/2.0)

    def rise(self, otherpoint):
        return otherpoint.y - self.y

    def run(self, otherpoint):
        return otherpoint.x - self.x



# =============================== Shapes ====================================
class Plot:
    def __init__(self, pos, color=(0,0,0), size=1):
        try:
            self.x
            self.y
        except:
            pos = Point(pos)
        self.pos = pos
        self.x = self.pos.x
        self.y = self.pos.y
        self.color = color
        self.size = size
        backend.plot(self)
    
    def change_att(color):
        pass


    

class Line:
    def __init__(self, start, end, color=(0,0,0)):
        self.start = Point(start)
        self.end = Point(end)
        self.x = self.start.x
        self.y = self.start.y
        self.color = color

        backend.create_line(self)

    def __repr__(self):
        return "A Line instance from (%d,%d) to (%d,%d)" %(self.x, self.y, self.end.x, self.end.y)
    
class Shape:
    def __init__(self, center, filled=False, 
                               color=(0,0,0), 
                               thickness=1):
        if isinstance(center, Point):
            self.center = center
        else:
            self.center = Point(center)

        self.filled = filled
        self.color = color
        self.thickness = thickness
        self.angle = 0

    def move_to(self, center):
        self.center = Point(center)
        backend.move_to(self, self.center)

    def move_by(self, dx=0, dy=0):
        self.center.x += dx
        self.center.y += dy
        backend.move_to(self, self.center)

    def rotate_to(self, angle):
        change = angle - self.angle
        self.angle = angle
        backend.rotate_by(self, change)

    def rotate_by(self, angle):
        self.angle += angle
        backend.rotate_by(self, angle)


class Box(Shape):
    def __init__(self, center, width, height, filled=False,
                                              color=(0,0,0),
                                              thickness=1):
        Shape.__init__(self, center, filled, color, thickness)
        self.height = height
        self.width = width
        
        backend.create_box(self)

    def __repr__(self):
        return "A Box instance at (%d,%d) with a width of %d and a height of %d" %(self.x, self.y, self.width, self.height)


class Polygon(Shape):
    def __init__(self, pos, points, filled=False,
                                    color=(0,0,0),
                                    thickness=1):
        Shape.__init__(self, pos, filled, color, thickness)
        self.points = points
        
        backend.create_polygon(self)
            
    def __repr__(self):
        return "A Polygon instance at (%i, %i) with the points:\n %t" %(self.x , self.y, self.points)
        

class Circle(Shape):
    def __init__(self, center, radius, filled=False, 
                                       color=(0,0,0), 
                                       thickness=1):
        Shape.__init__(self, center, filled, color, thickness)
        self.radius = radius
        
        backend.create_circle(self)

    def __repr__(self):
        return "A Circle instance at (%d, %d) with a radius of %d" %(self.x, self.y, self.radius)

class Arc(Shape):
    def __init__(self, center, radius, start_angle, end_angle, filled=False,
                                                               color=(0,0,0),
                                                               thickness=1):
        Shape.__init__(self, center, filled, color, thickness)
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        
        backend.create_arc(self)

    def __repr__(self):
        return "An Arc instance at (%d,%d) with start angle %d and end angle %d" %(self.center.x, self.center.y, self.start_angle, self.end_angle)


class Oval(Shape):
    def __init__(self, center, width, height, filled=False,
                                              color=(0,0,0),
                                              thickness=1):
        Shape.__init__(self, center, filled, color, thickness)
        self.width = width
        self.height = height

        backend.create_oval(self)

    def __repr__(self):
        return "An Oval instance at (%d, %d) with a width of %d and height of %d" %(self.x, self.y, self.width, self.height)
        
class Image(Shape):
    def __init__(self, file_path, center, width=None, 
                                       height=None):
        self.name = ''.join(file_path.split('.')[:-1]).split('/')[-1]
        self.path_name = file_path
        self.center = Point(center)
        self.width = width
        self.height = height
        backend.create_image(self)

    def __repr__(self):
        return "An Image instance at (%i, %i) from the file %s" %(self.x, self.y, self.path_name)

 
def move_to(obj, pos):
    obj.move_to(pos)

def move_by(obj, dx, dy):
    obj.move_by(dx, dy)

def rotate_to(obj, angle):
    obj.rotate_to(angle)

def rotate_by(obj, angle):
    obj.rotate_by(angle)


# =============================== Text ======================================

class Text:
    def __init__(self, text, pos, color=(0,0,0),
                                  size=12):
        self.text = text
        self.pos = Point(pos)
        self.color = color
        self.size = size


        backend.create_text(self)

# =============================== Sound =====================================

class Sound:
    def __init__(self, file_path):
        self.path = file_path
        self.name = ''.join(file_path.split('.')[:-1]).split('/')[-1]
        backend.create_sound(self)

    def play(self):
        backend.play_sound(self)

    def stop(self):
        backend.stop_sound(self)
        
def play_sound(sound): # Must be passed a sound object
    sound.play()

def stop_sound(sound): # Must be passed a sound object
    sound.stop()

# =========================== Event Functions ==============================

def mouse_position(): # Returns a Point() at the mouse's current position
    return Point(backend.mouse_pos())

def mouse_buttons():  # returns a dictionary of buttons current state
    return backend.mouse_pressed()

def keys_pressed(): # returns a list of all of the keys being currently pressed
    return backend.keys()

# ============================= GASP TOOLS ==================================

def screen_shot(filename):
    backend.screen_picture(filename)

random_choice = random.choice
random_between = random.randint

read_string = raw_input

def read_number(prompt='Please enter a number: '):
    while True:
        result = input(prompt)
        if type(result) in [types.FloatType, types.IntType]:
            return result
        print "But that wasn't a number!"

def read_yesorno(prompt='Yes or no? '):
    while True:
        result = raw_input(prompt)
        try: result = string.lower(string.split(result)[0])
        except: result=' '
        if result=='yes' or result=='y': return True
        if result=='no' or result=='n': return False
        print "Please answer yes or no."



if __name__ == "__main__":
    import doctest
    doctest.testmod()
