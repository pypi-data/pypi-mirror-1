Normally svn:externals are read from a file and set by a string.
Since bundles have potentially large numbers of svn:externals,
maintaining them from a file or as strings can be problematic,
especially since the bundle must be downloaded before it can be acted
upon (a limitation of svn).

The goal of externalator is to allow setting (changing, unsetting)
individual or groups of externals from the command line on a bundle or
a group of bundles.

