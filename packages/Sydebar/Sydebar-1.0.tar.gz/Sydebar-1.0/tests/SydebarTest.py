"""\
Tests for Sydebar
Copyright (C) 2008 Remy Blank
"""
# This file is part of Sydebar.
# 
# This program is free software; you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the 
# Free Software Foundation, version 2. A copy of the license is provided 
# in the file COPYING.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
# Public License for more details.

from cStringIO import StringIO
import mimetools
from urllib import urlencode
from urllib2 import Request, urlopen

from Sydebar import *
from ut.Assert import *
from ut.Util import *


def encodeMultipart(fields={}, files={}):
    """Encode a series of fields and files as multipart/form-data."""
    boundary = mimetools.choose_boundary()
    result = StringIO()
    for (name, value) in fields.iteritems():
        result.write('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (boundary, name, value))
    for (name, (fileName, contentType, content)) in files.iteritems():
        result.write('--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\n' % (boundary, name, fileName))
        result.write('Content-Type: %s\r\n\r\n%s\r\n' % (contentType, content))
    result.write("--%s--" % boundary)
    return ('multipart/form-data; boundary="%s"' % boundary, result.getvalue())
    

def postUrl(url, data, headers={}):
    """Perform an HTTP POST to an URL and return the result."""
    f = urlopen(Request(url, data, headers))
    try:
        return f.read()
    finally:
        f.close()


def validateHtml(content):
    """Validate the HTML content of an HTML file using the w3.org validator."""
    (contentType, data) = encodeMultipart({
        "charset": "(detect automatically)",
        "fbc": "1",
        "doctype": "Inline",
        "fbd": "1",
        "group": "0",
#        "ss": "1",
#        "st": "1",
#        "outline": "1",
#        "No200": "1",
#        "verbose": "1",
        "submit": "Check",
    }, {
        "uploaded_file": ("sydebar.html", "text/html", content),
    })
    result = postUrl("http://validator.w3.org/check", data, {
        "Content-Type": contentType,
        "Content-Length": str(len(data)),
    })
    return ("[Valid]" in result, result)
    

def validateCss(content):
    """Validate the CSS content of an HTML file using the w3.org validator."""
    (contentType, data) = encodeMultipart({
        "profile": "css21",
        "usermedium": "all",
        "warning": "1",
        "lang": "en",
    }, {
        "file": ("sydebar.html", "text/html", content),
    })
    result = postUrl("http://jigsaw.w3.org/css-validator/validator", data, {
        "Content-Type": contentType,
        "Content-Length": str(len(data)),
    })
    return ("NO ERRORS" in result, result)


def setUpModule():
    global urls
    urls = getDocUrls()

    
class GenerationTest(object):
    """Sidebar generation for version %(version)s"""
    version = sys.version.split()[0]
    
    def setUpClass(cls):
        cls.config = Config(["sydebar.py", "-u", urls[cls.version], "-n"], sys.stdout, sys.stderr)
        cls.doc = DocMetadata(cls.config)
        
    def testPanelCount(self):
        """Panel count (%(self.version)s)"""
        if versionKey(self.version) < (1, 5):
            assertEqual(4, len(self.doc.hrefs))
        elif versionKey(self.version) < (1, 5, 2) or versionKey(self.version) == (1, 6):
            assertEqual(5, len(self.doc.hrefs))
        else:
            assertEqual(6, len(self.doc.hrefs))
        
    def testModuleIndexPanel(self):
        """Content of module index panel"""
        for panel in self.doc.getPanels():
            if panel.name == "Mod":
                assertIn(panel.items[0][0], ("__builtin__", "__future__"))
                assertEqual("zlib", panel.items[-1][0])
        
    def testGeneration(self):
        """Generation of output page (%(self.version)s)"""
        page = self.doc.getPage()
    
    @tags("validate")
    def testHtmlValidation(self):
        """HTML validation (%(self.version)s)"""
        page = self.doc.getPage()
        (success, result) = validateHtml(page)
        if not success:
            print result
        assertTrue(success)
    
    @tags("validate")
    def testCssValidation(self):
        """CSS validation (%(self.version)s)"""
        page = self.doc.getPage()
        (success, result) = validateCss(page)
        if not success:
            print result
        assertTrue(success)
        

@tags("allVersions")
def testAllVersions():
    """Sidebar generation for all available documentation versions"""
    for vers in sorted(urls.iterkeys(), key=versionKey):
        class VersionGenerationTest(GenerationTest):
            """Sidebar generation for version %(version)s"""
            version = vers
        yield VersionGenerationTest

