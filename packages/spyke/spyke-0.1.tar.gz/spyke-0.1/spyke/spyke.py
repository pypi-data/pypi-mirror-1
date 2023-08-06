#!/usr/bin/env python
copying = """
    Copyright (C) 2007-2009  David Laban <alsuren@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License (in the "COPYING" file) for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>."""

import gobject
import dbus
import dbus.mainloop.glib


from connection import ExistingConnection, SpykeConnection
import connection
from helper_functions import *


def quit():
    global connections
    print 'quitting'
    for connection in connections:
        try:
            connection.Disconnect()
        except NotImplementedError:
            print 'NotImplementedError'
    do_later(mainloop.quit)

connections=[] 
def newconnection(*args, **kwargs):
    connections.append(ExistingConnection(*args, **kwargs))

def main():
    global mainloop
    mainloop=gobject.MainLoop(is_running=True)
    dmainloop=dbus.mainloop.glib.DBusGMainLoop()
    dbus.set_default_main_loop(dmainloop)
    #mainloop=dbus.mainloop.glib.DBusGMainLoop()
    gobject.threads_init()
    #do_later(quit)
    #newconnection()
    cm = connection.SpykeConnectionManager()
    #time.sleep(1)
    while mainloop.is_running():
        print 'running'
        try:
            mainloop.run()
        except KeyboardInterrupt:
            do_later(quit)
        print 'done\n\n'

if __name__ == "__main__":
    main()