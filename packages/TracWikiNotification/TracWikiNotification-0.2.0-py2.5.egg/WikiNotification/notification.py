# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: notification.py 58 2008-03-05 22:38:36Z s0undt3ch $
# =============================================================================
#             $URL: http://wikinotification.ufsoft.org/svn/branches/trac-0.10.x/WikiNotification/notification.py $
# $LastChangedDate: 2008-03-05 22:38:36 +0000 (Wed, 05 Mar 2008) $
#             $Rev: 58 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2006 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

import re
import md5

from trac import __version__
from trac.core import *
from trac.util.text import CRLF
from trac.wiki.model import WikiPage
from trac.versioncontrol.diff import unified_diff
from trac.notification import NotifyEmail
from trac.config import Option, BoolOption, IntOption, ListOption

diff_header = """Index: %(name)s
=========================================================================
--- %(name)s (version: %(oldversion)s)
+++ %(name)s (version: %(version)s)
"""

class WikiNotificationSystem(Component):
    smtp_from = Option(
        'wiki-notification', 'smtp_from', 'trac+wiki@localhost',
        """Sender address to use in notification emails.""")

    from_name = Option(
        'wiki-notification', 'from_name', None,
        """Sender name to use in notification emails.

        Defaults to project name.""")

    smtp_always_cc = ListOption(
        'wiki-notification', 'smtp_always_cc', [],
        doc="""Comma separated list of email address(es) to always send
        notifications to.

        Addresses can be seen by all recipients (Cc:).""")

    smtp_always_bcc = ListOption(
        'wiki-notification', 'smtp_always_bcc', [],
        doc="""Comma separated list of email address(es) to always send
        notifications to.

        Addresses do not appear publicly (Bcc:).""")

    use_public_cc = BoolOption(
        'wiki-notification', 'use_public_cc', False,
        """Recipients can see email addresses of other CC'ed recipients.

        If this option is disabled(the default),
        recipients are put on BCC.

        (values: 1, on, enabled, true or 0, off, disabled, false)""")

    attach_diff = BoolOption(
        'wiki-notification', 'attach_diff', False,
        """Send `diff`'s as an attachment instead of inline in email body.""")

    redirect_time = IntOption(
        'wiki-notification', 'redirect_time', 5,
        """The default seconds a redirect should take when
        watching/un-watching a wiki page""")

    subject_template = Option(
        'wiki-notification', 'subject_template', '$prefix $page.name $action',
        "A Genshi text template snippet used to get the notification subject.")

    banned_addresses = ListOption(
        'wiki-notification', 'banned_addresses', [],
        doc="""A comma separated list of email addresses that should never be
        sent a notification email.""")


class WikiNotifyEmail(NotifyEmail):
    template_name = "notification_email.cs"
    from_email = 'trac+wiki@localhost'
    COLS = 75
    newwiki = False
    wikidiff = None
    blocked_addresses = []

    def __init__(self, env):
        NotifyEmail.__init__(self, env)
        self.from_name = self.config.get('wiki-notification', 'from_name')
        self.banned_addresses = self.config.getlist('wiki-notification',
                                                    'banned_addresses')

    def notify(self, action, page,
               version=None,
               time=None,
               comment=None,
               author=None,
               ipnr=None):
        self.page = page
        self.change_author = author
        self.time = time

        if action == "added":
            self.newwiki = True

        self.hdf.set_unescaped('name', page.name)
        self.hdf.set_unescaped('text', page.text)
        self.hdf.set_unescaped('version', version)
        self.hdf.set_unescaped('author', author)
        self.hdf.set_unescaped('comment', comment)
        self.hdf.set_unescaped('ip', ipnr)
        self.hdf.set_unescaped('action', action)
        self.hdf.set_unescaped('link', self.env.abs_href.wiki(page.name))
        self.hdf.set_unescaped('linkdiff', self.env.abs_href.wiki(
                                            page.name, action='diff',
                                            version=page.version))

        if page.version > 0 and action == 'modified':
            diff = diff_header % {'name': self.page.name,
                                  'version': self.page.version,
                                  'oldversion': self.page.version -1
                                 }
            oldpage = WikiPage(self.env, page.name, page.version - 1)
            self.hdf.set_unescaped("oldversion", oldpage.version)
            self.hdf.set_unescaped("oldtext", oldpage.text)
            for line in unified_diff(oldpage.text.splitlines(),
                                     page.text.splitlines(), context=3):
                diff += "%s\n" % line
                self.wikidiff = diff

        self.hdf.set_unescaped('wikidiff', self.wikidiff)

        projname = self.config.get('project', 'name')
        subject = '[%s] Notification: %s %s' % (projname, page.name,
                                                action.replace('_', ' '))

        if not self.newwiki:
            subject = 'Re: %s' % subject

        NotifyEmail.notify(self, page.name, subject)

    def get_message_id(self, rcpt, time=0):
        """Generate a predictable, but sufficiently unique message ID."""
        s = '%s.%s.%d.%d.%s' % (self.config.get('project', 'url'),
                               self.page.name, self.page.version, time,
                               rcpt.encode('ascii', 'ignore'))

        dig = md5.new(s).hexdigest()
        host = self.from_email[self.from_email.find('@') + 1:]
        msgid = '<%03d.%s@%s>' % (len(s), dig, host)
        return msgid

    def get_recipients(self, pagename):
        if not self.db:
            self.db = self.env.get_db_cnx()
        cursor = self.db.cursor()
        QUERY_SIDS = """SELECT sid from session_attribute
                        WHERE name=%s AND value LIKE %s"""
        tos = []
        cursor.execute(QUERY_SIDS, ('watched_pages', '%,'+pagename+',%'))
        sids = cursor.fetchall()
        self.env.log.debug("SID'S TO NOTIFY: %s", sids)
        QUERY_EMAILS = """SELECT value FROM session_attribute
                          WHERE name=%s AND sid=%s"""
        for sid in sids:
            if sid[0] != self.change_author:
                self.env.log.debug('SID: %s', sid[0])
                cursor.execute(QUERY_EMAILS, ('email', sid[0]))
                tos.append(cursor.fetchone()[0])

        self.env.log.debug("TO's TO NOTIFY: %s", tos)
        return (tos, [])

    def send(self, torcpts, ccrcpts, mime_headers={}):
        from email.MIMEText import MIMEText
        from email.Utils import formatdate

        attach_diff = self.config.getbool('wiki-notification', 'attach_diff')
        if attach_diff:
            from email.MIMEMultipart import MIMEMultipart
            self.hdf.set_unescaped('wikidiff', '')

        body = self.hdf.render(self.template_name)
        projname = self.config.get('project', 'name')
        public_cc = self.config.getbool('wiki-notification', 'use_public_cc')
        headers = {}
        headers['X-Mailer'] = 'Trac %s, by Edgewall Software' % __version__
        headers['X-Trac-Version'] =  __version__
        headers['X-Trac-Project'] =  projname
        headers['X-URL'] = self.config.get('project', 'url')
        headers['Precedence'] = 'bulk'
        headers['Auto-Submitted'] = 'auto-generated'
        headers['Subject'] = self.subject
        headers['From'] = (self.from_name or projname, self.from_email)
        headers['Reply-To'] = self.replyto_email

        def build_addresses(rcpts):
            """Format and remove invalid addresses"""
            return filter(lambda x: x, \
                          [self.get_smtp_address(addr) for addr in rcpts])

        def remove_dup(rcpts, all):
            """Remove duplicates"""
            tmp = []
            for rcpt in rcpts:
                if rcpt in self.banned_addresses:
                    self.env.log.debug("Banned Address: %s", rcpt)
                    self.blocked_addresses.append(rcpt)
                elif not rcpt in all:
                    tmp.append(rcpt)
                    all.append(rcpt)
            return (tmp, all)

        toaddrs = build_addresses(torcpts)
        ccaddrs = build_addresses(ccrcpts)
        accparam = self.config.getlist('wiki-notification', 'smtp_always_cc')
        accaddrs = accparam and build_addresses(accparam) or []
        bccparam = self.config.getlist('wiki-notification', 'smtp_always_bcc')
        bccaddrs = bccparam and build_addresses(bccparam) or []

        recipients = []
        (toaddrs, recipients) = remove_dup(toaddrs, recipients)
        (ccaddrs, recipients) = remove_dup(ccaddrs, recipients)
        (accaddrs, recipients) = remove_dup(accaddrs, recipients)
        (bccaddrs, recipients) = remove_dup(bccaddrs, recipients)

        self.env.log.debug("Not notifying the following addresses: %s",
                           ', '.join(self.blocked_addresses))

        # if there is not valid recipient, leave immediately
        if len(recipients) < 1:
            self.env.log.info('no recipient for a wiki notification')
            return

        dest = self.change_author or 'anonymous'
        message_id = self.get_message_id(dest, self.time)
        headers['Message-ID'] = message_id
        headers['X-Trac-Wiki-URL'] = self.env.abs_href.wiki(self.page.name)
        if not self.newwiki:
            reply_msgid = self.get_message_id(dest)
            headers['In-Reply-To'] = headers['References'] = reply_msgid

        pcc = accaddrs
        if public_cc:
            pcc += ccaddrs
            if toaddrs:
                headers['To'] = ', '.join(toaddrs)
        if pcc:
            headers['Cc'] = ', '.join(pcc)
        headers['Date'] = formatdate()
        # sanity check
        if not self._charset.body_encoding:
            try:
                dummy = body.encode('ascii')
            except UnicodeDecodeError:
                raise TracError(_("WikiPage contains non-Ascii chars. " \
                                  "Please change encoding setting"))

        if attach_diff:
            # With MIMEMultipart the charset has to be set before any parts
            # are added.
            msg = MIMEMultipart()
            del msg['Content-Transfer-Encoding']
            msg.set_charset(self._charset)
            msg.preamble = 'This is a multi-part message in MIME format.'

            # The text Message
            mail = MIMEText(body, 'plain')
            mail.add_header('Content-Disposition', 'inline',
                            filename="message.txt")
            # Re-Setting Content Transfer Encoding
            del mail['Content-Transfer-Encoding']
            mail.set_charset(self._charset)
            msg.attach(mail)
            try:
                # The Diff Attachment
                attach = MIMEText(self.wikidiff.encode('utf-8'), 'x-patch')
                attach.add_header('Content-Disposition', 'inline',
                                  filename=self.page.name + '.diff')
                del attach['Content-Transfer-Encoding']
                attach.set_charset(self._charset)
                msg.attach(attach)
            except AttributeError:
                # We don't have a wikidiff to attach
                pass
        else:
            msg = MIMEText(body, 'plain')
            # Message class computes the wrong type from MIMEText constructor,
            # which does not take a Charset object as initializer. Reset the
            # encoding type to force a new, valid evaluation
            del msg['Content-Transfer-Encoding']
            msg.set_charset(self._charset)

        self.add_headers(msg, headers);
        self.add_headers(msg, mime_headers);
        self.env.log.info("Sending SMTP notification to %s:%d to %s"
                           % (self.smtp_server, self.smtp_port, recipients))
        msgtext = msg.as_string()
        # Ensure the message complies with RFC2822: use CRLF line endings
        recrlf = re.compile("\r?\n")
        msgtext = CRLF.join(recrlf.split(msgtext))
        try:
            self.server.sendmail(msg['From'], recipients, msgtext)
        except Exception, err:
            self.env.log.debug('Notification could not be sent: %r', err)

