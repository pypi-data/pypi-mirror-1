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

def getlocalname(e):
    tag = e.tag
    splited = tag.split("}")
    if len(splited) == 2:
        return splited[1]
    else:
        return splited[0]

class FormCollection(object):
    def __init__(self, elements):
        self.forms = [Form(e) for e in elements]
        
    def __getitem__(self, i):
        # if None were gotten, should i raise exception?
        return self.get(i)

    def get(self, i, default=None):
        if type(i) == str:
            return self.getByName(i, default)
        else:
            if len(self.forms) > i:
                return self.forms[i]
            else:
                return default

    def getByName(self, name, default=None):
        for f in self.forms:
            if f.get("name") == name:
                return f
        return default

    def __len__(self):
        return len(self.forms)

class Form(object):
    def __init__(self, element):
        self.element = element

    def get(self, name):
        return self.element.get(name)

    def setOptions(self, selectElement, values):
        selected = values[0]
        optValues = values[1]
        prefix = selectElement.prefix
        ns = ""
        if prefix:
            ns = "{%s}" % selectElement.nsmap[prefix]
        for optvalue, optlabel in optValues:
            opt = selectElement.makeelement("%soption" %  ns)
            if optvalue == selected:
                opt.set("selected", "selected")
            opt.set("value", optvalue)
            opt.text = optlabel
            selectElement.append(opt)

    def setRadio(self, elements, values):
        checked = values[0]
        radioValues = values[1]
        if len(radioValues) != len(elements):
            raise Exception, "Sorry and radio elements are not same length."
        
        for i, v in enumerate(radioValues):
            e = elements[i]
            e.set("value", v[0])

    def _set_values(self, values):
        for k,v in values.iteritems():
            elements = self.element.xpath(".//*[@name='%s']" % k)
            etype = getlocalname(elements[0])
            if etype == 'input':
                etype = elements[0].get("type")
            
            if etype == 'radio':
                self.setRadio(elements, v)
                return

            

            for e in elements:
                if type(v) == str:
                    if etype in ('text', 'password'):
                        e.set("value", v)
                    elif etype == 'textarea':
                        e.text = v
                elif type(v) == tuple:
                    if etype == "select": 
                        self.setOptions(e, v)
                    if etype == 'checkbox':
                        if v[0]:
                            e.set("checked", 'checked')
                        else:
                            del e.attrib["checked"]

                        e.set("value", v[1])
                else:
                    raise Exception
            

    def _get_values(self):
        values = dict()
        for e in self.element.xpath(".//*[local-name()='input']"):
            values[e.get("name")] = e.get("value")
        for e in self.element.xpath(".//*[local-name()='select']"):
            opts = e.xpath(".//*[local-name() = 'option']")
            selected = e.xpath(".//*[local-name() = 'option' and @selected='selected']")
            value = None
            if len(selected) > 0:
                value = selected[0].get("value")
            optvalues = [o.get("value") for o in opts]
            values[e.get("name")] = (value, optvalues)

        return values

    values = property(_get_values, _set_values)

