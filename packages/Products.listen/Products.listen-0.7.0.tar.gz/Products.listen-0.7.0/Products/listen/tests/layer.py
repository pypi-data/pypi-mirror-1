from Products.MailHost.interfaces import IMailHost
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase import layer
from Testing import ZopeTestCase
from utils import MockMailHost
import Products.listen.content.mailinglist
import transaction

ZopeTestCase.installProduct('ManagableIndex')
ZopeTestCase.installProduct('listen')


class ListenLayer(layer.PloneSite, layer.ZCML):
    ptc.setupPloneSite(products=('Products.listen',))
    orig_maildrop = Products.listen.content.mailinglist.MaildropHostIsAvailable

    @classmethod
    def setUp(cls):
        app = ZopeTestCase.app()
        from Products.Five import zcml
        import Products.listen
        zcml.load_config('profiles.zcml', Products.listen)
        zcml.load_config('configure.zcml', Products.listen)

        portal = app.plone

        # kill chickens to get our mailhost mock used
        portal._delObject('MailHost')
        mailhost = MockMailHost('MailHost')
        portal.MailHost = mailhost
        Products.listen.content.mailinglist.MaildropHostIsAvailable = True
        sm = portal.getSiteManager()
        sm.registerUtility(mailhost, IMailHost)
        transaction.commit()

    @classmethod
    def tearDown(cls):
        Products.listen.content.mailinglist.MaildropHostIsAvailable = cls.orig_maildrop


class LastLayer(ListenLayer):
    """This layer doesn't do anything, it's only here to force tests
    which explicitly tear down the entire component registry to be run
    after everything else."""
    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        raise NotImplementedError
