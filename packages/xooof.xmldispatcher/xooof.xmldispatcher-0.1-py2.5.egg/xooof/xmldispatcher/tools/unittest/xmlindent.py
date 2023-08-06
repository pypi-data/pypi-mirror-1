# -*- coding: utf-8 -*-
#-##########################################################################-#
#
# XOo°f - http://www.xooof.org
# A development and XML specification framework for documenting and
# developing the services layer of enterprise business applications.
# From the specifications, it generates WSDL, DocBook, client-side and
# server-side code for Java, C# and Python.
#
# Copyright (C) 2006 Software AG Belgium
#
# This file is part of XOo°f.
#
# XOo°f is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# XOo°f is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#-##########################################################################-#


import string,re
import xml.sax
from xml.sax.saxutils import XMLGenerator

class XMLIndentGenerator(XMLGenerator):
    """ An XMLGenerator that indents but does not support mixed content

        If mixed content is detected, RuntimeError is raised.
    """

    def __init__(self,out,encoding='iso-8859-1'):
        XMLGenerator.__init__(self,out,encoding)
        self.__out = out
        self.__inElement = 0
        self.__indent = -1
        self.__characters = []

    def _flushCharacters(self,mustBeWS):
        chars = string.join(self.__characters,"")
        if mustBeWS:
            if not re.match("\\s*$",chars):
                raise RuntimeError("non whitespace detected " \
                                   "(because of mixed content?): '%s'" % chars)
            #else: dot not print whitespace
        else:
            XMLGenerator.characters(self,chars)
        self.__characters = []

    def characters(self,characters):
        self.__characters.append(characters)

    def _start(self):
        self._flushCharacters(1)
        self.__inElement = 1
        self.__indent += 1
        self.__out.write("\n")
        self.__out.write("  "*self.__indent)

    def startElement(self,name,attrs):
        self._start()
        XMLGenerator.startElement(self,name,attrs)

    def startElementNS(self,name,qname,attrs):
        self._start()
        XMLGenerator.startElementNS(self,name,qname,attrs)

    def _end(self):
        self._flushCharacters(not self.__inElement)
        if not self.__inElement:
            self.__out.write("\n")
            self.__out.write("  "*self.__indent)
        self.__indent -= 1
        self.__inElement = 0

    def endElement(self,name):
        self._end()
        XMLGenerator.endElement(self,name)

    def endElementNS(self,name,qname):
        self._end()
        XMLGenerator.endElementNS(self,name,qname)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print >> sys.stderr, "usage: %s <in file> <out file>" % sys.argv[0]
        sys.exit(1)

    if sys.argv[1] == "-":
        inf = sys.stdin
    else:
        inf = open(sys.argv[1])

    if sys.argv[2] == "-":
        outf = sys.stdout
    else:
        outf = open(sys.argv[2],"w")

    xml.sax.parse(inf,XMLIndentGenerator(outf))
    outf.write('\n')
