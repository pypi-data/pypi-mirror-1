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
#     * Neither the project name nor the names of the contributors may be 
#       used to endorse or promote products derived from this software 
#       without specific prior written permission.
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
Linear Topic Maps Notation (LTM) 1.3.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - http://www.semagia.com/
:version:      $Rev: 169 $ - $Date: 2009-06-26 14:44:17 +0200 (Fr, 26 Jun 2009) $
:license:      BSD license
"""
import re
from cStringIO import StringIO
import codecs
from urllib import urlopen
from tm.mio import MIOException
from tm.mio.deserializer import Deserializer, Context
from mio.reader.ltm.runtime import LTMContext # pylint: disable-msg=E0611
try:
    set
except NameError:
    from sets import Set as set # pylint: disable-msg=W0622

__all__ = ['create_deserializer']

def create_deserializer(**kw):
    """\
    
    """
    return LTMDeserializer(legacy=kw.get('legacy', False))

def make_lexer():
    # pylint: disable-msg=E0611, F0401
    import ply.lex as lex
    from mio.reader.ltm import lexer
    return lex.lex(module=lexer, optimize=True, lextab='mio.reader.ltm.ltm_lextab')

def make_parser():
    # pylint: disable-msg=E0611, F0401
    import ply.yacc as yacc
    from mio.reader.ltm import parser
    return yacc.yacc(debug=False, module=parser, tabmodule='mio.reader.ltm.ltm_parsetab')

_ENCODING = re.compile(r'^@"([^"]+)"').match

class LTMDeserializer(Deserializer):
    """\
    
    """
    
    version = '1.3'
    
    def __init__(self, legacy=False, context=None, included_by=None):
        """\
        
        `legacy`
            Indicates if the parser should add an item identifier and subject 
            identifier iff a topic reifies a construct. (default: ``False``)
        `context`
            The context
        `included_by`
            A set of IRIs indicating the files this LTM source was included from.
        """
        super(LTMDeserializer, self).__init__()
        self.legacy = legacy
        self._context = context or Context()
        self._included_by = included_by or set()

    def _do_parse(self, source):
        """\
        
        """
        parser = make_parser()
        parser.context = LTMContext(handler=self.handler, 
                                    iri=source.iri, 
                                    subordinate=self.subordinate, 
                                    legacy=self.legacy,
                                    included_by = self._included_by,
                                    context=self._context)
        data = source.stream
        if not data:
            try:
                data = urlopen(source.iri)
            except IOError:
                raise MIOException('Cannot read from ' + source.iri)
        parser.parse(self._reader(data, source.encoding), lexer=make_lexer())

    def _reader(self, fileobj, encoding=None):
        encoding = encoding or 'iso-8859-1'
        line = fileobj.readline()
        if line.startswith(codecs.BOM_UTF8):
            encoding = 'utf-8'
            line = line[3:] # Skip BOM
        m = _ENCODING(line)
        if m:
            encoding = m.group(1)
        return codecs.getreader(encoding)(StringIO(''.join([line, fileobj.read()]))).read()
