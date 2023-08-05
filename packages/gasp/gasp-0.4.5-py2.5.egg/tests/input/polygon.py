import os
import gasp.testing
from gasp import *

wait = 0
begin_graphics()

p = Polygon([(30,30), (40, 100), (100,10)])
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(p)

p = Polygon([(30,30), (40, 100), (100,10)], filled=True, color=(50,100,150))
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(p)


end_graphics()
