"""Helper Functions to ease programming, which should be provided by other libs"""
copying = """
    Copyright (C) 2007  David Laban <alsuren@gmail.com>

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

import time
import re
import os
import sys
import pdb

import gobject
import dbus
import telepathy

DEBUG = True

def debuggable(func):
    """decorator"""
    if DEBUG:
        def decorated(*args):
            print "Entering ",func.func_name
            print "    args ",args
            ret = func(*args)
            print ret
            return ret
        return decorated
    else:
        return func

def dprint(*args):
    """ like py3k's print function, but controllable like logging. """
    if DEBUG:
        for arg in args:
            print arg,
        print
        sys.stdout.flush()

def do_later(function, *args, **kwargs):
    try:
        timeout=kwargs.pop('timeout')
    except KeyError:
        timeout = 500
    def do(*args, **kwargs):
        try:
            out = function(*args, **kwargs)
            if out is not None:
                print out
            return False
        except Exception, e:
            print e
            raise e
    gobject.timeout_add(timeout, do, *args, **kwargs)

def head_and_tail(string):
    splitted=string.split(None, 1)
    head, tail={
            0: ('', ''),
            1: splitted + [''],
            2: splitted
        }[len(splitted)]
    return head, tail.strip()

# dbus shit
def variant(val, type):
    types={ 'u': dbus.UInt32,
            'i': dbus.Int32,
            'q': dbus.UInt16,
            'n': dbus.Int16,
            't': dbus.UInt64,
            'x': dbus.Int64,
            'b': dbus.Boolean,
            'y': dbus.Byte,
            'd': dbus.Double  }
    if type in types:
        return types[type](val)
    else:
        return val # and hope python gets it right on its own

def pretty(dbus_object):
    try:
        if isinstance(dbus_object, (dbus.Array, list, tuple)):
            return [pretty(item) for item in dbus_object]
        elif isinstance(dbus_object, dict):
            return dict([pretty(item) for item in dbus_object.items()])
        elif isinstance(dbus_object, dbus.String):
            return str(dbus_object)
        elif isinstance(dbus_object, telepathy.client.conn.Connection):
            return pretty(dbus_object[telepathy.CONN_INTERFACE].GetProtocol())\
                        , pretty(dbus_object[telepathy.CONN_INTERFACE].InspectHandles(
                                telepathy.CONNECTION_HANDLE_TYPE_CONTACT,
                                [dbus_object[telepathy.CONN_INTERFACE].GetSelfHandle()]))
        elif isinstance(dbus_object, telepathy.client.channel.Channel):
            return dbus_object # TODO: inspect_handles without a Connection?
        elif isinstance(dbus_object, (int, dbus.UInt32)):
            if dbus_object >= 2**30:
                return time.ctime(dbus_object)
            else:
                return int(dbus_object)
        else: 
            return dbus_object
    except dbus.exceptions.DBusException:
        return dbus_object

def get_private_bus():
    raw_output = os.popen('dbus-launch --csh-syntax --exit-with-session').read()
    m=re.search(r"setenv\s+DBUS_SESSION_BUS_ADDRESS\s+'([^']*)'", raw_output)
    (address,)=m.groups()
    private_bus = dbus.bus.BusConnection(address)
    return private_bus


#Skype4Py shit

#output shit

def green(string):
    return '\033[0;32;40m'+string+'\033[0m'
def red(string):
    return '\033[0;31;40m'+string+'\033[0m'

def output(*args, **kwargs):
    print args, kwargs