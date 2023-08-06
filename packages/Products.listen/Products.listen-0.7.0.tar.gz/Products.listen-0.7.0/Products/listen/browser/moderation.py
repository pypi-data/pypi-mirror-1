from plone.mail import decode_header

from zope.component import getAdapter
from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from BTrees.OOBTree import OOBTree

from Products.listen.interfaces import IEmailPostPolicy
from Products.listen.interfaces import IMembershipModeratedList
from Products.listen.interfaces import IMembershipPendingList
from Products.listen.interfaces import IMembershipPolicy
from Products.listen.interfaces import IPostModeratedList
from Products.listen.interfaces import IPostPendingList
from Products.listen.interfaces import IPostPolicy
from Products.listen.interfaces import IUserEmailMembershipPolicy
from Products.listen.interfaces import IWriteMembershipList

from Products.listen.content import PendingList

from Products.listen.i18n import _

from Products.listen.config import PROJECTNAME
from Products.listen.config import MODERATION_FAILED

class ModerationView(BrowserView):
    """A view for moderating things """

    def __init__(self, context, request):
        super(ModerationView, self).__init__(context, request)
        self.mem_list = IWriteMembershipList(context)
        annot = IAnnotations(self.context)
        self.listen_annot = annot.setdefault(PROJECTNAME, OOBTree())
        self.mod_post_pending_list = getAdapter(context, IPostPendingList, 'pending_mod_post')
        self.pmod_post_pending_list = getAdapter(context, IPostPendingList, 'pending_pmod_post')
        self.sub_pending_list = getAdapter(context, IMembershipPendingList, 'pending_sub_mod_email')

    def __call__(self):
        form = self.request.form
        post = email = None
        action = ''
        postid = None
        reject_reason = ''
        plone_utils = getToolByName(self.context, 'plone_utils')

        # XXX moderation currently responds to GET requests....is this okay or a HORRIBLE IDEA?

        # first check if mass moderating all posts
        if form.get('discard_all_posts', False):
            action = 'discard'
            policy = getAdapter(self.context, IEmailPostPolicy)
            for post in self.get_pending_lists():
                postid = post['postid']
                email = post['user']
                req = dict(action=action, email=email, postid=postid)
                policy_result = policy.enforce(req)
                if policy_result == MODERATION_FAILED:
                    plone_utils.addPortalMessage(_(u'Could not moderate!'),
                                                 type='error')
                    break
                else:
                    plone_utils.addPortalMessage(_(u'All posts discarded.'),
                                                 type='info')
            self.request.response.redirect(self.nextURL())
            return 

        # users and posts to be moderated
        users = [ user.split('moderate-user-', 1)[-1] 
                  for user in form
                  if user.startswith('moderate-user-') ]
        posts = [ post.split('moderate-post-', 1)[-1].rsplit('-', 1) + [ action ]
                  for post, action in form.items()
                  if post.startswith('moderate-post-') ]
        approved_users = [ user for user in users
                           if form['moderate-user-' + user] == 'approve']
        denied_users = [ user for user in users
                           if form['moderate-user-' + user] == 'deny']

        # sort posts into users and whether approved or denied
        approved_posts = {}
        denied_posts = {}
        _posts = { 'approve': approved_posts, 'deny': denied_posts }
        for email, postid, action in posts:
            _posts[action].setdefault(email, set()).add(int(postid))

        # TODO: decide whether selecting user or selecting posts trumps in case of both selected

        # moderate posts
        if _posts['deny'] or _posts['approve']:
            policy = getAdapter(self.context, IEmailPostPolicy)
            for action, posts_dict in _posts.items():
                for email, posts in posts_dict.items():
                    for postid in posts:
                        req = dict(action=action, email=email, postid=postid)
                        policy_result = policy.enforce(req)
                        if policy_result == MODERATION_FAILED:
                            plone_utils.addPortalMessage(_(u'Could not moderate!'),
                                                         type='error')
                        else:
                            plone_utils.addPortalMessage(_(u'Post moderated.'),
                                                         type='info')
            self.request.response.redirect(self.nextURL())
            return

        return self.index()

    def nextURL(self):
        return '%s/%s' % (self.context.absolute_url(), self.__name__)

    ### methods for pending posts

    def _get_pending_list(self, pending_list):
        # XXX does this funtion need to exist?  can you just use pending_list directly?

        list_out = {}
        for user_email in pending_list.get_user_emails():
            posts = pending_list.get_posts(user_email)
            list_out[user_email] = []
            for post in posts:
                header = post['header']
                body = post['body']
                subject = decode_header(header.get('subject', 'No Subject'))
                postid = post['postid']
                list_out[user_email].append(dict(subject=subject, body=body, postid=postid)) 

        return list_out

    def get_pending_lists(self):
        """what is this supposed to do???"""
        # XXX e.g. what is mod_posts and pmod_posts?
        mod_posts = self.get_pending_mod_post_list()
        pmod_posts = self.get_pending_pmod_post_list()
        lists = mod_posts
        for key, value in pmod_posts.items():
            lists.setdefault(key, []).extend(value)
        lists = dict([(key, value) for key, value in lists.items() if value])
        return lists

    def get_pending_pmod_post_list(self):
        return self._get_pending_list(self.pmod_post_pending_list)

    def get_pending_mod_post_list(self):
        return self._get_pending_list(self.mod_post_pending_list)

    ### functions that are probably for DublinCore but I'm just guessing bc no one commented what they're actually for

    def Title(self): # XXX awful
        return 'Moderate Things'

    def Description(self): # XXX awful -- are these for something silly like DublinCore?
        return 'Moderate Things'

    ### front-end functions

    def is_post_moderated(self):
        return IPostModeratedList.providedBy(self.context)

    def is_membership_moderated(self):
        return IMembershipModeratedList.providedBy(self.context)

    def user_name(self, email):
        # XXX not sure if this is canonical
        return self.pmod_post_pending_list.get_user_name(email)
