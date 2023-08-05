# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import selector, signal, os, logging, sys

from threading import Thread
#from benri.wsgi import ContentTypeDispatcher

from benri.wsgiserver import CherryPyWSGIServer
from benri.log import initLogger

class InitFailure(Exception): pass

class Service(object):

    def __init__(self, config):
        # takes care of benri/server-specific initialization
        # defined in the [benri] and [server] section of the cfg-file
        
        bind = config["server"]["bind"].split(':')        
        self.bind = bind[0], int(bind[1])

        self.apps = []

        self.server = None
        
        initLogger('benri')
        self.__log = logging.getLogger('benri')

        self.secure = False
        
        try:
            sec_bind = config["server"]["secure_bind"].split(':')
            self.sec_bind = sec_bind[0], int(sec_bind[1])
            
            self.key_cert = config["server"]["ssl_key_cert_path"]
            self.ca_certs = config["server"]["ssl_cacert_path"]

            self.secure = True
        except KeyError, ke:
            self.__log.info('Could not configure the secure server. Missing %s in the [server]-section.' % (str(ke)))

        # install a signal handler for a clean shutdown when a kill is
        # received 
        signal.signal(signal.SIGTERM, self._sigterm)

    def _sigterm(self, signum, frame):
        raise SystemExit("Received signal SIGKILL")
        
    def addApp(self, app):
        self.apps.append(app)
        
    def start(self):
        dispatcher = selector.Selector()

        for app in self.apps:
            dispatcher.slurp(app.routes)

        if self.secure:
            self.https_server = CherryPyWSGIServer(self.sec_bind, dispatcher)

            self.https_server.ssl_key_cert = self.key_cert
            self.https_server.ssl_ca_certs = self.ca_certs
 
            # run the https server in a separate thread and the http server
            # in the main thread
            self.https_server_t = Thread(target=self.https_server.start)

            self.https_server_t.start()
            self.__log.info("HTTPS server started at " + self.sec_bind[0] + ':' + str(self.sec_bind[1]))
            
        self.server = CherryPyWSGIServer(self.bind, dispatcher)
        self.__log.info("HTTP server started at " + self.bind[0] + ':' + str(self.bind[1]))
         
        self.server.start()

    def stop(self):
        if self.server:
            self.__log.info('Initializing server shutdown...')
            if self.secure:
            # stop the https server and wait for its thread.
                self.https_server.stop()
                #self.https_server_t.stop()
                self.https_server_t.join()
                self.__log.info('HTTPS server shutdown server')
                
            self.server.stop()
            self.__log.info("HTTP server shutdown complete")
                    
                

