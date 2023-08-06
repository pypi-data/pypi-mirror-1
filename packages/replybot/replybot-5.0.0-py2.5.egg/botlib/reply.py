# Copyright 2005-2008 Barry A. Warsaw
#
# This file is part of the Python Replybot.
#
# The Python Replybot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# The Python Replybot is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# The Python Replybot.  If not, see <http://www.gnu.org/licenses/>.

"""Do the actual reply."""

from __future__ import with_statement

__metaclass__ = type
__all__ = [
    'do_reply',
    ]


import os
import sys
import errno
import logging
import smtplib
import urllib2
import datetime
import tempfile

from email import utils
from email.mime.message import MIMEMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

from botlib.configuration import config
from botlib import version

log = logging.getLogger('replybot')



def retrieve_response(reply_url, cache_directory):
    """Download and cache the response text.

    :param reply_url: The url to the autoresponse text
    :type reply_url: string
    :param cache_directory: The path to the cache directory
    :type cache_directory: string
    :return: the retrieved data and the filename its cached in
    :rtype: 2-tuple
    """
    # Download the file text, then cache it, returning the text and the file
    # cache file name.
    log.info('Retrieving url: %s', reply_url)
    fp = urllib2.urlopen(reply_url)
    try:
        data = fp.read()
    finally:
        fp.close()
    # Create the cache directory if it doesn't already exist
    try:
        os.mkdir(cache_directory, 02700)
    except OSError, e:
        if e.errno <> errno.EEXIST:
            raise
    fd, filename = tempfile.mkstemp('', '', cache_directory)
    log.info('Saving cache file: %s', filename)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)
    return data, filename



def get_response():
    """Get the response text.

    :return: the response text
    :rtype: string
    """
    now = datetime.datetime.now()
    notice = config.db.get_notice(config.reply_url)
    if notice is None:
        log.info('Caching new response text for: %s', config.reply_url)
        # We've never seen this url before, so retrieve the reply message,
        # cache it and record the new information.
        text, filename = retrieve_response(
            config.reply_url, config.cache_directory)
        config.db.put_notice(filename, config.reply_url, now)
    else:
        # See if the cache for this notice has expired
        if now > notice.retrieved + config.cache_period:
            log.info('Cache expired for url: %s', config.reply_url)
            # The cache has expired, so remove the old file, retrieve the new
            # data, cache it and record the new information.
            try:
                # XXX We probably don't want to remove the old file until
                # we've successfully retrieved the new one.
                os.remove(notice.filename)
            except OSError, e:
                if e.errno <> errno.ENOENT:
                    raise
            text, filename = retrieve_response(
                config.reply_url, config.cache_directory)
            notice.filename = unicode(filename)
            notice.retrieved = now
            config.db.store.commit()
        else:
            # The cache is good, so read from it.
            log.debug('Cache for %s: %s', config.reply_url, notice.filename)
            with open(notice.filename) as fp:
                text = fp.read()
    return text



def do_reply(msg, sender):
    """Do the actual reply.

    :param msg: the original message
    :type msg: email.message.Message
    ;param sender: the sender of the original message
    :type sender: string
    """
    msgid = msg.get('message-id')
    # Craft the reply message.  XXX Internationalize the response.
    log.info('Sending response to %s:%s, triggered by: %s',
             config.reply_context, sender,
             ('(no message id available)' if msgid is None else msgid))
    # Wrap the original message, craft the response, and compose
    original_msg    = MIMEMessage(msg)
    response_text   = get_response()
    response_msg    = MIMEText(response_text)
    response        = MIMEMultipart(_subparts=(response_msg, original_msg))
    # Set up headers
    response['From'] = utils.formataddr((config.replybot_who,
                                         config.replybot_from))
    response['To'] = sender
    response['Subject'] = 'Re: ' + msg.get('subject', '(no subject)')
    # Construct In-Reply-To and References headers according to RFC 2822,
    # $3.6.4
    if msgid is not None:
        response['In-Reply-To'] = msgid
    references = msg.get('references')
    if references is None:
        references = msg.get('in-reply-to')
    if references is not None:
        if msgid is not None:
            references += ', ' + msgid
        response['References'] = references
    # Guard against replybot loops!  Also, add other politeness headers.
    response['Precedence'] = 'bulk'
    response['X-No-Archive'] = 'Yes'
    response['X-Mailer'] = config.replybot_who + ' ' + version.VERSION
    response['X-Ack'] = 'No'
    response['X-Bug-Tracker'] = 'https://bugs.launchpad.net/replybot'
    # Send the message
    if config.options.debug:
        log.debug('Debugging.  Not sending email to %s:%s',
                  config.reply_context, sender)
        print >> sys.stderr, response.as_string()
    else:
        log.debug('Connecting to: %s:%s', config.mail_server, config.mail_port)
        conn = smtplib.SMTP()
        conn.connect(config.mail_server, config.mail_port)
        if config.mail_user and config.mail_password:
            log.debug('Authenticating to SMTP server as: %s', config.mail_user)
            conn.login(config.mail_user, config.mail_password)
        # Flatten the message and do substitutions before sending it out
        substitutions = dict(msg.items())
        substitutions.update(config.keywords)
        template = Template(response.as_string())
        flatmsg = template.safe_substitute(substitutions)
        log.debug('Sending %s bytes to: %s', len(flatmsg), sender)
        try:
            conn.sendmail(config.replybot_mailfrom, [sender], flatmsg)
        except smtplib.SMTPException:
            # Log these to our log, not to the mail server's log.  BAW: should
            # we do something special here, like not update the database?  Or
            # only update it if the exception wasn't SMTPRecipientsRefused?
            log.exception('sendmail() exception to sender: %s', sender)
        conn.quit()
    # Now update the database for this sender
    entry = config.db.get_entry(sender, config.reply_context)
    now = datetime.datetime.now()
    if entry is None:
        log.debug('Adding new database entry for sender: %s:%s',
                  config.reply_context, sender)
        entry = config.db.put_entry(sender, now, config.reply_context)
    else:
        log.debug('Setting last_sent for existing sender: %s:%s',
                  config.reply_context, sender)
        entry.last_sent = now
    config.db.store.commit()
