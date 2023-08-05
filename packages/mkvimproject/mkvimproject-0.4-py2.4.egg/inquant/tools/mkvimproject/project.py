# -*- coding: utf-8 -*-
#
# File: project.py
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
__revision__ = "$Revision: 2382 $"

import sys
import os
from mkvimproject import run
from mkvimproject import FILTERS

def create_project_file( filename, options ):
    pattern = FILTERS["none"]
    if options.filter:
        pattern = options.filter
    if options.filterset in FILTERS.keys():
        pattern = FILTERS[options.filterset]
    run( ".", file( filename, "w" ), pattern )

def launch_vim( projectfile ):
    import subprocess
    return subprocess.call( [ 'gvim', '-c', 'Project %s' % projectfile ] )


def main():
    import optparse
    parser = optparse.OptionParser()
    parser.add_option( "-U", "--update", action="store_true", dest="update", default=False, help="Update projectfile." )
    parser.add_option( "-X", "--nolaunch", action="store_false", dest="launch", default=True, help="Do noit launch vim. Use with -U." )
    parser.add_option( "-f", "--filter", dest="filter", action="append", help="The extensions to allow." )
    parser.add_option( "-s", "--filterset", dest="filterset", action="store", help="The filterset to use: one of %s" % ( ",".join(FILTERS.keys() ) ) )

    (options, args) = parser.parse_args()

    if len(args):
        os.chdir( args[0] )

    projectfile = "%s.vpj" % os.path.basename( os.getcwd() )

    if not os.path.exists( projectfile ) or options.update:
        create_project_file( projectfile, options )
        print "Projectfile %s created." % projectfile

    if options.launch:
        launch_vim( projectfile )

if __name__ == "__main__":
    main()

# vim: set ft=python ts=4 sw=4 expandtab :
