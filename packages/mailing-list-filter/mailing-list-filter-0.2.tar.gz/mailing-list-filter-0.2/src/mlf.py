#!/usr/bin/env python

# See RFC 3501.

"""
Given a Gmail IMAP mailbox, star all messages in which you were a participant
(either a sender or an explicit recipient in To: or Cc:), where thread grouping
is performed via the In-Reply-To and References headers.
"""

from __future__ import with_statement
from functools import partial
from commons.log import *
from contextlib import closing, contextmanager
import getpass, logging, shelve, email, re, os, imaplib, itertools
import argparse, collections, subprocess, shutil
from commons import log, startup, seqs, networking, files, sqlhash
from commons.path import path

info    = partial(log.info,    'main')
debug   = partial(log.debug,   'main')
warning = partial(log.warning, 'main')
error   = partial(log.error,   'main')
die     = partial(log.die,     'main')
exception = partial(log.exception, 'main')

#
# Functions for getting local file paths and opening them.
#

def dbpath(cfg, suffix):
  return ( cfg.cachedir /
           files.cleanse_filename(cfg.sender) + '-' + suffix )

def opendb(cfg, suffix, flags = 'r'):
  return sqlhash.Shelf(sqlhash.SQLhash(dbpath(cfg, suffix),
                                       flags = flags),
                       protocol = 2,
                       writeback = flags == 'w',
                       cache = flags == 'w')

#
# Functions for working with the server.
#

@contextmanager
def login_imap(cfg):
  info('connecting and logging in')
  with networking.logout(imaplib.IMAP4_SSL(cfg.host, cfg.port)) as imap:
    imap.login(cfg.user, cfg.passwd)
    # Close is only valid in the authenticated state.
    with closing(imap) as imap:
      info('selecting mailbox')
      imap.select(cfg.mailbox)
      yield imap

#
# Functions for fetching messages from the server.
#

def getmaxuid(imap):
  info( 'finding max UID' )
  # We use UIDs rather than the default of sequence numbers because UIDs are
  # guaranteed to be persistent across sessions.  This means that we can, for
  # instance, fetch messages in one session and operate on this locally cached
  # data before marking messages in a separate session.
  ok, [uids] = imap.uid('SEARCH', None, 'ALL')
  maxuid = int( uids.split()[-1] )
  del uids
  return maxuid

def fetch_range(imap, minuid, maxuid):
  info( 'fetching messages', minuid, 'to', maxuid )
  # The syntax/fields of the FETCH command is documented in RFC 2060.  Also,
  # this article contains a brief overview:
  # http://www.devshed.com/c/a/Python/Python-Email-Libraries-part-2-IMAP/3/
  # BODY.PEEK prevents the message from automatically being flagged as \Seen.
  query = '(FLAGS BODY.PEEK[HEADER.FIELDS ' \
          '(Message-ID References In-Reply-To From To Cc Subject)])'
  step = 1000
  for start in xrange(minuid, maxuid + 1, step):
    range = '%d:%d' % (start, min(maxuid, start + step - 1))
    while True:
      try:
        info('fetching', range)
        ok, chunk = imap.uid('FETCH', range, query)
      except imaplib.abort, ex:
        error('fetch failed:', ex.message)
        if 'System Error' not in ex.message: raise
      except:
        exception('fetch failed')
        raise
      else:
        break
    for row in chunk:
      yield row

def fetch_new_mail(cfg, imap):
  if cfg.refresh:
    try: os.remove(dbpath(cfg, 'fetched'))
    except: pass

  with closing(opendb(cfg, 'fetched', 'w')) as mid2msg:

    minuid = mid2msg.get('maxuid', 0) + 1
    maxuid = getmaxuid(imap)

    # Every second item is just a closing paren.
    # Example data:
    # [('13300 (BODY[HEADER.FIELDS (Message-ID References In-Reply-To)] {67}',
    #   'Message-ID: <mailman.13073.1209611191.30063.mailman@python.org>\r\n\r\n'),
    #  ')',
    #  ('13301 (BODY[HEADER.FIELDS (Message-ID References In-Reply-To)] {59}',
    #   'Message-Id: <20080501035935.A0867BC00DF@hvar.simpy.com>\r\n\r\n'),
    #  ')',
    #  ('13302 (BODY[HEADER.FIELDS (Message-ID References In-Reply-To)] {92}',
    #   'Message-ID: <C43EAFC0.2E3AE%nick@yahoo-inc.com>\r\nIn-Reply-To: <48192604.90109@gmail.com>\r\n\r\n')]
    pat = re.compile(r"(?P<seqno>\d+) \(UID (?P<uid>\d+) FLAGS \((?P<flags>[^)]+)\)")
    for i, ((envelope, data), paren) in enumerate(seqs.grouper(2, fetch_range(imap, minuid, maxuid))):
      # Parse the body.
      msg = email.message_from_string(data)

      # Parse the envelope.
      m = pat.match(envelope)
      if m is None: raise Exception('envelope: %r' % envelope)
      msg.seqno = m.group('seqno')
      msg.uid   = m.group('uid')
      msg.flags = m.group('flags').split()

      # Prepare a container for references to other msgs, and initialize the
      # thread ID.
      msg.refs = set()
      msg.tid = None

      # Add these to the map.
      if msg['Message-ID'] in mid2msg:
        log.warning( 'dups', 'duplicate message IDs:',
                     msg['Message-ID'], msg['Subject'] )
      mid2msg[ msg['Message-ID'] ] = msg

      # Periodically sync to disk.
      if len(mid2msg.cache) > 1000: mid2msg.sync()

    mid2msg['maxuid'] = maxuid
    # XXX
    mid2msg['procuid'] = mid2msg['maxuid']

#
# Function for analyzing messages.
#

def itermsgs(mid2msg, minuid, midsrc = None):
  if midsrc is None: midsrc = mid2msg
  special_keys = ['maxuid', 'procuid']
  for i, (mid, msg) in enumerate(midsrc.iteritems()):
    if mid not in special_keys and msg.uid >= minuid:
      if midsrc is mid2msg: yield msg
      else: yield mid2msg[mid]
      # Periodically sync to disk.
      if mid2msg.cache is not None and len(mid2msg.cache) > 10000:
        debug( 'syncing; now at i', i, 'mid', mid )
        mid2msg.sync()
  debug( 'syncing; finished after i', i, 'mid', mid )
  mid2msg.sync()

def thread_dfs(msg, tid, mid2msg):
  assert msg.tid is None
  msg.tid = tid
  for refmid in msg.refs:
    try:
      refmsg = mid2msg[refmid]
    except KeyError:
      log.warning('badref', 'no message with mid', refmid)
    else:
      if refmsg.tid is None: thread_dfs(refmsg, tid, mid2msg)
      else: assert refmsg.tid == tid

def mark_relevant_threads(cfg):

  shutil.copy(dbpath(cfg, 'fetched'), dbpath(cfg, 'bidir'))

  with closing(opendb(cfg, 'fetched')) as midsrc:
    with closing(opendb(cfg, 'bidir', 'w')) as mid2msg:
      procuid = mid2msg.get('procuid', 0)
      minuid = procuid + 1
      info( 'maxuid', midsrc['maxuid'], 'procuid', procuid )
      del procuid
      info( 'constructing bidirectional ref graph' )
      for msg in itermsgs(mid2msg, minuid, midsrc):
        debug('processing', msg['Message-ID'])
        irt  = msg.get_all('In-Reply-To', [])
        refs = msg.get_all('References', [])
        newrefs = ' '.join( irt + refs ).replace('><', '> <').split()
        msg.refs.update( newrefs )

        # Connect nodes in graph bidirectionally.  Ignore references to MIDs
        # that don't exist.
        for ref in newrefs:
          debug('adding', ref, '<->', msg['Message-ID'])
          try: mid2msg[ref].refs.add( msg['Message-ID'] )
          except KeyError: log.warning( 'badref', 'no message with mid', ref )

  shutil.copy(dbpath(cfg, 'bidir'), dbpath(cfg, 'threaded'))

  with closing(opendb(cfg, 'bidir')) as midsrc:
    with closing(opendb(cfg, 'threaded', 'w')) as mid2msg:
      info( 'looking for relevant msgs (grouping them into threads)' )
      tids = itertools.count()
      for msg in itermsgs(mid2msg, minuid, midsrc):
        debug('threading', msg['Message-ID'])
        if ( msg.tid is None and
             ( cfg.sender in msg.get('From', '') or
               cfg.sender in msg.get('To',   '') or
               cfg.sender in msg.get('Cc',   '') ) ):
          thread_dfs(msg, tids.next(), mid2msg)

#
# Functions for storing metadata changes back to the server.
#

def flag_relevant_msgs(cfg, imap, mid2msg):

  info( 'starring/unstarring relevant/irrelevant threads' )

  for msg in itermsgs(mid2msg, 0):
    if msg.tid is not None: # is a relevant msgs
      if r'\Flagged' not in msg.flags: # not already flagged
        mark_unseen = not cfg.no_mark_unseen and r'\Seen' in msg.flags
        log.info( 'star', '\n',
                  'star' + (' and mark unseen' if mark_unseen else ''),
                  msg )
        if not cfg.pretend:
          imap.uid('STORE', msg.uid, '+FLAGS', r'\Flagged')
          if mark_unseen: imap.uid('STORE', msg.uid, '-FLAGS', r'\Seen')
    else: # is not a relevant msg
      if r'\Flagged' in msg.flags: # was inadvertently flagged
        mark_seen = not cfg.no_mark_seen and r'\Seen' not in msg.flags
        log.info( 'unstar', '\n',
                  'unstar' + (' and mark seen' if mark_seen else ''),
                  msg )
        if not cfg.pretend:
          imap.uid('STORE', msg.uid, '-FLAGS', r'\Flagged')
          if mark_seen: imap.uid('STORE', msg.uid, '+FLAGS', r'\Seen')

  mid2msg['procuid'] = mid2msg['maxuid']

#
# Main function.
#

def main(argv):
  p = argparse.ArgumentParser(description = __doc__)
  p.add_argument('--credfile', default = path( '~/.mlf.auth' ).expanduser(),
      help = """File containing your login credentials, with the username on the
      first line and the password on the second line.  Ignored iff --prompt.""")
  p.add_argument('--cachedir', default = path( '~/.mlf.cache' ).expanduser(),
      help = "Directory to use for caching our data.")
  p.add_argument('--refresh', action = 'store_true',
      help = "Re-fetch all messages, wiping out existing cache.")
  p.add_argument('--prompt', action = 'store_true',
      help = "Interactively prompt for the username and password.")
  p.add_argument('--pretend', action = 'store_true',
      help = """Do not actually carry out any updates to the server. Use in
      conjunction with --debug to observe what would happen.""")
  p.add_argument('--no-mark-unseen', action = 'store_true',
      help = "Do not mark newly revelant threads as unread.")
  p.add_argument('--no-mark-seen', action = 'store_true',
      help = "Do not mark newly irrevelant threads as read.")
  p.add_argument('--no-fetch', action = 'store_true',
      help = "Do not fetch new messages; just process already-fetched messages.")
  p.add_argument('--debug', action = 'append', default = [],
      help = """Enable logging for messages of the given flags. Flags include:
      refs (references to missing Message-IDs), dups (duplicate Message-IDs),
      main (the main program logic), and star (which messages are being
      starred), unstar (which messages are being unstarred).""")
  p.add_argument('sender',
      help = "Your email address.")
  p.add_argument('server',
      help = "The server in the format: <host>[:<port>][/<mailbox>].")

  cfg = p.parse_args(argv[1:])

  config_logging(level = logging.ERROR, do_console = True, flags = cfg.debug)

  if cfg.prompt:
    print "username:",
    cfg.user = raw_input()
    print "password:",
    cfg.passwd = getpass.getpass()
  else:
    with file(cfg.credfile) as f:
      [cfg.user, cfg.passwd] = map(lambda x: x.strip('\r\n'), f.readlines())

  try:
    m = re.match( r'(?P<host>[^:/]+)(:(?P<port>\d+))?(/(?P<mailbox>.+))?$',
               cfg.server )
    cfg.host = m.group('host')
    cfg.port = int( m.group('port') or 993 )
    cfg.mailbox = m.group('mailbox') or 'INBOX'
  except:
    p.error('Need to specify the server in the correct format.')

  files.soft_makedirs(cfg.cachedir)

  if not cfg.no_fetch:
    with login_imap(cfg) as imap:
     fetch_new_mail(cfg, imap)

  mark_relevant_threads(cfg)

  with login_imap(cfg) as imap:
    with closing(opendb(cfg, 'threaded')) as mid2msg:
      flag_relevant_msgs(cfg, imap, mid2msg)

startup.run_main()
