# -*- coding: utf-8 -*-
#
# Copyright (c) 2007 - 2009 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
#     * Neither the name of the project nor the names of the contributors 
#       may be used to endorse or promote products derived from this 
#       software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""\
XML Utilities.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - http://www.semagia.com/
:version:      $Rev: 167 $ - $Date: 2009-06-26 14:13:53 +0200 (Fr, 26 Jun 2009) $
:license:      BSD license
"""
from xml.sax.xmlreader import InputSource

def as_inputsource(source):
    """\
    Converts a ``tm.mio.Source`` into a ``xml.sax.xmlreader.InputSource``
    """
    input_source = InputSource()
    input_source.setSystemId(source.iri)
    input_source.setByteStream(source.stream)
    input_source.setEncoding(source.encoding)
    return input_source


import sys
if sys.platform[:4] == 'java':
    # Jython's SAX implementation behaves differently from CPython. The Java
    # SAX parsers expect an empty string not ``None`` for the namespace
    # This work-around lets Jython accept "attrs.get((None, 'myattr')) instead
    # of "attrs.get(('', 'myattr'))
    from xml.sax.drivers2.drv_javasax import AttributesNSImpl #pylint: disable-msg=E0611, F0401
    class AttrsImpl(AttributesNSImpl):
        def __init__(self, attrs):
            AttributesNSImpl.__init__(self, attrs._attrs) #pylint: disable-msg=W0212
        def getValue(self, name):
            return AttributesNSImpl.getValue(self, (name[0] or '', name[1]))
    def attributes(attrs):
        """\
        Returns an AttributesNS implementation which accepts ``None`` for the
        non-existent namespace IRI, i.e. ``getValue((None, 'myattr'))``
        """
        return AttrsImpl(attrs)
else:
    def attributes(attrs):
        """\
        Returns the attributes unmodified
        """
        return attrs
del sys
