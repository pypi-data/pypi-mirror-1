#
# Authors: Brian Skahan <bskahan@etria.com>
#          Tom von Schwerdtner <tvon@etria.com>
#
# Copyright 2004-2005, Etria, LLP
# # This file is part of Quills
#
# Quills is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Quills is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Quills; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###############################################################################

# Zope imports
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from DateTime.DateTime import DateTime

# Plone imports
from Products.CMFCore.utils import getToolByName

# Archetypes imports
from Products.Archetypes.public import BaseSchema
from Products.Archetypes.public import Schema
from Products.Archetypes.public import TextField
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.public import RichWidget
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import registerType

from Products.Archetypes.Marshall import RFC822Marshaller

# Quills imports
from quills.core.interfaces import IWorkflowedWeblogEntry
from quills.app.topic import Topic
from quills.app.topic import AuthorTopic
from quills.app.utilities import QuillsMixin

# Local imports
from config import PROJECTNAME
import permissions as perms


WeblogEntrySchema = BaseSchema.copy() + Schema((

    TextField('description',
        searchable=1,
        accessor="Description",
        widget=TextAreaWidget(
            label='Excerpt',
            description="""A brief introduction for this entry.""",
            label_msgid="label_description",
            description_msgid="help_description",
            i18n_domain="quills"),
        ),

    TextField('text',
        searchable=1,
        default_output_type='text/x-html-safe',
        widget=RichWidget(label='Entry Text',
            rows=30,
            label_msgid="label_text",
            i18n_domain="quills"),
        ),
    ),

    marshall=RFC822Marshaller(),
    )

# Move the subject/topic picking to the main edit view as it should be used
# for every edit, really.
WeblogEntrySchema['subject'].schemata = 'default'
# The subject is not language-specific
WeblogEntrySchema['subject'].languageIndependent = True,
# Make sure it is presented after the main text entry field.
WeblogEntrySchema.moveField('subject', after='text')
# Make sure the allowDiscussion field's default is None
WeblogEntrySchema['allowDiscussion'].default = None
# Put the discussion setting on the main page...
WeblogEntrySchema['allowDiscussion'].schemata = 'default'
# ... at the bottom, after the subject keywords.
WeblogEntrySchema.moveField('allowDiscussion', after='subject')


class WeblogEntry(QuillsMixin, BaseContent):
    """Basic Weblog Entry.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWorkflowedWeblogEntry, WeblogEntry)
    True
    """

    implements(IWorkflowedWeblogEntry)

    schema = WeblogEntrySchema
    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    security.declareProtected(perms.View, 'getTitle')
    def getTitle(self):
        """See IWeblogEntry.
        """
        return self.Title()

    security.declareProtected(perms.View, 'getTopics')
    def getTopics(self):
        """See IWeblogEntry.
        """
        weblog = self.getWeblog()
        keywords = self.Subject()
        return [Topic(kw).__of__(weblog) for kw in keywords]

    security.declareProtected(perms.View, 'getAuthors')
    def getAuthors(self):
        """See IWeblogEntry.
        """
        weblog = self.getWeblog()
        creators = self.Creators()
        return [AuthorTopic(creator).__of__(weblog) for creator in creators]

    security.declareProtected(perms.View, 'getExcerpt')
    def getExcerpt(self):
        """See IWeblogEntry.
        """
        # This is just an alias for Description in this case.
        return self.Description()

    security.declareProtected(perms.EditContent, 'setExcerpt')
    def setExcerpt(self, excerpt):
        """See IWeblogEntry.
        """
        self.setDescription(excerpt)

    security.declareProtected(perms.EditContent, 'setTopics')
    def setTopics(self, topic_ids):
        """See IWeblogEntry.
        """
        self.setSubject(topic_ids)

    def setText(self, text, mimetype=None):
        """docstring for setText"""
        # if no mimetype was specified, we use the default
        if mimetype is None:
            mimetype = self.getMimeType()
        self.text.update(text, self, mimetype=mimetype)

    security.declareProtected(perms.EditContent, 'edit')
    def edit(self, title, excerpt, text, topics, mimetype=None):
        """See IWeblogEntry.
        """
        # if no mimetype was specified, we use the default
        if mimetype is None:
            mimetype = self.getMimeType()
        self.setText(text, mimetype=mimetype)
        self.setTitle(title)
        self.setExcerpt(excerpt)
        if topics:
            self.setTopics(topics)
        else:
            self.setTopics([])
        self.reindexObject()

    security.declareProtected(perms.View, 'getPublicationDate')
    def getPublicationDate(self):
        """See IWeblogEntry.
        """
        return self.getEffectiveDate()
        
    security.declareProtected(perms.View, 'getMimeType')
    def getMimeType(self):
        """See IWeblogEntry.
        """
        # (ATCT handles the mechanics for determining the default for us)
        return self.text.getContentType()
        
    security.declareProtected(perms.EditContent, 'setPublicationDate')
    def setPublicationDate(self, datetime):
        """See IWeblogEntry.
        """
        self.setEffectiveDate(datetime)

    security.declareProtected(perms.EditContent, 'publish')
    def publish(self, pubdate=None):
        """See IWorkflowedWeblogEntry.
        """
        wf_tool = getToolByName(self, 'portal_workflow')
        current_state = wf_tool.getInfoFor(self, "review_state")
        if current_state == "published":
            # do nothing if the entry has already been published
            return
        # XXX Need to be able to handle std library datetime objects for pubdate
        if pubdate is None:
            pubdate = DateTime()
        self.setPublicationDate(pubdate)
        wf_tool.doActionFor(self, 'publish')
        self.reindexObject()

    security.declareProtected(perms.EditContent, 'retract')
    def retract(self):
        """See IWorkflowedWeblogEntry.
        """
        wf_tool = getToolByName(self, 'portal_workflow')
        current_state = wf_tool.getInfoFor(self, "review_state")
        if current_state == "private":
            # do nothing if the entry has already been private
            return
        wf_tool.doActionFor(self, 'retract')
        self.setPublicationDate(None)
        self.reindexObject()

    security.declareProtected(perms.EditContent, 'isPublished')
    def isPublished(self):
        """See IWorkflowedWeblogEntry.
        """
        wf_tool = getToolByName(self, 'portal_workflow')
        review_state = wf_tool.getInfoFor(self, 'review_state')
        if review_state == 'published':
            return True
        return False

    security.declareProtected(perms.View, 'getWeblogEntryContentObject')
    def getWeblogEntryContentObject(self):
        """See IWeblogEntry.
        """
        return self


registerType(WeblogEntry, PROJECTNAME)
