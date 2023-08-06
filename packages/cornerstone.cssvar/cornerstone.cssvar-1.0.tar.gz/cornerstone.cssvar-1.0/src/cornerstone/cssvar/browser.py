# Copyright 2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD License derivative - see egg-info
__author__ = """Jens Klein <jens@bluedynamics.com>"""

import re
import logging
from zope.interface import implements
from zope.component import queryAdapter
from zope.app.publisher.browser.fileresource import FileResource
from zope.app.publisher.browser.directoryresource import DirectoryResource        
from cornerstone.cssvar.interfaces import ICSSVariables
from cornerstone.cssvar.resource import CSS
from cornerstone.cssvar.resource import CSSVarDef

logger = logging.getLogger('cornerstone.cssvar.browser')

p_vardeffile  = re.compile("vardef\(\s*?(.*)\s*?\)", flags=re.M)
p_vardefblock = re.compile("@variables\s*{(.*)}", flags=re.M+re.S)
p_vardefline  = re.compile("\s*(.*?)\s*:\s*(.*?)\s*;", flags=re.M+re.S)
p_var         = re.compile("var\(\s*?(.*?)\s*?\)")

class CSSResource(FileResource):
            
    @property
    def _variables(self):
        if hasattr(self, '_vardef'):
            return self._vardef
        match = p_vardeffile.search(self._data)
        if not match:
            raise ValueError, 'No "vardef(NAME)" declaration found in CSS file!'
        name = match.group(1)
        vardef = queryAdapter(self.request, ICSSVariables, name)
        if vardef is None:
            raise ValueError, \
                  ('vardef(%s) declaration is not registered!' % name)
        self._vardef = vardef
        return vardef
            
    def GET(self):        
        if not hasattr(self, '_data'):
            self._data = FileResource.GET(self)
        while True:
            match = p_var.search(self._data)
            if not match: 
                break
            key = match.group(1)
            self._data = "%s%s%s" % (self._data[:match.start()], 
                                     self._variables[key],
                                     self._data[match.end():]) 
        return self._data
    

class CSSResourceFactory(object):

    resourceClass = CSSResource

    def __init__(self, path, checker, name):
        self.__file = CSS(path, name)
        self.__checker = checker
        self.__name = name

    def __call__(self, request):
        resource = self.resourceClass(self.__file, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource

logger.info('Register CSSResourceFactory as factory (*.css) for use in '
            'zope.app.publisher resource-directories.')
DirectoryResource.resource_factories['.css'] = CSSResourceFactory    
    
class CSSVarDefResource(FileResource):
    
    implements(ICSSVariables)
    
    def get(self, key, default=None):
        if not hasattr(self, '_vars'):            
            self._vars = dict()
            data = self.GET()                
            for matchblock in p_vardefblock.finditer(data):
                for match in p_vardefline.finditer(matchblock.group(1)):
                    self._vars[match.group(1)] = match.group(2)
        return self._vars.get(key, default)

    def __getitem__(self, key):
        value = self.get(key)
        if value is None:
            raise AttributeError, 'CSS variable "%s" is not defined' % key
        return value
        

class CSSVarDefFactory(object):

    resourceClass = CSSVarDefResource

    def __init__(self, path, checker, name):
        self.__file = CSSVarDef(path, name)
        self.__checker = checker
        self.__name = name

    def __call__(self, request):
        resource = self.resourceClass(self.__file, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource
        