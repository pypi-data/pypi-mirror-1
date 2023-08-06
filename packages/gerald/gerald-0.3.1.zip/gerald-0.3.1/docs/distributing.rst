===================
Distributing Gerald 
===================

Introduction
------------

This document describes all of the steps to be followed when packaging and releasing a version of gerald.

Checking the Code
=================

In a working copy (checked out from Subversion) first run pychecker::

    $ pychecker gerald/*.py

Then when you have fixed all of the errors and looked at each of the warnings we bring out pylint::

    $ pylint gerald

For pylint we need to make sure that we use the appropriate configuration file. The only change from the standard I've made to mine is to add the following line::

    disable-msg=W0403,R0903,W0621


Update the Documentation
========================

Generating the API Documentation
--------------------------------

The API documentation is generated using epydoc_. 
The installation instructions for epydoc_ are `here <http://epydoc.sourceforge.net/manual-install.html>`_ although you can install it under Ubuntu_ with a simple ``apt-get install python-epydoc``

To format the output in the same style as the project web site you will need to use the stylesheet (``gerald.css``) included in the ``docs`` folder of the gerald source.

Once you have both of these things to hand you can generate the API documentation from the root of the gerald source distribution with this command::

    $ epydoc -o epydoc -v --url http://halfcooked.com/code/gerald --css docs/gerald.css --no-sourcecode gerald

.. _epydoc: http://epydoc.sourceforge.net
.. _Ubuntu: http://www.ubuntu.com

Copy the contents of the epydoc directory to the project web site. 

Updating the Web Site
---------------------

Update the file called index.rst in the docs directory.

Turn it into the appropriate html file with::

    $ rst2html.py --stylesheet=gerald.css --no-doc-title --title='Gerald the half a schema' index.rst > index.html

Or just use the `genhtml.sh` script in the docs directory::

    $ genhtml.sh index

Take the resulting html file and upload it to the project web site.::

    $ scp index.html andy47@scandium.sabren.com:/home/andy47/web/halfcooked.com/code/gerald/

Releasing the Code
==================

Tag the Release
---------------

First we need to complete all of the prior steps. Then we 'tag' the release.::

    $ svn copy http://halfcooked.svn.sourceforge.net/svnroot/halfcooked/trunk http://halfcooked.svn.sourceforge.net/svnroot/halfcooked/tags/release-<revision number>

Or checkout the whole Subversion repository and then do the copy internally.::

    $ svn checkout https://halfcooked.svn.sourceforge.net/svnroot/halfcooked/ hc-root
    $ cd hc-root
    $ svn copy trunk/ tags/release-<release number>

Packaging the Code
------------------

To send it to PyPI::

    $ python setup.py sdist [ --formats=zip,gztar ] bdist_egg upload
    $ python2.5 setup.py bdist_egg upload

Or to create local copies of the source distribution files::

    $ python setup.py sdist --formats=zip,gztar

To create a .tar.gz and a .zip file.

Upload the Code to SourceForge
------------------------------

Upload the distribution files to SourceForge using their web interface. Log on to the project site at https://sourceforge.net/projects/halfcooked and navigate to the File Manager (Project Admin|File Manager)

Create a new file under ``gerald`` named for the release. Right click it and select ``Uploads here`` and then upload the source and egg files using the ``Upload file`` link.

Update PyPi
-----------

Send a notification to PYPI of the latest release. In the release directory::

    $ python setup.py register

Increment the version number
----------------------------

In the trunk, edit the `__init__.py` file in the gerald module and increment the `__version__` variable appropriately.
