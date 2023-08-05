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
>>> t = Template()
>>> t.fromstring("<div/>")
>>> str(t)
'<div/>'

>>> t.merge('hello')
>>> str(t)
'<div>hello</div>'

>>> t = Template()
>>> t.fromstring("<div><span class='y'/></div>")
>>> t.merge({'y':['1', '2']})
>>> str(t)
'<div><span class="y">1</span><span class="y">2</span></div>'

>>> t = Template()
>>> t.fromstring("<div><span class='y'/></div>")
>>> t.merge({'y':[({'@id':'m1'}, '1'), 
...               ({'@id':'m2'}, '2')]})
>>> str(t)
'<div><span class="y" id="m1">1</span><span class="y" id="m2">2</span></div>'

>>> t.fromstring("<div><div class='box'><span class='x'/><span class='y'/></div></div>")
>>> t.merge({'box':[{'x':'1', 'y':'2'},
...                 {'x':'3', 'y':'4'}]})
>>> str(t)
'<div><div class="box"><span class="x">1</span><span class="y">2</span></div><div class="box"><span class="x">3</span><span class="y">4</span></div></div>'

>>> t.fromstring("<div/>")
>>> t.merge(ET.Element('span'))
>>> str(t)
'<div><span/></div>'
"""
import lxml.etree as ET
from StringIO import StringIO
from forms import FormCollection

class Template(object):
    def __init__(self):
        self.tree = ET.ElementTree()
        self._forms = None

    def fromfile(self, f):
        self.tree.parse(f)

    def fromstring(self, s):
        f = StringIO(s)
        self.fromfile(f)

    def merge(self, values):
        mergeValues(self.tree.getroot(), values)

    def __str__(self):
        return ET.tostring(self.tree)

    @property
    def forms(self):
        if self._forms is None:
            formElements = self.tree.xpath(r'//*[local-name()="form"]')
            self._forms = FormCollection(formElements)
        return self._forms

def copyTree(tree):
    element = tree.makeelement(tree.tag, tree.attrib)
    element.tail = tree.tail
    element.text = tree.text
    for child in tree:
        element.append(copyTree(child))
    return element

def mergeValues(element, value):
    ltype = type(value)
    if ET.iselement(value):
        element.append(value)
    elif ltype in (str, unicode):
        element.text = value
    elif ltype == dict:
        for k,v in value.iteritems():
            if k.startswith("@"):
                element.set(k[1:], v)
            else:
                children = element.xpath(r".//*[@id='%s']" % k)
                if len(children) == 0:
                    children = element.xpath(r".//*[@class='%s']" % k)
                if len(children) > 0:
                    for child in children:
                        mergeValues(child, v)
                else:
                    raise Exception, "children nodes not found for '%s'." % k
    elif ltype == tuple:
        for v in value:
            mergeValues(element, v)
    elif ltype == list:
        parent = element.getparent()
        parent.remove(element)
        for v in value:
            e = copyTree(element)
            mergeValues(e, v)
            parent.append(e)
    else:
        raise Exception, "Sorry, applicable types are str, unicode, dict, tuple and list."

if __name__ == '__main__':
    import doctest
    doctest.testmod()
