import os
import gasp.testing
from gasp import *

wait = 0

begin_graphics()

t = Text("Huston, we have a problem", (100,100))
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(t)

t = Text("Huston, we have a problem", (100,100), size=40)
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(t)

t = Text("Huston, we have a problem", (100,100), color=(255,0,0), size=40)
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(t)


end_graphics()
