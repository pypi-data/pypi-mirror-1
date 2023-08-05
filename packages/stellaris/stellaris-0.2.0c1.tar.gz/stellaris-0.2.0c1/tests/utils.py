# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import os

from paste.fileapp import _FileIter
from threading import Thread
from stellaris.service import Serve
from tempfile import mkstemp

def file_to_str(path):
    return ''.join([l for l in open(path, 'r')])

def dump_to_file(data):
    (fd, tmp_name) = mkstemp()

    f = os.fdopen(fd, 'w+')
    f.write(data)
    
    f.close()
    
    return tmp_name

def remove_dirs(dir_path):
    """
    Recursively removes the directory and all sub-directories.
    """
    for f in os.listdir(dir_path):
        cur_path = os.path.join(dir_path, f)
        if os.path.isdir(cur_path):
            remove_dirs(cur_path)
        else:
            os.remove(cur_path)

    os.rmdir(dir_path)
    
class StellarisServerThread(Thread):
    
    def __init__(self, config):
        Thread.__init__(self)
        self.server = Serve(config)
    
    def run(self):
        self.server.start()
        
    def stop(self):
        self.server.stop()
        self.join()
