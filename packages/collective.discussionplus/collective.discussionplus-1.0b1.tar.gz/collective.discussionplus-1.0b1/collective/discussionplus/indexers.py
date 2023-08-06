from BTrees.OOBTree import OOBTree

from five import grok

from zope.annotation.interfaces import IAnnotations
from plone.indexer.interfaces import IIndexer

from zope.app.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent

from Products.DCWorkflow.interfaces import IAfterTransitionEvent
from Products.CMFCore.interfaces import IContentish, IDiscussionResponse
from Products.CMFCore.utils import getToolByName

COUNT_KEY        = u"collective.discussionplus.count"        # integer
COMMENTATORS_KEY = u"collective.discussionplus.commentators" # dict of reply_id -> creator

# Subscribers to keep information up to date

@grok.subscribe(IDiscussionResponse, IObjectAddedEvent)
def comment_added(obj, event):
    """A comment was added. If it's published, increase the comment count on
    the ultimate parent. Regardless, record the user.
    """
    parents = obj.parentsInThread()
    if len(parents) > 0:
        content = parents[0]
        annotations = IAnnotations(content, None)
        if annotations is not None:
            
            # Update count if the comment is published already
            wf = getToolByName(obj, 'portal_workflow', None)
            if wf is not None:
                state = wf.getInfoFor(obj, 'review_state')
                if state == 'published':
                    old_count = annotations.get(COUNT_KEY, 0)
                    annotations[COUNT_KEY] = old_count + 1
            
            # Record creator
            commentators = annotations.setdefault(COMMENTATORS_KEY, OOBTree())
            commentators[obj.getId()] = obj.Creator()
            
            content.reindexObject(idxs=('number_of_comments', 'commentators',))

@grok.subscribe(IDiscussionResponse, IObjectRemovedEvent)
def commend_removed(obj, event):
    """A comment was removed. If it was published, decrease the comment count
    on the ultimate parent. Remove the user.
    """
    parents = obj.parentsInThread()
    if len(parents) > 0:
        content = parents[0]
        annotations = IAnnotations(content, None)
        if annotations is not None:
            
            # Update count if the comment was published
            wf = getToolByName(obj, 'portal_workflow', None)
            if wf is not None:
                state = wf.getInfoFor(obj, 'review_state')
                if state == 'published':
                    old_count = annotations.get(COUNT_KEY, 0)
                    if old_count > 0:
                        annotations[COUNT_KEY] = old_count - 1
            
            # Remove creator
            commentators = annotations.setdefault(COMMENTATORS_KEY, OOBTree())
            if obj.getId() in commentators:
                del commentators[obj.getId()]
        
            content.reindexObject(idxs=('number_of_comments', 'commentators',))

@grok.subscribe(IDiscussionResponse, IAfterTransitionEvent)
def comment_transitioned(obj, event):
    """A comment was transitioned. Update the comment count.
    """

    if event.transition is None:
        return
    
    parents = obj.parentsInThread()
    if len(parents) > 0:
        content = parents[0]
        annotations = IAnnotations(content, None)
        if annotations is not None:
            
            old_state = event.old_state
            new_state = event.new_state
            
            delta = 0
            
            # item is no longer published - decrease the count
            if old_state is not None and old_state.getId() == 'publshed' \
                    and (new_state is None or new_state.getId() != 'published'):
                delta = -1
            elif new_state is not None and new_state.getId() == 'published' \
                    and (old_state is None or old_state.getId() != 'published'):
                delta = 1
            
            if delta != 0:
                old_count = annotations.get(COUNT_KEY, 0)
                new_count = old_count + delta
                
                if new_count < 0:
                    new_count = 0
                
                if new_count != old_count:
                    annotations[COUNT_KEY] = new_count
                    content.reindexObject(idxs=('number_of_comments',))

# Indexers

class NumberOfCommentsIndexer(grok.Adapter):
    """Index the number of comments that have been left on this content item.
    """
    
    grok.implements(IIndexer)
    grok.context(IContentish)
    grok.name('number_of_comments')
    
    def __call__(self, portal, **kw):
        annotations = IAnnotations(self.context, None)
        if annotations is not None:
            return annotations.get(COUNT_KEY, 0)

class CommentatorsIndexer(grok.Adapter):
    """Index the users who have commented on this object
    """
    
    grok.implements(IIndexer)
    grok.context(IContentish)
    grok.name('commentators')
    
    def __call__(self, portal, **kw):
        annotations = IAnnotations(self.context, None)
        if annotations is not None:
            # return a list of unique items
            return tuple(set(annotations.get(COMMENTATORS_KEY, {}).values()))

class CommentSubjectIndexer(grok.Adapter):
    """Index the title of the object that a comment was left on
    """
    
    grok.implements(IIndexer)
    grok.context(IDiscussionResponse)
    grok.name('comment_subject')
    
    def __call__(self, portal, **kw):
        parents = self.context.parentsInThread()
        if len(parents) > 0:
            content = parents[0]
            return content.Title()
        return None

class CommentTextIndexer(grok.Adapter):
    """Index the text of a comment up to 500 characters. If truncated, show
    an ellipsis.
    """
    
    grok.implements(IIndexer)
    grok.context(IDiscussionResponse)
    grok.name('Description')
    
    def __call__(self, portal, **kw):
        text = self.context.text[:500]
        if len(self.context.text) > 500:
            text += " [...]"
        return text