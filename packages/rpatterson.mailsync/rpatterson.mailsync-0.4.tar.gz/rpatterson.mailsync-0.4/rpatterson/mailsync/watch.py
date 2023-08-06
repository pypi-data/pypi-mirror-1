"""Watch a given Maildir and returning change notifications optionally
checking changed folders before returning the notification"""

import os
import sys
import signal
import subprocess
import optparse
import logging

from rpatterson.mailsync import parse
from rpatterson.mailsync import check

logging.basicConfig()
logger = logging.getLogger('rpatterson.mailsync')

parser = optparse.OptionParser(description=__doc__)
parser.set_defaults(checker=check.EmacsclientChecker)
parser.add_option(
    '-m', '--maildir', metavar='DIR', help=
    'Override the setting of the $MAILDIR environment variable (or '
    '~/Maildir if $MAILDIR is not defined) with DIR.')
parser.add_option(
    '-t', '--template', default='%s', help=
    'Folder names are expanded using TEMPLATE, a Python string '
    'template, before processing [default: %default]')
parser.add_option(
    '-i', '--inbox', default='INBOX', metavar='STRING', help=
    'Substitute STRING for the INBOX folder [default: %default]')
parser.add_option(
    '-c', '--checker', type="string", action='callback',
    callback=check.get_checker, metavar='ENTRYPOINT', help=
    'Check folder using the checker at the stuptools ENTRYPOINT when '
    'folders are modified')
parse.add_options(parser, check.parser, 'Checkers')

class Watcher(object):
    __doc__ = __doc__

    def __init__(self, maildir=parser.defaults['maildir'],
                 template=parser.defaults['template'],
                 inbox=parser.defaults['inbox'],
                 checker=parser.defaults['checker'](), **kw):
        args = ['watch_maildirs']
        if maildir is not None:
            args.append('--maildir=%s' % maildir)
        logger.info("Running '%s'" % ' '.join(args))
        self.watcher = subprocess.Popen(
            args , stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.template = template
        self.inbox = inbox
        self.checker = checker

    # TODO iteration *should* work, but for some reason it blocks
    # def __iter__(self):
    #     for line in self.watcher.stdout:
    #         self.checker(*line.strip().split())
    #         yield line
    
    def __iter__(self):
        returncode = self.watcher.poll()
        while returncode is None:
            line = self.watcher.stdout.readline()
            if line:
                folders = self.fromLine(line)
                self.check(folders)
                yield ' '.join(folders)+'\n'
            returncode = self.watcher.poll()
        else:
            if returncode:
                sys.exit(returncode)
            
    def __del__(self):
        """Ensure the watcher process is always killed on exit"""
        returncode = self.watcher.poll()
        if returncode is None:
            os.kill(self.watcher.pid, signal.SIGTERM)
            self.watcher.wait()

    def fromLine(self, line):
        folders = []
        for folder in line.strip().split():
            if folder == 'INBOX':
                folder = self.inbox
            folders.append(self.template % folder)
        return folders
        
    def check(self, folders):
        logger.info("Running '%s'" % ' '.join(
            self.checker.getArgs(*folders)))
        out, err = self.checker(*folders)
        if out:
            logger.info('Checker output: %s' % out)
        if err:
            logger.error('Checker error: %s' % err)
                
    def printLines(self):
        for line in self:
            print line,
            sys.stdout.flush()

def main(args=None):
    options, args = parser.parse_args(args=args)
    options.checker = options.checker(**options.__dict__)
    Watcher(**options.__dict__).printLines()

gnus_parser = optparse.OptionParser(description=Watcher.__doc__)
gnus_parser.add_option(parser.get_option('--maildir'))
gnus_parser.add_option(parser.get_option('--template'))
gnus_parser.add_option(parser.get_option('--inbox'))
parse.add_options(gnus_parser, check.EmacsclientChecker.parser,
                  'Emacsclient Checker') 

def gnus_main(args=None):
    options, args = gnus_parser.parse_args(args=args)
    options.checker = check.EmacsclientChecker(**options.__dict__)
    Watcher(**options.__dict__).printLines()

if __name__ == '__main__':
    main()
