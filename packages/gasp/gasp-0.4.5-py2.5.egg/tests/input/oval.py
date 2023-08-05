import os
import gasp.testing
from gasp import *

wait = 0

begin_graphics()

o = Oval((200, 200), 300, 200)
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(o)

o = Oval((200, 200), 200, 300, filled=True, color=(50,100,150))
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(o)

o = Oval((200, 200), 200, 200, color=(150,100,50), thickness=5)
gasp.testing.grab_screen()
sleep(wait)
remove_from_screen(o)

end_graphics()
