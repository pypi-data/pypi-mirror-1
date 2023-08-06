from Acquisition import aq_get
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.MailBoxer.MailBoxer import FALSE
from Products.MailBoxer.MailBoxer import MailBoxer
from Products.MailBoxer.MailBoxer import TRUE
from Products.MailBoxer.MailBoxer import setMailBoxerProperties
from Products.MailBoxer.MailBoxerTools import splitMail
from Products.MailBoxer.messagevalidators import setDefaultValidatorChain
from Products.listen.interfaces import IMailFromString
from Products.listen.interfaces import IMessageHandler
from Products.listen.lib.browser_utils import getSiteEncoding
from Products.listen.lib.common import construct_simple_encoded_message
from email.Header import Header
from plone.mail import decode_header
from zope.app import zapi
from zope.component import queryMultiAdapter
import logging
import re
import rfc822
import zope.event


logger = logging.getLogger('listen.content.mailboxer_list')

# A REGEX for messages containing mail-commands
mail_command_re = re.compile('\(mail-command:([A-Za-z_-]+)',
                             re.IGNORECASE)


class MailBoxerMailingList(MailBoxer):
    """A slightly customized MailBoxer with some less cryptic method names

    Perform some basic test configuration:
        >>> import Products.Five
        >>> from Products.Five import zcml
        >>> zcml.load_config('meta.zcml', Products.Five)
        >>> zcml.load_config('permissions.zcml', Products.Five)
        >>> from Products.listen.content import tests
        >>> zcml.load_config('configure.zcml', tests)
        >>> from Products.Five import site
        >>> zcml.load_config('configure.zcml', site)

    Create a list to play with:
        >>> from Products.listen.content.mailboxer_list import MailBoxerMailingList
        >>> from DateTime import DateTime
        >>> mb = MailBoxerMailingList('mb', 'A mail boxer')
        >>> mb.mailto='list1@example.com'

    Fake the manage_afterAdd, because the catalog needs to be manually added:
        >>> mb.REQUEST = {}
        >>> mb.manage_afterAdd(mb, None)

    Our archive should be empty:
        >>> archive = mb.archive
        >>> date = DateTime()
        >>> archive.objectIds()
        []

    Now let's add a message:
        >>> mail_message = '''To: list1@example.com
        ... From: test1@example.com
        ... Subject: A new Subject
        ... Date: Wed, 5 Mar 2005 12:00:00 -0000
        ...
        ...
        ... A new message.
        ... '''
        >>> message = mb.addMail(mail_message)
        
    Let's try a message with an image embedded in it.
        >>> mail_message2 = '''Mime-Version: 1.0 (Apple Message framework v752.3)
        ... To: test_listen_list@lists.openplans.org
        ... Message-Id: <5A9F4BC4-2B14-41C1-9CB3-9D1803624D45@openplans.org>
        ... Content-Type: multipart/mixed;
        ... 	boundary=Apple-Mail-11-285035055
        ... From: Chris Abraham <cabraham@openplans.org>
        ... Subject: tiny image
        ... Date: Thu, 25 Oct 2007 15:29:59 -0400
        ... 
        ... 
        ... --Apple-Mail-11-285035055
        ... Content-Transfer-Encoding: 7bit
        ... Content-Type: text/plain;
        ... 	charset=US-ASCII;
        ... 	format=flowed
        ... 
        ... this text is before the image.
        ... here's the image:
        ... 
        ... 
        ... --Apple-Mail-11-285035055
        ... Content-Transfer-Encoding: base64
        ... Content-Type: image/gif;
        ... 	x-unix-mode=0644;
        ... 	name=world2.gif
        ... Content-Disposition: inline;
        ... 	filename=world2.gif
        ... 
        ... R0lGODlhFAAWAMIAAP///8z//8zMzJmZmQCZMwBmMwAAAAAAACH+TlRoaXMgYXJ0IGlzIGluIHRo
        ... ZSBwdWJsaWMgZG9tYWluLiBLZXZpbiBIdWdoZXMsIGtldmluaEBlaXQuY29tLCBTZXB0ZW1iZXIg
        ... MTk5NQAh+QQBAAABACwAAAAAFAAWAAADeBi63O4mytciuTjSKIj4HqgxxgViWFcYZNeFqLcu5et6
        ... eDfMQWnasE9hwKrdTiDBrrAy/oA6JtEZfF2GQwsw5BIMd9NUcvzN+j6nFHhZ/HGvzDirl0YTBvjy
        ... nG7L49d7PX5xX0s8NAaFhEwjEAZ+eI0UPRKSk5cMCQA7
        ... 
        ... --Apple-Mail-11-285035055
        ... Content-Transfer-Encoding: 7bit
        ... Content-Type: text/plain;
        ... 	charset=US-ASCII;
        ... 	format=flowed
        ... 
        ... 
        ... this text is after the image.
        ... done.
        ... --Apple-Mail-11-285035055--
        ... '''
        >>> message2 = mb.addMail(mail_message2)
        >>> print message2.body
        this text is before the image.
        here's the image:
        <BLANKLINE>
        <BLANKLINE>
        <BLANKLINE>
        this text is after the image.
        done.
        <BLANKLINE>

    We should have added a folder structure like archive/year/month/message,
    let's check:
        >>> str(date.year()) in archive.objectIds()
        True
        >>> year = getattr(archive, str(date.year()))
        >>> month = date.mm()
        >>> month in year.objectIds()
        True
        >>> month = getattr(year, month)
        >>> message.getId() in month.objectIds()
        True

    Let's inspect our message object:
        >>> print message.body
        <BLANKLINE>
        A new message.
        <BLANKLINE>
        >>> message.from_addr
        u'test1@example.com'
        >>> message.date.earliestTime() == date.earliestTime()
        True

    Ensure our message is actually a conformant IMailMessage:
        >>> from zope.interface.verify import verifyObject
        >>> from Products.listen.interfaces import IMailMessage
        >>> verifyObject(IMailMessage, message)
        True

    Our overridden getValueFor method should return mime encoded utf-8
    strings for any stored unicode strings, or site-encoded ASCII
        >>> mb.headers = 'a string'
        >>> mb.getValueFor('headers')
        'a string'
        >>> mb.headers = u'a string'
        >>> mb.getValueFor('headers')
        'a string'
        >>> mb.headers = 'a string \345\276\267\345\233\275'
        >>> mb.getValueFor('headers')
        '=?utf-8?b?YSBzdHJpbmcg5b635Zu9?='
        >>> mb.headers = u'a string \u5fb7\u56fd'
        >>> mb.getValueFor('headers')
        '=?utf-8?b?YSBzdHJpbmcg5b635Zu9?='

    This also works with lists of strings
        >>> mb.headers = ['a string', 'a string2']
        >>> mb.getValueFor('headers')
        ['a string', 'a string2']
        >>> mb.headers = ['a string', 'a string \345\276\267\345\233\275']
        >>> mb.getValueFor('headers')
        ['a string', '=?utf-8?b?YSBzdHJpbmcg5b635Zu9?=']

    Shouldn't fail on non-strings or lists, lists with non-string values
    are returned intact
        >>> mb.headers = {}
        >>> mb.getValueFor('headers')
        {}
        >>> mb.headers = ({}, 'a string', 'a string \345\276\267\345\233\275')
        >>> mb.getValueFor('headers')[2] == 'a string \345\276\267\345\233\275'
        True

    Messages with special subjects should be routed through an adapter.  Let's
    setup a simple adapter to test that our command message is routed as
    expected:
        >>> from zope.interface import Interface
        >>> from zope.interface import directlyProvides
        >>> from zope.interface import implements
        >>> from zope.component import provideAdapter
        >>> from ZPublisher.HTTPRequest import HTTPRequest
        >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
        >>> from Products.listen.interfaces import IMessageHandler
        >>> class SimpleAdapter(object):
        ...     implements(IMessageHandler)
        ...     def __init__(self, context, request):
        ...         self.context = context
        ...         self.request = request
        ...     def processMail(self):
        ...         self.request.set('processed', True)
        >>> provideAdapter(factory=SimpleAdapter,
        ...                adapts=(Interface, IDefaultBrowserLayer),
        ...                name='simple-command')
        >>> from sys import stdout # We need a legitimate seeming request
        >>> REQUEST = HTTPRequest(stdout, {'SERVER_NAME':'a',
        ...                                'SERVER_PORT': '80',
        ...                                'REQUEST_METHOD': 'GET'}, {})
        >>> directlyProvides(REQUEST, IDefaultBrowserLayer)
        >>> REQUEST['Mail'] = '''To: list1@example.com
        ... From: test1@example.com
        ... Subject: Re: Simple Command (mail-command:simple-command)
        ... Date: Wed, 5 Mar 2005 12:00:00 -0000
        ...
        ...
        ... A new message.
        ... '''
        >>> mb.manage_mailboxer(REQUEST)
        'TRUE'
        >>> REQUEST['processed']
        True

    Putting encoded strings in the subject should not break adaptMail():

        >>> REQUEST = HTTPRequest(stdout, {'SERVER_NAME':'a',
        ...                                'SERVER_PORT': '80',
        ...                                'REQUEST_METHOD': 'GET'}, {})
        >>> directlyProvides(REQUEST, IDefaultBrowserLayer)
        >>> REQUEST['Mail'] = '''To: Pe\xc3\xb1ate <foo@bar.com>
        ... From: Pe\xc3\xb1ate <bat@baz.com>
        ... Subject: Hi from Pe\xc3\xb1ate
        ...
        ...
        ... Hi, this is Pe\xc3\xb1ate'''
        >>> mb.adaptMail(REQUEST)
        False
        >>> # Hack around skins not being set up in this test:
        >>> mb.mail_reply = lambda *args, **kw: None
        >>> mb.manage_mailboxer(REQUEST)
        'TRUE'

    """

    # Mailboxer wants the name of a catalog to acquire
    catalog = 'mail_catalog'

    def manage_mailboxer(self, REQUEST):
        """ Override to allow triggering of pluggable mail handlers
        """
        if self.checkMail(REQUEST):
            return FALSE

        # Check for subscription/unsubscription-request and confirmations
        if self.requestMail(REQUEST):
            return TRUE

        if self.adaptMail(REQUEST):
            return TRUE

        if self.manager_mail(REQUEST):
            return TRUE

        # Process the mail...
        self.processMail(REQUEST)
        return TRUE


    def manager_mail(self, REQUEST):
        # Intended for subclasses to override.
        return False
    
    def adaptMail(self, REQUEST):
        """Adapts an incoming request to a specialized view for handling
        mail if requested."""

        mailString = self.getMailFromRequest(REQUEST)
        (header, body) = splitMail(mailString)

        encoding = getSiteEncoding(self)
        subject = decode_header(str(Header(header.get('subject',''), encoding)))

        command_match = re.search(mail_command_re, subject)
        if command_match:
            command_name = command_match.groups()[0]
            adapter = queryMultiAdapter((self, REQUEST), IMessageHandler,
                                        name=command_name)
            if adapter is not None:
                adapter.processMail()
                return True
        return False

    def sendCommandRequestMail(self, address, subject, body, from_address=None, extra_headers={}):
        if not address: 
            print ('Products.listen.content.MailBoxerMailingList.sendCommandRequestMail() '
                   'invalid address; user may have been deleted')
            return

        if from_address is None:
            from_address = self.mailto

        # Default headers:
        headers = {'X-Mailer': self.getValueFor('xmailer')}
        headers.update(extra_headers)
        encoding = getSiteEncoding(self)
        message = construct_simple_encoded_message(from_addr=from_address,
                                                   to_addr=address,
                                                   subject=subject,
                                                   body=body,
                                                   other_headers=headers,
                                                   encoding=encoding)
            
        # XXX: Acquire the MailHost, yuck
        mh = getToolByName(self, 'MailHost')
        mh.send(str(message))

    def manage_afterAdd(self, item, container, **kw):
        """Setup properties and sub-objects"""
        # Only run on add, not rename, etc.
        if not base_hasattr(self, 'mqueue'):
            setMailBoxerProperties(self, self.REQUEST, kw)
            # Setup the default checkMail validator chain
            setDefaultValidatorChain(self)

            # Add Archive
            archive = zapi.createObject('listen.ArchiveFactory', self.storage,
                                        title=u'List Archive')
            item._setObject(self.storage, archive)

            # Add moderation queue
            mqueue = zapi.createObject('listen.QueueFactory', self.mailqueue,
                                       title=u'Moderation queue')
            item._setObject(self.mailqueue, mqueue)

            ttool = getToolByName(self, 'portal_types', None)
            if ttool is not None:
                # If the archive/queue are CMF types then we must finish
                # constructing them.
                fti = ttool.getTypeInfo(mqueue)
                if fti is not None:
                    fti._finishConstruction(mqueue)
                fti = ttool.getTypeInfo(archive)
                if fti is not None:
                    fti._finishConstruction(archive)
        MailBoxer.manage_afterAdd(self, self.REQUEST, kw)

    # modified manage_addMail from MailBoxer.py to make things more modular
    def addMail(self, mailString):
        """ Store mail in date based folder archive.
            Returns created mail.  See IMailingList interface.
        """
        archive = aq_get(self, self.getValueFor('storage'), None)

        # no archive available? then return immediately
        if archive is None:
            return None

        (header, body) = splitMail(mailString)

        # if 'keepdate' is set, get date from mail,
        if self.getValueFor('keepdate'):
            timetuple = rfc822.parsedate_tz(header.get('date'))
            time = DateTime(rfc822.mktime_tz(timetuple))
        # ... take our own date, clients are always lying!
        else:
            time = DateTime()

        # now let's create the date-path (yyyy/mm)
        year  = str(time.year()) # yyyy
        month = str(time.mm())   # mm
        title = "%s %s"%(time.Month(), year)

        # do we have a year folder already?
        if not base_hasattr(archive, year):
            self.addMailBoxerFolder(archive, year, year, btree=False)
        yearFolder=getattr(archive, year)

        # do we have a month folder already?
        if not base_hasattr(yearFolder, month):
            self.addMailBoxerFolder(yearFolder, month, title)
        mailFolder=getattr(yearFolder, month)

        subject = header.get('subject', 'No Subject')
        sender = header.get('from','Unknown')

        # search a free id for the mailobject
        id = time.millis()
        while base_hasattr(mailFolder, str(id)):
             id = id + 1
        id = str(id)

        self.addMailBoxerMail(mailFolder, id, sender, subject, time,
                                                                   mailString)
        mailObject = getattr(mailFolder, id)

        return mailObject

    # Override the original MailBoxer method
    manage_addMail = addMail

    # Componentize folder creation
    def addMailBoxerFolder(self, context, id, title, btree=True):
        """ Adds an archive-folder using a configured factory
        """
        folder = zapi.createObject('listen.FolderFactory',
                                   id, title, btree=btree)
        context._setObject(id, folder)

    # Componentize mail creation
    def addMailBoxerMail(self, folder, id, sender, subject, date, mail):
        # Strip out the list name from the subject, as it serves no purpose
        # in the archive.
        subject = subject.replace('[%s]' % self.getValueFor('title'), '')

        new_message = zapi.createObject('listen.MailFactory',
                                        id, sender, subject, date)
        folder._setObject(id, new_message)
        msg = getattr(folder, id)
        # Adapt message to provide methods for parsing mail and extracting
        # headers
        settable_msg = IMailFromString(msg)
        # This is ugly, but it is the MailBoxer way, last option means no
        # attachments.
        store_attachments = self.archived == 0
        # Set properties on message
        settable_msg.createMailFromMessage(mail, store_attachments)
        zope.event.notify(
            zope.app.event.objectevent.ObjectModifiedEvent(msg))
        
        return msg

    # For now use the builtin methods
    resetBounces = MailBoxer.manage_resetBounces
    moderateMail = MailBoxer.manage_moderateMail

    # Override getValueFor to always return ASCII encoded strings, as they
    # may be included in an email header or body.  We use 7-bit encoded
    # in the site encoding if the string won't convert to ascii.
    # Our mailing list title, and email addresses may be unicode, this will
    # convert them
    def getValueFor(self, key):
        # value = MailBoxer.getValueFor(self, key)
        # Simplify: we have no need for all the strange 'getter' magic that
        # MailBoxer does
        value = self.getProperty(key)
        encoding = getSiteEncoding(self)
        try:
            if hasattr(value, 'encode'):
                value = self._encodedHeader(value, encoding)
            elif isinstance(value, list) or isinstance(value, tuple):
                value = [self._encodedHeader(v, encoding) for v in value]
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Just in case one of our 'utf-8' encoding attempts fails, we
            # give up
            pass
        except AttributeError:
            # No 'encode' method on a list element, so give up
            pass
        return value

    @staticmethod
    def _encodedHeader(value, encoding):
        """
        Given a value (or list of values) and an ecoding, return it
        encoded as per rfc2047 for use in a MIME message header.

        >>> from Products.listen.content.mailboxer_list import MailBoxerMailingList

        If the input can be converted to ascii, it will be, regardless
        of the encoding argument:

        >>> MailBoxerMailingList._encodedHeader('blah', 'utf8')
        'blah'

        If it can be encoded to the target encoding, it will be, and
        then encoded as per rfc2047:

        >>> input = u'\xbfhmm?'
        >>> MailBoxerMailingList._encodedHeader(input, 'utf8')
        '=?utf8?b?wr9obW0/?='
        >>> MailBoxerMailingList._encodedHeader(input.encode('utf8'), 'utf8')
        '=?utf8?b?wr9obW0/?='
        >>> raw = 'a string \345\276\267\345\233\275'
        >>> MailBoxerMailingList._encodedHeader(raw, 'utf8')
        '=?utf8?b?YSBzdHJpbmcg5b635Zu9?='

        All other cases will raise an exception. Typically this means
        a raw byte string in an incompatible encoding:

        >>> MailBoxerMailingList._encodedHeader(input.encode('latin1'), 'utf8')
        Traceback (most recent call last):
        ...
        UnicodeDecodeError: 'utf8' codec can't decode byte 0xbf in position 0: unexpected code byte
        """
        try:
            value = value.encode('ascii')
        except (UnicodeEncodeError, UnicodeDecodeError):
            try:
                value = Header(value.encode(encoding), encoding).encode()
            except UnicodeDecodeError:
                try:
                    value = Header(value, encoding).encode()
                except UnicodeDecodeError:
                    logger.error("Could not guess encoding of raw bytestring %r, there is probably a bug in the code that created this header." % value)
                    raise
        return value
