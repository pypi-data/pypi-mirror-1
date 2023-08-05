distutils recipe
================

For Python packages which are only installable with distutils, and aren't
yet avaiable as eggs. This recipe will download a distutils tarball, build it
and place it inside your buildout inside a parts/site-packages directory.

It is up to you to inform your Python about this site-packages directory.
You might do this with the zc.recipe.egg recipe::

	[buildout]
	parts =
	    mypython

	[mypython]
	recipe = zc.recipe.egg
	eggs = zc.recipe.egg
	extra-paths = ${buildout:directory}/parts/site-packages/
	interpreter = mypython
	scripts = mypython


Options
-------

url
    The URL of the archives to download and install. The archive specified
    will be installed inside a site-packages directory.

build_ext
	Additional build options passed to setup.py.

To-Do
-----

Currently only enough work has been done on this recipe to get it to
install mx-base and psycopg2. There is lots of room for improvement ...

Example Usage
-------------

A sample buildout.cfg that installs mx-base and psycopg2 inside the
site-packages directory. It also installs PostgreSQL for building
psycopg2, adjusting the build_ext for psycopg2 to point to an existing
PostgreSQL install would remove the need for this:

	[buildout]
	parts =
	    egenix-mx-base
	    mypython
	    postgresql
	    psycopg2

	[egenix-mx-base]
	recipe = collective.recipe.distutils
	url = http://downloads.egenix.com/python/egenix-mx-base-3.0.0.zip

	[mypython]
	recipe = zc.recipe.egg
	eggs = zc.recipe.egg
	extra-paths = ${buildout:directory}/parts/site-packages/
	interpreter = mypython
	scripts = mypython

	[postgresql]
	recipe = zc.recipe.cmmi
	url = http://www.bcgsc.ca/downloads/parts/software/resources/src/postgresql/postgresql-8.1.9.tar.gz

	[psycopg2]
	recipe = collective.recipe.distutils
	url = http://www.bcgsc.ca/downloads/parts/software/resources/src/psycopg2/psycopg2-2.0.6.tar.gz
	build_ext = --pg-config=${buildout:directory}/parts/postgresql/bin/pg_config --rpath=${buildout:directory}/parts/postgresql/lib

