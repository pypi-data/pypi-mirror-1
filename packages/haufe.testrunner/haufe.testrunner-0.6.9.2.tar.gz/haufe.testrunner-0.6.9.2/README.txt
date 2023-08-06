haufe.testrunner (HTR)
======================

haufe.testrunner is a wrapper around the standard Zope 2 testrunner (usually
started using "zopectl test...".  haufe.testrunner is designed to run regular
tests for different Zope configurations or sandboxes.  It supports a
configurable testing environment, reporting in plain text or HTML, email
notifications and  RSS. haufe.testrunner is basically designed to be run
through cron in order to test ongoing projects (continues integration).

Requirements
------------

- SQLAlchemy>=0.4.6

Installation
------------

haufe.testrunner is available directly from the HaufeComponents repository::

  svn co svn+ssh://svn.haufe.de/VCS/svnrep/svnep/HaufeComponents/haufe.testrunner/trunk haufe.testrunner
  python2.4 setup.py install

or by easy_install'ing directly from the repository::

  easy_install svn+ssh://svn.haufe.de/VCS/svnrep/svnep/HaufeComponents/haufe.testrunner/trunk haufe.testrunner


or it can be installed from an existing egg using easy_install::

  easy_install haufe.runner-x.y.z.egg

Ensure that your PYTHONPATH is set properly and included
$SOFTWARE_HOME/lib/python (in order to import zope.component and other Zope 3
related modules properly)


Using haufe.testrunner
----------------------

haufe.testrunner will install a command-line skript ``htr``.  ``htr`` requires
a configuration file that defines your testing environment. 

Example::


    [default]

    # Path to instance home of sandbox
    sandbox=/home/ajung/sandboxes/Zope-2.8/Zope

    # unique string for the sandbox (used for mail, reports)
    ident=Zope-HEAD

    # comma-seperated list of products or packages to be tested
    packages = Products.PageTemplates, 
               Products.HaufePortlet,
               zope.component

    # comma-seperated list of email addresses to send positive emails
    email_ok=foo@bar.org

    # comma-seperated list of email addresses to send negative emails
    email_failure=foo@bar.org

    # Base URL of the webserver pointing to your sandbox
    base_url=http://zopedev2/zopeDominoTesting

    # run testrunner with coverage option (optional, default: no coverage)
    coverage = 1

    # Database DSN
    dsn = postgres://user:password@host/dbname

    # optional support for integration tests:
    # (the test_suite() method must check the environment variable
    # $INTEGRATION_TESTS).
    integration_tests = 1

    # optional name for zope start script default ist set to 'zopectl`
    zope_start=zopectl

    # optional paramter to set test options
    #runner_options=-s -a

    # For Selenium tests (optional) we use a dedicated [selenium] section
    [selenium]

    # hostname where the Selenium RC server is running
    testrunner_host = hostname

    # port number of the Selenium RC server
    testrunner_port = 4444 

    # instance_url - the given URL is exposed to selenium testcases derived
    # from haufe.selenium.SeleniumTestcase as self.instance_url. This allows
    # you to run Selenium tests against different remote servers
    instance_url = http://zopedev2:16180


    # For integration tests we can run the tests against an existing ZEO server
    # instead of using DemoStorage
    [zeo]
    host = zopedev2
    port = 22222
    


Start haufe.testrunner using::

    htr --conf /path/to/yourconfig

The optional options --mail and --rss control the generation of mail
notifications and a RSS feed. If you specify --update then haufe.testrunner
will update your **Products**,  **lib/python** and **Base** directory before
running the tests.

--clean will remove directories with testrunner logs that are older than one
week

--db will save all results within a database (see below)


Database integration:
---------------------

All results can be optionally stored within a relational database 
(for external reporting, RSS feeds, webfrontend etc.).

Creating the database::

   htr_bootstrap -dt 

The database must be specified using the environment variable TESTING_DSN,
e.g.::

    export TESTING_DSN=postgres://username:password@dbhost/TestrunnerDB

For storing the results within the database pass the --db option to the 
``htr`` script.

The DSN can also specified using the 'dsn' option within the configuration 
file (see above).

You need to create the database first by calling the htr_bootstrap script first
(see above).


Author
------
``haufe.testrunner`` was written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
and ZOPYX Ltd. & Co. KG, Tuebingen, Germany.


License
-------
``haufe.testrunner`` is licensed under the Zope Public License 2.1.

See the included ZPL.txt file.


Contact
-------

| ZOPYX Ltd. & Co. KG
| Andreas Jung
| Charlottenstr. 37/1
| D-72070 Tuebingen, Germany
| E-mail: info at zopyx dot com
| Web: http://www.zopyx.com
