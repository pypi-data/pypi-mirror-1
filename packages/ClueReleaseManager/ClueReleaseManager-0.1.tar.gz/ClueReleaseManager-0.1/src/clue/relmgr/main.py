import logging
import optparse
import sys
from clue.relmgr import server
from clue.relmgr import utils

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = '8080'
DEFAULT_BASEFILEDIR = 'files'


def main(args=None, extraargs=None):
    logging.basicConfig()

    parser = optparse.OptionParser()
    parser.add_option('-p', '--port', dest='port',
                      help='Port to listen on, defaults to %s' % DEFAULT_PORT,
                      default=DEFAULT_PORT)
    parser.add_option('-i', '--interface', dest='host',
                      help='Host to listen on, defaults to %s' % DEFAULT_HOST,
                      default=DEFAULT_HOST)
    parser.add_option('-b', '--basefiledir', dest='basefiledir',
                      help='Base directory to store uploaded files, ' + \
                           'defaults to %s' % DEFAULT_BASEFILEDIR,
                      default=DEFAULT_BASEFILEDIR)
    parser.add_option('-d', '--debug', dest='debug',
                      action='store_true',
                      help='Activate debug mode',
                      default=False)

    if args is None:
        args = []
    if extraargs is None:
        extraargs = sys.argv[1:]
    options, args = parser.parse_args(args + extraargs)

    if options.debug:
        utils.logger.setLevel(logging.DEBUG)

    server.Server(host=options.host,
                  port=options.port,
                  basefiledir=options.basefiledir).run_server()


if __name__ == '__main__':
    main()
