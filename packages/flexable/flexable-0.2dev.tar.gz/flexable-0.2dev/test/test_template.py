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

def test_simple():
    for args in  (('<div/>',
                   'hello',
                  '<div>hello</div>'),
                  ('<div><div id="x"/></div>',
                   dict(x="hello"),
                   '<div><div id="x">hello</div></div>'),
                  ('<div/>',
                   {"@id":'x'},
                   '<div id="x"/>'),
                  ('<div/>',
                   ({"@id":'x'}, "hello"),
                   '<div id="x">hello</div>'),
                  ('<div><div class="message"/></div>',
                   {"message":["1", "2", "3"]},
                  '<div><div class="message">1</div>'
                  '<div class="message">2</div>'
                  '<div class="message">3</div></div>'),
                  ('<div><div class="message"/></div>',
                   {"message":[({"@id":"message1"}, "1"), 
                               "2", 
                               "3"]},
                  '<div><div class="message" id="message1">1</div>'
                  '<div class="message">2</div>'
                  '<div class="message">3</div></div>'),
                  ('<div><div class="message">'
                   '<span class="x1"/>'
                   '<span class="x2"/></div></div>',
                   {"message":[{"x1":"1", "x2":"4"},
                               {"x1":"2", "x2":"5"},
                               {"x1":"3", "x2":"6"}]},
                   '<div>'
                   '<div class="message"><span class="x1">1</span><span class="x2">4</span></div>'
                   '<div class="message"><span class="x1">2</span><span class="x2">5</span></div>'
                   '<div class="message"><span class="x1">3</span><span class="x2">6</span></div>'
                   '</div>')
                  ):
        yield merge, args[0], args[1], args[2]

def merge(data, values, result):
    t = Template()
    t.fromstring(data)
    t.merge(values)
    assert str(t) == result
