# Copyright 2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD License derivative - see egg-info
__author__ = """Jens Klein <jens@bluedynamics.com>"""

import logging
import Acquisition
from ZPublisher.HTTPRequest import HTTPRequest
from cornerstone.cssvar import browser  
logger = logging.getLogger('cornerstone.cssvar.five')

class FiveCSSResource(Acquisition.Explicit, browser.CSSResource): 

    def browserDefault(self, request):
        '''See interface IBrowserPublisher'''
        self.action = getattr(self, request['REQUEST_METHOD']) 
        return self, ()
    
    def __call__(self, *args):
        if hasattr(self, 'action'):
            return self.action()
        return self.GET()
        

class FiveCSSVarDefResource(Acquisition.Implicit, browser.CSSVarDefResource): 

    def browserDefault(self, request):
        '''See interface IBrowserPublisher'''
        self.action = getattr(self, request['REQUEST_METHOD']) 
        return getattr(self, request['REQUEST_METHOD']), ()

    def __call__(self, *args):
        if hasattr(self, 'action'):
            return self.action()
        return self.GET()

logger.info('Bind new method HTTPRequest.getHeader to HTTPRequest.get_header')
HTTPRequest.getHeader = HTTPRequest.get_header
    
logger.info('Enable publishing using bridged resourceClass')
browser.CSSResourceFactory.resourceClass = FiveCSSResource
browser.CSSVarDefFactory.resourceClass = FiveCSSVarDefResource
