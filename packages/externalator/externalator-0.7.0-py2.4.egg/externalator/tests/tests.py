"""
tests the functionality of externalator

Note:  if the tests hang, try a svn checkout manually.  It
could be that the certificate changed
"""

commands = [ # to be tested
    'add',
    'checkout',
    'delete',
    'diff',
    'freeze',
    'get',
    'help',
    'list',
    'merge',
    'set',
    'update',
    ]
    

# The obligatory imports:

import optparse
import os
import shutil
import subprocess
import tempfile

from paste.fixture import *
from externalator.repository import *

from externalator import externalator

# globals

repo_name = 'REPO'
checkout_name = 'CHECKOUT'
repo = os.path.join(os.getcwd(), repo_name)
repo_path = 'file://' + repo
checkout = os.path.join(os.getcwd(), checkout_name)

testdir = 'TEST'
newdirs = 'trunk', 'branch', 'dir1', 'dir2'

# front-end for externalator calls
def extcall(*args):
    print ' '.join(['externalator'] + list(args))

    s = externalator.main(args)
    if s:
        print s
    return s

# make sure the system is clean

def cleanup():
    for i in (repo, checkout, testdir) + newdirs:
        if os.path.exists(i):
            shutil.rmtree(i)

cleanup()

### parse options
parser = optparse.OptionParser()
parser.add_option('--no-clean', dest='clean',
                  default=True,
                  action='store_false',
                  help="don't remove the repositories on success")
(options, args) = parser.parse_args()

### test help
for command in commands:
    assert command in extcall('help', command)

###
print '-> Create a repository...'

assert not subprocess.call(['svnadmin', 'create', repo_name])

###
print '-> Checkout the repository...'

svn = SVN(repo_path)
svn.checkout(path=checkout_name)
assert checkout_name in os.listdir('.')

svn_co = SVN(checkout)
assert svn_co.is_repository()

assert not externalator.get_externals(checkout_name, 'svn')

###
print '-> list the bundle'

bundles = extcall('ls', checkout_name)
assert checkout_name in bundles

###
print '-> Add some externals...'

svn_external = 'https://svn.openplans.org/svn/dotemacs'
svn_external_name = svn_external.split('/')[-1]

extcall('-m', 'adding test svn external', 'add', '%s=%s' % 
              (svn_external_name, svn_external), checkout_name)

externals = externalator.parse_externals(checkout_name, 'svn')
assert len(externals) == 1
assert externals[0]['repository'] == svn_external

CVSROOT=':pserver:anonymous@cvs.zope.org:/cvs-repository'
cvs_external = 'Products/ZopeVersionControl'
cvs_external_name = cvs_external.split('/')[-1]
extcall('-m', 'adding test cvs external', 'add', '--cvs=%s' % CVSROOT,
              '%s=%s' % (cvs_external_name, cvs_external), checkout_name)

tgz_external = 'http://www.dieter.handshake.de/pyprojects/zope/AdvancedQuery.tgz'
extcall('-m', 'adding test tgz external', 'add', '--tgz',
              tgz_external, checkout_name)

print '-> Checkout the bundle and verify the externals are there...'

extcall('checkout', repo_path, testdir)

assert testdir in os.listdir('.')

dirlisting = os.listdir(testdir)
for i in svn_external_name, cvs_external_name:
    assert i in dirlisting

externals = externalator.parse_externals(testdir, 'svn')
assert len(externals) == 1
assert externals[0]['repository'] == svn_external

# test get
get = extcall('get', testdir)
assert svn_external in get

externals = externalator.parse_externals(testdir, 'cvs')
assert len(externals) == 1
assert externals[0]['repository'] == cvs_external
assert externals[0]['root'] == CVSROOT

###
print '-> Update the original checkout...'

extcall('update', checkout_name)

dirlisting = os.listdir(checkout_name)
for i in svn_external_name, cvs_external_name:
    assert i in dirlisting

externals = externalator.parse_externals(checkout_name, 'svn')
assert len(externals) == 1
assert externals[0]['repository'] == svn_external

externals = externalator.parse_externals(checkout_name, 'cvs')
assert len(externals) == 1
assert externals[0]['repository'] == cvs_external
assert externals[0]['root'] == CVSROOT

###
print '-> Remove some externals...'

extcall('-m', '"removing svn external"', 'remove', svn_external_name, checkout_name)

shutil.rmtree(testdir)
extcall('checkout', repo_path, testdir)

externals = externalator.parse_externals(checkout_name, 'svn')
assert not externals

externals = externalator.parse_externals(testdir, 'svn')
assert not externals

dirlisting = os.listdir(testdir)
assert svn_external_name not in dirlisting

###
print '-> Testing difference between bundles...'

extcall('-m', 'adding test svn external', 'add', '%s=%s' % 
        (svn_external_name, svn_external), checkout_name)


diff = extcall('diff', checkout_name, testdir)
assert svn_external_name in diff

###
print '-> Testing pegging to a revision...'

pegged_external = os.path.join(checkout_name, svn_external_name)
svn_ext = SVN(pegged_external)
newrevision = svn_ext.info('Revision')

log = svn_ext.read('log', pegged_external)
oldrevision = re.search('[0-9]+', 
                        [i for i in re.findall('\nr[0-9]+ |', log) 
                         if i][-1]).group()

assert oldrevision != newrevision

extcall('-m', 'pegging to an old revision', 'set', '%s=%s' %
        (svn_external_name, 'r' + oldrevision), checkout_name)

shutil.rmtree(testdir)
extcall('checkout', repo_path, testdir)

svn_ext = SVN(os.path.join(testdir, svn_external_name))
testrevision = svn_ext.info('Revision')

assert oldrevision == testrevision

### 
print '-> Test merging externals...'

for i in newdirs:
    svn('-m', 'making test directory', 'mkdir', svn.join(i))

# checkout the directories
for i in newdirs:
    svn_tmp = SVN(svn.join(i))
    svn_tmp.checkout()

s = extcall('ls', repo_path)

for i in newdirs:
    assert i in s

# add some externals
extcall('-m', 'adding test svn external', 'add', '%s=r%s:%s' % 
              (svn_external_name, oldrevision, svn_external), newdirs[0])
extcall('-m', 'adding test cvs external', 'add', '--cvs=%s' % CVSROOT,
              '%s=%s' % (cvs_external_name, cvs_external), newdirs[0])
extcall('-m', 'adding test tgz external', 'add', '--tgz',
              tgz_external, newdirs[0])

new_svn_external = 'https://svn.openplans.org/svn/standalone/contactthem'
new_svn_external_name = new_svn_external.split('/')[-1]
extcall('-m', 'adding newer version svn external', 'add', '%s=r%s:%s' % 
              (svn_external_name, newrevision, svn_external), newdirs[1])
extcall('-m', 'a different svn external', 'add', '%s=%s' % 
              (new_svn_external_name, new_svn_external), newdirs[1])

# merge them
extcall('merge', newdirs[0], newdirs[1])

# test the merge
shutil.rmtree(testdir)
extcall('checkout', newdirs[1], testdir)

dirlisting = os.listdir(testdir)

for i in new_svn_external_name, svn_external_name, cvs_external_name:
    try:
        assert i in dirlisting
    except AssertionError:
        print '%s not found in directory %s %s' % (i, testdir, dirlisting)
        raise

externals = externalator.parse_externals(testdir, 'svn')
assert len(externals) == 2

for i in new_svn_external_name, svn_external_name:
    assert i in [ j['name'] for j in externals ]

assert [ j['revision'] for j in externals if j['name'] == svn_external_name ][0] == oldrevision

###
print '-> Test freezing externals...'

freeze_repo = testdir

# find an unpegged external
externals = externalator.parse_externals(freeze_repo, 'svn')

for i in externals:
    if i['revision'] is None:
        unpegged = i
        break
else:
    print 'No unpegged externals found in %s' % freeze_repo
    sys.exit(1)

# freeze the repository
extcall('-m', 'freezing externals', 'freeze', freeze_repo)

# make sure the unpegged external is now pegged
externals = externalator.parse_externals(freeze_repo, 'svn')

for i in externals:
    if i['name'] == unpegged['name']:
        unpegged_repo = SVN(unpegged['repository'])
        revision = unpegged_repo.info('Revision')
        assert i['revision'] == revision
        break
else:
    print '%s no longer in %s externals!' % ( unpegged['name'], freeze_repo )
    sys.exit(1)

###
print '-> All tests passed.'
if options.clean:
    cleanup()
