documentation:
==============

A bundle is defined as a piece of software that resides in svn that is 
chiefly or exclusively defined by svn externals.  cvs and tgz externals 
may also be included, but the bundle should live in an svn repository.
{ personal comments not to be included in the real documentation will be
included in curly braces...like this one}
{ ultimately, this documentation should largely be known by the program}

Files:
------

description.txt: file describing the bundle.  This should
contain the bundle's purpose.  Maybe more stuff here too.  Maybe this
should be upper case to match the others.

Usage:
------

externalator [program options] <command> [command options]

Program Options:
----------------

  -h, --help            show this help message and exit
  -r REPOSITORY, --repository=REPOSITORY
  -b BUNDLES, --bundles=BUNDLES
  -v, --verbose
  -s, --strict
  -n, --nostrict
  -c CONFIGFILE, --configfile=CONFIGFILE
  -m MESSAGE, --message=MESSAGE
  --readme

Commands:
---------

add: add external(s) to bundle(s)

     usage: externalator add external0=...,external1=...,... <bundle> <bundle> <...>

     format of the externals string is:
     SVN: "externalname=r1234:http://repository.net/svn" [revision number optional]

checkout (co): checkout a bundle and external dependencies

	       usage: externalator checkout [bundle] <path>

delete (del, remove, rm): remove external(s) from bundle(s)

       usage: externalator delete external0,external1,... <bundle> <bundle> <...>

diff (di): difference between two bundles

     	   usage: externalator diff <from-bundle> [to-bundle]

	   Displays differences in bundles.  If the from-bundle isn't given,
	   the cwd is assumed.

freeze: peg all externals to the current revision

	usage: externalator peg [bundle] <bundle> <bundle>

	anything that's not pegged is pegged to the current revision

get: display the svn externals of bundle(s)

     usage: externalator get <external0,external1,...> <bundle> <bundle> <...>
     
help (?, h): gives help on a given command

     usage: externalator help [command]
	
     Displays program help, or if a command is given, displays help for
     the given command.

import: create a bundle from an svn repository entry

	usage: import [repository location]:

        imports an svn directory to bundle management,or the current working 
        directory if its an svn subtree of the repository.

        This includes making some files (like an about file) and allowing the
        user to edit them with his/her favorite editor.

#info: displays information on bundle(s)
#
#      usage: externalator info <bundle> <bundle> <...>
#
#      Displays info about the bundle. This includes its purpose, 
#      the externals, repository path.
#     
#      If the bundle argument is not given, all bundles in the 
#      repository are found are their info is displayed.

list (ls): lists bundles in a repository

     usage: externalator list 

     searches for and lists all bundles in the repository.

merge: merge external dependencies between bundles

       usage: externalator merge [from-bundle] [to-bundle] <to-bundle> <...>

       merge behavior from one bundle to another. 
       This adds the externals, if they did not exist, and
       pegs them to the same revision.  

       { should this have a list of externals? }

set: set the svn externals of bundle(s)
     
     usage: externalator set external0=...,external1=...,... <bundle> <bundle> <...>

     format of the externals string is:
     SVN: "externalname=r1234:http://repository.net/svn" [revision number optional]

update (up): update bundles and external dependencies

       usage: externalator update <path>

       updates the bundle, including cvs and tgz files.
