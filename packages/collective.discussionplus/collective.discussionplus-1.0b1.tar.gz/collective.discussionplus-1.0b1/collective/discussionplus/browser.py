from urllib import quote as url_quote

from five import grok
from zope.component import getMultiAdapter

from plone.intelligenttext.transforms import convertWebIntelligentPlainTextToHtml
from collective.discussionplus.interfaces import IDiscussionPlusLayer

from Acquisition import aq_inner, aq_parent
from AccessControl import getSecurityManager

from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.interfaces import IBelowContent

from Products.CMFCore.interfaces import IFolderish, IContentish, IDiscussionResponse
from Products.CMFCore.utils import getToolByName

from Products.CMFDefault.DiscussionTool import DiscussionNotAllowed

class CommentsViewlet(grok.Viewlet):
    """Show comments
    """
    
    grok.context(IContentish)
    grok.layer(IDiscussionPlusLayer)
    grok.viewletmanager(IBelowContent)
    grok.view(IViewView)
    grok.name('plone.comments')
    grok.require('zope2.View')
    
    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()

    def is_discussion_allowed(self):
        portal_discussion = getToolByName(aq_inner(self.context), 'portal_discussion', None)
        if portal_discussion is None:
            return False
        else:
            return portal_discussion.isDiscussionAllowedFor(aq_inner(self.context))

    def can_reply(self, obj=None):
        if obj is None:
            obj = aq_inner(self.context)
        return getSecurityManager().checkPermission('Reply to item', obj)

    def is_anonymous(self):
        return self.portal_state.anonymous()

    def login_action(self):
        return '%s/login_form?came_from=%s' % (self.site_url, url_quote(self.request.get('URL', '')),)

    def can_manage(self):
        return getSecurityManager().checkPermission('Manage portal', aq_inner(self.context))

    def member_info(self, creator):
        portal_membership = getToolByName(aq_inner(self.context), 'portal_membership', None)
        if portal_membership is None:
            return None
        else:
            return portal_membership.getMemberInfo(creator)

    def format_time(self, time):
        context = aq_inner(self.context)
        util = getToolByName(context, 'translation_service')
        return util.ulocalized_time(time, 1, context, domain='plonelocales')

    def get_replies(self):
        replies = []

        context = aq_inner(self.context)
        container = aq_parent(context)
        
        pd = getToolByName(context, 'portal_discussion')
        wf = getToolByName(context, 'portal_workflow')
        
        sm = getSecurityManager()

        def getRs(obj, replies, counter):
            rs = pd.getDiscussionFor(obj).getReplies()
            if len(rs) > 0:
                rs.sort(lambda x, y: cmp(x.created(), y.created()))
                for r in rs:
                    if sm.checkPermission('View', r):
                        actions = [a for a in wf.listActionInfos(object=r)
                                    if a['category'] == 'workflow' and a['allowed']]
                        
                        replies.append({
                             'depth': counter, 
                             'object': r,
                             'state': wf.getInfoFor(r, 'review_state'),
                             'actions': actions,
                             })
                        try:
                            getRs(r, replies, counter=counter + 1)
                        except DiscussionNotAllowed:
                            pass

        try:
            getRs(context, replies, 0)
        except DiscussionNotAllowed:
            pass
        
        return replies

class Review(grok.View):
    """List items for review and allow them to be either deleted or published.
    
    This is not fully generic: it assumes the review state is 'pending', the
    portal_type is 'Discussion Item' and that the 'publish' action is
    available.
    """
    
    grok.context(IFolderish)
    grok.layer(IDiscussionPlusLayer)
    grok.name('review-comments')
    grok.require('collective.discussionplus.ReviewComments')
    
    def cook(self, text):
        return convertWebIntelligentPlainTextToHtml(text)
    
    def format_time(self, time):
        context = aq_inner(self.context)
        util = getToolByName(context, 'translation_service')
        return util.ulocalized_time(time, 1, context, domain='plonelocales')
    
    def update(self):
        self.state = self.request.get('review_state', 'pending')
        self.transition = self.request.get('publish_transition', 'pending')
        self.limit = self.request.get('limit', 100)
        
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        
        self.comments_pending_review = catalog(
                path='/'.join(context.getPhysicalPath()),
                portal_type='Discussion Item',
                review_state=self.state,
                sort_on='created',
                sort_limit=self.limit,
            )
    
class DeleteComment(grok.View):
    """AJAX response handler for processing a comment
    """
    
    grok.context(IDiscussionResponse)
    grok.layer(IDiscussionPlusLayer)
    grok.name('review-delete-comment')
    grok.require('collective.discussionplus.ReviewComments')
    
    def update(self):
        comment = aq_inner(self.context)
        
        # Sanity check
        comment_id = self.request.form['comment_id']
        if comment_id != comment.getId():
            raise ValueError

        portal_discussion = getToolByName(comment, 'portal_discussion')
        
        parent = comment.inReplyTo()
        if parent is not None:
            talkback = portal_discussion.getDiscussionFor(parent)
        else:
            talkback = aq_parent(comment)
        
        talkback.deleteReply(comment.getId())
        
    def render(self):
        return ''

class PublishComment(grok.View):
    """AJAX response handler for processing a comment
    """
    
    grok.context(IDiscussionResponse)
    grok.layer(IDiscussionPlusLayer)
    grok.name('review-publish-comment')
    grok.require('collective.discussionplus.ReviewComments')
    
    def update(self):
        comment = aq_inner(self.context)
        # Sanity check
        comment_id = self.request.form['comment_id']
        if comment_id != comment.getId():
            raise ValueError
        
        action = self.request.form['action']
        portal_workflow = getToolByName(comment, 'portal_workflow')
        portal_workflow.doActionFor(comment, action)
        
    def render(self):
        return ''