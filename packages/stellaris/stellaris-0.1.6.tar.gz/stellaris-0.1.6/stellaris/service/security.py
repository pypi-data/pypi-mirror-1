# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import time, urllib2, base64, stellaris, os
from threading import Thread

log = stellaris._logger

class NoValidAuthorizationTypes(Exception): pass

class SecurityService(object):
    """A security service maintains a list of authorized users.
    """
    def __init__(self, config, interval=3600.0):
        """Initializes a SecurityService.
        
        @param config a ConfigParser object of the config-file.
        @param interval indicates how often the authorization data is updated.
        """

        self.auths = []
                
        try:
            path = config["security"]["gridmap_file_path"]
            if os.path.exists(path):
                self.auths.append(AuthorizeGridMapFile(path))
        except:
            pass
        
        try:
            path = config["security"]["auth_file_path"]
            if os.path.exists(path):
                self.auths.append(AuthorizeFlatFile(path))
        except Exception, e:
            pass

        try:
            service = config["security"]["vomrs"]
            user = config["security"]["vomrs_user"]
            password = config["security"]["vomrs_password"]
            self.auths.append(AuthorizeVOMRS(service, user, password))
        except:
            pass

        if len(self.auths) == 0:
            raise NoValidAuthorizationTypes('Configuration does not contain any valid authorization sources')
   
        self.interval = interval
        self.__running = False
        self.t = Thread(target=self._update)
        self.t.setDaemon(True)

    def _update(self):
        while self.__running:
            for a in self.auths:
                a.update()
            time.sleep(self.interval)

    def stop(self):
        self.__running = False

    def start(self):
        self.__running = True
        self.t.start()
                                
    def isAuthorized(self, dn):
        """Checks if a given user is authorized.
           
        @param dn string with X.509 subject DN
        """
        if len([True for auth in self.auths if auth.isAuthorized(dn)]) > 0:
            return True
        
        return False

class Authorize(object):
    def __init__(self, validusers=[]):
        # list of X.509 DN subject strings representing users
        self.validusers = set(validusers)

    def isAuthorized(self, dn):
        """Checks if a given user is authorized to access the service
           
        @param dn string with X.509 subject DN
        """
        for user in self.validusers:
            if dn.startswith(user):
                return True

        return False

    def replace(self, users):
        """Replace the current list of valid users
        
        @param users list of X.509 DN strings representing valid users
        """
        self.validusers = set(users)

    def merge(self, users):
        self.validusers = self.validusers.union(users)
                
# str.startsWith()

class AuthorizeVOMRS(Authorize):

    def __init__(self, service, user=None, password=None):
        self.service = service
        self.authstr = None

        if user != None and password != None and user != '' and password != '':
            self.authstr = base64.encodestring('%s:%s' % (user, password))[:-1]

        # checks when the last update occurred
        self.ts = 0.0
        
        # how often the service should be asked for a new list of users
        Authorize.__init__(self)

    def _fetch(self):
        req = urllib2.Request(self.service)
        authheader =  "Basic %s" % self.authstr
        req.add_header("Authorization", authheader)
        
        try:
            users = urllib2.urlopen(req)
            self.parse(users)
            self.ts = time.time()
        except IOError, e:
            log.debug("Failed to fetch user list from VOMRS service %s: %s", self.service, str(e))
        except:
            raise

    def parse(self, users):
        self.merge([(user.strip()).strip('"') for user in users])

    def update(self):
        self._fetch()
                
class AuthorizeFlatFile(Authorize):
    """Handles files with one X.509 DN/row.
    
    Format: <DN>\n
            A line starting with a #-character is ignored.
    """
    def __init__(self, path):
        self.path = path
        Authorize.__init__(self)

    def parse(self, path):
        f = file(path, "r")
        
        self.merge([user.strip() for user in f])
        f.close()
    
    def update(self):
        self.parse(self.path)
        
#        [self.parse(p) for p in self.paths]
            
class AuthorizeGridMapFile(Authorize):
    """Handles globus gridmap-files.
    
    Format: "<DN>"\t<Local user>\n
            A line starting with a #-character is ignored.
    """
    def __init__(self, path):
        self.path = path
        Authorize.__init__(self)
                
    def parse(self, path):
        f = file(path, "r")
        
        self.merge([(user.split('\t')[0]).strip('"') for user in f])
        f.close()

    def update(self):
        self.parse(self.path)
        
#        [self.parse(p) for p in self.paths]
        
