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
import logging
import weakref
import types
import datetime, time
import gobject


import telepathy.server
from telepathy.server.handle import Handle
from telepathy.constants import (   HANDLE_TYPE_CONTACT,
                                    HANDLE_TYPE_LIST,
                                    HANDLE_TYPE_GROUP,
                                    HANDLE_TYPE_ROOM,
                                    HANDLE_TYPE_NONE,
                                    CONNECTION_STATUS_CONNECTED,
                                    CONNECTION_STATUS_CONNECTING,
                                    CONNECTION_STATUS_REASON_REQUESTED)
from telepathy.interfaces import (  CHANNEL_TYPE_CONTACT_LIST, 
                                    CHANNEL_TYPE_TEXT,
                                    CONNECTION_INTERFACE_REQUESTS,
                                    )
import dbus.mainloop.glib
import dbus

import shiny

import skype
from helper_functions import *
from list_channel import SpykeListChannel
from text_channel import SpykeTextChannel
from contact_interfaces import (  SpykePresence,
                         SpykeSimplePresence,
                         SpykeContacts,
                         SpykeAliasing,)

logging.basicConfig(level=logging.INFO)
        
@shiny.debug_class
class SpykeConnectionManager(telepathy.server.ConnectionManager):
    #@shiny.debug_exceptions
    def __init__(self):
        telepathy.server.ConnectionManager.__init__(self, 'spyke')
        self._protos['skype'] = ExistingConnection

#@shiny.debug_class
class SpykeConnection(telepathy.server.Connection):
    def Connect(self):
        # Start Skype initialisation.
        mainloop=dbus.mainloop.glib.DBusGMainLoop()
        self._skype = skype.Skype()
        self._skype.register_callback('ATTACHMENTSTATUS', self.OnAttachmentStatus)
        self._skype.register_callback('CONNSTATUS', self.OnConnectionStatus)
        #FIXME: This is probably going to cause some kind of race condition someday.
        # text_channel_factory is part of SpykeRequests.
        self._skype.register_factory('CHAT', self.text_channel_factory)
    
    def Disconnect(self):
        self._manager.disconnected(self)
    
    #TODO: use memoisation decorator instead.
    def RequestChannel(self, type, handle_type, handle, suppress_handler):
        channel = self.request_channel(type, handle_type, handle, suppress_handler)
        return channel.__dbus_object_path__  
        


    #TODO: push this into a different class.
    def OnAttachmentStatus(self, Status):
        if Status == Skype4Py.apiAttachAvailable:
            self._skype.Attach() #FIXME
    
    def OnGroups(self, groups):
        for g in groups.split(', '):
            print self._skype.call('GET GROUP %s users' % g.strip(', '))

    def OnConnectionStatus(self, Status):
        if Status == 'ONLINE':
            self.StatusChanged(CONNECTION_STATUS_CONNECTED, CONNECTION_STATUS_REASON_REQUESTED)
            self.init_list_channels()
        else:
            raise NotImplemented

@shiny.debug_class
class SpykeRequests(telepathy.server.ConnectionInterfaceRequests):
    #NewChannels
    #CreateChannel
    #EnsureChannel
    def __init__(self):
        self._implement_property_get(CONNECTION_INTERFACE_REQUESTS, 
            {'RequestableChannelClasses' : self.getRequestableChannelClasses})
    

        
    
    def getRequestableChannelClasses(self):
        return dbus.Array([
            dbus.Struct((
                dbus.Dictionary({
                    dbus.String(u'org.freedesktop.Telepathy.Channel.TargetHandleType'): dbus.UInt32(HANDLE_TYPE_LIST, variant_level=1), 
                    dbus.String(u'org.freedesktop.Telepathy.Channel.ChannelType'): dbus.String(u'org.freedesktop.Telepathy.Channel.Type.ContactList', variant_level=1)},
                signature=dbus.Signature('sv')), 
                dbus.Array([
                    dbus.String(u'org.freedesktop.Telepathy.Channel.TargetHandle'), 
                    dbus.String(u'org.freedesktop.Telepathy.Channel.TargetID')], 
                signature=dbus.Signature('s'))
            ), signature=None), 
            dbus.Struct((
                dbus.Dictionary({
                    dbus.String(u'org.freedesktop.Telepathy.Channel.TargetHandleType'): dbus.UInt32(3L, variant_level=1), 
                    dbus.String(u'org.freedesktop.Telepathy.Channel.ChannelType'): dbus.String(u'org.freedesktop.Telepathy.Channel.Type.ContactList', variant_level=1)}, 
                signature=dbus.Signature('sv')), 
                    dbus.Array([dbus.String(u'org.freedesktop.Telepathy.Channel.TargetHandle'), 
                    dbus.String(u'org.freedesktop.Telepathy.Channel.TargetID')], signature=dbus.Signature('s')
                )
            ), signature=None),],
        signature=dbus.Signature('(a{sv}as)'))
        
        
        dbus.Array([#Publish and subscribe.
                ({'org.freedesktop.Telepathy.Channel.ChannelType': 'org.freedesktop.Telepathy.Channel.Type.ContactList',
                  'org.freedesktop.Telepathy.Channel.TargetHandleType': HANDLE_TYPE_LIST},                                   
                 ['org.freedesktop.Telepathy.Channel.TargetHandle',                                            
                  'org.freedesktop.Telepathy.Channel.TargetID']),  
                #Text chats.
                ({'org.freedesktop.Telepathy.Channel.ChannelType': 'org.freedesktop.Telepathy.Channel.Type.Text',                                                                                                                            
                   'org.freedesktop.Telepathy.Channel.TargetHandleType': HANDLE_TYPE_CONTACT},                                   
                  ['org.freedesktop.Telepathy.Channel.TargetHandle',                                            
                   'org.freedesktop.Telepathy.Channel.TargetID'])], 
                   signature='a(a{sv}as)') # otherwise it gets inferred as a(a{si}as) and errors out.

    def request_channel(self, type, handle_type, handle, suppress_handler):
        '''Implements Connection.RequestChannel, but in this class, because that's kinda where it belongs.'''
        conn = self #passing self in as the first argument to a function is confusing.
        handle_ = self._handles[handle_type, handle]
        if (handle_type, handle) in self._channel_map:
            channel = self._channel_map[handle_type, handle]
        elif handle_type == HANDLE_TYPE_LIST:
            channel = SpykeListChannel(conn, handle_)
            self._channel_map[handle_type, handle] = channel
            self._channels.add(channel)
        elif handle_type == HANDLE_TYPE_ROOM:
            raise NotImplemented #room
        elif handle_type == HANDLE_TYPE_CONTACT and type == CHANNEL_TYPE_TEXT:
            channel = SpykeTextChannel(conn, handle_)
            self.add_channel(channel, handle_, suppress_handler)
        else:
            raise NotImplemented #other
            
        #self.add_channel(channel, handle_, suppress_handler)
        return channel

    def init_list_channels(self):
        """Telepathy spec says we shuold do this once we're connected.
        I think it might be possible to get away without this."""
        #self._skype.OnGroups = self.OnGroups
        #self._skype.invoke('search groups')
        #handle, = self.RequestHandles(HANDLE_TYPE_GROUP, ['Skype'], 'self')
        #self.RequestChannel(CHANNEL_TYPE_CONTACT_LIST, HANDLE_TYPE_GROUP, handle, True)
        
        names = ['subscribe', 'publish']#, 'allow', 'hide', 'deny']                             
        handles = self.RequestHandles(HANDLE_TYPE_LIST, names, 'self')                          
        for name, handle in zip(names, handles):     
            self.request_channel(CHANNEL_TYPE_CONTACT_LIST, HANDLE_TYPE_LIST, handle, True)
            #TODO: self.NewChannels()
    
    
    def text_channel_factory(self, event):
        """This is for creating text channels when an unhandled CHAT event happens."""
        suppress_handler = False #not been requested by anyone
        chat = self._skype.wrap_object(event)
        status = chat.get('STATUS')
        handle_type = HANDLE_TYPE_CONTACT
        if status == 'DIALOG':
            
            name = chat.get('ADDER')
            handle, = self.RequestHandles(HANDLE_TYPE_CONTACT, [name], 'self')
            handle_ = self._handles[handle_type, handle]
            channel = SpykeTextChannel(self, handle_)
            channel.refresh_messages()
        else:
            raise NotImplemented("I only support 1:1 chats currently.")
        self.add_channel(channel, handle_, suppress_handler)
        

    
#DON'T @shiny.debug_class
class ExistingConnection(SpykeConnection,
                         SpykePresence,
                         SpykeSimplePresence,
                         SpykeRequests,
                         SpykeContacts,
                         SpykeAliasing,
                         ):
    #@shiny.debug_exceptions
    def __init__(self, manager, params, mainloop=None):
        #fixme: what is self._channels for? answer: ListChannels, add_channel(channel, handle, suppress_handler):
        self._Chats = {}
        self._channel_map = weakref.WeakValueDictionary() # {(type, handle): channel} for use in RequestChannel.
        self._handles_by_name = {}
        self._manager = weakref.proxy(manager)

        account = params['account']
        #account="alsuren"
        SpykeConnection.__init__(self, 'skype', account, 'spyke')
        logging.info("telepathy connection advertised")
        for class_ in (  SpykePresence,
                         SpykeSimplePresence,
                         SpykeRequests,
                         SpykeContacts,
                         SpykeAliasing,):
            class_.__init__(self)
        #self._handles_by_name = {}
        self_handle_id = self.get_handle_id()
        self.set_self_handle(Handle(self_handle_id, HANDLE_TYPE_CONTACT, account))
        
        # FIXME: this should be done in telepathy-python
        self._handles[HANDLE_TYPE_CONTACT, self_handle_id] = self._self_handle
        self._handles_by_name[HANDLE_TYPE_CONTACT, account] = self._self_handle
        
        self._manager.connected(self)