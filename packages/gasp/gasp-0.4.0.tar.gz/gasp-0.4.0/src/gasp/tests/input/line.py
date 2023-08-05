import os
import gasp.testing
from gasp import *

wait = 0
begin_graphics()

l = Line((0,0), (100,100))
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(l)

l = Line((0,0), (100,100), color=(0,255,0))
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(l)

l = Line((0, 100), (100, 100))
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(l)

l = Line((100, 0), (100, 100))
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(l)

l = Line((100, 0), (0, 100))
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(l)





end_graphics()
