import os
import gasp.testing
from gasp import *

begin_graphics()

c = Circle((100,100), 100)
gasp.testing.grab_screen()
remove_from_screen(c)

c = Circle((100,100), 100, filled=True, color=(50,100,150))
gasp.testing.grab_screen()
remove_from_screen(c)

c = Circle((100,100), 100, color=(150,100,50), thickness=5)
gasp.testing.grab_screen()
remove_from_screen(c)

end_graphics()
