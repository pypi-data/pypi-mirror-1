==============================================================
``jsjquery`` Install and list jQuery as a dependency via PyPI.
===============================================================
:Version: 1.3.2

            

=======================================
Synopsis
=======================================

With this package you can install and list jQuery as a dependency
for your Python applications.

You can get the path to the jQuery javascript file in two ways,

    Via Python::

        >>> import jsjquery
        >>> jsjquery.path
        /Library/Frameworks/Python.framework/Versions/2.6/lib/
        python2.6/site-packages/jsjquery-1.3.2-py2.6.egg/
        jsjquery/jquery-1.3.2.min.js

    or via the command line with the ``python-jquery`` command::

        $ python-jquery
        /Library/Frameworks/Python.framework/Versions/2.6/lib/
        python2.6/site-packages/jsjquery-1.3.2-py2.6.egg/
        jsjquery/jquery-1.3.2.min.js

======================================
Installation
======================================

To install:

    python ./setup.py install


Or via easy_install:

    easy_install jsjquery

Or via pip:
   
    pip install jsjquery 
