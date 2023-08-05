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

from flexable import Template
from flexable.forms import getlocalname
import lxml.etree as ET

test_template='''<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body>
<form name="searchForm">
<input type="text" name="name"/>
<input type="checkbox" value="public"/>
<select name="job">
</select>
<input type="radio" name="gender"/>male
<input type="radio" name="gender"/>female
<textarea name="comment"></textarea>
<input type="password" name="pass"/>
<input type="checkbox" name="privilege"/>
</form>
</body>
</html>
'''

def test_form():
    t = Template()
    t.fromstring(test_template)
    assert len(t.forms) == 1
    f = t.forms[0]
    assert f.get("name") == "searchForm"
    assert t.forms["searchForm"] == f

def test_text():
    t = Template()
    t.fromstring(test_template)
    f = t.forms["searchForm"]
    f.values = {"name":"aodag"}
    assert f.values["name"] == "aodag"
    assert t.tree.xpath("//*[@name='name']")[0].get("value") == "aodag"

def test_select1():
    t = Template()
    t.fromstring(test_template)
    f = t.forms["searchForm"]
    f.values = {"job":("1", [("1", "programmer"),
                             ("2", "project manager")])}
    #assert f.values["job"][0] == "1"
    jobOpts = t.tree.xpath("//*[@name='job']/*[local-name()='option']")
    assert jobOpts[0].get("value") == "1"
    assert jobOpts[0].get("selected") == "selected"
    assert jobOpts[0].text == 'programmer'
    assert jobOpts[1].get("value") == "2"
    assert jobOpts[1].get("selected") is None
    assert jobOpts[1].text == 'project manager'

def test_radio1():
    t = Template()
    t.fromstring(test_template)
    f = t.forms["searchForm"]
    f.values = {"gender":("1", [("1", "male"),
                                ("2", "female")])}
    jobOpts = t.tree.xpath("//*[@name='gender']")
    assert jobOpts[0].get("value") == "1"
    assert jobOpts[1].get("value") == "2"

def test_textarea():
    t = Template()
    t.fromstring(test_template)
    f = t.forms["searchForm"]
    comment = '''This is comment for aodag.
'''
    f.values = {"comment":comment}

    e = t.tree.xpath("//*[local-name()='textarea' and @name='comment']")[0]

    assert e.text == comment

def test_password():
    t = Template()
    t.fromstring(test_template)
    f = t.forms["searchForm"]
    password = 'passwd'
    f.values = {"pass":password}

    e = t.tree.xpath("//*[local-name()='input' and @type='password' and @name='pass']")[0]
    assert e.get('value') == password

def test_checkbox1():
    t = Template()
    t.fromstring(test_template)
    f = t.forms["searchForm"]
    privilege = (True, "admin")

    f.values = {"privilege":privilege}
    e = t.tree.xpath("//*[local-name()='input' and @type='checkbox' and @name='privilege']")[0]

    assert e.get('value') == "admin"
    assert e.get('checked') == 'checked'

    privilege = (False, "admin")

    f.values = {"privilege":privilege}
    e = t.tree.xpath("//*[local-name()='input' and @type='checkbox' and @name='privilege']")[0]

    assert e.get('value') == "admin"
    assert e.get('checked') == None
    
def test_getlocalname():
    e1 = ET.fromstring("<a/>")
    assert getlocalname(e1) == 'a'

    e2 = ET.fromstring("<a xmlns='urn:aodag'/>")
    assert getlocalname(e2) == 'a'

    e3 = ET.fromstring("<x:a xmlns:x='urn:aodag'/>")
    assert getlocalname(e3) == 'a'

    
