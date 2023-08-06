# Copyright (c) 2005 Open Source Applications Foundation.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions: 
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software. 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
from twisted.trial import unittest
import zanshin.util

class TestParseConfig(unittest.TestCase):

    def testDefaultHttpPort(self):
        parseResult = zanshin.util.parseConfigFromUrl("http://localhost/x")
        self.failUnlessEqual(
            parseResult,
            (False, "", "", "localhost", 80, "/x")
        )

    def testDefaultHttpsPort(self):
        parseResult = zanshin.util.parseConfigFromUrl("https://localhost")
        self.failUnlessEqual(
            parseResult,
            (True, "", "", "localhost", 443, "/")
        )

    def testUppercaseHttps(self):
        parseResult = zanshin.util.parseConfigFromUrl("HTtpS://localhost/x")
        self.failUnlessEqual(
            parseResult,
            (True, "", "", "localhost", 443, "/x")
        )

    def testHttpPortOverride(self):
        parseResult = zanshin.util.parseConfigFromUrl("http://www.example.com:81/")
        self.failUnlessEqual(
            parseResult,
            (False, "", "", "www.example.com", 81, "/")
        )

    def testHttpsPortOverride(self):
        parseResult = zanshin.util.parseConfigFromUrl("https://www.example.com:297/")
        self.failUnlessEqual(
            parseResult,
            (True, "", "", "www.example.com", 297, "/")
        )

    def testUsername(self):
        parseResult = zanshin.util.parseConfigFromUrl("https://yoyoma@www.example.com/")
        self.failUnlessEqual(
            parseResult,
            (True, "yoyoma", "", "www.example.com", 443, "/")
        )

    def testPassword(self):
        parseResult = zanshin.util.parseConfigFromUrl("http://yoyoma:whosemama@www.example.com/")
        self.failUnlessEqual(
            parseResult,
            (False, "yoyoma", "whosemama", "www.example.com", 80, "/")
        )
        
    def testForSlide(self):
        parseResult = zanshin.util.parseConfigFromUrl("http://root:root@localhost:8080/")
        self.failUnlessEqual(
            parseResult,
            (False, "root", "root", "localhost", 8080, "/")
        )


    def testBogusScheme(self):
        self.assertRaises(Exception, zanshin.util.parseConfigFromUrl, "httpp://www.example.com/")
        
    def testPathOnly(self):
        parseResult = zanshin.util.parseConfigFromUrl("/home/files")
        self.failUnlessEqual(
            parseResult,
            (None, '', '', '', None, '/home/files'))
        
class XmlParseTestCase(unittest.TestCase):
    def testSingleQuote(self):
        xml = "<D:prop xmlns:D='DAV:'>\n</D:prop>\n"
        prop = zanshin.util.ElementTree.XML(xml)
        
        self.failUnlessEqual(prop.text, u'\n')
        self.failUnlessEqual(prop.tag, '{DAV:}prop')

        

class DocTestCase(unittest.TestCase):
    TEST_MODULE = zanshin.util

    def _runDocTest(self):
        import doctest
        
        result = doctest.testmod(self.TEST_MODULE, optionflags=doctest.ELLIPSIS)
        
        return result


    def testDocs(self):
        from twisted.internet import threads
        return threads.deferToThread(self._runDocTest)
