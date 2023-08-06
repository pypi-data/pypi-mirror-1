import sys
import subprocess
import optparse
import pkg_resources

from rpatterson.mailsync import check

class Syncer(object):

    def __init__(self, specs, checkers=()):
        self.checkers = checkers
        self.accounts = {}
        self.folders = set()
        for spec in specs:
            sync = spec.split(':')
            if len(sync) == 2:
                account, folder = sync
            else:
                account, = sync
                folder = None
    
            account_folders = self.accounts.setdefault(account, set())
            if folder is not None:
                account_folders.add(folder)
                self.folders.add(folder)

        errors = {}
        for account, account_folders in self.accounts. iteritems():
            if account_folders != self.folders:
                errors[account] = self.folders.symmetric_difference(
                    account_folders)
                
        assert not errors, (
            'Cannot synchronize specific folders on specific '
            'accounts, so all folders must be the same for all '
            'accounts:\n%s' % '\n'.join( 
                '    %s - %s' % (account, ' '.join(error_folders))
                for account, error_folders in errors.iteritems()))

    def __call__(self):
        """If the sync is successful then run the checkers"""
        returncode = self.sync()
        if returncode == 0:
            self.check()
        return returncode

    def sync(self):
        raise NotImplementedError

    def check(self):
        for checker in self.checkers:
            print '+', ' '.join(checker.getArgs(*self.folders))
            out, err = checker(*self.folders)
            if out:
                print out
            if err:
                print err

class OfflineIMAPSyncer(Syncer):
    """Offlineimap can only take an isolated list of accounts and an
    isolated list of folders and as such can't handle the
    account:folder specs that mbsync can unless every folder
    should be synced for all accounts."""

    def sync(self):
        args = ['offlineimap', '-o']
        if self.accounts:
            args.extend(['-a', ','.join(self.accounts)])
        if self.folders:
            args.extend(['-f', ','.join(self.folders)])
    
        print '+', ' '.join(args)
        return subprocess.Popen(args).wait()

def load_syncer_factory(syncer):
    return pkg_resources.EntryPoint.parse(
        'syncer = %s' % syncer).load(require=False)

def main(args=None):
    parser = optparse.OptionParser()
    options, args = parser.parse_args(args=args)
    syncer = args[0]
    checkers = args[1:3]
    specs = args[3:]
    checkers = [
        check.load_checker_factory(checker)() for checker in checkers]
    sys.exit(load_syncer_factory(syncer)(checkers, specs)())

def offlineimap_gnus_main(args=None):
    parser = optparse.OptionParser()
    options, args = parser.parse_args(args=args)
    host = args[0]
    specs = args[1:]
    sys.exit(OfflineIMAPSyncer(
        checkers=[
            check.EmacsclientChecker(), check.SSHChecker(host)],
        specs=specs)())

def offlineimap_gnus_local(args=None):
    parser = optparse.OptionParser()
    options, args = parser.parse_args(args=args)
    sys.exit(OfflineIMAPSyncer(
        checkers=[check.EmacsclientChecker()], specs=args)())

def offlineimap_main(args=None):
    parser = optparse.OptionParser()
    options, args = parser.parse_args(args=args)
    sys.exit(OfflineIMAPSyncer(specs=args)())
    
if __name__ == '__main__':
    main()
    
