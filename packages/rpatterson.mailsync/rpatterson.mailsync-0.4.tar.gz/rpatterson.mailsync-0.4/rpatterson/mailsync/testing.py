import os, tempfile, subprocess, shutil

class PrintingChecker(object):

    def __init__(self, **kw):
        pass

    def __call__(self, *folders):
        out = ' '.join(self.getArgs(*folders))
        print out
        return out, ''

    def getArgs(self, *folders):
        return ('PrintingChecker:',)+folders

class MovingChecker(object):

    def __init__(self, src, dst, **kw):
        self.src = src
        self.dst = dst

    def __call__(self, *folders):
        out = ' '.join(self.getArgs(*folders))
        print out
        if os.path.isfile(self.src):
            common = len(os.path.commonprefix([self.src, self.dst]))
            print 'MovingChecker: moving %s to %s' %(
                self.src[common:], self.dst[common:])
            os.rename(self.src, self.dst)
        return out, ''

    def getArgs(self, *folders):
        return ('MovingChecker:',)+folders

def makeMaildir(*path):
    subprocess.Popen(['maildirmake', os.path.join(*path)]).wait()

def setUp(test):
    watcher_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'bin', 'mailsync_watch')
    tmp = tempfile.mkdtemp()
    maildir = os.path.join(tmp, 'Maildir')
    makeMaildir(maildir)
    foo = os.path.join(maildir, '.foo')
    makeMaildir(foo)
    test.globs.update(
        watcher_script=watcher_script, tmp=tmp, maildir=maildir, foo=foo)

def tearDown(test):
    shutil.rmtree(test.globs['tmp'])
