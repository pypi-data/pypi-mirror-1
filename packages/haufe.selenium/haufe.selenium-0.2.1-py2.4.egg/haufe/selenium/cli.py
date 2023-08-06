##########################################################################
# haufe.selenium
#
# (C) 2007, Haufe Mediengruppe
##########################################################################


import os
import sys
import tempfile
import logging
from optparse import OptionParser
import pkg_resources 

try:
    from zdaemon import zdctl
except ImportError:
    raise ImportError('zdaemon module not found - ensure that your PYTHONPATH includes $YOUR_ZOPE/lib/python.\n'
                      'As an alternative you can install zdaemon as an egg. Beware of potential conflicts\n'
                      'with an exisiting Zope installation.'
                     )

LOG = logging.getLogger()

def start_server(options, args):

    # copy jar file into a temporary directory  in order
    # to make the server runnable from an egg   
    jar_file = os.path.join(tempfile.gettempdir(), 'selenium-server.jar')
    if not os.path.exists(jar_file):
        open(jar_file, 'wb').write(pkg_resources.resource_string(__name__, 'selenium-server.jar'))
    else:
        LOG.info('%s exists - not overwriting it' % jar_file)
    
    if not args:
        raise ValueError('No action specified (Hint: selsrvctl start|stop|status|fg)')

    action = args[0]
    if not action in ('start', 'stop', 'status', 'fg', 'foreground'):
        raise ValueError('Command must be either start, stop, status or foreground(fg)')

    cmd = 'java -jar %s -port %d -proxyInjectionMode' % \
          (jar_file, options.port)

    if sys.platform == 'win32':
        # zdaemon has no Windows support
        if action not in ('fg', 'foreground'):
            raise ValueError("Windows supports only the 'fg' or 'foreground' option")
        os.system(cmd)

    else:
        args = ['-d', '-p', cmd, action]
        zdctl.main(args)


def main():

    parser = OptionParser()
    parser.add_option('-v', '--verbose', dest='verbose', action="store_true",
                      default=False, help='Verbose mode on')

    parser.add_option('-V', '--version', dest='version', action='store_true',
                      default=False,
                      help='Show version info about haufe.selenium package')

    parser.add_option('-p', '--port', dest='port', action='store', type='int',
                      default=4444,
                      help='Selenium remote server port (default=4444)')

    (options, args) = parser.parse_args()

    if options.version:
        show_version()
    else:
        start_server(options, args)


def show_version():

    print pkg_resources.require('haufe.selenium')[0]
        
if __name__ == '__main__':
    main()
