# Copyright 2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# BSD License derivative - see egg-info
__author__ = """Jens Klein <jens@bluedynamics.com>"""

from zope.app.publisher.fileresource import File

# those are named adapters on the request with ILocation implemented.

class CSS(File):
    """CSS objects stored in external files."""

    def __init__(self, path, name):
        super(CSS, self).__init__(path, name)
        self.content_type = 'text/css'       
        
class CSSVarDef(File):
    """CSS Variable Definitions objects stored in external files."""

    def __init__(self, path, name):
        super(CSSVarDef, self).__init__(path, name)
        self.content_type = 'text/css'