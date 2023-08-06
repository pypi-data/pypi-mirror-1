Supported options
=================

The recipe supports the following options:

Options
-------

This recipe supports the same options as the pybsddb module in
setup2.py. It accepts the names of the environment variables as
variable names and then sets those that are defined so ``pybsddb`` can
find them at build time.

  
berkeleydb_incdir
    Set the include directory

berkeleydb_libdir
    Set the lib directory

berkeleydb_dir
    Set the root of the build. If it is built in the buildout,
    I.e. ${bdb:location} if the BerkeleyDB section is named bdb.

lflags
    Set some ``LFLAGS``

libs
    Set some ``LIBS``


Example usage
=============

I don't really understand the testing environment here so the below is broken.

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = bsddb3 
    ...
    ... [bdb]
    ... location = somdir
    ...
    ... [bsddb3]
    ... recipe = koansys.recipe.pybsddb
    ... berkeleydb_dir = ${bdb:location}
    ... """
Running the buildout gives us::

    >>> print 'start', system(buildout) 
    start...
    Installing bsbddb.
    Unused options for test1: 'option2' 'option1'.
    <BLANKLINE>


