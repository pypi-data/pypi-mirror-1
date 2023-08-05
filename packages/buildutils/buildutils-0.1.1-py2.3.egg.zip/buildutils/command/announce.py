"""
Send a release announcement to ``python-announce-list@python.org`` or
elsewhere.
"""

import sys
import os
import os.path as path

from buildutils.cmd import Command
from distutils import log

default_recipients = ['rtomayko@gmail.com']
development_recipients = ['rtomayko@gmail.com']

sendmail = 'sendmail'

default_message =  """
${name} ${version} is available:

<${download_url}>

${long_description}

For more information, visit the ${name} project site:
<${url}>

${contact}
<${contact_email}>
"""

def get_default_recipient_list():
    this_file = path.abspath(__file__)
    for i in range(3):
        this_file = path.dirname(this_file)
    if path.exists(path.join(this_file, '.development')):
        return development_recipients
    else:
        return default_recipients

def massage_message(message):
    return message.strip()

class SendmailFailed(Exception):
    pass

class Announcement(object):
    message = None
    sender = None
    recipients = None
    server = None
    user = None
    password = None
    subject = None
    
    def __init__(self):
        pass
    
    def prepare(self, sender=None, recipients=None, subject=None, message=None):
        self.sender = sender or self.sender
        # TODO: need to parse recipient names into a list
        self.recipients = (recipients or self.recipients or
                           get_default_recipient_list())
        self.subject = (subject or self.subject)
        message = massage_message(message or self.message)
        self.message = '\n'.join(["TO: " + ';'.join(self.recipients),
                                  "FROM: " + self.sender,
                                  "SUBJECT: " + self.subject,
                                  '', message.strip()])
    def sendmail_send(self):
        p = os.popen("%s -t" % sendmail, 'w')
        p.write(self.message)
        exitcode = p.close()
        if exitcode:
            raise SendmailFailed("sendmail returned: %d" % exitcode)
        
    def smtp_send(self):
        # send the email via smtp
        from smtplib import SMTP
        print self.server
        session = SMTP(self.server)
        session.set_debuglevel(1)
        if self.user:
            session.login(self.user, self.password)
        rslt = session.sendmail(self.sender, self.recipients, self.message)
        session.quit()
        return rslt        
    
    def send(self):
        try:
            log.debug('trying sendmail...')
            self.sendmail_send()
        except SendmailFailed, e:
            log.debug(str(e) + '... trying smtp.')
            self.smtp_send()


class announce(Command):
    description = "send an announcement to python-announce-list@python.org or somewhere else"
    
    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [('recipients=', 't',
                     "list of email addresses separated by commas"),
                    ('reply-to=', 'f',
                     "your email address [default: maintainer or"
                     " authors email."),
                    ('subject=', 's',
                     "the email subject [default: ANN: ${name}-${version} ${description}"),
                    ('message=', 'm',
                     "a file containining the message to send [default: sensible]"),
                    ('edit', 'e',
                     "edit the message before sending (uses EDITOR, vi)"),
                    ('smtp-server=', 'h',
                     "the smtp host name (defaults to localhost)"),
                    ('smtp-user=', 'u',
                     "the smtp username if required.")]
    boolean_options = ['edit']
    expanding_options = ['message', 'smtp-server', 'smtp-user', 'reply-to',
                         'subject', 'recipients']
    
    def initialize_options(self):
        dist = self.distribution
        self.recipients = ['python-announce-list@python.org']
        self.subject = "ANN: ${fullname} - ${description}"
        contact = dist.get_contact_email()
        if contact == 'UNKNOWN':
            contact = None
        self.reply_to = contact
        self.message = None
        self.smtp_server = None
        self.smtp_user = None
        self.edit = 0
    
    def finalize_options(self):
        dist = self.distribution
        if self.message == '-':
            log.info("reading message from standard input... (single '.' line ends message)")
            message = []
            buf = sys.stdin.read()
            while buf:
                message.append(buf)
                buf = sys.stdin.read()
                if buf == '.\n':
                    break
            message = ''.join(message)
        elif self.message:
            self.message = open(self.message, 'r').read()
        else:
            self.message = default_message
        self.expand_options(notes='')
        self.ensure_string_list('recipients')
        self.ensure_string('subject')
        self.ensure_string('reply_to')
        
    def run(self):
        announcement = Announcement()
        announcement.server = self.smtp_server
        announcement.user = self.smtp_user
        announcement.prepare(sender=self.reply_to,
                             recipients=self.recipients,
                             subject=self.subject,
                             message=self.message)
        if self.edit:
            from buildutils.editor import edit_string, get_editor
            log.debug('bringing up editor (%r) on message..', get_editor())
            message = edit_string(announcement.message)
            if not message:
                log.info('no message, bailing..')
                return
            else:
                announcement.message = message
        
        def send_message():
            from socket import error as SocketError
            try:
                rslt = announcement.send()
            except SocketError, e:
                log.error('error connecting to mail server: %s', str(e))
            else:
                if rslt:
                    for recipient, error in rslt:
                        log.error('error sending to %r: %s' % (recipient, error[0]))
        log.debug('sending announcement to %r:\n%s',
                  announcement.recipients,
                  announcement.message)
        self.execute(send_message, (), msg='announcing...')
    
