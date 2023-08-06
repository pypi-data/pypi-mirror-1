from unittest import defaultTestLoader

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from zope.interface import alsoProvides
from zope.component import getAllUtilitiesRegisteredFor
from plone.browserlayer.interfaces import ILocalBrowserLayerType

from collective.discussionplus.interfaces import IDiscussionPlusLayer

@onsetup
def setup_product():
    import collective.discussionplus
    zcml.load_config('configure.zcml', collective.discussionplus)
    
    # simulates what happens during product setup
    from collective.discussionplus import patches
    patches.apply_patches()

setup_product()
ptc.setupPloneSite(products=['collective.discussionplus'])

class TestSetup(ptc.PloneTestCase):
    
    def test_action_installed(self):
        self.failUnless('review-comments' in self.portal.portal_actions.site_actions.objectIds())

    def test_workflows_installed(self):
        self.failUnless('comment_review_workflow' in self.portal.portal_workflow.objectIds())
        self.assertEquals(('one_state_workflow',),
                self.portal.portal_workflow.getChainForPortalType('Discussion Item'))
    
    def test_browserlayer_installed(self):
        layers = list(getAllUtilitiesRegisteredFor(ILocalBrowserLayerType))
        self.failUnless(IDiscussionPlusLayer in layers)
    
    def test_catalog_installed(self):
        self.failUnless('number_of_comments' in self.portal.portal_catalog.indexes())
        self.failUnless('commentators' in self.portal.portal_catalog.indexes())
        self.failUnless('number_of_comments' in self.portal.portal_catalog.indexes())
        self.failUnless('comment_subject' in self.portal.portal_catalog.schema())
    
    def test_collection_criteria_installed(self):
        try:
            self.portal.portal_atct.getIndex('commentators')
            self.portal.portal_atct.getIndex('number_of_comments')
            self.portal.portal_atct.getMetadata('number_of_comments')
        except AttributeError:
            self.fail()
        
    def test_permission(self):
        self.setRoles(('Reviewer',))
        self.failUnless(self.portal.portal_membership.checkPermission('Review comments', self.folder), self.folder)
        self.setRoles(('Member',))
        self.failIf(self.portal.portal_membership.checkPermission('Review comments', self.folder), self.folder)

class TestIndexingEvents(ptc.PloneTestCase):
    
    def afterSetUp(self):
        self.portal.portal_types['Document'].allow_discussion = True
        self.portal_discussion = self.portal.portal_discussion
    
        self.folder.invokeFactory('Document', 'doc1')
        self.talkback = self.portal_discussion.getDiscussionFor(self.folder.doc1)
    
        self.setRoles(('Reviewer',))
        alsoProvides(self.portal.REQUEST, IDiscussionPlusLayer)
    
    def test_pending(self):
        
        self.portal.portal_workflow.setChainForPortalTypes(('Discussion Item',), 
                                                            ('comment_review_workflow',))
        
        catalog = self.portal.portal_catalog
        
        # Create a reply - it should be pending
        
        reply_id = self.talkback.createReply(title="Comment 1", text="Comment 1", Creator='testuser1')
        reply = self.talkback.getReply(reply_id)
        
        # It should be in the catalog as such
        reply_brain = catalog(getId=reply_id)[0]
        self.assertEquals('Comment 1', reply_brain.Title)
        self.assertEquals('pending', reply_brain.review_state)
        
        # The document should be in the catalog too, with zero published comments
        doc_brain = catalog(getId='doc1')[0]
        self.assertEquals(0, doc_brain.number_of_comments)
        
        # The commentator should have been recorded as well
        self.assertEquals(doc_brain.getPath(), catalog(commentators='testuser1')[0].getPath())
        
        # Now let's publish the comment. The catalog should be updated.
        self.portal.portal_workflow.doActionFor(reply, 'publish')
        reply.reindexObject()
        
        reply_brain = catalog(getId=reply_id)[0]
        self.assertEquals('Comment 1', reply_brain.Title)
        self.assertEquals('published', reply_brain.review_state)
        
        # And the comment count is now 1
        doc_brain = catalog(getId='doc1')[0]
        self.assertEquals(1, doc_brain.number_of_comments)
    
        # Then let's delete the comment. The comment count should now go down to zero.
        self.talkback.deleteReply(reply_id)
        
        doc_brain = catalog(getId='doc1')[0]
        self.assertEquals(0, doc_brain.number_of_comments)
    
        # The last commentator should be deleted
        self.assertEquals(0, len(catalog(commentators='testuser1')))
    
    def test_published(self):
        
        self.portal.portal_workflow.setChainForPortalTypes(('Discussion Item',), 
                                                            ('one_state_workflow',))
        
        catalog = self.portal.portal_catalog
        
        # Create a reply - it should be published
        
        reply_id = self.talkback.createReply(title="Comment 1", text="Comment 1", Creator='testuser1')
        reply = self.talkback.getReply(reply_id)
        
        # It should be in the catalog as such
        reply_brain = catalog(getId=reply_id)[0]
        self.assertEquals('Comment 1', reply_brain.Title)
        self.assertEquals('published', reply_brain.review_state)
        
        # The document should be in the catalog too, with one published comment
        doc_brain = catalog(getId='doc1')[0]
        self.assertEquals(1, doc_brain.number_of_comments)
        
        # The commentator should have been recorded as well
        self.assertEquals(doc_brain.getPath(), catalog(commentators='testuser1')[0].getPath())

        # Then let's delete the comment. The comment count should now go down to zero.
        self.talkback.deleteReply(reply_id)
        
        doc_brain = catalog(getId='doc1')[0]
        self.assertEquals(0, doc_brain.number_of_comments)
    
        # The last commentator should be deleted
        self.assertEquals(0, len(catalog(commentators='testuser1')))
    
    def test_authors(self):
        
        self.portal.portal_workflow.setChainForPortalTypes(('Discussion Item',), 
                                                            ('one_state_workflow',))
        
        catalog = self.portal.portal_catalog
        doc_brain = catalog(getId='doc1')[0]
        
        # Let's create three replies. Two by the same author, and one by another
        
        reply1_id = self.talkback.createReply(title="Comment 1", text="Comment 1", Creator='testuser1')
        reply2_id = self.talkback.createReply(title="Comment 2", text="Comment 2", Creator='testuser2')
        reply3_id = self.talkback.createReply(title="Comment 3", text="Comment 3", Creator='testuser1')
        
        # We can find the item by either author
        self.assertEquals(doc_brain.getPath(), catalog(commentators='testuser1')[0].getPath())
        self.assertEquals(doc_brain.getPath(), catalog(commentators='testuser2')[0].getPath())
        
        # If we delete the comments, the commentators index retains the commentator
        # until the last reply is deleted

        self.talkback.deleteReply(reply1_id)
        self.assertEquals(doc_brain.getPath(), catalog(commentators='testuser1')[0].getPath())
        self.assertEquals(doc_brain.getPath(), catalog(commentators='testuser2')[0].getPath())
        
        self.talkback.deleteReply(reply2_id)
        self.assertEquals(doc_brain.getPath(), catalog(commentators='testuser1')[0].getPath())
        self.assertEquals(0, len(catalog(commentators='testuser2')))
        
        self.talkback.deleteReply(reply3_id)
        self.assertEquals(0, len(catalog(commentators='testuser1')))
        self.assertEquals(0, len(catalog(commentators='testuser2')))
        
class TestCommentOperations(ptc.PloneTestCase):
    
    def afterSetUp(self):
        self.portal.portal_types['Document'].allow_discussion = True
        self.portal.portal_workflow.setChainForPortalTypes(('Discussion Item',), 
                                                            ('comment_review_workflow',))
        
        self.folder.invokeFactory('Document', 'doc1')        
        self.portal_discussion = self.portal.portal_discussion
        
        self.talkback = self.portal_discussion.getDiscussionFor(self.folder.doc1)
        self.reply_id = self.talkback.createReply(title="Comment 1", text="Comment 1")
        self.reply = self.talkback.getReply(self.reply_id)
    
        self.setRoles(('Reviewer',))
        alsoProvides(self.portal.REQUEST, IDiscussionPlusLayer)
    
    def test_delete(self):
        self.portal.REQUEST.form['comment_id'] = self.reply_id
        view = self.reply.restrictedTraverse('@@review-delete-comment')
        view()
        self.failIf(self.reply_id in self.talkback.objectIds())

    def test_publish(self):
        self.portal.REQUEST.form['comment_id'] = self.reply_id
        self.portal.REQUEST.form['action'] = 'publish'
        self.assertEquals('pending', self.portal.portal_workflow.getInfoFor(self.reply, 'review_state'))
        view = self.reply.restrictedTraverse('@@review-publish-comment')
        view()
        self.assertEquals('published', self.portal.portal_workflow.getInfoFor(self.reply, 'review_state'))

def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)