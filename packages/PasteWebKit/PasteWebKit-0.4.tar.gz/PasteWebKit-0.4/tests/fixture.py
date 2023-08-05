from paste.fixture import *
import os
from paste.deploy import loadapp

here = os.path.dirname(__file__)

def makeapp(config_file, name=None):
    uri = 'config:' + config_file
    app = loadapp(uri, name=name,
                  relative_to=os.path.join(here, 'sample_configs'))
    testapp = TestApp(app)
    return testapp

                      
