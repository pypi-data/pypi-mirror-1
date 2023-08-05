import os
import gasp.testing
from gasp import *

wait = 0
begin_graphics()

a = Arc((100,100), 100, 30, 330)
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(a)

a = Arc((100,100), 100, 330, 360)
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(a)

a = Arc((100,100), 100, 30, 330, filled=True, color=(50,100,150))
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(a)


a = Arc((100,100), 100, 330, 360, filled=True, color=(50,100,150))
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(a)

a = Arc((100,100), 100, 30, 330, color=(150,100,50), thickness=5)
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(a)

end_graphics()
