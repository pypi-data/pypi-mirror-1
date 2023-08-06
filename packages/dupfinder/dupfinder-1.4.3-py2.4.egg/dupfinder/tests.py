import os, sys
import doctest
import tempfile

import finder
import manager

##############################
## Define globals for tests ##
##############################

testdir = '.'

def mkd(dpath):
    dpathlst = dpath.split('/')
    os.mkdir(os.path.join(testdir, *dpathlst))


def mkf(fname, dpath=""):
    if dpath:
        dpathlst = dpath.split('/')
        dpathlst.append(fname)
        fname = os.path.join(*dpathlst)
    fpath = os.path.join(testdir, fname)
    f = file(fpath,'w+b')

    return f


def createFile(fname, text, dpath=""):
    file = mkf(fname, dpath)
    file.write(text)
    file.close()


def ls(dpath=""):
    if dpath:
        dpathlst = dpath.split('/')
        dpath = os.path.join(*dpathlst)
    path = os.path.join(testdir, dpath)

    print "=== list%s directory ===" % (dpath and " " + dpath or "")
    dirlist = os.listdir(path); dirlist.sort()
    for name in dirlist:
        ipath = os.path.join(path, name)
        if os.path.islink(ipath):
            type = "L"
            size = -2
        elif os.path.isfile(ipath):
            type = "F"
            size = os.path.getsize(ipath)
        else:
            type = "D"
            size = -1

        print "%s :: %s :: %s" % (type, name, size)

def cat(path):
    apath = os.path.abspath(path)
    if os.path.isfile(apath):
        for l in file(apath).readlines():
            print l


def cleanTestDir():
    for dpath, dirs, files in os.walk(testdir, topdown=False):
        [os.remove(os.path.join(dpath, f)) for f in files]
        [os.rmdir(os.path.join(dpath, d)) for d in dirs]
    

def dupfind(strargs):
    """Duplication finder utility runner"""
    sys_argv = sys.argv[:]
    sys.argv = ['dupfind',] + strargs.split()
    finder.main()
    sys.argv = sys_argv
        
def dupmanage(strargs):
    """Duplication manager utility runner"""
    sys_argv = sys.argv[:]
    sys.argv = ['dupmanage',] + strargs.split()
    manager.main()
    sys.argv = sys_argv
        

##############################
##        Tests setup       ##
##############################

def setUp(dtest):
    global testdir
    testdir = tempfile.mkdtemp(dir=os.path.split(__file__)[0])
    outputf = os.path.join(testdir, 'res.csv')
    dtest.globs['testdir'] = testdir
    dtest.globs['outputf'] = outputf


def tearDown(dtest):
    cleanTestDir()
    os.rmdir(testdir)


def test_suite():
    suite = doctest.DocFileSuite(
        "README.txt",
        package="dupfinder",
        setUp=setUp,
        tearDown=tearDown,
        globs=globals(),
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE|doctest.REPORT_ONLY_FIRST_FAILURE
        )

    return suite

if __name__ == "__main__":
    from unittest import TextTestRunner
    TextTestRunner().run(test_suite())
