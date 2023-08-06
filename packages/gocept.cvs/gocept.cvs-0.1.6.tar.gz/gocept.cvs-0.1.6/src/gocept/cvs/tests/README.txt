Test for gocept.cvs
===================

This test suite works for the Native (with pysvn) implementation.

Setup
-----

We set up the CVS repository:

>>> import cvsrep
>>> cvstest = cvsrep.CVSTestRepository()
>>> cvstest.create()
>>> cvstest.create_testproject()

Checking out CVS links
----------------------

Create buildout using gocept.cvs:

>>> cd(sample_buildout)
>>> buildout_contents = '''
... [buildout]
... parts = cvspart
...
... [cvspart]
... recipe = gocept.cvs
... cvsroot = %s
... destination = products
... modules = gocept.test;HEAD;gocept.test''' % cvstest.cvsrep_path
>>> write('buildout.cfg', buildout_contents)


And run buildout:

>>> print system(buildout)
Installing cvspart.
U  gocept.test/.cvsignore
U  gocept.test/file
cvs checkout: Updating gocept.test

We get a part with a project checked out of the CVS:

>>> ls('parts')
d products
>>> ls('parts/products')
d gocept.test
>>> ls('parts/products/gocept.test/')
- .cvsignore
d CVS
- file


Modification
------------

If we add a file and run the recipe, this is ok:

>>> cd(sample_buildout)
>>> write('parts/products/gocept.test/README.txt', '''
... Sample file
... ''')
>>> print system(buildout)
Updating cvspart.
? gocept.test/README.txt
cvs update: Updating gocept.test

If we change the buildout.cfg and run buildout again, it should fail,
because of local modifications in the parts directory:

>>> buildout_contents = '''
... [buildout]
... parts = cvspart
...
... [cvspart]
... recipe = gocept.cvs
... cvsroot = %s
... destination = products
... modules = gocept.test;HEAD;gocept.test
...           gocept.test;HEAD;secondgocept.test''' % cvstest.cvsrep_path
>>> write('buildout.cfg', buildout_contents)

Run buildout again:

>>> print system(buildout)
Uninstalling cvspart.
Running uninstall recipe.
cvs update: Updating gocept.test
...
ValueError:
Local changes are made in gocept.test. Revert them first to update/uninstall using buildout.

After the new file is deleted, buildout runs smoothly and checks out the
second module:

>>> remove('parts/products/gocept.test/README.txt')
>>> print system(buildout)
Uninstalling cvspart.
Running uninstall recipe.
Installing cvspart.
U gocept.test/.cvsignore
U gocept.test/file
U secondgocept.test/.cvsignore
U secondgocept.test/file
cvs update: Updating gocept.test
cvs checkout: Updating gocept.test
cvs checkout: Updating secondgocept.test

If we edit a file, update buildout.cfg (removing the second module) it
should fail again:

>>> write('parts/products/gocept.test/file', 'File editing')
>>> buildout_contents = '''
... [buildout]
... parts = cvspart
...
... [cvspart]
... recipe = gocept.cvs
... cvsroot = %s
... destination = products
... modules = gocept.test;HEAD;gocept.test''' % cvstest.cvsrep_path
>>> write('buildout.cfg', buildout_contents)
>>> print system(buildout)
Uninstalling cvspart.
Running uninstall recipe.
cvs update: Updating gocept.test
...
ValueError:
Local changes are made in gocept.test. Revert them first to update/uninstall using buildout.

