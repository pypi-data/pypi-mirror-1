#!/usr/bin/env python

""" 
a script for svn bundle management
"""

###  imports

# system imports
import sys
import os
import tempfile
import types
import StringIO
from optparse import OptionParser

# package imports
from utils import *
from repository import *

### externalator internal constants

svn_props = {'svn': 'svn:externals',
             'cvs': 'externalator:cvs',
             'tgz': 'externalator:tgz'}
modes = svn_props.keys()

# the modes for displaying and outputing externals
display = { 'svn': [ 'name', 'revision', 'repository'], 
            'cvs': [ 'name', 'root', 'repository'],
            'tgz': [ 'name' ] }


### functions central to externalator-type externals

def print_external(external, external_type):
    """ `prints' the external to a string """

    s = ' '.join([ external[j] for j in display[external_type] 
               if external[j] ])
    return s

def get_externals(repo, external_type):
    """ get externals (svn, cvs, tgz) based on external type """

    svn = SVN(repo)

    if external_type == 'svn':
        return svn.externals()

    return svn.readlines('propget', 'externalator:' + external_type, repo)

def parse_externals(repo, mode='svn'):
    """ takes the externals string from svn and make a dictionary from it """

    strings = get_externals(repo, mode)

    # check if the mode is sane
    if mode not in modes:
        raise NotImplementedError('mode %s not implemented' % mode)

    externals = []
    
    # for mode = 'cvs'
    root = None

    for i in strings:
        i = i.split('#', 1)[0].strip() # remove comments

        # pass on empty strings
        if not i: 
            continue        

        # parse the root if in cvs mode
        if mode == 'cvs' and i.startswith('CVSROOT='):
           root = i.split('=',1)[1]
           continue

        j = i.split()

        # note: these will be the same for .tgz files
        name = j[0]
        repo = j[len(j) - 1]

        version = None
        if len(j[1:-1]):
            version = j[-2]
            version = version.split('r')[-1]

        externals.append({'name': name,
                          'revision': version,
                          'repository': repo})

        if mode == 'cvs':
            externals[-1]['root'] = root
        
    return externals

### externalator commands

class ExternalatorCommand(object, OptionParser):
    """ base class for commands """

    ### class data

    braces = ("[", "]") # for mandatory arguments
    optbraces = ("<", ">") # for optional arguments

    ### ctor and dtor

    def __init__(self):
        OptionParser.__init__(self)
        self.name = ''
        self.help = self.__class__.__doc__.strip()
        self.aliases = () 
        self.arguments = []
        self.externals = []

    def post_init(self):
        """ tasks to be performed after init """

    def __del__(self):
        if hasattr(self, 'dir_name'):
            os.removedirs(self.dir_name)

    ### informational functions

    def names(self):
        if not self.aliases:
            return self.name
        return self.name + " (" +  ', '.join(self.aliases) +")"


    # hack usage to make it a string for OptionParser

    _usage=None

    def usage():
        def fget(self):
            s = ' '.join(("%prog", self.name, self.option_string()))
            if self._usage:
                s += self._usage
            return s
        def fset(self, value):
            pass
        return property(**locals())
    usage = usage()

    def short_help(self):
        """ return brief help message """
        
        return self.names() + ": " + self.help

    def long_help(self):
        """ return full help message """

        # show basic usage
        string = [ self.short_help() ]
        usagestring = self.get_usage()
        string.append(usagestring)

        # add various messages depending on the arguments expected 
        for i in self.arguments:
            if 'bundle' in i['type']:
                pass
            elif i['type'] == 'externals' and i['settable']:
                    string.append('')
                    string.append('format of the externals string is:')
                    string.append('SVN: externalname=r1234:http://repository.net/svn/product/package')
                    string.append('\t[revision number optional, or can be rNone to unset]')
                    string.append('CVS: externalname=product/package [please remember to use --cvs=CVSROOT')
                    string.append('TGZ: http://example.com/package.tar.gz')

        # return the string
        return '\n'.join(string)

    def write(self, message):
        """ write a string to a buffer for later return """
        
        if not hasattr(self, 'message'):
            self.message = []
        self.message.append(message)

    def output(self):
        """ return the contents of the buffer string """
        
        if not hasattr(self, 'message'):
            return ''
        return '\n'.join(self.message)        

    ### functions for dealing with warnings/errors

    def error(self, message, warning=False):
        """ deal with errors and warnings """
        errstring = "ERROR"
        if warning:
            errstring = "WARNING"
        print errstring + ": " + message
        if not warning:
            sys.exit(1)

    def warning(self, message):
        self.error(message, warning=True)

    def misused(self, msg=None):
        """ exit if the command is misused, with a usage message """

        if msg:
            print msg
        self.print_usage()
        sys.exit(0)

    ### overloaded operators

    def __eq__(self, string):
        if self.name == string: 
            return True
        return string in self.aliases    

    def __call__(self):
        """ 
        should be overwritten with parsing logic
        for subclass
        """
        raise NotImplementedError

    ### functions related to editting files
    def edit(self, filename):

        # get the editor
        editor = self.options['editor-cmd']
        if not editor:
            for i in 'SVN_EDITOR', 'VISUAL', 'EDITOR':
                editor = os.environ.get(i, None)
                if editor: break
            else:
                self.error('Editor not defined.  use --editor-cmd or set EDITOR')

        # call the global edit function
        edit(filename, editor)

    ### functions for parsing

    def parse_args(self, *args):
        """
        universal top-level parsing.
        should be overwritten with parsing logic
        for subclass
        """

        ( options, args ) = OptionParser.parse_args(self, list(args))

        # XXX ug, this is hackish.  the interface needs to be changed
        # file-wide
        options = options.__dict__
        
        # parse the mode if it exists
        if options.get('CVSROOT', None):
            if options['mode']:
                self.error("mode overspecified: can't use --cvs and --%s" % options['mode'])
            options['mode'] = 'cvs'
            
        return options, args            

    def parse_bundles(self, *args):
        """ return a list of bundles from arguments """
        
        bundlelist = []
        
        if len(set(args)) != len(args):
            self.error('bundles given more than once')

        for i in args:
            bundle = self.check_bundle(i)
            if bundle:
                bundlelist.append(bundle)
            else:
                self.error('"%s" is not a bundle' % i)

        return bundlelist

    ### functions for command line arg parsing

    def brace(self, argument):
        """ surround the string argument with braces """
        return self.braces[0] + argument + self.braces[-1]

    def optbrace(self, argument):
        """
        surround the string argument with braces
        denoting it as optional
        """
        return self.optbraces[0] + argument + self.optbraces[-1]

    def add_modes(self):
        """ add modes for command-line parsing """

        self.add_option("--cvs", dest="CVSROOT")
        self.add_option("--svn", action="store_const",
                                  const="svn", dest="mode")
        self.add_option("--tgz", action="store_const", 
                                  const="tgz", dest="mode")

    def add_argument(self, **kwargs):
        """ add an positional argument to a list """
        
        self.arguments.append(kwargs)
        self.arguments[len(self.arguments) - 1]['parsed'] = None
    
    def add_command(self, name='command', optional=True):        
        self.add_argument(type='command', name=name, optional=optional)

    def add_path(self, name='path', optional=True):
        self.add_argument(type='path', name=name, optional=optional)

    def add_bundle(self, name='bundle', optional=True):
        self.add_argument(type='bundle', name=name, optional=optional)

    def add_bundles(self, name='bundle', optional=True):
        self.add_argument(type='bundles', name=name, optional=optional)

    def add_externals(self, optional=True, settable=False):
        self.add_argument(type='externals', name='external', optional=optional, 
                        settable=settable)

    def option_string(self):
        """ returns the option string the command takes """

        option_list = []
        for i in self.arguments:
            type = i['type']
            if i['optional']:
                b = self.optbrace
            else:
                b = self.brace
            if type == 'bundle':
                option_list.append(b(i['name']))
            elif type == 'bundles':
                if i['optional']:
                    ct = 2
                    s = ''
                else:
                    ct = 1
                    s = self.brace(i['name']) + " "
                    b = self.optbrace
                s += ' '.join([b(i['name']) for j in range(ct)] + [b('...')])

                option_list.append(s)
            elif type == 'externals':
                name = i['name']
                ext = ''
                if i['settable']:
                    ext = '=...'
                s = ','.join([name + str(j) + ext for j in range(2)] + ['...'])
                if i['optional']:
                    s = b(s)
                option_list.append(s)
            else:
                option_list.append(b(i['name']))
        
        return ' '.join(option_list)

    def parse_externals_string(self, extstring):
        """ parses an external string given by the command line """

        root = self.options.get('CVSROOT', None)
        self.externals = []
        isset = False

        externals = extstring.split(',')
        for i in externals:
            if '=' in i:
                isset = True
                name, repo = i.split('=')

                if repo.startswith('r'): # revision
                    repo = repo.split(':',1)
                    if len(repo) == 2:
                        revision, repo = repo
                    else:
                        revision = repo[0]
                        repo = None
                else:
                    revision = None

            else:
                name = i
                repo = None
                revision = None
                
            # sanity checking
            if revision:
                revision = revision[1:]
                if revision == 'None': # for unsetting revision pegs
                    revision = None
                elif not revision.isdigit():
                    error('Revision must be digits: "r%s"' % revision)

            self.externals.append({'name': name,
                                   'revision': revision,
                                   'repository': repo,
                                   'root': root})

        return isset

    def check_repository(self):
        # get the repository
        if not self.options['repository']:
            self.options['repository'] = '.'
            svn = SVN(self.options['repository'])
            self.options['repository'] = svn.root()
            if not self.options['repository']:
                parser.error('svn repository not specified - use "--repository"')
        else:
            if len(self.options['repository']) > 1:
                self.options['repository'] = self.options['repository'].rstrip('/')
            svn = SVN(self.options['repository'])        
            if not svn.root():
                parser.error('"%s" is not a valid repository' % 
                             self.options['repository'])                     


    ### functions central to bundles
    
    def is_bundle(self, repo):
        """ returns whether the repo is a bundle or not """
        # XXX now there is now bundle checking!
        # XXX this should always be true for a legitimate svn uri
        try:
            svn = SVN(repo)
            return True
        except Repository.RepositoryError:
            return False
        

    def check_bundle(self, bundle):
        """ 
        checks if bundle is a legitimate bundle
        if so, return a dictionary about it
        if not, return None
        """

        # is the bundle a fully qualified svn uri?
        if is_svn_uri(bundle):
            return {'name': bundle,
                    'directory': None,
                    'location': bundle}

        # is the bundle a (checked out) directory on disc?
        if os.path.exists(bundle) and self.is_bundle(bundle):
            svn = SVN(bundle)
            
            return {'name': bundle,
                    'directory': os.path.realpath(bundle),
                    'location': svn.info()['URL']}
        
    def check_bundles(self, repo, bundles):
        svn = SVN(repo)

        return [ i.rstrip('/') for i in bundles 
                 if self.is_bundle(svn.join(i)) ] 
        
    ### functions for checking out temporary copies of repositories

    def make_working_dir(self):
        """ makes a temporary working directory """
        self.dir_name = os.path.realpath(tempfile.mkdtemp(prefix='.externalator-tmp'))

    def checkout_bundles(self, bundlelist):

        tocheckout = [ i for i in bundlelist if not i['directory'] ]

        if tocheckout:
            if not getattr(self, 'dir_name', None):
                self.make_working_dir()
            cwd = os.getcwd()
            os.chdir(self.dir_name)
        else:
            return
                

        for i in tocheckout:

            dirname = os.path.join(self.dir_name, i['name'])
            svn = SVN(i['location'])
            svn('co', '--ignore-externals', i['location'], 
                dirname)
            i['directory'] = dirname
            
    def checkin_bundles(self, message, bundle=None):
        """ checkin bundles in the temporary directory """

        if not bundle:            
            thebundles = [ os.path.join(self.dir_name, bundle) ]
        else:
            thebundles = [ os.path.join(self.dir_name, i) 
                            for i in os.listdir(self.dir_name) ]

        svn = SVN(repository)

        for i in thebundles:
            svn('commit', i, '-m', message)            

    ### functions for dealing with externals

    def get_externals(self, m=modes):
        """  get the externals for the bundles """

        self.extdict = {}

        for i in self.bundle_list:
            thedict = self.extdict[i['name']] = {}
            repo = i['directory'] or i['location']
            for j in m:
                thedict[j] = parse_externals(repo, j)

    def set_externals(self, m, mode=''):
        """
        set the externals to the bundles.
        assumes the bundles have already been checked out
        """
        
        functions = { 'svn': self.svn_externals,
                      'cvs': self.cvs_externals,
                      'tgz': self.tgz_externals }        

        # write the commit message
        commit_message, filename = tempfile.mkstemp()
        
        message = self.options['message']
        if message:
            os.write(commit_message, message)

        os.write(commit_message, '\n-- externals changes --\n')

        for i in self.externals:
            s = ' '.join([ i[j] for j in display[m] if i[j] ]) + '\n'
            if mode:
                s = ' '.join((mode, s))
            os.write(commit_message, s)
        os.close(commit_message)

        if not message:
            self.edit(filename)

        # set the externals properties
        for i in self.bundle_list:
            svn = SVN(i['location'])
            
            string = functions[m](i['name'])
            if string:
                tmpfile, tmpfilename = tempfile.mkstemp()
                os.write(tmpfile, string)
                os.close(tmpfile)
                svn('propset', svn_props[m], '-F', tmpfilename, 
                    i['directory'])
                os.remove(tmpfilename)
            
            svn('commit', '--file', filename, i['directory'])
                
        # remove the temporary file
        os.remove(filename)        

    def svn_externals(self, bundle):
        """ 
        returns a string corresponding to the svn:externals property 
        """

        retval = []
        for i in self.extdict[bundle]['svn']:
            s = i['name'] + " "
            if i['revision']:
                s += "-r" + i['revision'] + " "
            s += i['repository']
            retval.append(s)
        return '\n'.join(retval) + '\n'

    def cvs_externals(self, bundle):
        """ 
        returns a string corresponding to the externalator:cvs property 
        """

        def sort_cvslist(thelist):
            retval = {}
            for i in thelist:                
                if not retval.has_key(i['root']):
                    retval[i['root']] = []
                retval[i['root']].append(i)
            return retval                

        cvslist = sort_cvslist(self.extdict[bundle]['cvs'])
        
        s = ""
        for root in cvslist:
            if not root:
                self.error("cvs externals -- CVSROOT unspecified!")
            s += "CVSROOT=%s\n" % root
            for item in cvslist[root]:
                s += "%s %s\n" % ( item['name'], item['repository'] )
        return s 

    def tgz_externals(self, bundle):
        """
        returns a string corresponding to the externalator:tgz property 
        """

        retval = [ i['name'] for i in self.extdict[bundle]['tgz'] ]
        return '\n'.join(retval) + '\n'

    def modify_externals(self, mode):
        # let python raise an error if the mode is illegal
        [ 'add', 'set' ].index(mode)

        # check out the bundles
        self.checkout_bundles(self.bundle_list)

        # get the externals dictionary for the bundles
        self.get_externals()

        # update the externals dictionary according to the command line
        for i in self.bundle_list:
            ext = self.extdict[i['name']][self.options['mode']]
            for external in self.externals:
                thedict = [ tmp for tmp in ext
                            if tmp['name'] == external['name'] ]

                # report duplicate externals
                if len(thedict) > 1:
                    self.error('Multiple entries for external "%s".  Please fix!' % external)

                    
                if not thedict:
                    ext.append(external)
                else:
                    if mode == 'add':
                        self.write('External %s already set for %s' % ( external, i['name'] ))
                        continue

                    thedict = thedict[0]
                    for i in external.keys():
                        if i == 'revision':
                            thedict[i] = external[i]
                        elif external[i]:
                            thedict[i] = external[i]
 
        # set the externals
        m = ''
        if mode == 'add':
            m = '+'
        self.set_externals(self.options['mode'], m)

        return ''

    def modify_externals_parse(self, *args):
        # parse the mode
        options, args = ExternalatorCommand.parse_args(*args)
        if args == False:
            return False

        # check number of arguments
        if not len(args):
            self.error('Not enough arguments to %s' % self.name)
        
        # get the externals
        self.parse_externals_string(args[0])
        
        # get the bundles
        if len(args) > 1:
            self.bundle_list = self.parse_bundles(*args[1:])
        else:
            self.bundle_list = self.parse_bundles('.')

        # assume svn mode by default
        if not self.options.get('mode', None):
            self.options['mode'] = 'svn'

## -> commands superficially similar to svn

class AddCommand(ExternalatorCommand):
    """ add external(s) to bundle(s) """

    def __init__(self):
        ExternalatorCommand.__init__(self)
        self.name = 'add'
        self.add_externals(optional=False, settable=True)
        self.add_bundles()
        self.add_modes()

    def parse_args(self, *args):
        if not self.modify_externals_parse(self, *args):
            return False

        # check externals to ensure repository is added
        for i in self.externals:
            if not i['repository']:
                if self.options['mode'] == 'tgz':
                    i['repository'] == i['name']
                else:
                    self.error('Repository location not given for external %s' % i['name'])

    def __call__(self):
        return self.modify_externals('add')

class CheckoutCommand(ExternalatorCommand):
    """ checkout a bundle and external dependencies """

    def __init__(self):
        ExternalatorCommand.__init__(self)
        self.name = 'checkout'
        self.aliases = ('co',)
        self.add_bundle(optional=True)
        self.add_path(optional=True)

    def parse_args(self, *args):
        if len(args) > 2:
            self.misused("Too many arguments to the %s command" % self.name)

        if not args:
            self.bundle_list = [ self.check_bundle('') ]
            self.path = '.'
        elif len(args) == 1:
            bundle = self.check_bundle(args[0])
            if bundle:
                self.bundle_list = [ bundle ]
            else:
                self.bundle_list = [ self.check_bundle('') ]

            self.path = args[0]

        else:  # two arguments
            bundle = self.check_bundle(args[0])
            self.bundle_list = [ bundle ]
            self.path = args[1]                    

        # make sure you have bundles to operate on
        if not [ i for i in self.bundle_list if i]:
            self.misused('No bundle found')

    def __call__(self):
        self.get_externals()
        bundle = self.bundle_list[0]
        svn = SVN(bundle['location'])
        svn.checkout(path=self.path)

        cwd = os.getcwd()
        os.chdir(self.path)

        external = self.extdict[bundle['name']]

        for item in external['cvs']:
            # CVS externals
            repo = CVS(item['root'])
            repo.checkout(item['repository'], item['name'])
            
        for item in external['tgz']:
            # TGZ externals
            repo = TGZ(item['repository'])
            repo.checkout()
        
        os.chdir(cwd)
        return ''

class DeleteCommand(ExternalatorCommand):
    """ remove external(s) from bundle(s) """

    def __init__(self):
        ExternalatorCommand.__init__(self)
        self.name = 'delete'
        self.aliases = ('del', 'remove', 'rm')
        self.add_externals(optional=False, settable=False)
        self.add_bundles()

    def parse_args(self, *args):
        if not args:
            self.error('Not enough arguments to %s' % self.name)

        self.parse_externals_string(args[0])

        # make sure the user isn't trying to set the externals
        for i in self.externals:
            if i['revision'] or i['repository']:
                self.error("Can't specify externals repository or version information with %s" % self.name)

        args = args[1:]
        if not args:
            args = ('.',)
        self.bundle_list = self.parse_bundles(*args)

    def __call__(self):
        # get the externals for the bundles
        self.get_externals()

        # keep track of what has changed
        changed = dict(zip(modes, [ False for i in modes ] ))

        ext = [ i['name'] for i in self.externals ]

        # remove the externals from internal storage
        for i in self.bundle_list:
            for j in self.extdict[i['name']]:
                for k in self.extdict[i['name']][j]:
                    if k['name'] in ext:
                        self.extdict[i['name']][j].remove(k)
                        changed[j] = True

        # commit the changes
        self.checkout_bundles(self.bundle_list)
        for j in changed:
            if changed[j]:
                self.set_externals(j, '-')

        return ''

class DiffCommand(ExternalatorCommand):
    """ difference between two bundles """
    
    def __init__(self):
        ExternalatorCommand.__init__(self)
        self.name = 'diff'
        self.aliases = ('di',)
        self.add_bundle(name='from-bundle', optional=True)
        self.add_bundle(name='to-bundle', optional=False)

    def parse_args(self, *args):
        if len(args) > 2:
            self.error("Too many argumentss given to %s" % self.name)
        if not args:
            self.error("Not enought argumentss given to %s" % self.name)

        if len(args) == 2:
            self.from_bundle = args[0]
            self.to_bundle = args[1]
        else:
            self.from_bundle = '.'
            self.to_bundle = args[0]

        self.bundle_list = self.parse_bundles(self.from_bundle, 
                                              self.to_bundle)

    def __call__(self):
        self.get_externals()

        fromext = {} # items in from_bundle not in to_bundle
        toext = {} # items in to_bundle not in from_bundle
        changedext = {} # items in both bundles, but not set the same

        for j in 'svn', 'cvs', 'tgz':
            fromext[j] =[]
            toext[j] = []
            changedext[j] = []

            for k in self.extdict[self.from_bundle][j]:
                for kk in self.extdict[self.to_bundle][j]:
                    if k['name'] == kk['name']:
                        if k != kk:
                            changedext[j].append((k, kk))
                        kk['found'] = True # mark it found
                        break
                else:
                    fromext[j].append(k)
                    
            for k in self.extdict[self.to_bundle][j]:
                if not k.has_key('found'):
                    toext[j].append(k)
        
        s = StringIO.StringIO()

        for j in 'svn', 'cvs', 'tgz':
            for i in fromext[j]:
                print >> s, '+', print_external(i, j)
            for i in toext[j]:
                print >> s, '-', print_external(i, j)
            for i in changedext[j]:
                print >> s, print_external(i[0], j), '->', print_external(i[1], j)
      
        return s.getvalue()
                            

class HelpCommand(ExternalatorCommand):
    """ gives help on a given command """
    
    def __init__(self):
        ExternalatorCommand.__init__(self)
        self.name = 'help'
        self.aliases = ('?', 'h')
        self.add_command(optional=False)

    def parse_args(self, *args):
        if not args:
            self.write(self.long_help())
            self.write(list_commands('Available commands:'))

        for i in args:
            for j in commands:
                if j == i:
                    self.write(j.long_help())
                    break
            else:
                self.error('Unknown command: "%s"' % i)

    def __call__(self):
        return self.output()
                

class ListCommand(ExternalatorCommand):
    """ lists bundles in a repository """
    
    def __init__(self):
        ExternalatorCommand.__init__(self)
        self.name = 'list'
        self.aliases = ('ls',)
        self.repolist = None

    def parse_args(self, *args):
        if len(args) != 1:
            self.misused("Command takes one argument")
        self.repo = args[0]

    def __call__(self):
        svn = SVN(self.repo)

        self.write("Finding bundles in %s :" % self.repo)
        bundles = self.find_bundles(self.repo)
        if not bundles:
            self.write("No bundles found")
        else:
            self.write('\n'.join(bundles))

        return self.output()
                   
    ### functions central to finding + listing bundles

    def build_repo_list(self, repo):
        """ build a recursive listing of the whole repository """

        svn = SVN(repo)
        self.repolist = svn.ls(recursive=True)


    def find_bundles(self, repo):
        """ find all bundles in the repository and return a list """

        svn = SVN(repo)
        
        bundlelist = []
        
        if not self.repolist:
            self.build_repo_list(repo)

        if self.is_bundle(repo):
            bundlelist.append(repo)

        # only consider directories
        bundlelist += self.check_bundles(repo, [ i for i in self.repolist 
                                                if i.endswith('/') ])
        

        return bundlelist

    def list_bundles(self, repo):
        svn = SVN(repo)
        bundlelist = []
        if self.is_bundle(repo):
            bundlelist.append(repo)
            # should i return here?
            
        bundlelist += self.check_bundles(repo, [i for i in svn.ls(repo)
                                                if i.endswith('/')])
        return bundlelist

class MergeCommand(ExternalatorCommand):
    """ merge external dependencies between bundles """

    def __init__(self):
        ExternalatorCommand.__init__(self)
        self.name = 'merge'
        self.add_bundle(name='from-bundle', optional=False)
        self.add_bundles(name='to-bundle', optional=False)

    def parse_args(self, *args):
        if len(args) < 2:
            self.misused('Not enough arguments to %s' % self.name)

        self.from_bundle = args[0]
        self.bundle_list = self.parse_bundles(*args)

    def __call__(self):
        m = modes
        self.get_externals(m)

        for i in self.bundle_list[1:]:
            for j in m:
                fromlist = self.extdict[self.from_bundle][j]
                tolist = self.extdict[i['name']][j]
                
                for k in fromlist:
                    match = [ tmp for tmp in tolist 
                              if tmp['name'] == k['name'] ]
                    if len(match) > 1:
                        error('Multiple entries for external "%s" in bundle "%s".  Please fix!' % (k['name'], i['name']))
                    elif len(match) == 1:
                        match[0].update(k)
                    else:
                        tolist.append(k)

        # fill out message for svn commit
        self.options['message'] = ('merging externals from %s' % 
                                   self.from_bundle)
        self.externals = '' # dummy string for svn commit
        for j in m:
            self.set_externals(j)
                
    
class UpdateCommand(ExternalatorCommand):
    """ update bundles and external dependencies """
    
    def __init__(self):
        ExternalatorCommand.__init__(self)
        self.name = 'update'
        self.aliases = ('up',)
        self.add_path()

    def parse_args(self, *args):
        if not args:
            args = ('.')

        self.bundle_list = self.parse_bundles(*args)

        for i in self.bundle_list:
            if not i['directory']:
                self.error('bundle %s not on disk' % i['name'])

    def __call__(self):

        extlist = ['cvs', 'tgz' ]

        self.get_externals(extlist)

        for i in self.bundle_list:
            # update svn
            svn = SVN(i['location'])
            svn.update(i['directory'])

            # update '3rd party' externals
            cwd = os.getcwd()
            for j in self.extdict[i['name']]['cvs']:
                cvs = CVS(j['root'])
                os.chdir(i['directory'])
                path = j['name']
                if os.path.exists(path):
                    # update the external if it exists
                    cvs.update(path)
                else:
                    # checkout the external
                    cvs.checkout(j['repository'], path)
            os.chdir(cwd)

            for j in self.extdict[i['name']]['tgz']:
                tgz = TGZ(j['repository'])
                tgz.update(i['directory'])
            
            return ''

## -> commands that don't correspond to svn commands

class FreezeCommand(ExternalatorCommand):
    """ peg all unpegged svn externals to the current version """

    def __init__(self):
        ExternalatorCommand.__init__(self)
        self.name = 'freeze'
        self.add_bundle()

    def parse_args(self, *args):        

        # attempt to use the cwd as a bundle if no arguments
        if not args:
            args = ('.', )

        if len(args) > 1:
            self.misused("Too many arguments to %s" % self.name)

        self.bundle_list = self.parse_bundles(*args)
        

    def __call__(self):

        # get the externals
        self.get_externals()

        # if revision isn't set, peg it to the current
        for i in self.bundle_list:

            # currently only svn externals can be pegged
            for j in self.extdict[i['name']]['svn']:
                if not j['revision']:
                    svn = SVN(j['repository'])
                    j['revision'] = svn.info('Revision')

        # set the externals
        self.set_externals('svn')

class GetCommand(ExternalatorCommand):
    """ display the svn externals of bundle(s) """

    def __init__(self):
        ExternalatorCommand.__init__(self)
        self.name = 'get'
        self.add_externals()
        self.add_bundles()
        self.add_modes()

    def parse_args(self, *args):

        length = len(args) # initial length of arguments
        
        # attempt to use the cwd as a bundle if no arguments
        if not args:
            args = ('.', )
            

        # get bundles and externals
        if (self.is_bundle(args[0])):
            self.bundle_list = self.parse_bundles(*args)
        else:
            if not length:
                self.misused()
            
            self.parse_externals_string(args[0])
            if args[1:]:
                self.bundle_list = self.parse_bundles(*args[1:])
            else:
                self.bundle_list = self.parse_bundles('.')
        
        self.externals = getattr(self, 'externals', [])

        # make sure the user isn't trying to set the externals
        for i in self.externals:
            if i['revision'] or i['repository']:
                self.error("Can't specify externals repository or version information with %s" % self.name)

        # replace externals list of dictionaries with a flat list
        self.externals = [ i['name'] for i in self.externals ]

    def __call__(self):
        # if mode not specified, use all modes
        if self.options['mode']:
            m = [ self.options['mode'] ]
        else:
            m = modes
                            
        self.get_externals(m)

        found = [ False for item in self.externals ]

        retval = StringIO.StringIO()
        # display the externals
        for i in self.bundle_list:
            print >> retval, i['name']
            for j in m:
                ext = self.extdict[i['name']][j]

                table = []
                min_table_size = 0
                # don't display the 1-item header 
                # for tarball externals
                if j != 'tgz':
                    table = [ display[j] ]
                    min_table_size = 1

                if self.externals:
                    ext = [ tmp for tmp in ext 
                            if tmp['name'] in self.externals ]
                    
                    for index in range(len(self.externals)):
                        name = self.externals[index]
                        row = [ [ str(k[n]) for n in display[j] ]
                                for k in ext if k['name'] == name ]
                        if row:
                            if found[index]:
                                error('External "%s" already found!  Having multiple externals with the same name can cause issues!' % name, warning=True)
                            else:
                                found[index] = True
                        
                        table += row
                else:
                    table += [ [ str(k[n]) for n in display[j] ] 
                               for k in ext ]

                # display the table
                if len(table) > min_table_size:
                    print >> retval, "%s externals:" % j
                    for row in print_table(table):
                        print >> retval, row
                    print >> retval, ""
                else:
                    if not self.externals:
                        print >> retval, 'No %s externals' % j

            # display the externals that aren't found
            if self.externals:
                for index in range(len(self.externals)):
                    if not found[index]:
                        print >> retval, 'No external "%s" found in %s bundle' % ( self.externals[index], i['name'] )

            return retval.getvalue()

class SetCommand(ExternalatorCommand):
    """ set the svn externals of bundle(s) """

    def __init__(self):
        ExternalatorCommand.__init__(self)
        self.name = 'set'
        self.add_externals(optional=False, settable=True)
        self.add_bundles()
        self.add_modes()

    def parse_args(self, *args):
        return self.modify_externals_parse(self, *args)

    def __call__(self):
        return self.modify_externals('set')
        
def set_commands():
    """  set up the list of commands globally """

    commands = [x() for x in globals().values()
                if isinstance(x, type)
                and issubclass(x, ExternalatorCommand)
                and x is not ExternalatorCommand]
    commands.sort()
    globals()['commands'] = commands

# setup the global command
set_commands()

### functions for parsing and UI

def list_commands(header="Available subcommands:"):
    string = header + '\n'
    for i in commands:
        string += "   " + i.names() + '\n'
    return string

def get_command(*args):
    """ 
    returns the first command found in args
    and the remaining args
    """

    for i in range(len(args)):
        for j in commands:
            if j == args[i]:
                return j, args[:i] + args[i+1:]

    return None, args

def readconfigfile(configfile=None):
    """ reads a user's config file """

    if configfile is None:        
        configfile = os.path.join(os.environ.get('HOME', ''), 
                                  '.externalator')

    try:
        execfile(configfile)
    except IOError:
        return {}

    retval = locals().copy()
    retval.pop('configfile')
    return retval

def parse_options(parser, args=None):
    """ parses command-line options """

    if args is None:
        args = sys.argv[1:]

    # setup command-line for usage display
    parser.add_command(name='global_options')
    parser.add_command(name='subcommand', optional=False)
    parser.add_command(name='command_options')
    parser.add_command(name='arguments')

    parser._usage = '\n\n' + list_commands()

    # if no arguments, display usage
    if not args:
        parser.misused()

    # find the command
    command, args = get_command(*args)

    # if the command exists, set the parser equal to it
    if command:
        parser = command

    # add global options
    # XXX this should probably live with the commands
    parser.add_option("-v", "--verbose", action="count", dest="verbose")
    parser.add_option("-m", "--message", dest="message", 
                      help="message to use for svn commits")
    parser.add_option("--readme", action="store_true", dest="readme")
    parser.add_option("--editor-cmd", dest="editor-cmd",
                      help="which command to invoke for editting")

    # parse global options
    options, args = ExternalatorCommand.parse_args(parser, *args)

    # print readme info if --readme is used
    if options['readme']:
        command = [ i for i in commands if i == 'help' ][0]

        for i in commands:
            command.parse_args(i.name)
        sys.exit(0)

    # ensure a command was given
    if not command:
        parser.misused('You must give a command name (try "help")')

    return command, options, args

### entry point function

def main(args=sys.argv[1:]):

    # setup global commands
    set_commands()

    # construct top-level parser
    parser = ExternalatorCommand()

    # parse options
    command, options, args = parse_options(parser, args)

    # set the options on the bundles
    command.options = options

    # parse command options
    command.parse_args(*args)

    # execute the parsed command and return its string
    return command()

if __name__ == '__main__':
    s = main()
    if s: 
        print s
