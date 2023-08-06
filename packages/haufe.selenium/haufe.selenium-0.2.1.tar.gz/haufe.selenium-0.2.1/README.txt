haufe.selenium
==============

A wrapper for controlling the Selenium remote server. The Selenium RC server
is a Java-based server for the remote executing of Selenium tests.

See also::

    http://www.openqa.org/selenium-rc/

Installation
------------

Use easy_install::

    easy_install --no-deps haufe.selenium


Usage
-----

You can control the server process using ``selsrvctl``::

    selsrvctl start | stop | status | foreground | fg


SeleniumTestcase
----------------

haufe.selenium also provides a dedicated testcase that should be used as a base
class for all Selenium related unittests.

Configuration through environment variables:

**SELENIUM_HOST**  - defines the hostname where the Selenium remote server
is running

**SELENIUM_PORT** - defines the port of the Selenium remote server

**SELENIUM_BROWSER** -  the browser name to be used for running tests (`*iexplore`, `*firefox`, ...). 
Check the Selenium RC server documentation for details

**SELENIUM_INSTANCE_URL** -  the base URL of the webserver to be used to run
the test against. The URL must not contain any path information - only
something like::
    
    http://host:port


Licence
-------
This package is released under the LGPL 2.1. See LICENSE.txt.

Copyright
---------
haufe.selenium is (C) Andreas Jung & Haufe Mediengruppe, D-79111 Freiburg, Germany
