from zope.event import notify
from zope.app.container.contained import (
        ObjectAddedEvent,
        ObjectRemovedEvent,
    )

from DateTime import DateTime
from Products.CMFDefault.DiscussionItem import DiscussionItem
from Products.CMFDefault.DiscussionItem import DiscussionItemContainer

# Monkey patch createReply and deleteReply to fire object events
    
def createReply(self, title, text, Creator=None, text_format='structured-text'):
    """Create a reply and fire ObjectAddedEvent
    """
    
    container = self._container

    id = int(DateTime().timeTime())
    while self._container.get( str(id), None ) is not None:
        id = id + 1
    id = str( id )

    item = DiscussionItem( id, title=title, description=title )
    self._container[id] = item
    item = item.__of__(self)

    item.setFormat(text_format)
    item._edit(text)
    item.addCreator(Creator)
    item.setReplyTo(self._getDiscussable())

    # PATCH - default event handler for ObjectAddedEvent takes care of this
    # item.indexObject()
    item.notifyWorkflowCreated()

    # PATCH - tell the world about the new comment
    notify(ObjectAddedEvent(item, self, id))

    return id

createReply.__doc__ = DiscussionItemContainer.createReply.__doc__

def deleteReply(self, reply_id):
    """Delete a reply and fire ObjectRemovedEvent
    """
    
    if self._container.has_key( reply_id ):
            reply = self._container.get( reply_id ).__of__( self )
            my_replies = reply.talkback.getReplies()
            for my_reply in my_replies:
                my_reply_id = my_reply.getId()
                self.deleteReply(my_reply_id)

            if hasattr( reply, 'unindexObject' ):
                reply.unindexObject()
            
            del self._container[reply_id]
            
            # PATCH - tell the world about the deleted comment
            notify(ObjectRemovedEvent(reply, self, reply_id))

deleteReply.__doc__ = DiscussionItemContainer.deleteReply.__doc__

def apply_patches():
    DiscussionItemContainer.createReply = createReply
    DiscussionItemContainer.deleteReply = deleteReply
    
    # Don't hardcode DiscussionItem's state as 'published'
    
    if hasattr(DiscussionItem, 'review_state'):
        delattr(DiscussionItem, 'review_state')