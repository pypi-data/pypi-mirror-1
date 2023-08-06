gocept.cxoracle - A zc.buildout recipe to easily get cx_Oracle running
======================================================================

The main purpose is to set up the environment required to build a cx_Oracle egg
and then provide a loader which sets environment variables required to load the
shared libraries.

Oracle doesn't allow the libraries required to be distributed freely. That
means that they must be downloaded by the user or developer from
http://www.oracle.com/technology/software/tech/oci/instantclient/index.html

Two archives are required per architecture / operating system:

1. Instant client basic lite
2. The SDK

>>> import os.path
>>> basiclite = os.path.join(
...     os.path.dirname(__file__), 'basiclite-linux.zip')
>>> sdk = os.path.join(
...     os.path.dirname(__file__), 'sdk-linux.zip')

Both files have to be configured in the buildout:

>>> write("buildout.cfg", """
... [buildout]
... parts = python-oracle
... python = python-oracle
...
... [python-oracle]
... recipe = gocept.cxoracle
... instant-client = %(basiclite)s
... instant-sdk = %(sdk)s
...
... """ % {'basiclite': basiclite,
...        'sdk': sdk}
... )

>>> print system(buildout),
Installing python-oracle.

We have an oracle-home now in the parts. It contains the contents of both
archives mixed together *plus* a symlink for ``libclntsh.so ->
libclntsh.so.10.1``:

>>> ls('parts', 'python-oracle')
-  BASIC_LITE_README
-  classes12.jar
-  genezi
-  libclntsh.so
-  libclntsh.so.10.1
-  libnnz10.so
-  libocci.so.10.1
-  libociicus.so
-  libocijdbc10.so
-  ojdbc14.jar
d  sdk

>>> import os
>>> os.path.islink(os.path.join('parts', 'python-oracle', 'libclntsh.so'))
True
>>> os.readlink(os.path.join('parts', 'python-oracle', 'libclntsh.so'))
'.../parts/python-oracle/libclntsh.so.10.1'


In the bin directory there is a wrapper which sets the ``LD_LIBRARY_PATH`` (or
``DYLD_LIBRARY_PATH`` on darwin) and the ``ORACLE_HOME`` environment variables:

>>> ls('bin')
-  buildout
-  python-oracle

The wrapper can be called like any python interpreter:

>>> system(os.path.join('bin', 'python-oracle') +
...     """ -c "import os; print os.environ['ORACLE_HOME']" """)
'.../parts/python-oracle\n'

>>> script = '''\
... import os
... import sys
... if sys.platform == 'darwin':
...     varname = 'DYLD_LIBRARY_PATH'
... else:
...     varname = 'LD_LIBRARY_PATH'
... print os.environ[varname]
... '''

>>> system(os.path.join('bin', 'python-oracle') +
...     """ -c "%s" """ % script)
'.../parts/python-oracle\n'


On Mac OS X / Darwin the libraries are not called .so but .dylib. The recipe
handles this correctly:


>>> basiclite = os.path.join(
...     os.path.dirname(__file__), 'basiclite-darwin.zip')
>>> sdk = os.path.join(
...     os.path.dirname(__file__), 'sdk-darwin.zip')

Both files have to be configured in the buildout:

>>> write("buildout.cfg", """
... [buildout]
... parts = python-oracle
... python = python-oracle
...
... [python-oracle]
... recipe = gocept.cxoracle
... instant-client = %(basiclite)s
... instant-sdk = %(sdk)s
...
... """ % {'basiclite': basiclite,
...        'sdk': sdk}
... )

>>> print system(buildout),
Uninstalling python-oracle.
Installing python-oracle.

The archives are merged as for linux, the a symlink is  ``libclntsh.dylib ->
libclntsh.dylib.10.1`` this time:

>>> ls('parts', 'python-oracle')
    -  BASIC_LITE_README
    -  classes12.jar
    -  genezi
    -  libclntsh.dylib
    -  libclntsh.dylib.10.1
    -  libnnz10.dylib
    -  libocci.dylib.10.1
    -  libociicus.dylib
    -  libocijdbc10.dylib
    -  libocijdbc10.jnilib
    -  ojdbc14.jar
    d  sdk


>>> import os
>>> os.path.islink(os.path.join('parts', 'python-oracle', 'libclntsh.dylib'))
True
>>> os.readlink(os.path.join('parts', 'python-oracle', 'libclntsh.dylib'))
'.../parts/python-oracle/libclntsh.dylib.10.1'

When an archive cannot be extracted we'll get an informative error:

>>> write("buildout.cfg", """
... [buildout]
... parts = python-oracle
... python = python-oracle
...
... [python-oracle]
... recipe = gocept.cxoracle
... instant-client = /does/not/exist
... instant-sdk = %(sdk)s
...
... """ % {'sdk': sdk}
... )

>>> print system(buildout),
Uninstalling python-oracle.
Installing python-oracle.
While:
  Installing python-oracle.
<BLANKLINE>
An internal error occured due to a bug in either zc.buildout or in a
recipe being used:
Traceback (most recent call last):
    ...
Exception: Extraction of file '/does/not/exist' failed.
