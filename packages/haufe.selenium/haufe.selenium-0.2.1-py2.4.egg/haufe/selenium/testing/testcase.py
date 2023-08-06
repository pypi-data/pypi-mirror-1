################################################################
# haufe.selenium
# (C) 2007, Haufe Mediengruppe
################################################################

"""
Selenium Testcase
"""

import os
import unittest 
import httplib
import socket
from selenium import selenium

def click(self, locator):

    self.do_command("click", [locator,])
    self.new_wait_for_page_to_load(30000)
    html = self.get_html_source()

    assert 'ist ein Fehler aufgetreten' not in html,\
            'Last click command(%s) caused an error' % locator 
        
def wait_for_page_to_load(self, delay): pass

selenium.click = click
selenium.new_wait_for_page_to_load = selenium.wait_for_page_to_load
selenium.wait_for_page_to_load = wait_for_page_to_load



class SeleniumTestcase(unittest.TestCase):
    """ Selenium testcase to be used against a Selenium remote server.
        For implementing test cases against different browsers, you should
        subclass SeleniumTestcase and adjust the 'browser' class variable.
    """

    browser = '*firefox'   # or '*iexplore', '*opera', ....

    def setUp(self):
        self.verificationErrors = []
        secure = getattr(self, 'secure', False)
        self.host = os.environ.get('SELENIUM_HOST', 'localhost')
        if secure:
            self.port = int(os.environ.get('SELENIUM_HTTPS_PORT', '4445'))
        else:
            self.port = int(os.environ.get('SELENIUM_PORT', '4444'))
        #self.instance_url = os.environ.get('SELENIUM_INSTANCE_URL')
        for envvar in os.environ:
            if envvar.startswith('SELENIUM_INSTANCE_URL'):
                attr = envvar.replace('SELENIUM_', '', 1).lower()
                setattr(self, attr, os.environ.get(envvar))
        self.base_url = "http://%s:%d" % (self.host, self.port)

        # Check if HTTP port of the Selenium RC server is reachable
        timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(5)
        try:
            conn = httplib.HTTPConnection(self.host, self.port)
        except socket.error:
            raise IOError('Selenium RC server at %s not reachable' % self.base_url)            

        conn.request('HEAD', '/')
        resp = conn.getresponse()
        if not resp.status in (403, 200):
            raise IOError('Selenium RC server at %s not reachable' % self.base_url)            

        socket.setdefaulttimeout(timeout)
        self.selenium = selenium(self.host, self.port,  self.browser, self.base_url)
        self.selenium.start()

    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

    def do_command(self, verb, args):
        __traceback_info__ = '%s %s' % (verb, args)
        super(SeleniumTestcase, self).do_command(verb, args)
