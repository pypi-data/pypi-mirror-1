# Copyright (c) 2006 John Hampton

# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do  so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__version__ = '0.1'

import os
import sys
from urllib import urlopen

import neo_cgi
# The following line is needed so that ClearSilver can be loaded when
# we are being run in multiple interpreters under mod_python
neo_cgi.update()
import neo_util

from turboclearsilver import HDFWrapper

try:
    import tidy
except ImportError:
    tidy = False

class TurboClearsilver:
    extension = "cs"

    def __init__(self, extra_vars_func=None, options=None):
        self.get_extra_vars = extra_vars_func
        self.options = options
        self.compiledTemplates = {}
        try:
            self.loadpaths = options['loadpaths']
        except (KeyError, TypeError):
            self.loadpaths = None
        try:
            self.hdfdump = options['hdfdump']
        except (KeyError, TypeError):
            self.hdfdump = False
        try:
            self.normpath = options['normpath']
        except (KeyError, TypeError):
            self.normpath = False
        print "normpath: %s" % str(self.normpath)

    def render (self, info, format="html", fragment=False, template=None):
        '''
        Renders the template to a string using the provided info.
        info: dict of variables to pass into template
        format: can only be "html" at this point
        template: path to template
        '''
        if isinstance(info, dict):
            hdf = HDFWrapper(loadpaths=self.loadpaths)
            for key, value in info.items():
                hdf[key] = value
            info = hdf.hdf
        if isinstance(template, (str, unicode)):
            if self.normpath:
                filename = template
            else:
                filename = '%s.%s' % (os.path.join(*template.split('.')),
                                      self.extension)
            import neo_cs
            cs_template = neo_cs.CS(info)
            cs_template.parseFile(filename)
        elif isinstance(template, neo_cs.CS):
            cs_template = template
        if self.hdfdump:
            return str(hdf)
        return cs_template.render()


    def load_template ( self, templatename ) :
        ''' unused but required by tg '''
        pass
    
    def transform ( self, info, template ) :
        ''' unused but required by tg '''
        pass

