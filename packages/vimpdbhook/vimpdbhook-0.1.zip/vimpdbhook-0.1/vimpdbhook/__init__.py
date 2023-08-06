import os
from os.path import exists
from os import system

import appscript


def activate_terminal():
    terminal_program = os.environ.get("VIMPDBHOOK_TERMINAL_APP", "iTerm")
    appscript.app(terminal_program).activate()

VIM_KEYS = "%(lineno)dgg<ESC><ESC>:setlocal cursorline<CR>zz"

def vim(self):
    vimpdb_program = os.environ.get("VIMPDBHOOK_MVIM_SCRIPT", "vimpdb")
    frame, lineno = self.stack[self.curindex]
    filename = self.canonic(frame.f_code.co_filename)
    if exists(filename):
        system('%(vimpdb_program)s --remote-silent %(filename)s' % locals())
        keys = VIM_KEYS % locals()
        system('%s --remote-send "%s"' % (vimpdb_program, keys))

def preloop(self):
    vim(self)
    activate_terminal()

def precmd(self, line):
    vim(self)
    activate_terminal()
    return line


