Introduction
============

This package provides some enhancements to Plone's standard commenting
functionality. It attempts to keep as much of the existing commenting
machinery as possible, but adds the following features:

Events:

 * An `IObjectAddedEvent` is fired when a discussion item (described by the
   interface `Products.CMFCore.interfaces.IDiscussionResponse`) is created.
 * Similarly, an `IObjectRemovedEvent` is fired when a discussion item is
   deleted.
 
Indexing:
 
 * Content items gain two additional catalogue indexes: `number_of_comments`,
   which contains the number of comments left on a content item, and
   `commentators`, which contains a list of unique usernames of those who
   have left one or more comments on the content item. `number_of_comments`
   is also available as catalogue metadata.
 * Collections are configured so that it is possible to search by these 
   indexes. For example, the 'Current author' criterion can be used to list
   all content items upon which the current user has left a comment.
 * Discussion items gain an additional catalogue metadata column, 
   `comment_subject`, which contains the title of the content item that was
   commented upon (note that this is not updated if the content item changes
   title).
 
Workflow:
 
 * Discussion items will respect the workflow set in portal_workflow. By
   default, the `one_state_workflow` is used, which means a comment is
   always published. An additional `comment_review_workflow` is installed,
   which has two states: `pending` and `published`. Comments may either be
   published or deleted.
 * A new view, @@review-comments, is available for any folder or the portal
   root. This allows site-wide (or folder-wide) moderation of comments, with
   quick publish/delete operations.
   
Note that the @@review-comments view makes a few assumptions:

 * Comments pending review are always in the `pending` state. You can add
   a `review_state` request parameter to specify a different state to search
   for, however.
 * There is a transition called `publish` to move a comment from `pending` to
   `published`. You can request a different transition by providing a
   request parameter `publish_transition`.

Furthermore:

  * The `number_of_comments` index will only include comments in the
    `published` state.
  * Neither the `portal_catalog` `Clear and rebuild`, nor the 
    `portal_workflow` `Update security settings` operation will correctly
    find and update comments, due to the way that comments are stored.

Requirements
============

This product requires Plone 3.3+ (and will likely not work with Plone 4). In
particular, it relies on `plone.indexer`, which is part of Plone 3.3+.

