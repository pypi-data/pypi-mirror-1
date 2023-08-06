from Products.listen.lib.common import lookup_email
from Products.Five import BrowserView
from Products.SecureMailHost.SecureMailHost import EMAIL_RE
from Products.listen.config import MEMBERSHIP_ALLOWED
from Products.listen.config import MEMBERSHIP_DEFERRED
from Products.listen.i18n import _
from Products.listen.interfaces import IUserEmailMembershipPolicy
from Products.listen.interfaces import IUserTTWMembershipPolicy
from Products.listen.interfaces import IWriteMembershipList
from Products.CMFCore.utils import getToolByName
from zope.component import getAdapter

class UpdateSubscription(BrowserView):
    """update the user's subscription status"""

    def __call__(self):
        sub_action = self.request.get('subscribe_member', None)
        unsub_action = self.request.get('unsubscribe_member', None)
        email_action = self.request.get('subscribe_email', None)

        self.mem_list = IWriteMembershipList(self.context)

        mtool = getToolByName(self.context, 'portal_membership')
        mem = mtool.getAuthenticatedMember()
        if mtool.isAnonymousUser():
            self.user_email = None
            self.user_logged_in = False
        else:
            self.user_email = lookup_email(mem.getId(), self.context)
            self.user_logged_in = True

        self.mem_list = IWriteMembershipList(self.context)

        # the appropriate sub_policy needs to be instantiated
        # depending on list type
        self.sub_policy = getAdapter(self.context, IUserTTWMembershipPolicy)

        plone_utils = getToolByName(self.context, 'plone_utils')

        if sub_action:
            self.subscribe()
        elif unsub_action:
            self.unsubscribe()
        elif email_action:
            address = self.request.get('email_address', None)
            if not address:
                plone_utils.addPortalMessage(_('An email address is required'), type='error')
            elif EMAIL_RE.match(address) is None:
                plone_utils.addPortalMessage(_('This email address is invalid'), type='error')
            elif self.mem_list.is_subscribed(address):
                plone_utils.addPortalMessage(_('This email address is already subscribed'), type='error')
            else:
                # everything is OK, send a request mail the
                # appropriate sub_policy needs to be instantiated
                # depending on list type
                sub_policy_for_email = getAdapter(self.context, IUserEmailMembershipPolicy)

                ret = sub_policy_for_email.enforce({'email':address,
                                                    'subject':'subscribe'})
                if ret == MEMBERSHIP_ALLOWED:
                    # make user a subscriber
                    self.mem_list.subscribe(address)
                    plone_utils.addPortalMessage(u'Email subscribed')
                elif ret == MEMBERSHIP_DEFERRED:
                    plone_utils.addPortalMessage(u'Subscription request sent')
                else:
                    plone_utils.addPortalMessage(u'Bad email address')
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        redirect_to = self.request.get('nextURL')
        if redirect_to is not None:
            return redirect_to
        return self.context.absolute_url()

    def subscribe(self):
        req = {'action':'subscribe', 'email':self.user_email}
        if self.user_logged_in:
            req['use_logged_in_user'] = True
        ret = self.sub_policy.enforce(req)

        plone_utils = getToolByName(self.context, 'plone_utils')
                                       
        if ret == MEMBERSHIP_ALLOWED:
            self.mem_list.subscribe(self.user_email)
            plone_utils.addPortalMessage(u'You have been subscribed')
        elif ret == MEMBERSHIP_DEFERRED:
            plone_utils.addPortalMessage(u'Your subscription request is pending '
                                         'moderation by the list manager.')

    def unsubscribe(self):
        plone_utils = getToolByName(self.context, 'plone_utils')
        self.mem_list.unsubscribe(self.user_email)
        plone_utils.addPortalMessage(u'You have been unsubscribed')
