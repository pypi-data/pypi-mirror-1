"""$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/quixote/server/util.py $
$Id: util.py 25579 2004-11-11 20:56:32Z nascheme $

Miscellaneous utility functions shared by servers.
"""

from optparse import OptionParser
from quixote.util import import_object

def main(run):
    parser = OptionParser()
    parser.set_description(run.__doc__)
    default_host = 'localhost'
    parser.add_option(
        '--host', dest="host", default=default_host, type="string",
        help="Host interface to listen on. (default=%s)" % default_host)
    default_port = 8080
    parser.add_option(
        '--port', dest="port", default=default_port, type="int",
        help="Port to listen on. (default=%s)" % default_port)
    default_factory = 'quixote.demo.create_publisher'
    parser.add_option(
        '--factory', dest="factory",
        default=default_factory,
        help="Path to factory function to create the site Publisher. "
             "(default=%s)" % default_factory)
    (options, args) = parser.parse_args()
    run(import_object(options.factory), host=options.host, port=options.port)
