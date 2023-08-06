from Acquisition import Implicit
import email

class MockMailHost(Implicit):
    meta_type = 'Maildrop Host'

    def __init__(self, name):
        self.messages = []
        self.name = name

    def send(self, msg, mto=None, mfrom=None, subject=None):
        if (mto is None) or (mfrom is None) or (subject is None):
            # support headers embedded in message text
            if type(msg) == unicode:
                msg = msg.encode('utf-8')
            msgob = email.message_from_string(msg)
            msg = msgob.get_payload()
            mto = mto or msgob.get('to')
            mfrom = mfrom or msgob.get('from')
            subject = subject or msgob.get('subject')
            if isinstance(mto, basestring):
                mto = [addy.strip() for addy in mto.split(',')]
        msg = {'msg': msg,
               'mto': mto,
               'mfrom': mfrom,
               'subject': subject,
               }
        self.messages.append(msg)

    secureSend = send

    def _send(self, mfrom, mto, msg):
        return self.send(msg, mto, mfrom)
