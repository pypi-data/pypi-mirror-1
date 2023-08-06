from AccessControl.interfaces import IRoleManager

from Products.CMFCore.utils import getToolByName

from Products.listen.content import ListTypeChanged
from Products.listen.content.mailinglist import archiveOptionsVocabulary
from Products.listen.interfaces import IListLookup
from Products.listen.lib.common import assign_local_role
from Products.listen.lib.is_email import is_email

from kss.core import kssaction
from plone.app.kss.plonekssview import PloneKSSView

from zope.app.component.hooks import setSite
from zope.component import getUtility
from zope.event import notify
from zope.schema.interfaces import IVocabularyFactory
import zope.lifecycleevent

class MailingListEditView(PloneKSSView):
    """View for editting mailing list properties"""

    def __init__(self, context, request):
        super(MailingListEditView, self).__init__(context, request)
        self.handlers = { 'edit': self.edit,
                          'archive': self.archive,
                          'security': self.security }
        self.form_errors = {'title': None, 'mailto': None}

    def __call__(self):
        
        if not self.request.environ.get('REQUEST_METHOD') == 'POST':
            return self.index()

        for handler in self.handlers:
            if self.request.get(handler):
                self.handlers[handler]()

        # since this means that we've been posted to
        # we should redirect (unless we have errors)
        if self.has_form_errors:
            return self.index()
        else:
            self.request.response.redirect(self.nextURL())


    def nextURL(self):
        return self.context.absolute_url()


    ### POST request handlers

    def edit(self):
        """handle POST to edit list preferences"""
        ml = self.context
        plone_utils = getToolByName(ml, 'plone_utils')
        encoding = plone_utils.getSiteEncoding()
        form = self.request.form
        changes = []

        if form.has_key('title'):
            title = form['title']
            error_msg = self._validate_list_title(title)
            if error_msg is None:
                if title != ml.title:
                    changes.append("title")
                    ml.setTitle(title)
            else:
                self.form_errors['title'] = error_msg

        if form.has_key('description'):
            desc = form['description'].decode(encoding)
            if desc != ml.description:
                changes.append("description")
                ml.description = desc

        if form.has_key('mailto'):
            mailto = form['mailto']
            error_msg = self._validate_list_address(mailto)
            if error_msg is None:
                if mailto != ml.mailto:
                    changes.append("address")
                    ml.mailto = mailto
            else:
                self.form_errors['mailto'] = error_msg

        if changes:
            self._assign_local_roles_to_managers()
            notify(zope.lifecycleevent.ObjectModifiedEvent(ml))
            if len(changes) == 1:
                msg = "Updated list %s." % changes[0]
            else:
                msg = "Updated list %s and %s." % (", ".join(changes[:-1]), changes[-1])
            plone_utils.addPortalMessage(msg)


    def archive(self):
        """handle POST to change list archive type"""
        ml = self.context
        plone_utils = getToolByName(ml, 'plone_utils')

        try:
            new_archive_pref = int(self.request.form['archived']) - 1
        except ValueError:
            new_archive_pref = ml.archived
            plone_utils.addPortalMessage("Invalid archive option", type='error')

        if new_archive_pref != ml.archived:
            ml.archived = new_archive_pref
            notify(zope.lifecycleevent.ObjectModifiedEvent(ml))
            plone_utils.addPortalMessage("Updated list archive settings.")
            

    def security(self):
        """handle POST to change list security type"""
        ml = self.context
        type_name = self.request.form['form.list_type']
        new_list_type = self.get_list_type(type_name)
        old_list_marker = ml.list_type.list_marker
        if new_list_type.list_marker != old_list_marker:
            plone_utils = getToolByName(ml, 'plone_utils')
            plone_utils.addPortalMessage('Changed list type from %s to %s.' % (ml.list_type.title, new_list_type.title))
            ml._set_list_type(new_list_type)
            notify(zope.lifecycleevent.ObjectModifiedEvent(ml))
            notify(ListTypeChanged(ml, old_list_marker, new_list_type.list_marker))


    ### KSS form validation actions
    @kssaction
    def validate_title(self, title):
        corekss = self.getCommandSet('core')
        title_div = corekss.getHtmlIdSelector('title-div')
        error_box = corekss.getCssSelector('#title-div .fieldErrorBox')

        error_msg = self._validate_list_title(title)
        if error_msg:
            classes = "field error"
        else:
            classes = "field"
        
        corekss.replaceHTML(error_box, "<div class='fieldErrorBox'>%s</div>" % error_msg) 
        corekss.setAttribute(title_div, 'class', classes)


    @kssaction
    def validate_mailto(self, mailto):
        corekss = self.getCommandSet('core')
        mailto_div = corekss.getHtmlIdSelector('mailto-div')
        error_box = corekss.getCssSelector('#mailto-div .fieldErrorBox')
        error_msg = self._validate_list_address(mailto)
        if error_msg:
            classes = "field error"
        else:
            classes = "field"
        
        corekss.replaceHTML(error_box, "<div class='fieldErrorBox'>%s</div>" % error_msg) 
        corekss.setAttribute(mailto_div, 'class', classes)
                
    ### local utility methods
    
    def has_form_errors(self):
        for error in self.form_errors.values():
            if error is not None:
                return True
        return False

    def _validate_list_title(self, title):
        if title == '':
            return "Please enter a list title."
    
    def _validate_list_address(self, mailto):
        # For some reason this wasn't set, causing getListForAddress() to die below
        setSite(self.context)
        list_for_addr = getUtility(IListLookup).getListForAddress(mailto)
        if mailto == '':
            return "Please enter an address for the list."
        elif not is_email(mailto):
            return "This list address is invalid."
        elif list_for_addr is not None and list_for_addr != self.context:
            return "This list address is already in use."
        else:
            return None

    def get_list_type(self, type_name):
        """Takes the human-readable list type and returns the list type object"""
        for x in self.list_type_options():
            if x.title == type_name:
                return x

    def _assign_local_roles_to_managers(self):
        ml = self.context
        assign_local_role('Owner', ml.managers, IRoleManager(ml))

    def list_type_options(self):
        vf = getUtility(IVocabularyFactory, 'List Types')
        list_types = vf(self.context)
        return [list_type.value for list_type in list_types]

    def archive_options(self):
        options = archiveOptionsVocabulary(self.context)
        options = dict([(option, value.token) 
                        for option, value in options.by_value.items()])
        return [options[option] for option in sorted(options)]
