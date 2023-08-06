"""Perform some action such as having an MUA check mail on the folders
to be synchronized."""

import sys
import subprocess
import pkg_resources
import optparse

from rpatterson.mailsync import parse

def get_checker(option, opt_str, value, parser):
    setattr(parser.values, option.dest,
            pkg_resources.EntryPoint.parse(
                'checker = %s' % value).load(require=False))

class Checker(object):
    __doc__ = __doc__

    def getArgs(self, *folders):
        raise NotImplementedError

    def __call__(self, *folders):
        args = self.getArgs(*folders)
        process = subprocess.Popen(
            args , stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        out = process.communicate()
        if process.returncode:
            sys.exit(process.returncode)
        return out

class EmacsclientChecker(Checker):
    """Call an arbitrary elisp function in a running emacs using
    emacsclient."""

    parser = optparse.OptionParser(description=__doc__)
    parser.set_defaults(elisp_func='mailsync/gnus-check')
    parser.add_option(
        '-e', '--elisp-func', metavar='FUNC', help=
        'The name of the elisp function to be called with the folder '
        'list as an argument.   The default uses the %default '
        'function provided by the included mailsync-gnus.el library '
        'to allow gnus to check the folder and do splitting')

    def __init__(self, elisp_func=parser.defaults['elisp_func'],
                 **kw):
        self.elisp_func = elisp_func

    def getArgs(self, *folders):
        folders = ' '.join(
            ('"%s"' % folder.replace('/', '.') for folder in folders))
        return ['emacsclient', '--eval',
                '(%s (quote (%s)))' % (self.elisp_func, folders)]

class SSHChecker(Checker):
    """Run the specified checker on a remote host using SSH."""

    parser = optparse.OptionParser(description=__doc__)
    parser.add_option(
        '-a', '--host', help='Connect to HOST via SSH.')
    parser.add_option(
        '-s', '--ssh-checker', type="string", action='callback',
        callback=get_checker, metavar='ENTRYPOINT', help=
        'Run the checker at the stuptools ENTRYPOINT')

    def __init__(self, host, ssh_checker=EmacsclientChecker(), **kw):
        self.host = host
        self.checker = ssh_checker

    def getArgs(self, *folders):
        command = ["'%s'" % arg
                   for arg in self.checker.getArgs(*folders)]
        return ["ssh", self.host] + command

parser = optparse.OptionParser(description=Checker.__doc__)
parse.add_options(
    parser, EmacsclientChecker.parser, 'Emacsclient Checker')
parse.add_options(parser, SSHChecker.parser, 'SSH Checker')
