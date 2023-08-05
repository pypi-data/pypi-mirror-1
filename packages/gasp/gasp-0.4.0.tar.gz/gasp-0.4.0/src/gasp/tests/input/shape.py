import os
import gasp.testing
from gasp import *

wait = 0

begin_graphics()

b = Box((100,100), 200, 200, filled=True)
gasp.testing.grab_screen()
sleep(wait)

move_to(b, (200,200))
gasp.testing.grab_screen()
sleep(wait)

move_by(b, 100, 100)
gasp.testing.grab_screen()
sleep(wait)

move_by(b, -100, -100)
gasp.testing.grab_screen()
sleep(wait)

rotate_to(b, 30)
gasp.testing.grab_screen()
sleep(wait)

rotate_by(b, 70)
gasp.testing.grab_screen()
sleep(wait)

rotate_by(b, -40)
gasp.testing.grab_screen()
sleep(wait)


end_graphics()
