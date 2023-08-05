import os
import gasp.testing
from gasp import *

wait = 1

begin_graphics(300, 600, title="TESTING", background=(50, 100, 150))
gasp.testing.grab_screen()
sleep(wait)

end_graphics()
