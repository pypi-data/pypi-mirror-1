#!/usr/bin/env python
 
import os
import gtk
import vte
from subprocess import Popen, PIPE
 
def BuildKernel(vte):
  vte.feed_child('cd /usr/src\n')

def write(terminal, text):
  x, y = terminal.get_cursor_position()
  terminal.feed(text + '\n', len(text) + 1)

def console():
  import gtk, vte, pango
  vte = vte.Terminal()
  vte.connect ("child-exited", gtk.main_quit)
  write(vte, '\033[1;31m Close this window after your patch is applied. Do NOT type "exit".\033[0m')
  vte.fork_command('bash')
  vte.connect ("show", BuildKernel)
  font = pango.FontDescription("monospace normal 8")
  vte.set_font(font)
  window = gtk.Window()
  window.add(vte)
  window.connect('destroy', lambda w: gtk.main_quit())
  window.show_all()
  gtk.main()
