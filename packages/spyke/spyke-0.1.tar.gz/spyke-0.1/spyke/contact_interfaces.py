
import time

import telepathy.server
from telepathy.constants import (   HANDLE_TYPE_CONTACT,
                                    HANDLE_TYPE_LIST,
                                    HANDLE_TYPE_GROUP,
                                    HANDLE_TYPE_ROOM,
                                    HANDLE_TYPE_NONE,)

import shiny

import dbus

from skype_event_mappings import telepathy_status, skype_status, printer

@shiny.debug_class
class SpykeContacts(telepathy.server.ConnectionInterfaceContacts):
    """This is actually stolen from telepathy-butterfly.
    
    I do kinda feel that the generated classes really should skeleton-implement
    the properties too. There's *no* mention of them in the generated code.
    """
    
    attributes = {
        telepathy.CONNECTION : 'contact-id',
        telepathy.CONNECTION_INTERFACE_SIMPLE_PRESENCE : 'presence',
        telepathy.CONNECTION_INTERFACE_ALIASING : 'alias',
        #telepathy.CONNECTION_INTERFACE_AVATARS : 'token'
        }

    def __init__(self):
        telepathy.server.ConnectionInterfaceContacts.__init__(self)

        dbus_interface = telepathy.CONNECTION_INTERFACE_CONTACTS

        self._implement_property_get(dbus_interface, \
                {'ContactAttributeInterfaces' : self.get_contact_attribute_interfaces})

    # Overwrite the dbus attribute to get the sender argument
    @dbus.service.method(telepathy.CONNECTION_INTERFACE_CONTACTS, in_signature='auasb',
                            out_signature='a{ua{sv}}', sender_keyword='sender')
    def GetContactAttributes(self, handles, interfaces, hold, sender):
        #InspectHandle already checks we're connected, the handles and handle type.
        for interface in interfaces:
            if interface not in self.attributes:
                raise telepathy.errors.InvalidArgument(
                    'Interface %s is not supported by GetContactAttributes' % (interface))

        handle_type = telepathy.HANDLE_TYPE_CONTACT
        ret = {}
        for handle in handles:
            ret[handle] = {}

        functions = {
            telepathy.CONNECTION :
                lambda x: zip(x, self.InspectHandles(handle_type, x)),
            telepathy.CONNECTION_INTERFACE_SIMPLE_PRESENCE :
                lambda x: self.GetPresences(x).items(),
            telepathy.CONNECTION_INTERFACE_ALIASING :
                lambda x: self.GetAliases(x).items(),
            #telepathy.CONNECTION_INTERFACE_AVATARS :
            #    lambda x: self.GetKnownAvatarTokens(x).items()
            }

        #Hold handles if needed
        if hold:
            self.HoldHandles(handle_type, handles, sender)

        # Attributes from the interface org.freedesktop.Telepathy.Connection
        # are always returned, and need not be requested explicitly.
        interfaces = set(interfaces + [telepathy.CONNECTION])
        for interface in interfaces:
            interface_attribute = interface + '/' + self.attributes[interface]
            results = functions[interface](handles)
            for handle, value in results:
                ret[int(handle)][interface_attribute] = value
        return ret

    def get_contact_attribute_interfaces(self):
        return self.attributes.keys()



#Note: message actually corresponds to "Mood" in skype speak.
_details = {'message' : 's'}

# you get one of these for each status
# {name:(type, self_settable, exclusive, {argument:types}}
#names = ['offline','available','away','xa','hidden','dnd']
#types = [1,        2,            3,    4,    6,        6]
PRESENCES = {
    'available':(
        telepathy.CONNECTION_PRESENCE_TYPE_AVAILABLE,
        True, True, _details),
    'away':(
        telepathy.CONNECTION_PRESENCE_TYPE_AWAY,
        True, True, _details),
    'dnd':(
        6, #FIXME: tp-python should include this, like the spec.
        #telepathy.CONNECTION_PRESENCE_TYPE_BUSY,
        True, True, _details),
    'xa':(
        telepathy.CONNECTION_PRESENCE_TYPE_EXTENDED_AWAY,
        True, True, _details),
    'hidden':(
        telepathy.CONNECTION_PRESENCE_TYPE_HIDDEN,
        True, True, _details),
    'offline':(
        telepathy.CONNECTION_PRESENCE_TYPE_OFFLINE,
        True, True, _details)
}
@shiny.debug_class
class SpykeSimplePresence(telepathy.server.ConnectionInterfaceSimplePresence):
    
    #@shiny.blocking
    def GetPresences(self, handles):
        usernames = self.InspectHandles(
                    telepathy.CONNECTION_HANDLE_TYPE_CONTACT, 
                    handles)
        presences = []
        for username, handle in zip(usernames, handles):
            status_ = self._skype.get_user(username, 'ONLINESTATUS')
            status = telepathy_status[status_]
            presence_type = PRESENCES[status][0]
            personal_message = self._skype.get_user(username, 'MOOD_TEXT')
            presences.append((handle, (presence_type,status,personal_message)))
        return presences


@shiny.debug_class
class SpykeAliasing(telepathy.server.ConnectionInterfaceAliasing):
    
    def init(self):
        pass
    
    def GetAliasFlags(self):
        return 0
        
    
    def RequestAliases(self, handles):
        return self.InspectHandles(telepathy.CONNECTION_HANDLE_TYPE_CONTACT, handles)
    pass


@shiny.debug_class
class SpykePresence(telepathy.server.ConnectionInterfacePresence):

    
    def GetStatuses(self):
        return PRESENCES
    
    @shiny.blocking #due to skype.get()
    def GetPresence(self, handles):
        presences = {}
        usernames = self.InspectHandles(
                    telepathy.CONNECTION_HANDLE_TYPE_CONTACT, 
                    handles)
        for username, handle in zip(usernames, handles):
            timestamp = int(self._skype.get_user(username, 'LASTONLINETIMESTAMP'))
            #FIXME: this probably isn't required
            if not timestamp: 
                timestamp = int(time.time()) - 24*60*60
            status_ = self._skype.get_user(username, 'ONLINESTATUS')
            status = telepathy_status[status_]
            personal_message = self._skype.get_user(username, 'MOOD_TEXT')

            details = {}
            details['message'] = personal_message

            presences[handle] = (timestamp, {status : details})
        return presences
    
    #TODO: make this non-blocking.
    def RequestPresence(self, handles):
        self.PresenceUpdate(self.GetPresence(handles))
    
    def SetStatus(self, statuses):
        (status,) = statuses
        self._skype.register_callback('UserStatus', self.OnUserStatus)
        self._skype.set('userstatus', skype_status[status])
        
    #TODO: split these into their own class
    def OnUserStatus(self, Status):
        '''This event is caused by a user status change.

        @param Status: New user status.
        @type Status: L{User status<enums.cusUnknown>}
        '''
        #print dir(self.parent)
        #print [i for i in self.parent._handles.items()]
        handle = self.GetSelfHandle()
        status = telepathy_status[Status]
        self.PresenceUpdate({handle: (0, {status:{} })})
        #preserve mood?
