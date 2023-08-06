# -*- coding: utf-8 -*-
#
# File: oofill.parser
#
# Copyright (c) 2007 atReal
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

"""
$Id$
"""

__author__ = """Jean-Nicolas Bès <contact@atreal.net>"""
__docformat__ = 'plaintext'
__licence__ = 'GPL'


import os
from os.path import isfile, exists, dirname

import StringIO
import zipfile

from xml.sax import ContentHandler
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces

class LogWrapper:
    def __init__(self, fileobj):
        self.fileobj = fileobj
    
    def write(self, data):
        print "WROTE", repr(data)
        return self.fileobj.write(data)
    
    def seek(self, *args):
        print "SEEK", args
        return self.fileobj.seek(*args)
    
    def read(self, *args):
        print "READ", args
        return self.fileobj.read(*args)

class Finder(ContentHandler):
    def __init__(self, newContent, view):
        self.newContent = newContent
        self.view = view
        self.level=0
        self.inprotected = []
        self.replace = False
   
    def printOut(self, line):
        print "  "*(self.level+2) + line
     
    def startElement(self, name, attrs):
        if (name =="text:section"
                and attrs.get('text:protected', None)
                and attrs.get('text:name', None).startswith('replace')):
            #self.inprotected.append(self.level)
            self.replace = True
        if not (self.inprotected or self.replace):
            newTag = "<"+ name
            for key, val in attrs._attrs.items():
                newTag+= ' %s="%s"' % (key, val)
            newTag+=">"
            self.newContent.write(newTag.encode('utf-8'))
                              
        if (name =="text:section"
                and attrs.get('text:protected', None)):
            self.inprotected.append(self.level)
            sectname = attrs._attrs['text:name']
            getter = getattr(self.view, sectname, None)
            if getter is None:
                self.inprotected.pop()
            else:
                text = getter().encode('utf-8')
                #print "REPLACED BY", repr(text)
                self.newContent.write(text)
                #print "PROTECTED", bool(self.inprotected)
        self.level+=1
    
    def characters(self, data):
        if not self.inprotected:
            self.newContent.write(data.encode('utf-8'))
        
    
    def endElement(self, name):
        self.level -= 1
        if self.inprotected and self.level == self.inprotected[-1]:
            self.inprotected.pop()
            #print "PROTECTED", bool(self.inprotected)
        if not self.inprotected:
            if self.replace:
                self.replace = False
                return
            newTag = "</"+ name
            newTag+=">"
            #print "  "*self.level+newTag
            self.newContent.write(newTag.encode('utf-8'))

class OOFill:
    """
    """
    def __init__(self, odt):
        if isinstance(odt, (str, unicode)) and exists(odt):
            odtfile = file(odt,'r')
        elif isinstance(odt, (file, StringIO.StringIO)):
            odtfile = odt
        else:
            odtfile = StringIO.StringIO()
            for block in odt:
                odtfile.write(block)
        
        self.odtzip = zipfile.ZipFile(odtfile, "r")
    
    def render(self, view, outfile = None):
        if isinstance(outfile, (file, StringIO.StringIO)):
            newodtfile = outfile
        elif outfile and exists(dirname(outfile)):
            newodtfile = file(outfile, 'w+')
        else:
            newodtfile = StringIO.StringIO()
        newodtzip = zipfile.ZipFile(newodtfile, "w")
        for innerfile in self.odtzip.namelist():
            if innerfile == "content.xml":
                continue
            newodtzip.writestr(innerfile, self.odtzip.read(innerfile))
        
        content = StringIO.StringIO(self.odtzip.read("content.xml"))
        self.odtzip.close()
        
        newContent = StringIO.StringIO()
        #newContent = LogWrapper(newContent)
        newContent.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        
        parser = make_parser()
        dh = Finder(newContent, view)
        parser.setContentHandler(dh)
        parser.parse(content)
        
        newContent.seek(0)
        newodtzip.writestr("content.xml", newContent.read())
        newodtzip.close()
        newodtfile.seek(0)
        return newodtfile
    
    #def iterResult(self):
    #    for block in 



if __name__ == "__main__":
    import unittest
    TestRunner = unittest.TextTestRunner
    suite = unittest.TestSuite()
    
    if os.path.exists('tests'):
        tests = os.listdir('tests')
        tests = [n[:-3] for n in tests if n.startswith('test') and n.endswith('.py')]
    else:
        tests = ()
    
    for test in tests:
        print "testing", test
        m = __import__("tests."+test, None, None, [1])
        #print m
        if hasattr(m, 'test_suite'):
            suite.addTest(m.test_suite())
    TestRunner().run(suite)
    print "Tests done."
