from zope.component import getAdapter
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from Acquisition import aq_inner
from Acquisition import aq_chain

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

from Products.listen.interfaces import IMailingList
from Products.listen.interfaces import IMembershipPendingList
from Products.listen.interfaces import IWriteMembershipList
from Products.listen.lib.browser_utils import encode, obfct_de
from Products.listen.lib.common import lookup_email
from Products.listen.content import archiveOptionsVocabulary

class IListDetailsPortlet(IPortletDataProvider):
    """Portlet that displays details (e.g., addres, title) for a Listen mailing list"""

class Assignment(base.Assignment):
    implements(IListDetailsPortlet)
    
    title = _(u'Mailing list details')

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('list_details.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.ml = None
        for obj in aq_chain(aq_inner(context)):
            if IMailingList.providedBy(obj):
                self.ml = obj
        self.view = view
        mtool = getToolByName(self.context, 'portal_membership')
        mem = mtool.getAuthenticatedMember()
        if mtool.isAnonymousUser():
            self.user_email = None
        else:
            self.user_email = lookup_email(mem.getId(), self.context)

        if self.ml:
            self.mem_list = IWriteMembershipList(self.ml)

    @property
    def available(self):
        # Only show portlet if we've got a mailing list AND we're not on the edit view
        return self.ml and not self.__parent__.__name__ == 'edit'

    def address(self):
        if not self.ml.mailto:
            return u''
        return obfct_de(encode(self.ml.mailto, self.ml))

    def archived(self):
        archived = self.ml.archived
        vocab = archiveOptionsVocabulary(self.ml)
        return vocab.getTerm(archived).token + '. '

    def list_managers(self):
        managers = []
        creator = self.ml.Creator()
        for manager in self.ml.managers:
            markup = obfct_de(encode(manager, self.ml))
            if manager == creator:
                managers.append('%s (creator)' % markup)
            else:
                managers.append(markup)
        return ', '.join(managers)

    def mailinglist(self):
        return self.ml

    def list_title(self):
        return self.ml.Title()

    def list_type(self):
        list_type = self.ml.list_type
        if list_type is None:
            return _(u'List Type not set')
        return '%s. %s' % (list_type.title, list_type.description)

    def description(self):
        return self.ml.Description()

    def can_edit(self):
        mstool = getToolByName(self.context, 'portal_membership')
        return mstool.checkPermission('Listen: Edit mailing list', self.context)

    def subscribe_keyword(self):
        # Mailboxer stores the subject line keyword used for subscribing as
        # a property
        return self.context.getValueFor('subscribe')

    def unsubscribe_keyword(self):
        # Mailboxer stores the subject line keyword used for unsubscribing as
        # a property
        return self.context.getValueFor('unsubscribe')

    def isPending(self):
        sub_mod_pending_list = getAdapter(self.ml,
                                          IMembershipPendingList,
                                          'pending_sub_mod_email')

        return sub_mod_pending_list.is_pending(self.user_email)

    def isSubscribed(self):
        if self.user_email:
            return self.mem_list.is_subscribed(self.user_email)
        else:
            return False

    def manager_email(self):
        if not self.ml.manager_email:
            return u''
        return obfct_de(self.ml.manager_email)

class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
