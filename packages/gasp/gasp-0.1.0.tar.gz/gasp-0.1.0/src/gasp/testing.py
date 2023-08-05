import os
import gasp.tests
import gasp.api

OUTPUT_DIR = os.path.join(
    os.path.dirname(gasp.tests.__file__), 'output')

TEST_CASE = None

def grab_screen():
    basename = TEST_CASE.basename
    count = TEST_CASE.counter
    filename = '%s.%i.png' %(basename, count)
    gasp.api.screen_shot(os.path.join(OUTPUT_DIR, filename))
    TEST_CASE.counter += 1