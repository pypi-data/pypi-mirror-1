import os
from gasp import *
import gasp.tests

begin_graphics()

o = Oval((100,100), 100, 100)
screen_shot(
  os.path.join(os.path.dirname(gasp.tests.__file__), 'output', 'oval.png'))
remove_from_screen(o)

o = Oval((100,100), 100, 100, filled=True, color=(50,100,150), thickness=3)
screen_shot(
        os.path.join(os.path.dirname(gasp.tests.__file__), 'output', 'oval2.png'))


end_graphics()
