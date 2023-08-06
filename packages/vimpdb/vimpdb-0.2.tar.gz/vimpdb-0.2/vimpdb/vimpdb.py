# -*- coding: utf-8 -*-
#
# File: vimpdb.py
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
__revision__  = "$Revision: 66626 $"
__version__   = '$Revision: 66626 $'[11:-2]


import sys
import os
import socket
import logging
import pdb
import subprocess

_info = logging.getLogger("VIMPDB").info

def info(msg):
    print "*****", msg

VIMFILE = os.path.join(os.path.dirname(__file__), "pdb.vim")
GVIM = os.environ.get("GVIM", "/Users/seletz/bin/gvim")


class Vim(object):
    """
    Class to allow easy communication with a server-enabled
    gvim.

    >>> exe = "/Users/seletz/bin/gvim"

    Instantiate the class::

    >>> from inquant.vim import Vim
    >>> vim = Vim(exe, "PDB")

    open stuff::

    >>> vim.open("/tmp/haha")

    Send keys::

    >>> vim.send("imuha<CR>haha<ESC>")

    """
    def __init__(self, executable, servername):
        self.servername = servername
        self.filename = None
        self.VIM = executable

    def call(self, *args):
        subprocess.Popen([self.VIM,] + list(args))

    def call_pipe(self, args):
        return subprocess.Popen([self.VIM,] + list(args),
                stdout=subprocess.PIPE)

    def servers(self):
        return self.call_pipe('--serverlist')

    def is_running(self):
        return self.servername in self.servers()

    def send(self, keys):
        self.call('--remote-send', keys, '--servername', self.servername)

    def open(self, filename):
        self.call('--remote', filename, '--servername', self.servername)


class VimPdbClient(Vim):
    def _callback(self, which, args):
        info("VimPdbClient: CB %s: %s" % ( which, args))
        self.send("<C-\><C-N>:call Pdb_cb_%s(%s)<CR>" % (which, args))

    def source(self, filename):
        info("VimPdbClient: source %s" % filename )
        self.send("<C-\><C-N>:source %s<CR>" % filename)

    def init(self):
        self._callback("init", "")

    def message(self, message):
        self._callback("message", "['%s']" % message)

    def sign_set(self, id, type, filename, line):
        self._callback("sign_set", "'%s', '%s', '%s', %d" % (id, type, filename, line))

    def sign_clr(self, id, type, filename, line):
        self._callback("sign_clr", "'%s', '%s', '%s', %d" % (id, type, filename, line))

    def sign_clr_all(self):
        self._callback("sign_clr_all", "" )

    def current_line(self, filename, line):
        self._callback("current_line", "'%s', %d" % (filename, line))

class VimPdb(pdb.Pdb):
    """
    A Pdb variant which communicates with a server-enabled Vim
    """
    PORT = 6666
    BUFLEN = 512

    def __init__(self, gvim=GVIM, servername="PDB"):
        pdb.Pdb.__init__(self)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.server.bind(('', self.PORT))
        self.vim = VimPdbClient(gvim, servername)
        self.vim.source(VIMFILE)
        self.vim.init()

    def wait_for_line(self):
        (message, address) = self.server.recvfrom(self.BUFLEN)
        info("RCV: from %s: %s" % ( address, message))
        return message

    def vim_start(self):
        frame, lineno = self.stack[self.curindex]
        filename = self.canonic(frame.f_code.co_filename)

        info("VimPdb: file %s, line %d" % ( filename, lineno))
        info("VimPdb: co_filename: %s" % (frame.f_code.co_filename))

        self.vim.current_line(filename, lineno)

    def vim_update(self):
        frame, lineno = self.stack[self.curindex]
        filename = self.canonic(frame.f_code.co_filename)
        info("VimPdb: file %s, line %d" % ( filename, lineno))

        self.vim.current_line(filename, lineno)
        self.vim.message("current file: %s" % filename)

    def cmdloop(self, intro=None):
        stop = False
        self.preloop()
        self.vim_start()
        while not stop:
            self.vim_update()
            line = self.wait_for_line()
            line = self.precmd(line)
            stop = self.onecmd(line)
            stop = self.postcmd(stop,line)
        self.postloop()

    def do_toggle_breakpoint(self, arg):
        info("VimPdb: do_toggle_breakpoint: %s" % arg )
        msg = ""
        try:
            filename, line_number = arg.split()
            line_number = int(line_number)
        except:
            self.vim.error("toggle_break: invalid args: %s" % arg)
            return

        # First, prepare a list of all available breakpoints for this file.
        breakpoints = self.get_file_breaks(filename)[:] # Make a copy so we won't be affected by changes.

        if (line_number in breakpoints):
            # Unset breakpoint.
            self.clear_break(filename, line_number)
            msg="breakpoint at %s:%d CLEARED" % (filename, line_number)
        else:
            # Set the breakpoint.
            self.set_break(filename, line_number)
            msg="breakpoint at %s:%d SET" % (filename, line_number)

        # Re-Highlight the breakpoints.
        self.vim_bp_show_all(filename, *self.get_breakpoints_for_file(filename))
        self.vim.message(msg)

    #######
    # Breakpoint stuff

    def vim_bp_show(self, filename, id, type, linelist):
        for linenr in linelist:
            self.vim.sign_set(id, type, filename, linenr)

    def vim_bp_clear_all(self):
        self.vim.sign_clr_all()

    def vim_bp_show_all(self, filename, regular_breakpoints, conditional_breakpoints, temporary_breakpoints):
        """Highlights the active breakpoints in the given file."""
        self.vim_bp_clear_all()

        self.vim_bp_show( filename, 1, "breakpoint", regular_breakpoints)
        self.vim_bp_show( filename, 1, "breakpoint", conditional_breakpoints)
        self.vim_bp_show( filename, 1, "breakpoint", temporary_breakpoints)

    def get_breakpoints_for_file(self, filename):
        """Returns a tuple of (regular_breakpoints, conditional_breakpoints, temporary_breakpoints) for
        a given filename."""

        regular_breakpoints = self.get_file_breaks(filename)[:] # Make a copy so we won't be affected by changes.
        conditional_breakpoints = self.get_conditional_breakpoints(filename)
        temporary_breakpoints = self.get_temporary_breakpoints(filename)
        info("bps: %s, %s, %s" % (regular_breakpoints, conditional_breakpoints, temporary_breakpoints))

        # Remove any breakpoints which appear in the regular_breakpoints list, and are actually
        # conditional or temporary breakpoints.
        for breakpoint in regular_breakpoints:
            if ((breakpoint in conditional_breakpoints) or (breakpoint in temporary_breakpoints)):
                regular_breakpoints.remove(breakpoint)

        return (regular_breakpoints, conditional_breakpoints, temporary_breakpoints)

    def get_conditional_breakpoints(self, filename):
        """Returns a list of line numbers with conditional breakpoints for a given filename."""

        conditional_breakpoints = []

        # First, get the line numbers which have breakpoints set in them.
        file_breaks = self.get_file_breaks(filename)

        for line_number in file_breaks:
            breakpoint_instances = self.get_breaks(filename, line_number)

            for breakpoint in breakpoint_instances:
                if (breakpoint.cond):
                    # Found a conditional breakpoint - add it to the list.
                    conditional_breakpoints.append(line_number)

        return conditional_breakpoints

    def get_temporary_breakpoints(self, filename):
        """Returns a list of line numbers with temporary breakpoints for a given filename."""

        temporary_breakpoints = []

        # First, get the line numbers which have breakpoints set in them.
        file_breaks = self.get_file_breaks(filename)

        for line_number in file_breaks:
            breakpoint_instances = self.get_breaks(filename, line_number)

            for breakpoint in breakpoint_instances:
                if (breakpoint.temporary):
                    # Found a temporary breakpoint - add it to the list.
                    temporary_breakpoints.append(line_number)

        return temporary_breakpoints


# Simplified interface

def run(statement, globals=None, locals=None):
    VimPdb().run(statement, globals, locals)

def runeval(expression, globals=None, locals=None):
    return VimPdb().runeval(expression, globals, locals)

def runctx(statement, globals, locals):
    # B/W compatibility
    run(statement, globals, locals)

def runcall(*args):
    return apply(VimPdb().runcall, args)

def set_trace():
    VimPdb().set_trace()

# Post-Mortem interface

def post_mortem(t):
    p = VimPdb()
    p.reset()
    while t.tb_next is not None:
        t = t.tb_next
    p.interaction(t.tb_frame, t)

def pm():
    post_mortem(sys.last_traceback)


# vim: set ft=python ts=4 sw=4 expandtab :
