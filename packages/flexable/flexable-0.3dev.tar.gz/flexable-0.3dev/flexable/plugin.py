# -*- coding:utf-8 -*-
# Copyright (c) 2007, Atsushi Odagiri

# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
WSGI Template Plugin
http://docs.turbogears.org/1.0/TemplatePlugins
"""
import sys
import os
from template import Template

class FlexablePlugin (object):
    """
    Template Plugin for flexable.
    options

     - flexable.path separated by ":" or seaquence of template directory paths. default value is sys.path .
     - flexable.output_encoding output encoding. default value is 'utf-8'
     - flexable.output_format 'xhtml', 'xml' or 'html'not yet implemented.
     - flexable.suffix suffix of template filename.default value is '.html'
    """

    def __init__(self, extra_vars_func=None, options=None):
        self.extra_vars_func = extra_vars_func
        self.options = options
        paths = options.get('flexable.paths', sys.path)
        if isinstance(paths, str) or isinstance(paths, unicode):
            paths = paths.split[':']
        self.paths = paths
        self.suffix = options.get('flexable.suffix', '.html')

    def load_template(self, templatename):
        path = templatename.split('.')
        path[-1] = "%s%s" % (path[-1], self.suffix)
        path = os.path.join(*path)
        for dir in self.paths:
            fullpath = os.path.join(dir, path)
            if os.path.exists(fullpath) and os.path.isfile(fullpath):
                return Template(fullpath)
        msgprm = (path, ":".join(self.paths))
        msg = 'template "%s" is not found in paths "%s"' % msgprm
        raise Exception, msg

    def render(self, info, format="html", fragment=False, template=None):
        "Renders the template to a string using the provided info."
        if template is None:
            return str(info)
        t = self.load_template(template)
        t.merge(info)
        return str(t)

    def transform(self, info, template):
        "Render the output to Elements"
        pass
    
