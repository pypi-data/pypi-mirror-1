"""Sending Roundup-specific mail over SMTP.
"""
__docformat__ = 'restructuredtext'
# $Id$

import time, quopri, os, socket, smtplib, re

from cStringIO import StringIO
from MimeWriter import MimeWriter

from roundup.rfc2822 import encode_header
from roundup import __version__

try:
    from email.Utils import formatdate
except ImportError:
    def formatdate():
        return time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

class MessageSendError(RuntimeError):
    pass

class Mailer:
    """Roundup-specific mail sending."""
    def __init__(self, config):
        self.config = config

        # set to indicate to roundup not to actually _send_ email
        # this var must contain a file to write the mail to
        self.debug = os.environ.get('SENDMAILDEBUG', '') \
            or config["MAIL_DEBUG"]

    def get_standard_message(self, to, subject, author=None):
        '''Form a standard email message from Roundup.

        "to"      - recipients list
        "subject" - Subject
        "author"  - (name, address) tuple or None for admin email

        Subject and author are encoded using the EMAIL_CHARSET from the
        config (default UTF-8).

        Returns a Message object and body part writer.
        '''
        # encode header values if they need to be
        charset = getattr(self.config, 'EMAIL_CHARSET', 'utf-8')
        tracker_name = self.config.TRACKER_NAME
        if charset != 'utf-8':
            tracker = unicode(tracker_name, 'utf-8').encode(charset)
        if not author:
            author = straddr((tracker_name, self.config.ADMIN_EMAIL))
        else:
            name = author[0]
            if charset != 'utf-8':
                name = unicode(name, 'utf-8').encode(charset)
            author = straddr((encode_header(name, charset), author[1]))

        message = StringIO()
        writer = MimeWriter(message)
        writer.addheader('Subject', encode_header(subject, charset))
        writer.addheader('To', ', '.join(to))
        writer.addheader('From', author)
        writer.addheader('Date', formatdate())

        # Add a unique Roundup header to help filtering
        writer.addheader('X-Roundup-Name', encode_header(tracker_name,
            charset))
        # and another one to avoid loops
        writer.addheader('X-Roundup-Loop', 'hello')
        # finally, an aid to debugging problems
        writer.addheader('X-Roundup-Version', __version__)

        writer.addheader('MIME-Version', '1.0')

        return message, writer

    def standard_message(self, to, subject, content, author=None):
        """Send a standard message.

        Arguments:
        - to: a list of addresses usable by rfc822.parseaddr().
        - subject: the subject as a string.
        - content: the body of the message as a string.
        - author: the sender as a (name, address) tuple
        """
        message, writer = self.get_standard_message(to, subject, author)

        writer.addheader('Content-Transfer-Encoding', 'quoted-printable')
        body = writer.startbody('text/plain; charset=utf-8')
        content = StringIO(content)
        quopri.encode(content, body, 0)

        self.smtp_send(to, message)

    def bounce_message(self, bounced_message, to, error,
                       subject='Failed issue tracker submission'):
        """Bounce a message, attaching the failed submission.

        Arguments:
        - bounced_message: an RFC822 Message object.
        - to: a list of addresses usable by rfc822.parseaddr(). Might be
          extended or overridden according to the config
          ERROR_MESSAGES_TO setting.
        - error: the reason of failure as a string.
        - subject: the subject as a string.

        """
        # see whether we should send to the dispatcher or not
        dispatcher_email = getattr(self.config, "DISPATCHER_EMAIL",
            getattr(self.config, "ADMIN_EMAIL"))
        error_messages_to = getattr(self.config, "ERROR_MESSAGES_TO", "user")
        if error_messages_to == "dispatcher":
            to = [dispatcher_email]
        elif error_messages_to == "both":
            to.append(dispatcher_email)

        message, writer = self.get_standard_message(to, subject)

        part = writer.startmultipartbody('mixed')
        part = writer.nextpart()
        part.addheader('Content-Transfer-Encoding', 'quoted-printable')
        body = part.startbody('text/plain; charset=utf-8')
        body.write(quopri.encodestring ('\n'.join(error)))

        # attach the original message to the returned message
        part = writer.nextpart()
        part.addheader('Content-Disposition', 'attachment')
        part.addheader('Content-Description', 'Message you sent')
        body = part.startbody('text/plain')

        for header in bounced_message.headers:
            body.write(header)
        body.write('\n')
        try:
            bounced_message.rewindbody()
        except IOError, message:
            body.write("*** couldn't include message body: %s ***"
                       % bounced_message)
        else:
            body.write(bounced_message.fp.read())

        writer.lastpart()

        self.smtp_send(to, message)

    def smtp_send(self, to, message):
        """Send a message over SMTP, using roundup's config.

        Arguments:
        - to: a list of addresses usable by rfc822.parseaddr().
        - message: a StringIO instance with a full message.
        """
        if self.debug:
            # don't send - just write to a file
            open(self.debug, 'a').write('FROM: %s\nTO: %s\n%s\n' %
                                        (self.config.ADMIN_EMAIL,
                                         ', '.join(to),
                                         message.getvalue()))
        else:
            # now try to send the message
            try:
                # send the message as admin so bounces are sent there
                # instead of to roundup
                smtp = SMTPConnection(self.config)
                smtp.sendmail(self.config.ADMIN_EMAIL, to,
                              message.getvalue())
            except socket.error, value:
                raise MessageSendError("Error: couldn't send email: "
                                       "mailhost %s"%value)
            except smtplib.SMTPException, msg:
                raise MessageSendError("Error: couldn't send email: %s"%msg)

class SMTPConnection(smtplib.SMTP):
    ''' Open an SMTP connection to the mailhost specified in the config
    '''
    def __init__(self, config):

        smtplib.SMTP.__init__(self, config.MAILHOST)

        # start the TLS if requested
        if config["MAIL_TLS"]:
            self.starttls(config["MAIL_TLS_KEYFILE"],
                config["MAIL_TLS_CERFILE"])

        # ok, now do we also need to log in?
        mailuser = config["MAIL_USERNAME"]
        if mailuser:
            self.login(mailuser, config["MAIL_PASSWORD"])

# use the 'email' module, either imported, or our copied version
try :
    from email.Utils import formataddr as straddr
except ImportError :
    # code taken from the email package 2.4.3
    def straddr(pair, specialsre = re.compile(r'[][\()<>@,:;".]'),
            escapesre = re.compile(r'[][\()"]')):
        name, address = pair
        if name:
            quotes = ''
            if specialsre.search(name):
                quotes = '"'
            name = escapesre.sub(r'\\\g<0>', name)
            return '%s%s%s <%s>' % (quotes, name, quotes, address)
        return address

# vim: set et sts=4 sw=4 :
