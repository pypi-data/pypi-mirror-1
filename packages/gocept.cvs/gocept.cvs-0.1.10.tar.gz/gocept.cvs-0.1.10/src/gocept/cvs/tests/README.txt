Test for gocept.cvs
===================

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


And run buildout (with high verbosity):

>>> print system(buildout + ' -vv')
Installing 'zc.buildout', 'setuptools'.
...
verbosity = 20
[cvspart]
...
recipe = gocept.cvs
<BLANKLINE>
Installing cvspart.
U gocept.test/.cvsignore
U gocept.test/file
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

New file
~~~~~~~~

If we add a file and run the recipe, this is ok:

>>> cd(sample_buildout)
>>> write('parts/products/gocept.test/README.txt', '''
... Sample file
... ''')
>>> print system(buildout)
Updating cvspart.
? gocept.test/README.txt
>>> print system(buildout)
Updating cvspart.
? gocept.test/README.txt


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
...
ValueError:
Local changes are made in gocept.test. Revert them first to update/uninstall using buildout.
--
? gocept.test/README.txt

After the new file is deleted, buildout runs smoothly and checks out the
second module:

>>> remove('parts/products/gocept.test/README.txt')
>>> print system(buildout + ' -v')
Installing 'zc.buildout', 'setuptools'.
...
Uninstalling cvspart.
Running uninstall recipe.
Installing cvspart.
U gocept.test/.cvsignore
U gocept.test/file
U secondgocept.test/.cvsignore
U secondgocept.test/file


Changed file
~~~~~~~~~~~~

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
...
ValueError:
Local changes are made in gocept.test. Revert them first to update/uninstall using buildout.
--
M gocept.test/file

>>> remove('parts/products/gocept.test/file')
>>> print system(buildout + ' -v')
Installing 'zc.buildout', 'setuptools'.
...
Uninstalling cvspart.
Running uninstall recipe.
Installing cvspart.
U gocept.test/.cvsignore
U gocept.test/file
cvs update: warning: `gocept.test/file' was lost


Added file
~~~~~~~~~~

If we add a new file, add it to the repository the buildout should stop
as well if the part is uninstalled:

>>> write('parts/products/gocept.test/newfile.txt', 'New file')
>>> print system('cvs add parts/products/gocept.test/newfile.txt')
cvs add: scheduling file `parts/products/gocept.test/newfile.txt' for addition
cvs add: use `cvs commit' to add this file permanently

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
>>> print system(buildout)
Uninstalling cvspart.
Running uninstall recipe.
...
ValueError:
Local changes are made in gocept.test. Revert them first to update/uninstall using buildout.
--
A gocept.test/newfile.txt

>>> remove('parts/products/gocept.test/newfile.txt')
>>> print system(buildout)
Uninstalling cvspart.
Running uninstall recipe.
Installing cvspart.
cvs update: warning: new-born `gocept.test/newfile.txt' has disappeared


Deleted file
~~~~~~~~~~~~

If we remove a file ("cvs remove"), which is under version control but
do not commit yet, the buildout should stop as well if the part is
uninstalled:

>>> print system('cvs remove -f parts/products/gocept.test/file')
cvs remove: scheduling `parts/products/gocept.test/file' for removal
cvs remove: use `cvs commit' to remove this file permanently

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
...
ValueError:
Local changes are made in gocept.test. Revert them first to update/uninstall using buildout.
--
R gocept.test/file

