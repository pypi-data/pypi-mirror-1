#!/usr/bin/env python
"""\
Browser sidebar generator for Python documentation
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

# TODO: Nicer layout for documentation
# TODO: Add complete keyboard navigation
# TODO: Don't measure for layout
# TODO: Use jQuery?

import base64
from cStringIO import StringIO
from HTMLParser import HTMLParser
import mimetypes
import optparse
from os.path import abspath, basename, dirname, join
import re
import sys
import textwrap
from urllib2 import urlopen
from urlparse import urljoin, urlsplit
from xml.sax.saxutils import escape

# Project metadata
class metadata(object):
    project         = "Sydebar"
    version         = "1.0"
    date            = "2008-06-02"
    author          = "Remy Blank"
    authorEmail     = "software@c-space.org"
    copyright       = "Copyright (C) %s %s" % (date[0:4], author)
    license         = "GPLv2"
    licenseUrl      = "http://www.gnu.org/licenses/gpl-2.0.html"
    url             = "http://c-space.org/software/%s.html" % project
    downloadBase    = "http://c-space.org/download/%s/" % project
    download        = "%s%s-%s.tar.gz" % (downloadBase, project, version)
    repository      = "http://rc.c-space.org/hg/%s" % project
    description     = "A browser sidebar generator for Python documentation"
    longDescription = """\
Sydebar is a browser sidebar generator for Python documentation pages.
It can generate Python documentation sidebars for all Python versions.
The documentation pages can be either local or on a remote web server.
"""
    keywords = ["Python sidebar", "Python", "documentation", "sidebar", "reference"]
    platforms = ["OS Independent"]
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Documentation",
    ]

__author__ = metadata.author
__version__ = metadata.version
__date__ = metadata.date

# Constants
docBaseUrl = "http://www.python.org/doc/"
docVersionsUrl = "%sversions/" % docBaseUrl

whitespace = re.compile(r"\s+")
nonNumeric = re.compile(r"([^0-9]+)")
version = re.compile(r"^/doc/([0-9]+\.[0-9]+(?:\.[0-9]+)?(?:p[0-9])?)/$")

# Add MIME type for Microsoft icons
mimetypes.add_type("image/vnd.microsoft.icon", ".ico", True)

        
def readFile(path, mode="r"):
    """Read and return the content of a local file."""
    f = open(path, mode)
    try:
        return f.read()
    finally:
        f.close()


def getUrl(url):
    """Read and return the content of an URL using an HTTP GET."""
    f = urlopen(url)
    try:
        return f.read()
    finally:
        f.close()


def makeDataUri(path):
    """Create a data: URI for the given file."""
    (mimeType, _) = mimetypes.guess_type(path, False)
    if mimeType is None:
        raise Exception("Cannot guess MIME type for '%s'" % path)
    return "data:%s;base64,%s" % (mimeType, base64.b64encode(readFile(path, "rb")))


def escapeAttr(data):
    """Escape an XML attribute value to be double-quoted."""
    return escape(data, {'"': "&quot;", "\n": "&#10;", "\r": "&#13;", "\t":"&#9;"})


def tryInt(value):
    """Return value converted to an int or value if the conversion is not possible."""
    try:
        return int(value)
    except ValueError:
        return value


def versionKey(version):
    """Return a key for numerically comparing versions."""
    return tuple(tryInt(each) for each in re.split(nonNumeric, version) if each != ".")

    
class Parser(HTMLParser):
    """HTML parser base class"""
    def __init__(self, url):
        HTMLParser.__init__(self)
        self.url = url
        self.setup()
        data = getUrl(url)
        data = data.replace(r'"\n src="../icons/', '" src="../icons/')   # Workaround for 1.5.1p1
        self.parse(data)

    def setup(self):
        pass
    
    def parse(self, data):
        self.feed(data)


class VersionParser(Parser):
    """Parser for the page listing all documentation versions"""
    def setup(self):
        self.urls = {}
        
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            href = attrs.get("href")
            if href is not None:
                match = version.match(href)
                if match:
                    self.urls[match.group(1)] = urljoin(self.url, href)
            

def getDocUrls():
    """Return a dict mapping versions to the corresponding documentation URL."""
    urls = VersionParser(docVersionsUrl).urls
    urls["2.6svn"] = "http://docs.python.org/dev/"
    urls["3.0svn"] = "http://docs.python.org/dev/3.0/"
    return urls


class Panel(object):
    """Panel generator base class"""
    def __init__(self, name):
        self.name = name
        
    def makeMenuItem(self):
        return """<li id="menu-%s" onclick="onMenuClick(this);">%s</li>""" % (
            self.name, self.getMenuItemText())
            
    def getMenuItemText(self):
        return self.name
        

class ParserPanel(Panel, Parser):
    """Panel generated from parsed content"""
    def __init__(self, url, name):
        Panel.__init__(self, name)
        Parser.__init__(self, url)


class TreePanel(ParserPanel):
    """Tree panel generator"""
    def setup(self):
        self.items = []
        self.path = []
        self.href = None
        self.data = None
        self.active = False
        self.done = False
        
    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        attrs = dict(attrs)
        if not self.active:
            if tag in ("ul", "dl"):
                self.path.append(self.items)
                self.active = True
            elif tag == "div" and attrs.get("class") == "related":
                self.__class__ = TreePanel26
        elif tag == "ul":
            self.path.append(self.path[-1][-1][2])
        elif tag == "a":
            self.href = attrs.get("href", "")
            self.data = ""
        elif tag == "tt":
            if self.data is not None:
                self.data += "<tt>"
        
    def handle_endtag(self, tag):
        if not self.active:
            return
        if tag in ("ul", "dl"):
            self.path.pop()
            if not self.path:
                self.active = False
                self.done = True
        elif tag == "a":
            if self.data:
                data = re.sub(whitespace, " ", self.data)
                self.path[-1].append((data, self.href, []))
                self.href = None
                self.data = None
        elif tag == "tt":
            if self.data is not None:
                self.data += "</tt>"
        
    def handle_data(self, data):
        if self.data is not None:
            self.data += data

    def handle_charref(self, name):
        if self.data is not None:
            self.data += "&#%s;" % name

    def handle_entityref(self, name):
        if self.data is not None:
            self.data += "&%s;" % name
        
    def writeLevel(self, out, items, indent):
        for (text, href, children) in items:
            if children:
                out.write("""%s<li>\n%s<img onclick="onFolderClick(this);" src="" alt="image-plus"/><a href="%s">%s</a>\n""" % (
                    indent, indent + " " * 4, urljoin(self.url, href), text))
                out.write("""%s<ul class="hidden">\n""" % (indent + " " * 4))
                self.writeLevel(out, children, indent + " " * 8)
                out.write("%s</ul>\n%s</li>\n" % (indent + " " * 4, indent))
            else:
                out.write("""%s<li><a href="%s">%s</a></li>\n""" % (
                    indent, urljoin(self.url, href), text))
        
    def writePanel(self, out, config):
        out.write("""\
            <div id="panel-%s" class="hidden">
                <ul class="tree">
""" % self.name)
        self.writeLevel(out, self.items, " " * 20)
        out.write("""\
                </ul>
            </div>
""")


class TreePanel26(TreePanel):
    """Tree panel generator for version >= 2.6"""
    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        attrs = dict(attrs)
        if not self.active:
            if tag == "div" and attrs["class"] == "section":
                self.active = True
                self.liCnt = 0
        elif tag == "ul":
            if self.path:
                self.path.append(self.path[-1][-1][2])
            else:
                self.path.append(self.items)
        elif tag == "a":
            self.href = attrs.get("href", "")
            self.data = ""
        elif tag == "tt":
            if self.data is not None:
                self.data += "<tt>"
        
    def handle_endtag(self, tag):
        if not self.active:
            return
        if tag  == "ul":
            self.path.pop()
        elif tag == "div":
            self.active = False
            self.done = True
        elif tag == "a" and self.path:
            data = re.sub(whitespace, " ", self.data)
            self.path[-1].append((data, self.href, []))
            self.href = None
            self.data = None
        elif tag == "tt":
            if self.data is not None:
                self.data += "</tt>"
        
    
class ModuleIndexPanel(ParserPanel):
    """Module index panel generator"""
    def setup(self):
        self.items = []
        self.href = None
        self.data = None
        self.wantExtra = False
        self.active = False
        self.done = False
        
    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        attrs = dict(attrs)
        if tag == "a":
            self.href = attrs.get("href", "")
            self.data = ""
            self.wantExtra = False
        elif tag == "em":
            if self.wantExtra:
                self.data = ""
        
    def handle_endtag(self, tag):
        if self.done:
            return
        if tag == "table":
            if self.active:
                self.active = False
                self.done = True
        elif tag == "a":
            if not self.active and self.data.startswith("__"):
                self.active = True
            if self.active:
                data = self.data.split(" ", 1)
                (name, extra) = (data[0], (len(data) > 1) and data[1].strip() or "")
                self.items.append([name, extra, self.href])
                self.href = None
                self.data = None
                self.wantExtra = not extra
        elif tag == "em":
            if self.wantExtra and self.data:
                self.items[-1][1] = self.data.strip()
                self.data = None
                self.wantExtra = False
        elif tag == "td":
            self.data = None
            self.wantExtra = False
            
        
    def handle_data(self, data):
        if self.data is not None:
            self.data += data

    def handle_charref(self, name):
        if self.data is not None:
            self.data += "&#%s;" % name

    def handle_entityref(self, name):
        if self.data is not None:
            self.data += "&%s;" % name
        
    def writeList(self, out, indent):
        for (name, extra, href) in self.items:
            out.write("""%s<li><a href="%s" onkeypress="onListKeyPress(event, this);"><tt>%s</tt>%s</a></li>\n""" % (
                indent, urljoin(self.url, href), name, extra and ("<em> %s</em>" % extra)))
            
    def writePanel(self, out, config):
        out.write("""\
            <div id="panel-%s" class="hidden">
                <form class="search-form" action="" onsubmit="return onIncrementalSubmit(this);">
                    <input value="" type="text" size="%d" class="search-field" onkeypress="onIncrementalFilter(event, this);" onchange="filterList(this);"/><input name="submit" type="image" class="clear-button" alt="image-clear"/>
                </form>
                <ul class="list">
""" % (self.name, config.fieldWidth))
        self.writeList(out, " " * 20)
        out.write("""\
                </ul>
            </div>
""")


class DocMetadata(Parser):
    """Python documentation metadata extractor"""
    version = "unknown"
    
    panels = [
        ("Tut", TreePanel, ["tutorial"]),
        ("Ref", TreePanel, ["language reference"]),
        ("Lib", TreePanel, ["library reference"]),
        ("Api", TreePanel, ["python/c api"]),
        ("Ext", TreePanel, ["extending and embedding"]),
        ("Mod", ModuleIndexPanel, ["global module index"]),
        ("Search", None, []),
    ]
    _generatedPanels = None
    _page = None
    
    def __init__(self, config):
        self.config = config
        Parser.__init__(self, config.url)
        
    def setup(self):
        self.labels = {}
        for (name, _, labels) in self.panels:
            for label in labels:
                self.labels[label] = name
        self.hrefs = {}
        self.href = None
        self.data = None
        
    def parse(self, data):
        pattern = re.compile(r"(?:Python\s+v?|Release\s+)([0-9]+(?:(?:\.|a|b|p|rc)[0-9]+)+)")
        match = pattern.search(data)
        if match:
            self.version = match.group(1)
        Parser.parse(self, data)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            self.href = attrs.get("href", None)
            self.data = ""

    def handle_endtag(self, tag):
        if tag == "a":
            if self.data is not None:
                data = re.sub(whitespace, " ", self.data).strip().lower()
                if data in self.labels:
                    self.hrefs[self.labels[data]] = self.href
                self.href = None
                self.data = None
        
    def handle_data(self, data):
        if self.data is not None:
            self.data += data

    def getPanels(self):
        if self._generatedPanels is None:
            self._generatedPanels = [panelType(urljoin(self.url, self.hrefs[name]), name) 
                for (name, panelType, _) in self.panels if name in self.hrefs]
        return self._generatedPanels
        
    def getPage(self):
        """Generate and return the documentation sidebar page."""
        if self._page is None:
            self.config.stderr.write("Generating sidebar for Python %s\n" % self.version)
            panels = self.getPanels()
            initPanel = self.config.panel
            if initPanel not in [each.name for each in panels] + ["Search"]:
                self.config.stderr.write("Warning: Default panel '%s' cannot be generated from this source.\n" % initPanel)
                self.config.stderr.write("         Using panel 'Tut' as default.\n")
                initPanel = "Tut"
        
            images = "".join("""<img id="image-%s" src="%s" alt=""/>""" % (name, makeDataUri(path)) 
                for (name, path) in self.config.images.iteritems())
            content = StringIO()
            for panel in panels:
                panel.writePanel(content, self.config)
            
            (scheme, location, path, _, _) = urlsplit(urljoin(self.config.url, "."))
            if scheme == "file":
                (scheme, location, path, _, _) = urlsplit(urljoin(docBaseUrl, self.version + "/"))
            docSearchSite = location + path
            
            template = readFile(self.config.template)
            page = template % dict(
                    author=escapeAttr(metadata.author),
                    content=content.getvalue(),
                    copyright=escapeAttr(metadata.copyright),
                    description=escapeAttr(metadata.description),
                    docSearchSite=docSearchSite,
                    docUrl=escapeAttr(self.config.url),
                    fieldWidth=self.config.fieldWidth,
                    images=images,
                    keywords=escapeAttr(", ".join(metadata.keywords)),
                    menu="".join(each.makeMenuItem() for each in panels),
                    panel=initPanel,
                    project=metadata.project,
                    fontSize=self.config.fontSize,
                    title="Python documentation",
                    version=self.version)
            if self.config.pack:
                page = re.sub(r"(?m)>\s+<", "><", page)
            self._page = page
        return self._page
    
    
class HelpFormatter(optparse.IndentedHelpFormatter):
    """Slightly customized option help formatter"""
    def format_usage(self, usage):
        return "Usage: %s\n" % usage
    
    def format_heading(self, heading):
        if heading == "options":
            heading = "Options"
        return optparse.IndentedHelpFormatter.format_heading(self, heading)
        
    def format_description(self, description):
        if not description:
            return ""
        width = self.width - self.current_indent
        indent = " " * self.current_indent
        (header, body) = description.split("\n\n", 1)
        return header + "\n\n" + "\n\n".join(textwrap.fill(each, width, initial_indent=indent, 
            subsequent_indent=indent) for each in body.split("\n\n")) + "\n"


def packageJoin(relPath):
    """Return an abolute path corresponding to a path relative to the package."""
    return abspath(join(dirname(__file__), relPath))


class Config(optparse.Values):
    """Program configuration container"""
    allVersions = False
    debug = False
    fieldWidth = 25
    images = dict(
        clear="clear.png",
        icon="python.ico",
        minus="minus.png",
        plus="plus.png",
        search="search.png")
    output = "-"
    pack = True
    panel = "Mod"
    template = "template.html"
    fontSize = 11
    url = None
    
    def __init__(self, argv, stdout, stderr, doc=False):
        optparse.Values.__init__(self)
        self.stdout = stdout
        self.stderr = stderr
        
        if not doc:
            self.template = packageJoin(self.template)
            self.images = dict((k, packageJoin(v)) for (k, v) in self.images.iteritems())
        self.url = urljoin(docBaseUrl, sys.version.split()[0] + "/")
        
        self.parser = optparse.OptionParser(
            usage="%prog [options]", prog=basename(argv[0]),
            description="%s %s   %s\n%s\n\n%s" % (metadata.project, metadata.version, metadata.description,
                metadata.copyright, metadata.longDescription),
            formatter=HelpFormatter(), add_help_option=False)
        self.parser.version = version="%prog " + metadata.version

        self.parser.add_option("", "--debug", action="store_true", dest="debug",
            help="Show a full traceback when exceptions are raised during execution.")
        self.parser.add_option("-h", "--help", action="help",
            help="Show this help message and exit.")
        self.parser.add_option("", "--version", action="version",
            help="Show the program version and exit.")

        inputOptions = optparse.OptionGroup(self.parser, "Input options")
        for name in sorted(self.images.iterkeys()):
            inputOptions.add_option("", "--image-%s" % name, action="callback", type="string", metavar="FILE", 
                callback=self.setImage, default=self.images[name],
                help="Read the '%s' image from FILE. The default is '%%default'." % name)
        inputOptions.add_option("-t", "--template", dest="template", type="string", metavar="FILE", default=self.template,
            help="Read the page template from FILE. The default is '%default'.")
        inputOptions.add_option("-u", "--url", dest="url", type="string", metavar="URL", default=self.url,
            help="Generate the sidebar for the Python documentation located at URL. The default is '%default'.")
        self.parser.add_option_group(inputOptions)
        
        outputOptions = optparse.OptionGroup(self.parser, "Output options")
        panelNames = [name for (name, _, _) in DocMetadata.panels]
        outputOptions.add_option("-a", "--all-versions", action="store_true", dest="allVersions",
            help="Generate sidebars for all documentation versions available on python.org. The output "
                "file name must contain a '%s' pattern that will be replaced by the version string.")
        outputOptions.add_option("-f", "--field-width", dest="fieldWidth", type="int", metavar="N", default=self.fieldWidth,
            help="Set the width of text fields to N characters. The default is %default.")
        outputOptions.add_option("-n", "--no-pack", action="store_false", dest="pack",
            help="Don't pack the resulting XHTML file (i.e. don't remove non-significant "
                "white space). This will output nicely indented and readable XHTML.")
        outputOptions.add_option("-o", "--output", dest="output", type="string", metavar="FILE", default=self.output,
            help="Write the output to FILE. If FILE is '-', the output is written to standard "
                "output. The default is '%default'.")
        outputOptions.add_option("-p", "--panel", dest="panel", type="choice", metavar="PANEL", 
            choices=panelNames, default=self.panel,
            help="Show PANEL when loading the sidebar. PANEL can be one of %s. The default is to "
                "show the module index if it is available, and the tutorial otherwise." % ", ".join(panelNames))
        outputOptions.add_option("-s", "--font-size", dest="fontSize", type="int", metavar="N", default=self.fontSize,
            help="Set the base font size to N pixels. The default is %default.")
        self.parser.add_option_group(outputOptions)
        
        if doc:
            self.parser.print_help(stdout)
            return
        
        (_, args) = self.parser.parse_args(args=argv[1:], values=self)
        if len(args) > 1:
            stderr.write("Invalid arguments\n")
            config.parser.print_help(stderr)
            sys.exit(2)

    def setImage(self, option, opt, value, parser):
        self.images[opt[8:]] = value
    
    def getOutput(self):
        if self.output == "-":
            return self.stdout
        return open(self.output, "w")


def makeSidebar(config):
    """Make one sidebar for the given configuration."""
    doc = DocMetadata(config)
    page = doc.getPage()
    output = config.getOutput()
    try:
        output.write(page)
    finally:
        if output is not config.stdout:
            output.close()

    
def main(argv, stdout, stderr):
    """Execute main program."""
    config = None
    try:
        config = Config(argv, stdout, stderr)
        if config.allVersions:
            outputBase = config.output
            if "%s" not in outputBase:
                config.stderr.write("Error: Generating all versions requires a '%s' pattern in the output name\n")
                return 2
            urls = getDocUrls()
            for version in sorted(urls.iterkeys(), key=versionKey):
                config.url = urls[version]
                config.output = outputBase % version
                try:
                    makeSidebar(config)
                except KeyboardInterrupt:
                    raise
                except Exception, e:
                    stderr.write("Error: %s\n" % str(e))
        else:
            makeSidebar(config)
        return 0
    except SystemExit, e:
        return e.code
    except KeyboardInterrupt:
        stderr.write("Interrupted\n")
        return 1
    except Exception, e:
        if config is None or config.debug:
            raise
        stderr.write("Error: %s\n" % str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv, sys.stdout, sys.stderr))
