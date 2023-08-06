# -*- coding: utf-8 -*-
#
# File: .py
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

__author__    = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__  = "$Revision: 67357 $"
__version__   = '$Revision: 67357 $'[11:-2]

import sys
import os

from optparse import OptionParser

from pkg_resources import Requirement, resource_filename 

def get_datafile_path(filename):
    return resource_filename(Requirement.parse("vimpdb"), filename)


def launch_vim(*args):
    """ launch vim 

        launches gvim.  Tries to fetch the executable path from the
        environment.
    """
    import subprocess
    global options
    gvim = os.environ.get("GVIM", "gvim")

    if options.verbose:
        print "using gvim executable: %s" % gvim

    cmdline = [gvim, ]

    if args:
        cmdline.extend(args)

    if options.verbose:
        print "commandline used:", cmdline

    if options.start:
        return subprocess.call(cmdline)
    else:
        if options.verbose:
            print "NOT starting vim as requested."


class Options(object):
    def __init__(self):
        self.options = self.args = None

    def parse(self, cmdline=None):
        parser = OptionParser()
        parser.add_option("-d", "--debug", action="store_true", default=False, dest="debug", help="enable debug logging" )
        parser.add_option("-v", "--verbose", action="store_true", default=True, dest="verbose", help="verbose (log on STDERR too)." )
        parser.add_option("-q", "--quiet", action="store_false", dest="verbose", help="quiet logging -- no output on STDERR." )
        parser.add_option("-X", "--no-start", action="store_false", dest="start", default=True, help="Do NOT start vim." )
        parser.add_option("-D", "--post-mortem", action="store_true", dest="postmortem", default=False, help="launch post-mortem pdb on exceptions" )

        if cmdline:
            sys.argv[:] = cmdline
        options, args = parser.parse_args()
        self.options = options
        self.args = args

    def __getattr__(self, key):
        return getattr(self.options, key)

options = Options()

def main():
    options.parse()
    vim_script = get_datafile_path("vimpdb/pdb.vim")
    vim_rc = get_datafile_path("vimpdb/vimrc.vim")

    if options.verbose:
        print "vimpdb vim script used:", vim_script

    launch_vim("-n", "--noplugin", "--servername", "PDB", "-U", vim_rc, "-c", "source %s" % vim_script)


# vim: set ft=python ts=4 sw=4 expandtab :
