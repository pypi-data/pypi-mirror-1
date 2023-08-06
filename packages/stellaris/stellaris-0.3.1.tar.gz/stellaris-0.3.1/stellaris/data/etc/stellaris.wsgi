import sys, os, atexit

os.environ['PYTHON_EGG_CACHE'] = '/var/tmp/eggs'

from stellaris.service.serve import StellarisApp
from stellaris.env import Environment

def test_write(path):
    f = file(path, "w")
    f.write("hello world!\n")
    f.close()
    os.remove(path)

# use the environment in which the wsgi script is located
env_path = os.path.dirname(os.path.dirname(str(__file__)))

if not os.path.exists(env_path):
    sys.exit('Environment path not found: %s' % env_path)

#print >> sys.stderr, "Environment path: ", env_path, " ", os.geteuid(), " ", os.getuid(), " ", os.getlogin()

try:        
    test_write(os.path.join(env_path, "logs/test_rights.txt"))
    test_write(os.path.join(env_path, "db/test_rights.txt"))
    test_write(os.path.join(env_path, "data/test_rights.txt"))
except IOError, e:
    sys.exit('Cannot write to the environment path %s\nMake sure that the user running mod_wsgi has write access to the stellaris environment.\n' % env_path) 

env = Environment(env_path)

app = StellarisApp(env)

atexit.register(app.stop)

application = app.application
