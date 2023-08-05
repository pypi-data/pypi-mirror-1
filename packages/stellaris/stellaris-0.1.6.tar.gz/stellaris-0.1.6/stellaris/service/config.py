# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import os
from ConfigParser import SafeConfigParser

class ConfigFileMissing(Exception): pass

class Config(object):
    
    def __init__(self, configpath, workdir):
        config = SafeConfigParser()
        
        if config.read([configpath]) == []:
            raise ConfigFileMissing("Configuration file: " + configpath + " not found")

        self.data = {}
        
        for sec in config.sections():
            self.data[sec] = {}
            
            for (item,value) in config.items(sec):
                if item.endswith('_path'):
                    if value.startswith('./'):
                        value = value[2:]
                    value = os.path.join(workdir, value)
                
                self.data[sec][item] = value
        
    def __getitem__(self, key):
        return self.data[key]                        
