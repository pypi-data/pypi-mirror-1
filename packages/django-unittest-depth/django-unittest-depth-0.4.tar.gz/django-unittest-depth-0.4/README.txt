========================================
``django-unittest-depth`` Run Django unittests recursively 
========================================
:Version: 0.4 

            

=======================================
Synopsis
=======================================

I wanted a different test directory layout than the default $appname/tests.py,
so I wrote this suite set-up, so you can have directory layouts like:

    $appname/
        tests/
            __init__.py
            test_models/
                __init__.py
                test_Blog.py
                test_Author.py
                test_Repository.py
            test_views.py

instead.

To use this in your django app, you just add the following to your
$appname/tests/__init__.py module:

>>> from djangox.test.depth import alltests
...
>>> def suite():
... return alltests(__file__, __name__)
        

======================================
Installation
======================================

To install:

    >>> python ./setup.py install


Or via easy_install:

    >>> easy_install django-unittest-depth
