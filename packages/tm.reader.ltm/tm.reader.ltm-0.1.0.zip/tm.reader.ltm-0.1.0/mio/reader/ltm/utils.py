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
This module provides utility unescape unicode characters.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - http://www.semagia.com/
:version:      $Rev: 169 $ - $Date: 2009-06-26 14:44:17 +0200 (Fr, 26 Jun 2009) $
:license:      BSD license
"""
import re
from tm.mio import MIOException as ParseError

def unescape_unicode(value):
    return u4(value)

# Stolen from rdflib..., needs further work 
quot = {'t': '\t', 'n': '\n', 'r': '\r', '\\': '\\'}
r_safe = re.compile(ur'(["\x20\x21\x23-\x5B\x5D-\x7E\u00A0-\uFFFF]+)')
r_quot = re.compile(r'\\(t|n|r|\\)')
r_uniquot = re.compile(r'\\u([0-9A-Fa-f]{4})')

def u4(s):
   """Unquote an N-Triples string.
      Derived from: http://inamidst.com/proj/rdf/ntriples.py
   """
   result = []
   while s:
      m = r_safe.match(s)
      if m:
         s = s[m.end():]
         result.append(m.group(1))
         continue

      m = r_quot.match(s)
      if m:
         s = s[2:]
         result.append(quot[m.group(1)])
         continue

      m = r_uniquot.match(s)
      if m:
         s = s[m.end():]
         u = m.group(1)
         codepoint = int(u, 16)
         if codepoint > 0x10FFFF:
            raise ParseError("Disallowed codepoint: %08X" % codepoint)
         result.append(unichr(codepoint))
      elif s.startswith('\\'):
         raise ParseError("Illegal escape at: %s..." % s[:10])
      elif (s[0] in '\n"'):
         result.append(s[0])
         s = s[1:]
      else: raise ParseError("Illegal literal character: %r in %s" % (s[0], s))
   return unicode(''.join(result))