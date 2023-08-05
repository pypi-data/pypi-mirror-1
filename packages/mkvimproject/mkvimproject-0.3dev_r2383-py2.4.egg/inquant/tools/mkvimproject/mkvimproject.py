# -*- coding: utf-8 -*-
#
# File: mkvimproject.py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__ = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__ = "$Revision: 2084 $"

import sys
import os
import logging

LOGGER="autotest.seleniumrcevent"
def info(msg):
    logging.getLogger(LOGGER).info(msg)

def debug(msg):
    logging.getLogger(LOGGER).debug(msg)

def error(msg):
    logging.getLogger(LOGGER).error(msg)

FILTERS= {
    "python":   ".diff .patch .py .txt",
    "plone":    ".diff .patch .py .pt .txt .zcml .xml .cpt .cpy .vpy .metadata .dtml",
    "c":        ".diff .patch .c .cpp .h .m .dbg .mk .in",
    "objc":     ".diff .patch .c .cpp .h .m .dbg .mk .in .nib .applescript .plist .strings",
    "none":     "",
}

class DirEntry(object):
    def __init__(self, dir, pattern=[] ):
        self.dir = dir
        self.pattern = filter( len, pattern )
        self.children = []
        self.files = []

    def indent(self, level):
        return " " * level

    def addChild( self, child ):
        self.children.append( child )

    def addFile( self, fn ):
        if not len(self.pattern): # no pattern means "*"
            self.files.append( fn )
        else:
            _, ext = os.path.splitext( fn )
            if not len(ext) or ext in self.pattern:
                self.files.append( fn )

    def getFilter(self):
        if len( self.pattern ):
            return " ".join( [ "*%s" % f for f in self.pattern ] )
        else:
            return "*"

    def scan( self, path ):
        root, dirs, files = os.walk( path ).next()
        for fn in files:
            self.addFile( fn )

        for dir in dirs:
            if dir.startswith("."):
                continue
            entry = DirEntry( dir, self.pattern )
            entry.scan( os.path.join( root, dir ) )
            self.addChild( entry )
            

    def write( self, f, level ):
        if level == 0:
            root = os.path.abspath( self.dir )
            name = os.path.basename( root ).replace(" ", "_" )
        else:
            root = name = self.dir
            name.replace( " ", "_" )

        print >>f, "%s%s=\"%s\" CD=. filter=\"%s\" {" % (
                self.indent(level),
                name, root,
                self.getFilter(), )

        for child in self.children:
            child.write( f, level+1 )

        for fn in self.files:
            print >>f, "%s%s" % ( self.indent(level + 1), fn )


        print >>f, "%s}" % ( self.indent(level) )

def run( dir, outfile, pattern ):
    root = DirEntry( dir, pattern=pattern.split(" ") )
    root.scan( dir )
    root.write( outfile, 0 )

def main():
    import optparse
    parser = optparse.OptionParser()
    parser.add_option( "-d", "--dir", dest="dir", default=".", help="the directory to scan" )
    parser.add_option( "-o", "--out", dest="out", help="The output file" )
    parser.add_option( "-f", "--filter", dest="filter", action="append", help="The extensions to allow." )
    parser.add_option( "-s", "--filterset", dest="filterset", action="store", help="The filterset to use: one of %s" % ( ",".join(FILTERS.keys() ) ) )

    (options, args) = parser.parse_args()
    outfile = sys.stdout
    if options.out:
        if not options.out.endswith(".vpj"):
            options.out = "%s.vpj" % options.out
        outfile = file( options.out, "w" )

    pattern = FILTERS["plone"]
    if options.filter:
        pattern = options.filter

    if options.filterset in FILTERS.keys():
        pattern = FILTERS[options.filterset]

    run( options.dir, outfile, pattern )

if __name__ == "__main__":
    main()

# vim: set ft=python ts=4 sw=4 expandtab :
