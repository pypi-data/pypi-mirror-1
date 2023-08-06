import re
import pdb
import weakref
import shiny

import telepathy
from telepathy.server.channel import (  ChannelTypeText,
                                        ChannelInterfaceGroup,
                                        )
#is it worth splitting these constants out?
from telepathy import (   CHANNEL_TYPE_TEXT, 
                                    HANDLE_TYPE_CONTACT, 
                                    CHANNEL_GROUP_CHANGE_REASON_NONE,
                                    CHANNEL_TEXT_MESSAGE_TYPE_NORMAL,
                                    )

from skype import SkypeObject, parse_reply





@shiny.debug_class
class SpykeTextChannel(
        ChannelTypeText,
        SkypeObject,):
    """A 1:1 chat"""
    
    objtype = 'CHAT' #so that we can be used for callbacks
    def __init__(self, conn, handle_):
        self._skype = conn._skype
        #self._recv_id = 0
        ChannelTypeText.__init__(self, weakref.proxy(conn), handle_)
        name = handle_.get_name()
        reply = self._skype.call('CHAT CREATE', name)
        id = parse_reply('CHAT %s STATUS DIALOG', reply)
        self.id = id
        self._skype.register_object(self)
    
    def received(self, id, timestamp, sender, type, flags, text):
        """Wrapper around broken Received signal"""
        if id not in self._pending_messages:
            self.Received(id, timestamp, sender, type, flags, text)
    def set_current_members(self, handles, 
                            local_pending=[], 
                            remote_pending = [],
                            message='', 
                            actor=0, 
                            reason=CHANNEL_GROUP_CHANGE_REASON_NONE):
        handles = set(int(h) for h in handles)
        removed = self._members.difference(handles)
        added = handles.difference(self._members)
        
        self.MembersChanged(message, added, removed, local_pending, remote_pending, actor, reason)
    
    def Send(self, type, message):
        reply = self._skype.call('CHATMESSAGE', self.id, message)
        message_id = parse_reply('CHATMESSAGE %s STATUS SENDING', reply)
    
    def AcknowledgePendingMessages(self, ids):
        for id in ids:
            self._skype.invoke('SET CHATMESSAGE %s SEEN' % id)
        ChannelTypeText.AcknowledgePendingMessages(self, ids)

    def Close(self):
        """Overriding the Channel provided one, because I think dbus is keeping a reference to me."""
        self.Closed()
        self._conn.remove_channel(self) # deletes the reference that's there on purpose.
        self.remove_from_connection() # should delete dbus references.
        del self._prop_getters # objgraph shows a reference loop here. Thought I might as well.


    def notify(self, string):
        propname, _, value = string.partition(' ')
        if propname == 'ACTIVITY_TIMESTAMP':
            # We've probably got a new message
            #self.refresh_messages()
            pass
        elif propname == '_ACTIVITY_MESSAGE':
            self.refresh_message(value)
    
    def refresh_messages(self):
        messages = self.get('RECENTCHATMESSAGES')
        for id in messages.split(', '):
            self.refresh_message(id)
            
    def refresh_message(self, id):
        message = SkypeObject('CHATMESSAGE', id, self)
        timestamp = message.get('TIMESTAMP')
        sender = message.get('FROM_HANDLE')
        sender, = self._conn.RequestHandles(HANDLE_TYPE_CONTACT, [sender], 'self')
        type = message.get('TYPE')
        status = message.get('STATUS')
        text = message.get("BODY")
        if status == 'SENT':
            self.Sent(timestamp, CHANNEL_TEXT_MESSAGE_TYPE_NORMAL, text)
        elif status == 'RECEIVED':
            if type == 'SAID':
                type = CHANNEL_TEXT_MESSAGE_TYPE_NORMAL
                flags = 0
                self.Received(int(id), int(timestamp), sender, type, flags, text)
            elif type in ('CREATEDCHATWITH', 'EMOTED'):
                pass # todo: see if there's any telepathy signals to wire these to.
            else:
                raise NotImplemented('Message type not understood')
        elif status in ('SENDING', 'READ', 'CREATEDCHATWITH', ):
            pass
        else:
            raise  NotImplemented('Message status not understood')
        
    


