import os
import gasp.testing
from gasp import *

wait = 0

begin_graphics()

b = Box((100,100), 200, 200, filled=True)
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(b)
gasp.testing.grab_screen()
sleep(wait)
b = Box((100,100), 200, 200, filled=True)
gasp.testing.grab_screen()
sleep(wait)
clear_screen()
gasp.testing.grab_screen()



end_graphics()
