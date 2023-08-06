from AccessControl.interfaces import IRoleManager
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapter
from zope.i18n import translate
from zope.i18nmessageid import Message

from Acquisition import aq_inner
from BTrees.OOBTree import OOBTree

from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.listen.config import PROJECTNAME
from Products.listen.config import MEMBERSHIP_ALLOWED
from Products.listen.config import MEMBERSHIP_DENIED

from Products.listen.content import PendingList

from Products.listen.i18n import _

from Products.listen.interfaces import IMailingList
from Products.listen.interfaces import IManagerTTWMembershipPolicy
from Products.listen.interfaces import IMembershipModeratedList
from Products.listen.interfaces import IMembershipPendingList
from Products.listen.interfaces import IMembershipPolicy
from Products.listen.interfaces import IPostModeratedList
from Products.listen.interfaces import IPostPendingList
from Products.listen.interfaces import ISubscriptionList
from Products.listen.interfaces import IWriteMembershipList

from Products.listen.lib.browser_utils import encode
from Products.listen.lib.browser_utils import obfct_de

from Products.listen.lib.common import assign_local_role
from Products.listen.lib.common import is_email
from Products.listen.lib.common import lookup_member_id
from Products.listen.lib.common import lookup_email
from Products.listen.lib.common import to_email

from Products.listen.lib.default_email_text import user_subscribe_request

from Products.listen.permissions import SubscribeSelf

from Products.SecureMailHost.SecureMailHost import EMAIL_RE

class ManageMembersView(BrowserView):
    """A basic view of displaying subscribed members and allowed senders """

    def __init__(self, context, request):
        super(ManageMembersView, self).__init__(context, request)
        self.policy = getAdapter(context, IManagerTTWMembershipPolicy)
        self.mem_list = IWriteMembershipList(context) # e.g. Products.listen.content.subscriptions.WriteMembershipList
        self.handlers = { 'manage_senders': self.manage_senders,
                          'invite': self.invite_members,
                          'pending_members': self.pending_members}
    
    def __call__(self):

        if not self.request.environ.get('REQUEST_METHOD') == 'POST':
            return self.index()
        
        for handler in self.handlers:
            if self.request.get(handler):
                self.handlers[handler]()

        # since this means that we've been posted to
        # we should redirect
        self.request.response.redirect(self.nextURL())

    ### POST request handlers

    def manage_senders(self):
        form = self.request.form
        self.errors = ''
        to_remove = []
        subscribed_list = set()
        wassubscribed_list = set()
        new_managers = []
        removed_managers = []
        for name, value in form.items():
            if name.lower() == 'save' and value.lower() == 'save changes': continue
            valuetype, name = name.split('_', 1)
            if valuetype == 'remove':
                to_remove.append(name)
            elif valuetype == 'subscribed':
                subscribed_list.add(name)
            elif valuetype == 'wassubscribed':
                wassubscribed_list.add(name)
            elif valuetype == 'position':
                current_position = self.user_position(name).lower()
                new_position = value.lower()
                if new_position != current_position:
                    plone_utils = getToolByName(self.context, 'plone_utils')
                    encoding = plone_utils.getSiteEncoding()
                    name = name.decode(encoding)
                    if new_position == 'manager':
                        new_managers.append(name)
                    else:
                        removed_managers.append(name)

        to_subscribe = subscribed_list - wassubscribed_list
        to_unsubscribe = wassubscribed_list - subscribed_list

        self._remove(to_remove)
        self._subscribe(to_subscribe)
        self._unsubscribe(to_unsubscribe)
        self._add_managers(new_managers)
        self._remove_managers(removed_managers)

        psm = ""

        if to_remove:
            psm += 'Removed: %s.  ' % ', '.join(to_remove)
        if to_subscribe:
            psm += 'Subscribed: %s.  ' % ', '.join(to_subscribe)
        if to_unsubscribe:
            psm += 'Unsubscribed: %s.  ' % ', '.join(to_unsubscribe)
        if new_managers:
            psm += 'Added manager(s): %s. ' % ', '.join(new_managers)
        if removed_managers:
            psm += 'Removed manager(s): %s. ' % ', '.join(removed_managers)

        if psm:
            context = aq_inner(self.context)
            plone_utils = getToolByName(context, 'plone_utils')
            plone_utils.addPortalMessage(psm)


    def invite_members(self):
        form = self.request.form
        CRLF = '\r\n'
        subscribed = True # subscribe members by default (at least for now)
        
        # results for PSMs
        added = []
        errors = []

        to_add = form.get('add_email', None).strip()
        message = form.get('invite-message')
        if to_add:

            # split on commas and newlines
            to_add = [ i.strip() for i in to_add.split(',') if i.strip() ]
            to_add = sum([ [ i.strip() for i in i.split(CRLF) if i.strip() ] for i in to_add ], [])

            for _to_add in to_add:
                if self._add(_to_add, subscribed, message):
                    added.append(_to_add)
                else:
                    errors.append(_to_add)
                
        if added or errors:
            context = aq_inner(self.context)
            plone_utils = getToolByName(context, 'plone_utils')

            if errors:
                plone_utils.addPortalMessage('Bad user or email address: %s' % ', '.join(errors))

            if added:
                plone_utils.addPortalMessage('Added: %s' % ', '.join(added))

    def pending_members(self):

        users = dict([ (user.split('moderate-user-', 1)[-1], status)
                       for user, status in self.request.form.items()
                       if user.startswith('moderate-user-')])
        approved_users = set([user for user, status in users.items()
                              if status == 'approve'])
        denied_users = set(users.keys()).difference(approved_users)

        for user in approved_users:
            self._add(user, subscribed=True)

        self._remove(denied_users)

        plone_utils = getToolByName(self.context, 'plone_utils')
        n_approved, n_denied = len(approved_users), len(denied_users)
        if n_approved:
            plone_utils.addPortalMessage('%s member(s) approved' % n_approved)
        if n_denied:
            plone_utils.addPortalMessage('%s member(s) denied' % n_denied)

    def pending_member_posts(self):
        """Posts from pending members. This will return back a structure that's
           easy to use in the template."""
        pending_list = getAdapter(self.context, IPostPendingList, 'pending_mod_post') 
        retval = []
        for email in pending_list.get_user_emails():
            posts = pending_list.get_posts(email)
            retval.append(dict(email=email, posts=posts))
        retval.sort()
        return retval

    def nextURL(self):
        return '%s/%s' % (self.context.absolute_url(), self.__name__)

    def _add(self, user, subscribed, message=None):
        request = {'action': 'add_allowed_sender', 'email': user}
        policy_result = self.policy.enforce(request)
        if policy_result == MEMBERSHIP_ALLOWED:
            self.mem_list.add_allowed_sender(user)
        elif policy_result == MEMBERSHIP_DENIED:
            return False

        if subscribed:
            request = {'action': 'subscribe', 
                       'email': user,
                       'body': message}

            if self.policy.enforce(request) == MEMBERSHIP_ALLOWED:
                self.mem_list.subscribe(user)
        return True

    def _remove(self, remove_list):
        for user in remove_list:
            if self.mem_list.is_subscribed(user):
                request = {'action': 'unsubscribe', 'email':user}
            else:
                request = {'action': 'remove_allowed_sender', 'email':user}
                
            if self.policy.enforce(request) == MEMBERSHIP_ALLOWED:
                pending_list = getAdapter(self.context, IPostPendingList, 'pending_mod_post') 
                pending_list.remove(user)


    def _subscribe(self, add_list):
        for user in add_list:
            request = {'action': 'subscribe', 'email': user}
            policy_result = self.policy.enforce(request)
            if policy_result == MEMBERSHIP_ALLOWED:
                self.mem_list.subscribe(user)

    def _unsubscribe(self, remove_list):
        for user in remove_list:
            request = {'action': 'unsubscribe', 'email': user}
            if self.policy.enforce(request) == MEMBERSHIP_ALLOWED:
                self.mem_list.unsubscribe(user)

    def _assign_manager_role(self):
        """we need to make sure to assign user ids to management roles, and not
           email addresses"""
        user_ids = [lookup_member_id(m, None) for m in self.context.managers]
        user_ids = filter(None, user_ids)
        assign_local_role('Owner', user_ids, self.context)

    def _add_managers(self, add_list):
        self.context.managers += tuple(add_list)
        self._assign_manager_role()

    def _remove_managers(self, remove_list):
        ml = self.context
        ml.managers = tuple([m for m in ml.managers
                             if m not in remove_list])
        self._assign_manager_role()
        
    def Title(self):
        return _(u'Manage Allowed Senders')

    def Description(self):
        return _(u'Manage Allowed Senders')

    ### front-end functions to be accessed in the page template

    def allowed_senders_data(self):
        return self.mem_list.allowed_senders_data

    def is_subscribed(self, user):
        return self.mem_list.is_subscribed(user)

    def is_email(self, user):
        return is_email(user)
    
    def is_manager(self, user):
        return user in self.context.managers

    def is_moderated(self):
        """returns if the list is post-moderated"""
        return IPostModeratedList.providedBy(self.mem_list.context)

    def is_member_moderated(self):
        """returns if the list is member-moderated"""
        return IMembershipModeratedList.providedBy(self.mem_list.context)
    
    def lookup_email(self, user):
        return lookup_email(user, self.context)

    def user_subscribe_request(self):
        """
        returns the text of the default user_subscribe_request email
        in a form useful to this view
        """

        mapping = { 'listname': self.context.title,
                    'listmanager': self.context.manager_email }
        return translate(Message(user_subscribe_request, 
                                 mapping=mapping))

    def can_manage_membership(self):
        mstool = getToolByName(self.context, 'portal_membership')
        return mstool.checkPermission('Listen: Manage subscriptions', self.context)

    def user_position(self, user):
        return (user in self.context.managers
                and u"Manager"
                or u"Member")

    def show_position_menu(self, user):
        mstool = getToolByName(self.context, 'portal_membership')
        current_mem = mstool.getAuthenticatedMember().getId()
        return not is_email(user) and self.can_manage_membership() \
            and user != current_mem


    def pending_status(self, user):
        annot = IAnnotations(self.context)
        listen_annot = annot.setdefault(PROJECTNAME, OOBTree())

        subscribe_pending_list = getAdapter(self.context, IMembershipPendingList, 'pending_sub_email')
        unsubscribe_pending_list = getAdapter(self.context, IMembershipPendingList, 'pending_unsub_email')
        sub_mod_pending_list = getAdapter(self.context, IMembershipPendingList, 'pending_sub_mod_email')

        email_address = is_email(user) and user or lookup_email(user, self.context)

        inlist = lambda lst: lst.is_pending(email_address)
        status = lambda msg, lst: msg + lst.get_pending_time(email_address)

        status_msg = ''
        if inlist(subscribe_pending_list):
            status_msg += status('subscription pending user confirmation: ', subscribe_pending_list)
        if inlist(unsubscribe_pending_list):
            status_msg += status('unsubscription pending user confirmation: ', unsubscribe_pending_list)
        if inlist(sub_mod_pending_list):
            status_msg += status('subscription pending manager moderation: ', sub_mod_pending_list)

        return status_msg

    def obfct_de(self, value):
        return obfct_de(value)
