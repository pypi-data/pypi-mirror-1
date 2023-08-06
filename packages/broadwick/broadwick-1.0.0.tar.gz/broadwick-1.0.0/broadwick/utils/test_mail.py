"""In order to run these unit tests you need to set these environment variables:
    SMTP_SERVER
    SMTP_USER
    SMTP_PASSWORD
    SMTP_FROM
    SMTP_TO
"""
import os
# assert 'SMTP_SERVER' in os.environ
# assert 'SMTP_USER' in os.environ
# assert 'SMTP_PASSWORD' in os.environ
# assert 'SMTP_FROM' in os.environ
# assert 'SMTP_TO' in os.environ

from twisted.trial import unittest
from twisted.internet import reactor, defer

from broadwick.utils.mail import sendmail, sendmail_twisted, Emailer

FROM = '%s <%s>' % (os.path.basename(__file__), os.environ['SMTP_FROM'])
TO = os.environ['SMTP_TO'].split(',')

WAIT = 1

class StdEmailTests(object):
    def tearDown(self):
        """Wait for TCP connections to terminate"""
        d = defer.Deferred()
        reactor.callLater(WAIT, d.callback, None)
        return d

    def test_email_simple(self):
        return self.emailer.send(
                'This is a test', 
                'blah blah blah\n\nRegards,\n\nJon.',
                TO,
                )

    def test_email_html(self):
        return self.emailer.send(
                'This is a test', 
                '<html><body><h1>blah blah blah</h1>\n\nRegards,\n\nJon.</body></html>',
                TO,
                body_content_type = 'text/html'
                )

    def test_email_attachment(self):
        return self.emailer.send(
                'This is a test', 
                '<html><body><h1>blah blah blah</h1>\n\nRegards,\n\nJon.</body></html>',
                TO,
                body_content_type = 'text/html',
                attachments = [self.emailer.fileAttachment(__file__)]
                )


class TestEmailer(unittest.TestCase, StdEmailTests):
    def setUp(self):
        self.emailer = Emailer(os.environ['SMTP_SERVER'], 
                               FROM)   

    tearDown = StdEmailTests.tearDown

class TestAuthEmailer(unittest.TestCase, StdEmailTests):
    def setUp(self):
        self.emailer = Emailer(os.environ['SMTP_SERVER'], 
                               FROM,
                               username=os.environ['SMTP_USER'],
                               password=os.environ['SMTP_PASSWORD']
                               )
    tearDown = StdEmailTests.tearDown

class SendmailTests:
    def test_simple(self):
        return self.sendmail(TO, 'yada yada yada', 'bing bang bong', FROM)

class TestSendmail(unittest.TestCase, SendmailTests):
    def sendmail(self, *args, **kwargs):
        sendmail(*args, **kwargs)

class TestSendmailTwisted(unittest.TestCase, SendmailTests):
    def tearDown(self):
        d = defer.Deferred()
        reactor.callLater(WAIT, d.callback, None)
        return d

    def sendmail(self, *args, **kwargs):
        return sendmail_twisted(*args, **kwargs)
    

