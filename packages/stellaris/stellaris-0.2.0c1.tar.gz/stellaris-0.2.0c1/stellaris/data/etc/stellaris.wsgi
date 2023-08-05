import sys, os, atexit

os.environ['PYTHON_EGG_CACHE'] = '/var/tmp/eggs'
sys.path.append("/home/mikael/_install/lib/python2.5/site-packages/")

from stellaris.service.serve import StellarisApp

try:
    config = os.environ['STELLARIS_CONFIG']
except KeyError, e:
    sys.exit('Configuration file not defined.')
    
app = StellarisApp(config)

atexit.register(app.stop)

application = app.application

