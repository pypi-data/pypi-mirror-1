import re
import subprocess

from utils import *

### utility functions

svn_uri_re = re.compile(uri_re_string(('http', 'https', 'file', 
                                       'svn', 'svn+ssh')), re.I)

def is_svn_uri(string):
    """ indicates if the given string is legitimate svn uri syntax """

    if re.match(svn_uri_re, string):
        return True
    return False

### repositories

class Repository(object):
    """ abstract class for repositories """

    class RepositoryError(Exception):
        pass
    
    def __init__(self, repo):
        self.repository = repo

    def _call(self, *args):
        stdout = stderr = subprocess.PIPE    

        process = subprocess.Popen(args, stdout=stdout, stderr=stderr,
                                   universal_newlines=True)

        retval = {}
        retval.update(dict(zip(['stdout', 'stderr'], process.communicate())))
        retval['code'] = process.wait()

        return retval    

    def __call__(self, command, *args):
        args = (self.name, command) + args
        return self._call(*args)

    def is_repository(self):
        return False

    def join(self, *args):
        return '/'.join([ i.strip('/') 
                          for i in (self.repository, ) + args ])

    def readlines(self, command, *args):
        i = self.read(command, *args)
        if not i:
            return []
        i = i.split('\n')
        if not i[-1]:
            i = i[:-1]
        return i

    def read(self, command, *args):
        return self(command, *args)['stdout']

class SVN(Repository):
    """ class for svn repositories """

    def __init__(self, repo):        
        Repository.__init__(self, repo)
        self.name = 'svn'
        if not self.info():
            raise self.RespositoryError
    
    def checkout(self, item='', path=None):

        if path:
            return self('co', self.join(item), path)
        else:
            return self('co', self.join(item))
    
    def is_repository(self):
        return bool(self.root())

    def update(self, path=None):
        if path:
            self('update', path)
        else:
            self('update')

    def ls(self, recursive=False):
        if recursive:
            return self.readlines('ls', '-R', self.repository)
        else:
            return self.readlines('ls', self.repository)

    def info(self, query=''):
        """ 
        return the svn info as a dictionary
        if a query string is given, return that
        dictionary entry or None if it doesn't
        exist
        """

        i = self('info', self.repository)
        if not i['code']:
            info_dict = read_dictionary(i['stdout'])
            if query:
                return info_dict.get(query, None)
            else:
                return info_dict
        else:
            raise self.RepositoryError

    def root(self):
        """ return the root of the svn repository """

        try:
            return self.info('Repository Root')
        except self.RepositoryError:
            return None

    def externals(self):
        return self.readlines('propget', 'svn:externals', self.repository)


class CVS(Repository):
    """ class for cvs repositories """

    # can we get a URI like this?
    # cvs://anonymous@cvs.sourceforge.net/cvsroot/linuxsh;module=linux;date=20051111

    def __init__(self, repo, options='-z9 -q'):
        Repository.__init__(self, repo)
        self.name = 'cvs'
        self.options = options.split()

    def checkout(self, item='', path=None):
        arglist = list(self.options) + [ '-d', self.repository, 'co' ]
        if path:
            arglist += [ '-d', path ]
        arglist.append(item)
        return self(*arglist)            

    def update(self, path=None):
        if path:
            cwd = os.getcwd()
            os.chdir(path)
        arglist = self.options + ['update', '-dP']
        self(*arglist)
        if path:
            os.chdir(cwd)        

class TGZ(Repository):
    """ class for tarballs """

    def __init__(self, repo):
        Repository.__init__(self, repo)
        self.name = 'tgz'
        self.short_name = self.repository.split('/')[-1]
        
        self.options = 'xvf'

        # note that this assumes the name is sensible
        # -- that is, it has the same name as the archive
        # this could be done slightly more robustly by
        # parsing tar tzvf, but if it has more
        # than one directory, you're still pwned
        ext = ''
        for i in '.tgz', '.tar.gz':
            if self.short_name.endswith(i):
                ext = i
                self.options = 'z' + self.options
                break
        else:
            i = '.tar'
            if self.short_name.endswith(i):
                ext = i
                        
        index = self.short_name.rfind(ext)
        if index > -1:
            self.dir_name = self.short_name[:index]

    def checkout(self, item='', path=None):
        # note: item is bypassed alltogether
        self._call('wget', self.repository)
        
        if path:
            retval = self._call('tar', self.options, self.short_name,
                                '-C', path)
        else:
            retval = self._call('tar', self.options, self.short_name)
            
        self._call('rm', self.short_name)
        return retval

    def update(self, path=None):
        dir = self.dir_name
        if path:
            dir = os.path.join(path, dir)
        self._call('rm', '-rf', dir) # dangerous!
        return self.checkout(self, path=path)
