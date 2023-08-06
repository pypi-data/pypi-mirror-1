#!/usr/bin/python

"""
Given a Gmail IMAP mailbox, star all messages in which you were a participant
(either a sender or an explicit recipient in To: or Cc:), where thread grouping
is performed via the In-Reply-To and References headers.
"""

from __future__ import with_statement
from collections import defaultdict
from email import message_from_string
from getpass import getpass
from imaplib import IMAP4_SSL
from argparse import ArgumentParser
from path import path
from re import match
from functools import partial
from itertools import count
from commons.decs import pickle_memoized
from commons.files import cleanse_filename, soft_makedirs
from commons.log import *
from commons.misc import default_if_none, seq
from commons.networking import logout
from commons.seqs import concat, grouper
from commons.startup import run_main
from contextlib import closing
import logging
from commons import log

info    = partial(log.info,    'main')
debug   = partial(log.debug,   'main')
warning = partial(log.warning, 'main')
error   = partial(log.error,   'main')
die     = partial(log.die,     'main')

def thread_dfs(msg, tid, tid2msgs):
  assert msg.tid is None
  msg.tid = tid
  tid2msgs[tid].append(msg)
  for ref in msg.refs:
    if ref.tid is None:
      thread_dfs(ref, tid, tid2msgs)
    else:
      assert ref.tid == tid

def getmail(imap):
  info( 'finding max UID' )
  # We use UIDs rather than the default of sequence numbers because UIDs are
  # guaranteed to be persistent across sessions.  This means that we can, for
  # instance, fetch messages in one session and operate on this locally cached
  # data before marking messages in a separate session.
  ok, [uids] = imap.uid('SEARCH', None, 'ALL')
  maxuid = int( uids.split()[-1] )
  del uids

  info( 'actually fetching the messages in chunks up to max', maxuid )
  # The syntax/fields of the FETCH command is documented in RFC 2060.  Also,
  # this article contains a brief overview:
  # http://www.devshed.com/c/a/Python/Python-Email-Libraries-part-2-IMAP/3/
  # BODY.PEEK prevents the message from automatically being flagged as \Seen.
  query = '(FLAGS BODY.PEEK[HEADER.FIELDS ' \
          '(Message-ID References In-Reply-To From To Cc Subject)])'
  step = 1000
  return list( concat(
    seq( lambda: info('fetching', start, 'to', start + step - 1),
         lambda: imap.uid('FETCH', '%d:%d' % (start, start + step - 1),
                          query)[1] )
    for start in xrange(1, maxuid + 1, step) ) )

def main(argv):
  p = ArgumentParser(description = __doc__)
  p.add_argument('--credfile', default = path( '~/.mlf.auth' ).expanduser(),
      help = """File containing your login credentials, with the username on the
      first line and the password on the second line.  Ignored iff --prompt.""")
  p.add_argument('--cachedir', default = path( '~/.mlf.cache' ).expanduser(),
      help = "Directory to use for caching our data.")
  p.add_argument('--prompt', action = 'store_true',
      help = "Interactively prompt for the username and password.")
  p.add_argument('--pretend', action = 'store_true',
      help = """Do not actually carry out any updates to the server. Use in
      conjunction with --debug to observe what would happen.""")
  p.add_argument('--no-mark-unseen', action = 'store_true',
      help = "Do not mark newly revelant threads as unread.")
  p.add_argument('--no-mark-seen', action = 'store_true',
      help = "Do not mark newly irrevelant threads as read.")
  p.add_argument('--debug', action = 'append',
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
    cfg.passwd = getpass()
  else:
    with file(cfg.credfile) as f:
      [cfg.user, cfg.passwd] = map(lambda x: x.strip('\r\n'), f.readlines())

  try:
    m = match( r'(?P<host>[^:/]+)(:(?P<port>\d+))?(/(?P<mailbox>.+))?$',
               cfg.server )
    cfg.host = m.group('host')
    cfg.port = int( default_if_none(m.group('port'), 993) )
    cfg.mailbox = default_if_none(m.group('mailbox'), 'INBOX')
  except:
    p.error('Need to specify the server in the correct format.')

  soft_makedirs(cfg.cachedir)

  with logout(IMAP4_SSL(cfg.host, cfg.port)) as imap:
    imap.login(cfg.user, cfg.passwd)
    # Close is only valid in the authenticated state.
    with closing(imap) as imap:
      # Select the main mailbox (INBOX).
      imap.select(cfg.mailbox)

      # Fetch message IDs, references, and senders.
      xs = pickle_memoized \
          (lambda imap: cfg.cachedir / cleanse_filename(cfg.sender)) \
          (getmail) \
          (imap)

      log.debug('fetched', xs)

      info('building message-id map and determining the set of messages sent '
           'by you or addressed to you (the "source set")')

      srcs = []
      mid2msg = {}
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
      for (envelope, data), paren in grouper(2, xs):
        # Parse the body.
        msg = message_from_string(data)

        # Parse the envelope.
        m = match(
            r"(?P<seqno>\d+) \(UID (?P<uid>\d+) FLAGS \((?P<flags>[^)]+)\)",
            envelope )
        msg.seqno = m.group('seqno')
        msg.uid   = m.group('uid')
        msg.flags = m.group('flags').split()

        # Prepare a container for references to other msgs, and initialize the
        # thread ID.
        msg.refs = []
        msg.tid = None

        # Add these to the map.
        if msg['Message-ID'] in mid2msg:
          log.warning( 'dups', 'duplicate message IDs:',
                        msg['Message-ID'], msg['Subject'] )
        mid2msg[ msg['Message-ID'] ] = msg

        # Add to "srcs" set if sent by us or addressed to us.
        if ( cfg.sender in default_if_none( msg['From'], '' ) or
             cfg.sender in default_if_none( msg['To'],   '' ) or
             cfg.sender in default_if_none( msg['Cc'],   '' ) ):
          srcs.append( msg )

      info( 'constructing undirected graph' )

      for mid, msg in mid2msg.iteritems():
        # Extract any references.
        irt   = default_if_none( msg.get_all('In-Reply-To'), [] )
        refs  = default_if_none( msg.get_all('References'), [] )
        refs  = set( ' '.join( irt + refs ).replace('><', '> <').split() )

        # Connect nodes in graph bidirectionally.  Ignore references to MIDs
        # that don't exist.
        for ref in refs:
          try:
            refmsg = mid2msg[ref]
            # We can use lists/append (not worry about duplicates) because the
            # original sources should be acyclic.  If a -> b, then there is no b ->
            # a, so when crawling a we can add a <-> b without worrying that later
            # we may re-add b -> a.
            msg.refs.append(refmsg)
            refmsg.refs.append(msg)
          except:
            log.warning( 'refs', ref )

      info('finding connected components (grouping the messages into threads)')

      tids = count()
      tid2msgs = defaultdict(list)
      for mid, msg in mid2msg.iteritems():
        if msg.tid is None:
          thread_dfs(msg, tids.next(), tid2msgs)

      info( 'starring the relevant threads, in which I am a participant' )

      rel_tids = set()
      for srcmsg in srcs:
        if srcmsg.tid not in rel_tids:
          rel_tids.add(srcmsg.tid)
          for msg in tid2msgs[srcmsg.tid]:
            if r'\Flagged' not in msg.flags:
              log.info( 'star', '\n', msg )
              if not cfg.pretend:
                imap.uid('STORE', msg.uid, '+FLAGS', r'\Flagged')
                if not cfg.no_mark_unseen and r'\Seen' in msg.flags:
                  imap.uid('STORE', msg.uid, '-FLAGS', r'\Seen')

      info( 'unstarring irrelevant threads, in which I am not a participant' )

      all_tids = set( tid2msgs.iterkeys() )
      irrel_tids = all_tids - rel_tids
      for tid in irrel_tids:
        for msg in tid2msgs[tid]:
          if r'\Flagged' in msg.flags:
            log.info( 'unstar', '\n', msg )
            if not cfg.pretend:
              imap.uid('STORE', msg.uid, '-FLAGS', r'\Flagged')
              if not cfg.no_mark_seen and r'\Seen' not in msg.flags:
                imap.uid('STORE', msg.uid, '+FLAGS', r'\Seen')

run_main()
