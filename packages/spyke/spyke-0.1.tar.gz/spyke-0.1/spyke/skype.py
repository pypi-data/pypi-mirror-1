#!/usr/bin/env python


import sys
import types
import weakref
import pdb
import re

import gobject
import dbus
import dbus.service

import shiny
#import commandline

# Utility functions that really should be in some external library.

def blocking(func):
    """A decorator for blocking functions, so that you don't accidentally call
    them from within event handlers."""
    func.is_blocking = True
    return func

def iscallable(func):
    return isinstance(func, (types.FunctionType, types.MethodType))

def print_prompt():
    print '> ',
    sys.stdout.flush()
def print_reply(reply):
    print '< ', reply
    print_prompt()
def print_event(event):
    print 
    print '#', event
    print_prompt()
def print_error(*args, **kwargs):
    print args, kwargs


@shiny.only_once
def init_dbus():
    """Creates the global bus object, which is a dbus.SessionBus"""
    global bus
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    return bus



def parse_reply(format, reply):
    """basically scanf()"""
    pattern = format.replace('%s', r'(.*)').replace('$', '\$')
    ret = re.match(pattern, reply).groups()
    if len(ret) == 1:
        ret, = ret
    return ret

class SkypeObject(object):
    """This class is a wrapper around some functionality provided by skype
    objects: https://developer.skype.com/Docs/ApiDoc/Objects"""
    def __init__(self, objtype, id, parent):
        self._skype = parent._skype
        self.id = id
        self.objtype = objtype
        
    def get(self, name):
        """For getting properties."""
        propname = name.upper()
        reply = self._skype.call('GET', self.objtype, self.id, propname)
        format = ' '.join( (self.objtype, self.id, propname, '%s') )
        value = parse_reply(format, reply)
        return value
    
    def notify(self, string):
        raise NotImplemented


#@shiny.debug_class
class Skype(dbus.service.Object):
    """This is to replace Skype4Py.Skype(), in a non-threaded kind of way."""
    #@blocking
    def __init__(self):
        bus = init_dbus()
        dbus.service.Object.__init__(self, bus, '/com/Skype/Client')
        
        self._callbacks = {}#weakref.WeakValueDictionary() # key=UPPERCASE command name. value=callback
        # key = object type from https://developer.skype.com/Docs/ApiDoc/Objects.
        # value = dict of id:callback.
        self._objects = {} # contatins a weakref.WeakValueDictionary() 
        self._factories = {} #TODO: fix because bound methods can't be put in a weakref.WeakValueDictionary()
        
        self._skype = weakref.proxy(self) # to make us look like all spyke classes.
        skype_object = bus.get_object('com.Skype.API', '/com/Skype')
        self._Skype = dbus.Interface(skype_object, 'com.Skype.API')
        assert self.call('NAME console') == 'OK'
        assert self.call('PROTOCOL 5') == 'PROTOCOL 5'

            
    @dbus.service.method('com.Skype.API.Client', in_signature='v')
    def Notify(self, event):
        """
        THIS SHOULD NOT BE PART OF THE PUBLIC API, BUT SKYPE REQUIRES IT.
        Accept events (strings) from skype, and dispatches them to the
        appropriate handler."""
        self.notify(event)
        
    @shiny.debug_exceptions
    def notify(self, event):
        """
        Accept events (strings) from skype, and dispatches them to the
        appropriate handler."""
        objtype, _, args = event.partition(' ')
        id, _, prop = args.partition(' ')
        if objtype == 'CHATMESSAGE':
            self._translate_event(event)
        elif objtype in self._callbacks:
            cb = self._callbacks[objtype]
            cb(args)
        elif objtype in self._objects and id in self._objects[objtype]: 
            obj = self._objects[objtype][id]
            obj.notify(prop)                
        elif objtype in self._factories:
            factory = self._factories[objtype]
            factory(event)
        else:
            print self._factories.keys()
            print_event(event)
    
    def _translate_event(self, event):
        """Skype doesn't provide any events on the CHAT object a message has
        been received in, so we have to fake it.
        the event takes the form of a new property
        CHAT <chat_id> _ACTIVITY_MESSAGE <message_id>
        (think ACTIVITY_TIMESTAMP but actually useful)
        """
        message = self.wrap_object(event)
        chat_id = message.get('CHATNAME')
        status = message.get('STATUS')
        if status not in ['READ']:
            self.Notify('CHAT %s _ACTIVITY_MESSAGE %s' % (chat_id, message.id))
    
    def wrap_object(self, event):
        """Create a SkypeObject representing the object, from a property update event."""
        objtype, id, prop, value = event.split()
        obj = SkypeObject(objtype, id, self)
        return obj
        
    
    # Public API
    def invoke(self, command, *args):
        """Proxy method for skype.Invoke(). Note that replies are sent to Notify."""
        command = command + ' '.join(args)
        self._Skype.Invoke(command, reply_handler=self.Notify, error_handler=print_error)

    def set(self, name, value):
        """Sends "set name value" to skype."""
        command = ' '.join(['SET', name, value])
        self.invoke(command)
        
        
    def register_callback(self, name, callback):
        """For registering interst in status updates etc.
        If the first word of the skype event string is name then
        callback will be called with the first word stripped from the event string. """
        key = name.upper()
        self._callbacks[key] = callback
        
    def register_object(self, obj):
        """For registering interest in status updates. 
        obj should have the attributes objtype, id, and notify()"""
        objtype = obj.objtype
        id = obj.id
        assert objtype != 'CHATMESSAGE' , "Sorry. Listen to CHAT _ACTIVITY_MESSAGE instead."
        registry = self._objects.setdefault(objtype, weakref.WeakValueDictionary())
        registry[id] = obj #FIXME: circular references
        
    def register_factory(self, objtype, factory):
        """If an object of the required type is not found, but a factory 
        function is registered, it will be called with the full event string."""
        self._factories[objtype]=factory
    
    #@blocking
    def get(self, name):
        """Sends "get name" to skype. and returns the value returned by skype (minus the name)."""
        command = 'GET ' + name
        reply = self.call(command)
        assert name in reply
        return reply.partition(name)[-1].strip()
    
    #@blocking
    def call(self, command, *args):
        command = ' '.join((command,) + args)
        reply = self._Skype.Invoke(command)
        assert not reply.startswith('ERROR')
        return reply

    def get_user(self, username, property):
        return self.get('USER %s %s' % (username, property))





class Repl(Skype):
    """Read, Evaluate, Print Loop"""
    def __init__(self):
        Skype.__init__(self)
        gobject.io_add_watch(sys.stdin, gobject.IO_IN, self.handle_input)
        print_prompt()
    def apply_substitutions(self, line):
        """Hook for doing variable substitiution etc. at a later date."""
        return line
        
    def handle_input(self, fd, _):
        """Called by dbus for every line of input. Just invokes commands and 
        waits for replies."""
        line=fd.readline()
        if line=='': # no \n. probably EOF
            gobject.idle_add(exit)
            return False # Don't ask for more input
        else:
            command = self.apply_substitutions(line)
            self.invoke(command)
            return True

def main():
    """This provides a console for skype commands, using the skype api."""
    repl = Repl()
    loop = gobject.MainLoop()
    loop.run()


if __name__ == "__main__":
    #commandline.run_as_main(main)
    main()
