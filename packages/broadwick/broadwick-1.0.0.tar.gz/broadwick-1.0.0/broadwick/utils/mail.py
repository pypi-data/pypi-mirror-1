import logging
import smtplib
from StringIO import StringIO
import MimeWriter
import mimetypes
import base64
import os
import re

try:
    from twisted.mail import smtp
    from twisted.internet import reactor, defer
except ImportError:
    pass

from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email import Encoders

def sendmail(to, subject, message, email_from, cc = [], bcc = [], 
             content_type = 'text/plain', attach = [], 
             mail_server = None, username = None, password = None):
    """Send an email to a list of recipients. This is a blocking send.

       to, cc and bcc are lists (or tuples) email addresses
       attach is None or [(file, name) ...]
            where file is a string giving the filename or a file-like object

    """
    mail_server = _mail_server(mail_server)

    if not (to + cc + bcc):
        raise ValueError("Email request with subject '%s' has no recipients!" % subject)

    s = None

    try:
        try:
            s = smtplib.SMTP(mail_server)
            s.ehlo()
            #s.esmtp_features["auth"] = ["PLAIN", "LOGIN"]
            #print ("SMTP extended: %s " % s.esmtp_features)

            if username is not None:
                s.login(username, password)
            msg = StringIO()
            writer = MimeWriter.MimeWriter(msg)
            writer.addheader('From', email_from)
            writer.addheader('To', ', '.join(to))
            writer.addheader('Cc', ', '.join(cc))
            writer.addheader('Subject',  subject)
            writer.startmultipartbody('mixed')

            body_part = writer.nextpart()
            body = body_part.startbody(content_type)
            body.write(message)

            if attach:
                for path_to_file, name_of_attachment in attach:
                    attach_part = writer.nextpart()
                    attach_part.addheader('Content-Transfer-Encoding', 'base64')
                    attach_part.addheader('Content-Disposition', 'attachment; filename=' + name_of_attachment)
                    if isinstance(path_to_file, (str, unicode)):
                        f = open(path_to_file, 'rb')
                    else:
                        f = path_to_file
                    try:
                        base64.encode(f, attach_part.startbody('text/plain'))
                    finally:
                        f.close()

            all_recips = to + cc + bcc

            if all_recips:
                logging.info('Sending email to %s, subject: %s' % (all_recips, subject))
                s.sendmail(email_from, all_recips, msg.getvalue())
            else:
                logging.error("Email request with subject '%s' has no recipients!" % subject)

        except smtplib.SMTPServerDisconnected, e:
            logging.error('Email gateway disconnected: %s\n' % e)
            raise 
    finally:
        if s:
            s.quit()

def sendmail_twisted(
             to, subject, message, email_from, cc = [], bcc = [], 
             content_type = 'text/plain', attach = [], 
             mail_server = None, username = None, password = None):
    """Like sendmail but is asyncrhonous. Returns a deferred"""

    mail_server = _mail_server(mail_server)
    if not (to + cc + bcc):
        raise ValueError("Email request with subject '%s' has no recipients!" % subject)

    logging.info('Sending async email to %s, subject: %s' % (to + cc + bcc, subject))
    e = Emailer(mail_server, email_from, username=username, password=password)
    attachments = []
    for path, name in attach:
        attachments.append(e.fileAttachment(path, None, name))

    def success(result):
        logging.debug('Mail with subject %r sent OK' % (subject, ))
        return result

    def failure(result, *rest):
        logging.error('Mail to %r with subject %r failed: %s' % (to, subject, result))
        return result # pass the error on

    return e.send(subject, message, to, cc, bcc, content_type, attachments)\
            .addCallback(success)\
            .addErrback(failure)

def sendmail_auto(*args, **kwargs):
    """Send mail using twisted if the reactor is up, otherwise use blocking send"""
    if reactor.running:
        return sendmail_twisted(*args, **kwargs)
    else:
        return sendmail(*args, **kwargs)

#############################################################################
# Twisted emailing helper.
# Helper functions above are easier for most use cases but not as flexible

class Emailer(object):
    def __init__(self, smtpHost, smtpSender, 
                 senderDomainName=None, port=25, 
                 username=None, password=None
                 ):
        self.smtpHost = smtpHost
        self.smtpSender = smtpSender
        self.username = username
        self.password = password

        r = re.search('<(.*)>', self.smtpSender)
        if r:
            self.smtpSenderAddress = r.group(1)
        else:
            self.smtpSenderAddress = self.smtpSender
        self.senderDomainName = senderDomainName
        self.port = port
        
    def htmlAttachment(self, content, type='text/html', name=None):
        return self.attachment(content, type, name)

    def xmlAttachment(self, content, type='text/xml', name=None):
        return self.attachment(content, type, name)

    def textAttrachment(self, content, type='text/plain', name=None):
        return self.attachment(content, type, name)

    def fileAttachment(self, filename, type=None, name=None):
        if name is None:
            name = os.path.split(filename)[1]
        if type is None:
            type = mimetypes.guess_type(filename)[0]

        try:
            f = open(filename, 'rb')
            return self.attachment(f.read(), type, name)
        finally:
            f.close()

    def attachment(self, content, type, name):
        return [content, type, name]  
    
    def send(self, subject, body, to, cc=[], bcc=[], 
                    body_content_type='text/plain', attachments=[], headers = {}):
        message = MIMEMultipart()
        message['From'] = self.smtpSender
        message['To'] = ';'.join(to)
        message['Cc'] = ';'.join(cc)
        message['Subject'] = subject

        for header, value in headers.items():
            message[header] = value
            
        if body is not None:
            textPart = MIMEBase(*(body_content_type.split('/')))
            textPart.set_payload(body)
            message.attach(textPart)

        for attachment in attachments:
            if not attachment[1]: attachment[1] = 'application/octet-stream'
            maintype, subtype = attachment[1].split('/')
            attach = MIMEBase(maintype, subtype)
            attach.set_payload(attachment[0])
            # base64 encode for safety
            Encoders.encode_base64(attach)
            # include filename info
            if attachment[2] is not None:
                attach.add_header('Content-Disposition', 'attachment',
                                      filename=attachment[2])
            message.attach(attach)

        return self._sendmail(
                to + cc + bcc, 
                message.as_string(unixfrom=False),
                )

    def _sendmail(self, to, msg):
        if self.username is None:
            return smtp.sendmail(
                    self.smtpHost, 
                    self.smtpSenderAddress, 
                    to,
                    msg,
                    self.senderDomainName, self.port
                    )
        else:
            if not hasattr(msg,'read'):
                # It's not a file
                msg = StringIO(str(msg))

            d = defer.Deferred()
            factory = smtp.ESMTPSenderFactory(
                    self.username,
                    self.password,
                    self.smtpSenderAddress, 
                    to, 
                    msg, 
                    d,
                    requireTransportSecurity = False
                    )

            if self.senderDomainName is not None:
                factory.domain = self.senderDomainName

            reactor.connectTCP(self.smtpHost, self.port, factory)

            return d

def _mail_server(mail_server):
    if mail_server is None:
        email_env = 'SMTP_SERVER'
        try:
            mail_server = os.environ[email_env]
        except KeyError:
            raise ValueError("Can't send email - mail_server not given and environment variable %s not defined" % email_env)
            return
    return mail_server


def main():
    import sys
    import os
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-t", "--to", dest="to", help="comma-separated list of addresses")
    parser.add_option("-f", "--from", dest="email_from", help="where this email is coming from")
    parser.add_option("-s", "--subject", dest="subject", help="message subject, enclosed in quotes if contains spaces")
    parser.add_option("-b", "--body", dest="body", help="message body, enclosed in quotes if contains spaces")
    parser.add_option("-a", "--attachments", dest="attach", help="comma-separated list of attachments")
    parser.add_option("-m", "--mailhost", dest="mail_server", help="mail server")
                      
    #parser.set_defaults(mail_server="10.0.0.224")

    options, args = parser.parse_args()
    
    if "," in options.to:
        options.to = options.to.split(",")
    else:
        options.to = [options.to]

    
    if options.attach is not None:
        if "," in options.attach:
            options.attach = options.attach.split(",")
        else:
            options.attach = [options.attach]
        # now convert to pairs of tuples
        options.attach = [
            (os.path.abspath(att), os.path.basename(att))
            for att in options.attach
            ]
    
    sendmail(to=options.to, subject=options.subject,
             message=options.body,
             email_from=options.email_from,
             attach=options.attach,
             mail_server=options.mail_server)



if __name__ == '__main__':
    main()
