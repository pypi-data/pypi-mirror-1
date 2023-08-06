
NoseJS is a `Nose`_ plugin to run JavaScript tests using `Rhino`_ in a Java subprocess.

.. _Nose: http://www.somethingaboutorange.com/mrl/projects/nose/
.. _Rhino: http://www.mozilla.org/rhino/

.. contents::

Install
=======

First, you need to download `Rhino`_.  More on that below.

You can get NoseJS with `easy_install <http://peak.telecommunity.com/DevCenter/EasyInstall>`_ ::
    
    $ easy_install NoseJS

Or you can clone the source using `Mercurial <http://www.selenic.com/mercurial/wiki/index.cgi/Mercurial>`_ from http://bitbucket.org/kumar303/nosejs/ and install it with ::
    
    $ python setup.py develop

Usage
=====

Here is the most basic way to invoke NoseJS (assumes you've downloaded `Rhino`_ into ~/src) ::
    
    $ nosetests --with-javascript --rhino-jar ~/src/rhino1_7R1/js.jar 

This command would look for any files along Nose's path ending in .js that match Nose's current test pattern (by default: files with "test" in the name), collect them all, then execute them using Rhino in a Java subprocess at the end of all other tests.

The idea behind NoseJS is that you might have a Python web application that relies on JavaScript for some of its functionality and you want to run both Python and JavaScript tests with one command, `nosetests <http://www.somethingaboutorange.com/mrl/projects/nose/>`_.  You can put these JavaScript tests wherever you want in your project.

Here is a more realistic example that shows how the `Fudge <http://farmdev.com/projects/fudge/>`_ project is tested simultaneously for Python and JavaScript functionality.  Its project layout looks roughly like this::

    |-- fudge
    |   |-- __init__.py
    |   |-- patcher.py
    |   |-- tests
    |   |   |-- __init__.py
    |   |   |-- test_fudge.py
    |   |   |-- test_patcher.py
    |-- javascript
    |   |-- fudge
    |   |   |-- fudge.js
    |   |   |-- tests
    |   |   |   |-- test_fudge.html
    |   |   |   `-- test_fudge.js
    `-- setup.py

Both Python and JavaScript tests can be run with this command::
    
    $ nosetests  --with-javascript \
                 --rhino-jar ~/src/rhino1_7R1/js.jar \
                 --with-dom \
                 --load-js-resource jquery-1.3.1.js \
                 --load-js-resource jquery/qunit-testrunner.js \
                 --js-test-dir javascript/fudge/tests/
    ......................................................
    ----------------------------------------------------------------------
    Test Fake
      can find objects
      can create objects
      expected call not called
      call intercepted
      returns value
      returns fake
    Test ExpectedCall
      ExpectedCall properties
      call is logged
    Test fudge.registry
      expected call not called
      start resets calls
      stop resets calls
      global stop
      global clear expectations

    Loaded 6 JavaScript files

    OK
    ----------------------------------------------------------------------
    Ran 54 tests in 0.392s

    OK
    
Be sure to read the Caveats section below ;)

Specifying a path to JavaScript files
=====================================

If JavaScript files are nested in a subdirectory, like the above example, specify that directory with::
    
    $ nosetests --with-javascript --js-test-dir javascript/fudge/tests/ --js-test-dir ./another/dir

nosejs JavaScript namespace
===========================

All scripts have the ``nosejs`` JavaScript namespace available for use.  The following methods are available:

- **nosejs.requireFile(path)**
  
  - Load a JavaScript file from your test script.  If you require the same file multiple times, it will only 
    be loaded once.  If the file does not start with a slash, then it should be a path relative to the directory 
    of the script where requireFile() was called from.  For example, here is how test_fudge.js requires the 
    fudge library before testing::
        
        if (nosejs) {
            nosejs.requireFile("../fudge.js");
        }

- **nosejs.requireResource(name)**
  
  - Require a JavaScript file that is bundled with NoseJS.  There are a few available resources:
    
    jquery-1.3.1.js
        Will load the `JQuery <http://jquery.com/>`_ library before loading any other tests

    jquery/qunit-testrunner.js
        Will load a very minimal set of JavaScript functions for testing.  It is a partial implementation of the `QUnit test runner <http://docs.jquery.com/QUnit>`_ interface.  
        Supported methods: module(), test(), equals(), ok(), and expect()
    
    For example, test_fudge.js uses jquery and the testrunner ::
    
        if (nosejs) {
            nosejs.requireResource("jquery-1.3.1.js");
            nosejs.requireResource("jquery/qunit-testrunner.js");
            nosejs.requireFile("../fudge.js");
        }

Using the DOM
=============

If your JavaScript under test relies on a browser-like DOM environment, it might work :)  Just run::
    
    $ nosetests --with-javascript --with-dom

This will load John Resig's `env.js <http://ejohn.org/projects/bringing-the-browser-to-the-server/>`_ script to simulate a DOM before loading any other JavaScript.  There are a few patches that are marked with @@nosejs in the NoseJS source.

Caveats
=======

Currently if JavaScript tests fail, nosetests **will not** indicate failure.  I can't figure out a clean way to do this.  Please get in touch if you'd like to help.  In general, JavaScript tests are not very well integrated into Nose.

Contributing
============

Please submit `bugs and patches <http://bitbucket.org/kumar303/nosejs/issues/>`_.  All contributors will be acknowledged.  Thanks!
