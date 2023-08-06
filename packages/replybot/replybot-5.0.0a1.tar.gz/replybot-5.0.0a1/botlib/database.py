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

"""Manage the database."""

from __future__ import with_statement

__metaclass__ = type
__all__ = [
    'Corruption',
    'Database',
    'Entry',
    'Notice',
    'Version',
    'Whitelist',
    ]


import re
import os
import sys
import time
import errno
import logging
import datetime
import pkg_resources

from email.utils import parseaddr
from storm.locals import *

from botlib import version
from botlib.configuration import config
from botlib.i18n import _


SCHEMA_KEY = u'DatabaseSchema'
PROGRAM_KEY = u'Replybot'

log = logging.getLogger('replybot')



class Corruption(Exception):
    """Database is corrupted"""



class Entry(Storm):
    __storm_table__ = 'entry'

    id = Int(primary=True)
    address = Unicode()     # who we're send a reply to
    last_sent = DateTime()  # when a reply was last sent
    key = Unicode()         # the reply 'key'

    def __init__(self, address, last_sent, key):
        self.address = unicode(address)
        self.last_sent = last_sent
        self.key = unicode(key)


class Whitelist(Storm):
    __storm_table__ = 'whitelist'

    id = Int(primary=True)
    matcher     = Unicode() # address or regexp
    is_pattern  = Bool()    # whether this item is a regexp

    def __init__(self, matcher):
        matcher = unicode(matcher)
        if matcher.startswith('^'):
            self.is_pattern = True
            self.matcher = matcher[1:]
        else:
            self.is_pattern = False
            self.matcher = matcher


class Notice(Storm):
    __storm_table__ = 'notice'

    id = Int(primary=True)
    filename = Unicode()    # where the reply is cached
    uri = Unicode()         # where the original reply lives
    retrieved = DateTime()  # when the message was last retrieved

    def __init__(self, filename, uri, retrieved):
        self.filename = unicode(filename)
        self.uri = unicode(uri)
        self.retrieved = retrieved


class Version(Storm):
    __storm_table__ = 'version'

    id = Int(primary=True)
    component = Unicode()   # the thing we're versioning
    version = Int()         # version number

    def __init__(self, component, version):
        self.component = unicode(component)
        self.version = version




class Database:
    """Basic interface to the database."""

    def __init__(self, uri):
        """Initialize the database connection.

        :param url: The database url
        :type url: string
        :raise Corruption: when the schema version in the database does not
            match the expected schema version.
        """
        database = create_database(uri)
        self._store = store = Store(database)
        # Check the sqlite master database to see if the version table exists.
        # If so, then assume the database schema is correctly initialized.
        # Storm does not currently have schema creation, so this is a cheap
        # and easy way to do it for now.
        table_names = [item[0] for item in
                       store.execute('select tbl_name from sqlite_master;')]
        if 'version' not in table_names:
            schema = pkg_resources.resource_string('botlib', 'replybot.sql')
            for statement in schema.split(';'):
                store.execute(statement + ';')
        # Validate the schema version.
        v = store.find(Version, component=SCHEMA_KEY).one()
        if v is None:
            v = Version(component=SCHEMA_KEY, version=version.__schema__)
            store.add(v)
            v = Version(component=PROGRAM_KEY, version=version.HEX_VERSION)
            store.add(v)
        elif v.version != version.__schema__:
            raise Corruption('Unexpected schema version: %d' % v.version)
        store.commit()

    def get_version(self, component):
        """Return the version of the given component.

        :param component: the component key to look up
        :type component: string
        :return: the component's version
        :rtype: Version
        """
        return self._store.find(
            Version,
            Version.component == unicode(component)).one()

    def get_entry(self, address, key):
        """Get a matching entry.

        :param address: the email address to find
        :type address: string
        :param key: the entry 'key' (used to uniquify across domains)
        :type key: string
        :return: the matching entry or None
        :rtype: Entry
        """
        return self._store.find(
            Entry,
            Entry.address == unicode(address),
            Entry.key == unicode(key)).one()

    @property
    def entries(self):
        """All the entries, in no particular order."""
        for entry in self._store.find(Entry):
            yield entry

    def get_notice(self, uri):
        """Get the notice matching a uri.

        :param uri: the uri of the notice
        :type uri: string
        :return: the notice text or None
        :rtype: string
        """
        return self._store.find(
            Notice,
            Notice.uri == unicode(uri)).one()

    def is_whitelisted(self, address):
        """Return whether the address is whitelisted or not.

        :param address: the address to check
        :type address: string
        :return: True if the address is whitelisted
        :rtype: bool
        """
        # First look for exact matches
        match = self._store.find(
            Whitelist,
            Whitelist.matcher == unicode(address)).one()
        if match is not None:
            # There was exactly one match, so this address is whitelisted.
            return True
        # Check all the regular expressions.
        matchers = self._store.find(Whitelist, Whitelist.is_pattern == True)
        for matcher in matchers:
            if re.match(matcher.matcher, address, re.IGNORECASE):
                return True
        return False

    def put_whitelist(self, pattern):
        """Add a pattern or address to the whitelist.

        :param pattern: the pattern or address.  If the pattern starts with
            the caret (^) character, it is interpreted as a regular
            expression.  Otherwise it is interpreted as a literal address.
        :type pattern: string
        """
        # Find out if this is a regular expression or an address.
        if pattern.startswith('^'):
            is_pattern = True
            matcher = pattern[1:]
        else:
            is_pattern = False
            matcher = pattern
        # See if this entry is in the database.
        matcher = self._store.find(
            Whitelist,
            Whitelist.matcher == unicode(matcher),
            Whitelist.is_pattern == is_pattern).one()
        if matcher is None:
            # It's not in the database yet, so go ahead and add it.
            whitelist = Whitelist(pattern)
            self._store.add(whitelist)
            self._store.commit()

    def purge_whitelisted(self):
        """Purge the whitelist of all entries."""
        self._store.find(Whitelist).remove()
        log.debug('Whitelist purged')
        self._store.commit()

    def put_notice(self, filename, uri, retrieved):
        """Add a notice to the database.

        :param filename: the filename to store the notice in the cache as
        :type filename: string
        :param uri: the uri of the notice (i.e. where it was downloaded from)
        :type uri: string
        :param retrieved: the date the notice was downloaded from the uri
        :type retrieved: datetime
        :return: the Notice object
        :rtype: Notice
        """
        notice = Notice(filename=filename, uri=uri, retrieved=retrieved)
        self._store.add(notice)
        self._store.commit()
        return notice

    def purge_notices(self, cache_directory):
        """Purge all notices from the database and cache.

        :param cache_directory: the directory containing the cached notices
        :type cache_directory: string
        """
        self._store.find(Notice).remove()
        log.debug('Notices purged')
        # Remove all cache files.
        for filename in os.listdir(cache_directory):
            try:
                purgefile = os.path.join(cache_directory, filename)
                log.debug('Purging cache file: %s', purgefile)
                os.remove(purgefile)
            except OSError, error:
                if e.errno != errno.ENOENT:
                    raise
        self._store.commit()

    def put_entry(self, address, last_sent, key):
        """Put an entry representing a sent reply.

        :param address: the email address we're recording a response to
        :type address: string
        :param last_sent: the date the last response was sent
        :type last_sent: datetime
        :param key: the response 'key' (used to uniquify across domains)
        :type key: string
        :return: the recorded entry
        :rtype: Entry
        """
        entry = Entry(address=address, last_sent=last_sent, key=key)
        self._store.add(entry)
        self._store.commit()
        return entry

    def purge_entries(self, key=None):
        """Purge all entries for the given key.

        :param key: the domain 'key' to purge.  If None (the default), purge
            all entries for all keys.
        :type key: string or None
        """
        if key is None:
            self._store.find(Entry).remove()
            log.debug('Purged all key/address entries')
        else:
            self._store.find(Entry, Entry.key == key).remove()
            log.debug('Purged all addresses for key: %s', key)
        self._store.commit()

    def do_purges(self, which):
        """Purge some or all of the database.

        :param which: what to purge; can be one of 'notices', 'replies', or
            'whitelist', or 'all'.
        :type which: sequence of strings
        """
        purge_set = set(which)
        if 'all' in purge_set:
            purge_set.update(('notices', 'replies', 'whitelist'))
        if 'notices' in purge_set:
            self.purge_notices(config.cache_directory)
            log.info(_('Notices cache has been purged'))
        if 'replies' in purge_set:
            self.purge_entries()
            log.info(_('Reply times have been purged'))
        if 'whitelist' in purge_set:
            self.purge_whitelisted()
            log.info(_('Whitelist has been purged'))

    def do_whitelist(self, additions, whitelist_file=None):
        """Add to the whitelist.

        :param additions: the set of whitelist additions, as accepted by
            `put_whitelist()`
        :type additions: sequence
        :param whitelist_file: the name of a text file containing whitelist
            patterns as accepted by `put_whitelist()`
        :type whitelist_file: string
        """
        for pattern in additions:
            self.put_whitelist(pattern)
        if not opts.whitelist_file:
            return
        with open(opts.whitelist_file) as fp:
            for line in fp:
                line = line[:-1]
                if line.startswith('^'):
                    self.put_whitelist(line)
                else:
                    realname, address = parseaddr(line)
                    self.put_whitelist(address)

    def process_message(self, msg):
        """Process a message.

        :param msg: the message object
        :type msg: email.message.Message
        :return: True if a reply was sent
        :rtype: bool
        """
        # Process the message
        message_id = msg.get('message-id', '(no message id available)')
        # If this message has a Precedence: bulk, junk, or list, do not
        # respond to it.  If we did, we'd probably end up spamming mailing
        # lists, other replybots, etc.
        precedence = msg.get('precedence', '').lower()
        if precedence in ('bulk', 'junk', 'list'):
            log.info('[%s] No reply sent to Precedence %s',
                     message_id, precedence)
            return False
        # Extract the sender from the message
        sender_from = msg.get('from')
        if sender_from is None:
            log.info('[%s] No reply sent to missing sender', message_id)
            return False
        realname, sender = parseaddr(sender_from)
        if not sender:
            log.info('[%s] No reply sent to empty sender', message_id)
            return False
        sender = sender.lower()
        # An empty envelope sender means it's a bounce, so don't reply to it!
        if msg.get('return-path') == '<>':
            log.info('[%s] Not replying to bounce', message_id)
            return False
        # Check the X-Ack: header; if it's set to 'no' we do not reply under
        # any circumstances, but if it's set to 'yes', we force a reply
        # regardless of the grace period.
        ack = msg.get('x-ack', '').lower()
        if ack == 'no':
            log.info('[%s] Not replying to X-Ack: no', message_id)
            return False
        elif config.options.testing and ack == 'yes':
            self.do_reply(msg, sender)
            return True
        else:
            # Keep processing.
            pass
        # XXX Try to see if the message is spam and don't reply to it if so.
        pass
        # See if the sender is due a response, first by checking the whitelist.
        if self.is_whitelisted(sender):
            log.info('[%s] Not replying to whitelisted address: %s',
                     message_id, sender)
            return False
        # See if we've already sent this sender a response.
        entry = self.get_entry(sender, config.options.key)
        if entry is None:
            # We've have no record of this address in our database, meaning
            # they have never been sent a reply from us.  Do so now.
            self.do_reply(msg, sender)
            return True
        # See if we've sent them a message within the grace period.
        now = datetime.datetime.now()
        if entry.last_sent and now < entry.last_sent + config.grace_period:
            log.info('Not replying to graced address %s:%s %s',
                     config.key, sender, msgid)
            return
        do_reply(opts, msg, sender)
