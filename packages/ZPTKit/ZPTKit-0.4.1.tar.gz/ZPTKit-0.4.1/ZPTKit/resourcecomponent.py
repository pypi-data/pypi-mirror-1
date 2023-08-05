##########################################################################
#
# Copyright (c) 2005 Imaginary Landscape LLC and Contributors.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##########################################################################
"""
This module can be used to create fall-back resources.  E.g., if you
have no Context/stylesheet.css, you may define another directory where
these resources may be found.

Typically you use this by turning ExtraPathInfo on in
Application.config, and adding a component to index.py (or Main.py)
like::

    components = SitePage.components + [
        ResourceComponent(resource_paths)]
"""

import os
import mimetypes
from Component import ServletComponent, Component

class ResourceServletComponent(ServletComponent):

    def __init__(self, resource_dirs):
        if isinstance(resource_dirs, (str, unicode)):
            resource_dirs = [resource_dirs]
        self.resource_dirs = resource_dirs

    def awakeEvent(self, trans):
        req = trans.request()
        res = trans.response()
        path = req.extraURLPath()
        if not path:
            return
        assert path.startswith('/')
        path = path.lstrip('/')
        assert not path.startswith('/')
        for dir in self.resource_dirs:
            filename = os.path.join(dir, path)
            if os.path.exists(filename):
                break
        else:
            res.setHeader('status', '404 Not Found')
            res.write('''<html><head><title>Not Found</title>
            </head><body>
            <h1>Not Found</h1>
            The resource %s was not found.
            </body></html>''' % 
                      req.environ().get('REQUEST_URI'))
            self.servlet().endResponse()
        type, encoding = mimetypes.guess_type(filename)
        res.setHeader('content-type', type)
        if encoding:
            res.setHeader('content-encoding', encoding)
        res.flush()
        f = open(filename, 'rb')
        while 1:
            t = f.read(8000)
            if not t:
                break
            res.write(t)
        f.close()
        self.servlet().endResponse()

class ResourceComponent(Component):

    _componentClass = ResourceServletComponent
    
