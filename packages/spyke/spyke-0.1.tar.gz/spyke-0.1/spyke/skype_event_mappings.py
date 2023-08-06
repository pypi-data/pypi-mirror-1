"""This is the wrong way to do it. 
What I should really be doing is adding event handlers for the things telepathy needs."""

import time, datetime
import pdb
from helper_functions import dprint

from telepathy.constants import (HANDLE_TYPE_CONTACT,
                                 CONNECTION_STATUS_CONNECTED,
                                 CONNECTION_STATUS_CONNECTING,
                                 CONNECTION_STATUS_REASON_REQUESTED,
                                 CONNECTION_STATUS_REASON_NONE_SPECIFIED,
                                 CHANNEL_TEXT_MESSAGE_TYPE_NORMAL)

#from text_channel import TextChannel

class EventsToStdout(object):
    def __getattr__(self, name):
        def show(*args, **kwargs):
            if kwargs:
                print name+'('+', '.join(repr(arg) for arg in args) + ', '+repr(kwargs)+'** )'
            else:
                print name+'('+', '.join(repr(arg) for arg in args) + ')'
        return show

telepathy_status = {
'UNKNOWN':'offline', # FIXME
'OFFLINE':'offline',
'ONLINE':'available',
'AWAY':'away',
'NA':'xa',
'DND':'dnd',
'INVISIBLE':'hidden',
'SKYPEOUT':'hidden', # FIXME
'SKYPEME':'available'}

skype_status = dict(map(reversed, telepathy_status.items()))

printer = EventsToStdout()


# comment out methods if not sure about them.
class EventsToTelepathy(EventsToStdout):

    def __init__(self, parent):
        self.parent=parent


    def Command(self, Command):
        '''This event is triggered when a command is sent to the Skype API.

        @param Command: Command object.
        @type Command: L{ICommand}
        '''
        dprint('>', Command.Command)
        
    def Reply(self, Command):
        '''This event is triggered when the API replies to a command object.

        @param Command: Command object.
        @type Command: L{ICommand}
        '''
        dprint('<', Command.Reply)
        

    def Notify(self, Notification):
        '''This event is triggered whenever Skype client sends a notification.

        @param Notification: Notification string.
        @type Notification: unicode
        @note: Use this event only if there is no dedicated one.
        '''
        pass #shouldn't need to use it ever. Touch wood.        
        
        
        

        
#    def ApplicationConnecting(self, App, Users):
        '''This event is triggered when list of users connecting to an application changes.

        @param App: Application object.
        @type App: L{IApplication}
        @param Users: Connecting users.
        @type Users: tuple of L{IUser}
        '''
        

#    def ApplicationDatagram(self, App, Stream, Text):
        '''This event is caused by the arrival of an application datagram.

        @param App: Application object.
        @type App: L{IApplication}
        @param Stream: Application stream that received the datagram.
        @type Stream: L{IApplicationStream}
        @param Text: The datagram text.
        @type Text: unicode
        '''

#    def ApplicationReceiving(self, App, Streams):
        '''This event is triggered when list of application receiving streams changes.

        @param App: Application object.
        @type App: L{IApplication}
        @param Streams: Application receiving streams.
        @type Streams: tuple of L{IApplicationStream}
        '''

#    def ApplicationSending(self, App, Streams):
        '''This event is triggered when list of application sending streams changes.

        @param App: Application object.
        @type App: L{IApplication}
        @param Streams: Application sending streams.
        @type Streams: tuple of L{IApplicationStream}
        '''

#    def ApplicationStreams(self, App, Streams):
        '''This event is triggered when list of application streams changes.

        @param App: Application object.
        @type App: L{IApplication}
        @param Streams: Application streams.
        @type Streams: tuple of L{IApplicationStream}
        '''

    def AsyncSearchUsersFinished(self, Cookie, Users):
        '''This event occurs when an asynchronous search is completed.

        @param Cookie: Search identifier as returned by L{ISkype.AsyncSearchUsers}.
        @type Cookie: int
        @param Users: Found users.
        @type Users: tuple of L{IUser}
        @see: L{ISkype.AsyncSearchUsers}
        '''
        #org.freedesktop.Telepathy.Channel.Type.ContactSearch?

    def AttachmentStatus(self, Status):
        '''This event is caused by a change in the status of an attachment to the Skype API.

        @param Status: New attachment status.
        @type Status: L{Attachment status<enums.apiAttachUnknown>}
        '''
        #self.StatusChanged(CONNECTION_STATUS_CONNECTING,_)

    def AutoAway(self, Automatic):
        '''This event is caused by a change of auto away status.

        @param Automatic: New auto away status.
        @type Automatic: bool
        '''
        if Automatic:
            self.parent.PresenceUpdate({handle: (0, {'xa':{'reason':'auto'} })})
        else:
            self.parent.PresenceUpdate({handle: (0, {'online':{'reason':'auto'} })})

#    def CallDtmfReceived(self, Call, Code):
        '''This event is caused by a call DTMF event.

        @param Call: Call object.
        @type Call: L{ICall}
        @param Code: Received DTMF code.
        @type Code: unicode
        '''

#    def CallHistory(self):
        '''This event is caused by a change in call history.
        '''

#    def CallInputStatusChanged(self, Call, Active):
        '''This event is caused by a change in the Call voice input status change.

        @param Call: Call object.
        @type Call: L{ICall}
        @param Active: New voice input status (active when True).
        @type Active: bool
        '''
        #StreamEngine?

#    def CallSeenStatusChanged(self, Call, Seen):
        '''This event occurs when the seen status of a call changes.

        @param Call: Call object.
        @type Call: L{ICall}
        @param Seen: True if call was seen.
        @type Seen: bool
        @see: L{ICall.Seen}
        '''
        #StreamEngine?

#    def CallStatus(self, Call, Status):
        '''This event is caused by a change in call status.

        @param Call: Call object.
        @type Call: L{ICall}
        @param Status: New status of the call.
        @type Status: L{Call status<enums.clsUnknown>}
        '''

#    def CallTransferStatusChanged(self, Call, Status):
        '''This event occurs when a call transfer status changes.

        @param Call: Call object.
        @type Call: L{ICall}
        @param Status: New status of the call transfer.
        @type Status: L{Call status<enums.clsUnknown>}
        '''

#    def CallVideoReceiveStatusChanged(self, Call, Status):
        '''This event occurs when a call video receive status changes.

        @param Call: Call object.
        @type Call: L{ICall}
        @param Status: New video receive status of the call.
        @type Status: L{Call video send status<enums.vssUnknown>}
        '''

#    def CallVideoSendStatusChanged(self, Call, Status):
        '''This event occurs when a call video send status changes.

        @param Call: Call object.
        @type Call: L{ICall}
        @param Status: New video send status of the call.
        @type Status: L{Call video send status<enums.vssUnknown>}
        '''

#    def CallVideoStatusChanged(self, Call, Status):
        '''This event occurs when a call video status changes.

        @param Call: Call object.
        @type Call: L{ICall}
        @param Status: New video status of the call.
        @type Status: L{Call video status<enums.cvsUnknown>}
        '''

    def ChatMemberRoleChanged(self, Member, Role):
        '''This event occurs when a chat member role changes.

        @param Member: Chat member object.
        @type Member: L{IChatMember}
        @param Role: New member role.
        @type Role: L{Chat member role<enums.chatMemberRoleUnknown>}
        '''
        print 'ChatMemberRoleChanged', Member, Role

    def ChatMembersChanged(self, Chat, Members):
        '''This event occurs when a list of chat members change.

        @param Chat: Chat object.
        @type Chat: L{IChat}
        @param Members: Chat members.
        @type Members: tuple of L{IUser}
        '''
        try:
            channel = self.parent._Chats[Chat]
        except KeyError:
            channel = TextChannel(self.parent, Chat)
            self.parent._Chats[Chat] = channel
        
        Handles = [m.Handle for m in Chat.Members]
        handles = self.parent.RequestHandles(HANDLE_TYPE_CONTACT, Handles, 'self')
        
        channel.set_current_members(handles)
        #print 'ChatMembersChanged', Chat, Members

#    def ChatWindowState(self, Chat, State):
        '''This event occurs when chat window is opened or closed.

        @param Chat: Chat object.
        @type Chat: L{IChat}
        @param State: True if the window was opened or False if closed.
        @type State: bool
        '''

#    def ClientWindowState(self, State):
        '''This event occurs when the state of the client window changes.

        @param State: New window state.
        @type State: L{Window state<enums.wndUnknown>}
        '''



    def ConnectionStatus(self, Status):
        '''This event is caused by a connection status change.

        @param Status: New connection status.
        @type Status: L{Connection status<enums.conUnknown>}
        '''
        if Status == 'ONLINE':
            self.parent.StatusChanged(CONNECTION_STATUS_CONNECTED, CONNECTION_STATUS_REASON_REQUESTED)
            self.parent.init_list_channels()
        elif Status == 'CONNECTING':
            print "CONNECTING: What the fuck?" #FIXME
            #self.parent.StatusChanged(CONNECTION_STATUS_CONNECTING, CONNECTION_STATUS_REASON_NONE_SPECIFIED)
        else:
            printer.ConnectionStatus(self, Status)

    def ContactsFocused(self, Username):
        '''This event is caused by a change in contacts focus.

        @param Username: Name of the user that was focused or empty string if focus was lost.
        @type Username: unicode
        '''
        pass # ui

#    def Error(self, Command, Number, Description):
        '''This event is triggered when an error occurs during execution of an API command.

        @param Command: Command object that caused the error.
        @type Command: L{ICommand}
        @param Number: Error number returned by the Skype API.
        @type Number: int
        @param Description: Description of the error.
        @type Description: unicode
        '''
        #probably quite important

#    def FileTransferStatusChanged(self, Transfer, Status):
        '''This event occurs when a file transfer status changes.

        @param Transfer: File transfer object.
        @type Transfer: L{IFileTransfer}
        @param Status: New status of the file transfer.
        @type Status: L{File transfer status<enums.fileTransferStatusNew>}
        '''
        #not standardised yet dec 2007

#    def GroupDeleted(self, GroupId):
        '''This event is caused by a user deleting a custom contact group.

        @param GroupId: Id of the deleted group.
        @type GroupId: int
        '''
        #org.freedesktop.Telepathy.Channel.Interface.Group
        #org.freedesktop.Telepathy.Channel.Closed()

    def GroupExpanded(self, Group, Expanded):
        '''This event is caused by a user expanding or collapsing a group in the contacts tab.

        @param Group: Group object.
        @type Group: L{IGroup}
        @param Expanded: Tells if the group is expanded (True) or collapsed (False).
        @type Expanded: bool
        '''
        pass #ui

    def GroupUsers(self, Group, Users):
        '''This event is caused by a change in a contact group members.

        @param Group: Group object.
        @type Group: L{IGroup}
        @param Users: Group members.
        @type Users: tuple of L{IUser}
        '''
        printer.GroupUsers(self, Group, Users)

    def GroupVisible(self, Group, Visible):
        '''This event is caused by a user hiding/showing a group in the contacts tab.

        @param Group: Group object.
        @type Group: L{IGroup}
        @param Visible: Tells if the group is visible or not.
        @type Visible: bool
        '''
        pass #ui

#    def MessageHistory(self, Username):
        '''This event is caused by a change in message history.

        @param Username: Name of the user whose message history changed.
        @type Username: unicode
        '''

    def MessageStatus(self, Message, Status):
        '''This event is caused by a change in chat message status.

        @param Message: Chat message object.
        @type Message: L{IChatMessage}
        @param Status: New status of the chat message.
        @type Status: L{Chat message status<enums.cmsUnknown>}
        '''
        #org.freedesktop.Telepathy.Channel.Type.Text
        #SendError ( u: error, u: timestamp, u: type, s: text )
        #Sent ( u: timestamp, u: type, s: text )
        Chat=Message.Chat
        try:
            channel = self.parent._Chats[Chat]
        except KeyError:
            channel = TextChannel(self.parent, Chat)
            self.parent._Chats[Chat] = channel
        
        if Message.Type == 'SAID':
            Time = Message.Datetime
            timestamp = time.mktime(Time.timetuple())
            (sender,) = self.parent.RequestHandles(HANDLE_TYPE_CONTACT, [Message.FromHandle], 'self')
            type = CHANNEL_TEXT_MESSAGE_TYPE_NORMAL
            text = Message.Body
            if Status in ('RECEIVED', 'READ'):
                channel.received(Message.Id, timestamp, sender, type, 0, text)
            elif Status in ('SENT',):
                channel.Sent(timestamp, type, text)
            elif Status == 'SENDING':
                pass
            else:
                printer._MessageStatus((Message.Chat,Message.Id,Message.Body), Status)
        
        else:
            print Message.Type
            print 'empty message'
            #for key in Message.__dict__:
            #    if key[0].isupper():
            for key in ["Body", "ChatName", "ChatName", 
                        "EditedTimestamp", "FromDisplayName", 
                        "Id", "IsEditable", #"LeaveReason", "Seen", 
                        "Sender", "Status", "Timestamp", "Type", "Users"]:
                try:
                    print key, getattr(Message, key)
                except AttributeError:
                    pass

#    def Mute(self, Mute):
        '''This event is caused by a change in mute status.

        @param Mute: New mute status.
        @type Mute: bool
        '''
        


    def OnlineStatus(self, User, Status):
        '''This event is caused by a change in the online status of a user.

        @param User: User object.
        @type User: L{IUser}
        @param Status: New online status of the user.
        @type Status: L{Online status<enums.olsUnknown>}
        '''
        (handle,)=self.parent.RequestHandles(HANDLE_TYPE_CONTACT, [User.Handle], 'self')
        status = telepathy_status[Status]
        self.parent.PresenceUpdate({int(handle): (0, {status:{} })})

    def PluginEventClicked(self, Event):
        '''This event occurs when a user clicks on a plug-in event.

        @param Event: Plugin event object.
        @type Event: L{IPluginEvent}
        '''
        pass #ui

    def PluginMenuItemClicked(self, MenuItem, Users, PluginContext, ContextId):
        '''This event occurs when a user clicks on a plug-in menu item.

        @param MenuItem: Menu item object.
        @type MenuItem: L{IPluginMenuItem}
        @param Users: Users this item refers to.
        @type Users: tuple of L{IUser}
        @param PluginContext: Plug-in context.
        @type PluginContext: unicode
        @param ContextId: Context Id.
        @type ContextId: unicode
        @see: L{IPluginMenuItem}
        '''
        pass #ui


#    def SmsMessageStatusChanged(self, Message, Status):
        '''This event is caused by a change in the SMS message status.

        @param Message: SMS message object.
        @type Message: L{ISmsMessage}
        @param Status: New status of the SMS message.
        @type Status: L{SMS message status<enums.smsMessageStatusUnknown>}
        '''

#    def SmsTargetStatusChanged(self, Target, Status):
        '''This event is caused by a change in the SMS target status.

        @param Target: SMS target object.
        @type Target: L{ISmsTarget}
        @param Status: New status of the SMS target.
        @type Status: L{SMS target status<enums.smsTargetStatusUnknown>}
        '''

    def UserMood(self, User, MoodText):
        '''This event is caused by a change in the mood text of the user.

        @param User: User object.
        @type User: L{IUser}
        @param MoodText: New mood text.
        @type MoodText: unicode
        '''
        (handle,)=self.parent.RequestHandles(HANDLE_TYPE_CONTACT, [User.Handle], 'self')
        presence = self.parent.GetPresence([int(handle)])
        self.parent.PresenceUpdate(presence)

    def UserStatus(self, Status):
        '''This event is caused by a user status change.

        @param Status: New user status.
        @type Status: L{User status<enums.cusUnknown>}
        '''
        #print dir(self.parent)
        #print [i for i in self.parent._handles.items()]
        handle = self.parent.GetSelfHandle()
        status = telepathy_status[Status]
        self.parent.PresenceUpdate({handle: (0, {status:{} })})
        #preserve mood?

#    def VoicemailStatus(self, Mail, Status):
        '''This event is caused by a change in voicemail status.

        @param Mail: Voicemail object.
        @type Mail: L{IVoicemail}
        @param Status: New status of the voicemail.
        @type Status: L{Voicemail status<enums.vmsUnknown>}
        '''

    def WallpaperChanged(self, Path):
        '''This event occurs when client wallpaper changes.

        @param Path: Path to new wallpaper bitmap.
        @type Path: unicode
        '''
        pass #ui
