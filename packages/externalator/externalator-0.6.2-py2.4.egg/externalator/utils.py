""" 
Generic functions needed by externalator.
These can live anywhere, maybe should be part of a library.
"""

import os
import re
import shlex
import subprocess

### functions for uri parsing

def uri_re_string(scheme=('http','https')):
    """ returns a regular expression pattern for matching uris """

    if scheme:
        scheme = r'(' + r'|'.join(scheme) + r')' + r'://'
    else:
        scheme = r''        
    return ( r'^' + scheme + r'(?:[/a-z0-9\-]+|[a-z0-9][a-z0-9\-\.\_]*\.[a-z]+)'
             + r'(?::[0-9]+)?' + r'(?:/.*)?$' )

url_re = re.compile(uri_re_string(), re.I)

def is_url(string):
    """ indicates if the given string is legitimate url syntax """

    if re.match(url_re, string):
        return True
    return False

### misc functions

def memoize(f):
    """ decorator to cache the result of a function """

    result = []
    def wrapped(*args, **kw):
        if not result:
            result.append(f(*args, **kw))
        return result[0]
    return wrapped

def read_dictionary(strings, char=":"):
    """ reads a list of strings into a dictionary based on a separator """
    
    # if strings is a string, split it by line
    # otherwise, assume its a sequence
    if isinstance(strings, basestring):
        strings = strings.splitlines()

    return dict([ [n.strip() for n in  i.split(char, 1)] for i in strings if i])

def print_table(table, joiner=' '):
    """ 
    return a list of strings from a table (list of lists with the
    same number of columns
    """

    strings = []
    if not table:
        return strings
    ncol = len(table[0])
    cols = range(ncol)
    maxlen = [ 0 for i in cols ]
    for i in table:
        if len(i) != ncol:
            return None
        for j in cols:
            length = len(i[j])
            if length > maxlen[j]:
                maxlen[j] = length
        
    for i in table:
        strings.append(joiner.join([ i[j].ljust(maxlen[j]) for j in cols ]))
            
    return strings

def edit(filename=None, editor=None):
    """ edit a file in an external editor """    

    if not filename:
        filename = tempfile.mktemp()

    if not editor:
        editor = os.environ.get('EDITOR', 'vi')

    cmdline = shlex.split(editor)
    cmdline.append(filename)

    j = subprocess.Popen(cmdline)
    j.communicate()

    return filename
