# placeholder

import os

selenium_enabled = os.environ.has_key('SELENIUM_HOST')
if not selenium_enabled:
    import logging
    LOG = logging.getLogger()
    LOG.warn('Selenium testing is disabled ($SELENIUM_HOST unset)')
