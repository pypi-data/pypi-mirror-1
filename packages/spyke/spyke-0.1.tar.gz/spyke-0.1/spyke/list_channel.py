import weakref
import telepathy
from telepathy.constants import (HANDLE_TYPE_CONTACT,
                                 HANDLE_TYPE_LIST,
                                 CONNECTION_STATUS_CONNECTED,
                                 CONNECTION_STATUS_CONNECTING,
                                 CONNECTION_STATUS_REASON_REQUESTED)

        #todo attach to GroupUsers(self, Group, Users)
        #todo attach to GroupDeleted(self, GroupId)

import shiny

class SpykeListChannel(
        telepathy.server.ChannelTypeContactList, #includes Channel
        telepathy.server.ChannelInterfaceGroup,):
    """Only used for magic lists."""
    @shiny.blocking
    def __init__(self, conn, handle_):
        telepathy.server.ChannelTypeContactList.__init__(self, conn, handle_)
        telepathy.server.ChannelInterfaceGroup.__init__(self)
        self.conn = weakref.proxy(conn)
        usernames = self.conn._skype.call('SEARCH FRIENDS').replace(',', '').split()[1:]
        handles = self.conn.RequestHandles(HANDLE_TYPE_CONTACT, usernames, 'self')
        self._members.update(int(h) for h in handles)

    
    def GetLocalPendingMembersWithInfo(self):
        return []
