===================
rpatterson.mailsync
===================

Integration between mswatch, OfflineIMAP, and Gnus for realtime mail

.. contents::

This package provides some scripts that wrap parts of mswatch and
OfflineIMAP and integrate with Gnus to provide a local maildir that
is synchronized with a remote maildir as changes occur, instead of
polling on a regular basis.  This provides for near instant delivery
of new mail while also reducing resource utilization.  Integration
with the Emacs mail and newsreader, Gnus, is also provided in such a
way that your single threaded Emacs process is blocked much less as
changes occur to the maildirs.

Requirements
============

* `mswatch <http://mswatch.sourceforge.net>`_
* `OfflineIMAP <http://software.complete.org/software/projects/show/offlineimap>`_
* `Gnus <http://gnus.org>`_

Actually, they're all kinda optional.  The OfflineIMAP sync wrapper
script can be used with mswatch without Gnus.  The Gnus checkers can
be used without OfflineIMAP.  For that matter, the OfflineIMAP sync
wrapper script can be used without mswatch, but why would you?  :)

Installation
============

All you need is easy_install_::

  $ easy_install rpatterson.mailsync

The mailsync-gnus.el library will be installed in the site-lisp
directory in the egg.  To use the library, you'll need to add this
path to your emacs load-path.  It should be something like the
following but be sure to substitute the question marks with the
appropriate values for your version of Python, the version of
rpatterson.mailsync, and your easy_install site-dirs::

    /usr/lib/python?.?/site-packages/rpatterson.mailsync-?-py?.?.egg/site-lisp/

Alternatively, if you have a /usr/local/emacs/site-lisp directory, the
mailsync-gnus.el library can be installed into that directory if you
install rpatterson.mailsync from a source distribution.  You can still
use easy_install to get the source distribution::

  $ easy_install --editable --build-directory=/usr/local/src rpatterson.mailsync
  $ cd /usr/local/src/rpatterson.mailsync/
  $ python setup.py install

Once the library is on Emacs' load-path, to use the
mailsync/gnus-check function, you'll need to make sure it's loaded in
your Emacs.  You can do this by adding the following to your .gnus.el::

    (load-library "mailsync-gnus")

To use mswatch, copy the example ~/.mswatchrc to your home directory
and see the "MAILSYNC:" comments for what to change.  Use
"mailsync_gnus_watch --help" to see what options are available to
modifying the watcher behavior::

    # minimum time after first queued mailbox change to synchronization (default: 10s)
    #base_delay 10
    
    # minimum time between two syncs or failed attempts (default: 60s)
    #inter_delay 60
    
    # minimum time between two syncs or failed attempts for specific lists
    #inter_delay 30 important_list
    #inter_delay 600 high_volume_list another_list
    
    # maximum waiting time between failed attempts (default: 600s)
    #max_delay 600
    
    # program (and arguments) to run to sync the mail stores (required)
    # sync mswatch-sync
    
    # MAILSYNC: use the following to have mswatch use your OfflineIMAP
    # setup to sync folders on change.
    sync mailsync_offlineimap
    
    # prefix this string to sync's mailboxes; useful as mbsync channel (optional)
    # the first string ("mydomain") is always prefixed
    # the second string (":") is prefixed only when syncing a particular mailbox
    mailbox_prefix foo :
    
    # a store to watch, call it "local" (required)
    store local
    {
    	# program (and args) that will monitor this store for changes (required)
    	# see 'man watch_maildirs' to tell watch_maildirs where to find mail
    	# watch watch_maildirs
    
            # MAILSYNC: use the following to have your local Gnus check
            # folders as they change, otherwise, just use the above.
    	watch mailsync_gnus_watch
    }
    
    # the other store to watch, call it "mydomain" (required)
    store foo.com
    {
    	# program (and args) that will monitor this store for changes (required).
    	#
    	# Uses ssh private/public keys to login without password prompting.
    	# Uses ssh BatchMode so that 'mswatch' promptly detects disconnects.
    	# Uses 'inputkill' to run 'watch_maildirs' so that 'watch_maildirs'
    	# promptly exits if the connection dies.
            # watch ssh -o BatchMode=yes foo.com inputkill watch_maildirs
    
            # MAILSYNC: use the following to have your remote Gnus check
            # folders as they change, otherwise, just use the above.
    	watch ssh -o BatchMode=yes foo.com inputkill mailsync_gnus_watch
    }

.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall#installing-easy-install
