import os
from gasp import *
import gasp.tests

begin_graphics()

a = Arc((100,100), 100, 30, 330)
screen_shot(
  os.path.join(os.path.dirname(gasp.tests.__file__), 'output', 'oval.png'))
remove_from_screen(a)

a = Arc((100,100), 100, 30, 330, filled=True, color=(50,100,150))
screen_shot(
        os.path.join(os.path.dirname(gasp.tests.__file__), 'output', 'oval2.png'))
remove_from_screen(a)

a = Arc((100,100), 100, 30, 330, color=(150,100,50), thickness=4)
screen_shot(
        os.path.join(os.path.dirname(gasp.tests.__file__), 'output', 'oval3.png'))

end_graphics()
