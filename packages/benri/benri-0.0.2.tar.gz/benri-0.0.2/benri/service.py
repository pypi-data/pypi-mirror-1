# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import selector, signal, os, logging, sys

from threading import Thread
from paste.httpexceptions import HTTPExceptionHandler

#from benri.wsgi import ContentTypeDispatcher

from benri.wsgiserver import CherryPyWSGIServer
from benri.log import initLogger

class InitFailure(Exception): pass

class Application(object):
    
    def __init__(self):
        self._wsgi_app = None
        self._apps = []
        self._app = None
            
    def add(self, app):
        self._apps.append(app)
    
    def replace(self, app):
        # this is used when applying filters by replacing the current app
        self._app = app
        
    def fixate(self):
        # use fix when the middleware is composed
        # this will load all apps into the dispatcher
    
        if len(self._apps) > 0:
            dispatcher = selector.Selector()

            # add the any_noun pattern which consumes anything up to the ;
            dispatcher.parser.patterns['any_noun'] = '[^;]+'
            
            for app in self._apps:
                dispatcher.slurp(app.routes)
        
            self._app = dispatcher

    @property
    def application(self):
        return self._app
            
class Service(object):

    def __init__(self, config, server_threads=20):
        # takes care of benri/server-specific initialization
        # defined in the [benri] and [server] section of the cfg-file
        
        self.__server_threads = server_threads
        
        bind = config["server"]["bind"].split(':')        
        self.bind = bind[0], int(bind[1])

        self.server = None
        
        initLogger('benri')
        self.__log = logging.getLogger('benri')

        self.secure = False
        
        self.wsgi_app = None
        
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

    def useApplication(self, app):
        self.wsgi_app = app
        
    def _sigterm(self, signum, frame):
        raise SystemExit("Received signal SIGKILL")
                            
    def start(self):
        wsgi_app = HTTPExceptionHandler(self.wsgi_app)
        
        if self.secure:
            self.https_server = CherryPyWSGIServer(self.sec_bind, wsgi_app, numthreads=self.__server_threads)

            self.https_server.ssl_key_cert = self.key_cert
            self.https_server.ssl_ca_certs = self.ca_certs
 
            # run the https server in a separate thread and the http server
            # in the main thread
            self.https_server_t = Thread(target=self.https_server.start)

            self.https_server_t.start()
            self.__log.info("HTTPS server started at " + self.sec_bind[0] + ':' + str(self.sec_bind[1]))
            
        self.server = CherryPyWSGIServer(self.bind, wsgi_app, numthreads=self.__server_threads)
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
