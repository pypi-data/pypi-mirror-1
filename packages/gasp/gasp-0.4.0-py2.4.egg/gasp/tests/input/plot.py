import os
import gasp.testing
from gasp import *
wait = 0
begin_graphics()


p = Plot((100,100))
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(p)

p = Plot((100,100), size=10)
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(p)


p = Plot((100,100), color=(150, 100, 50))
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(p)

p = Plot((100,100), color=(50, 100, 150), size=10)
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(p)

end_graphics()
