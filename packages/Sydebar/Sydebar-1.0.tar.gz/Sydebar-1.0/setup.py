#!/usr/bin/env python
"""\
Installation script for Sydebar
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

# TODO: Substitute help text by actually running main("sydebar.py", "-h")

from cStringIO import StringIO
from distutils.command.build import build
from distutils.command.sdist import sdist
from distutils.core import Command, Distribution, setup
from distutils.errors import DistutilsFileError
from distutils.util import convert_path
import os
import re
import sys
from xml.sax.saxutils import escape


def readFile(path):
    """Read a file and return its content."""
    f = open(path)
    try:
        return f.read()
    finally:
        f.close()


def writeFile(path, content):
    """Write a file with the given content."""
    f = open(path, "w")
    try:
        f.write(content)
    finally:
        f.close()


def generateDoc(dst, context):
    """Generate doc from a template."""
    (base, ext) = os.path.splitext(dst)
    src = base + "-template" + ext
    if os.path.exists(src):
        content = readFile(convert_path(src))
        writeFile(convert_path(dst), content % context)
    elif not os.path.exists(dst):
        raise DistutilsFileError("Destination file '%s' doesn't exist, and template is not available" % dst)


class DocDistribution(Distribution):
    """Distribution including documentation generation"""
    def __init__(self, attrs=None):
        self.docs = []
        Distribution.__init__(self, attrs)


class DocSdist(sdist):
    """Documentation-building sdist"""
    def run(self):
        for (dst, context) in self.distribution.docs:
            self.execute(generateDoc, (dst, context), "generating %s" % dst)
        sdist.run(self)


class DocBuild(build):
    """Documentation-building build"""
    def run(self):
        for (dst, context) in self.distribution.docs:
            self.execute(generateDoc, (dst, context), "generating %s" % dst)
        build.run(self)

        
class Context(object):
    """Context for keyword expansion in documentation"""
    def __init__(self, object):
        self.object = object
    
    def __getattr__(self, name):
        return getattr(self.object, name)
        
    def __getitem__(self, key):
        elements = key.split("|")
        try:
            value = getattr(self, elements[0])
        except AttributeError:
            raise KeyError(key)
        for filter in elements[1:]:
            if ":" in filter:
                (begin, end) = filter.split(":", 1)
                value = value[int(begin):int(end)]
            elif filter == "join":
                value = ", ".join(value)
            elif filter == "obfuscate":
                value = "mailto:" + value
                value = "this.href=" + "+".join("'%s'" % value[i:i + 3] for i in range(0, len(value), 3))
        return escape(value, {'"': "&quot;"})


if __name__ == "__main__":
    if sys.version_info[:2] < (2, 4):
        print "Sydebar requires Python 2.4 or later"
        sys.exit(1)
    
    # Import project metadata
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "lib")))
    from Sydebar import Config, metadata

    # Get output of --help option
    out = StringIO()
    config = Config(["sydebar.py"], out, None, doc=True)
    
    # Create doc generation context
    docContext = Context(metadata)
    docContext.help = out.getvalue().rstrip("\n")
    
    # Execute commands
    setup(
        name = metadata.project,
        version = metadata.version,
        author = metadata.author,
        author_email = metadata.authorEmail,
        license = metadata.license,
        url = metadata.url,
        download_url = metadata.download,
        description = metadata.description,
        long_description = metadata.longDescription,
        keywords = metadata.keywords,
        platforms = metadata.platforms,
        classifiers = metadata.classifiers,
        
        package_dir = {"": "lib"},
        py_modules = [],
        packages = ["Sydebar"],
        package_data = {"Sydebar": ["*.png", "*.ico", "*.html"]},
        scripts = ["bin/sydebar.py"],
        docs = [("doc/Sydebar.html", docContext)],
        data_files = [
            ("share/doc/Sydebar-%s" % metadata.version,
                ["ChangeLog",
                 "COPYING",
                 "README",
                 "doc/Sydebar.html"]),
        ],
        
        distclass = DocDistribution,
        cmdclass = {"sdist": DocSdist, "build": DocBuild},
    )
    
