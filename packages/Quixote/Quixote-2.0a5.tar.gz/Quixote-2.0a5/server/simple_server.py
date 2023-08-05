#!/usr/bin/env python
"""$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/quixote/server/simple_server.py $
$Id: simple_server.py 25777 2004-12-15 17:43:14Z dbinger $

A simple, single threaded, synchronous HTTP server.
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urllib
import quixote
from quixote import get_publisher
from quixote.http_request import HTTPRequest

class HTTPRequestHandler(BaseHTTPRequestHandler):

    def get_cgi_env(self, method):
        env = dict(
            SERVER_SOFTWARE="Quixote/%s" % quixote.__version__,
            SERVER_NAME=self.server.server_name,
            GATEWAY_INTERFACE='CGI/1.1',
            SERVER_PROTOCOL=self.protocol_version,
            SERVER_PORT=str(self.server.server_port),
            REQUEST_METHOD=method,
            REMOTE_ADDR=self.client_address[0],
            SCRIPT_NAME='')
        if '?' in self.path:
            env['PATH_INFO'], env['QUERY_STRING'] = self.path.split('?')
        else:
            env['PATH_INFO'] = self.path
        env['PATH_INFO'] = urllib.unquote(env['PATH_INFO'])
        if self.headers.typeheader is None:
            env['CONTENT_TYPE'] = self.headers.type
        else:
            env['CONTENT_TYPE'] = self.headers.typeheader
        env['CONTENT_LENGTH'] = self.headers.getheader('content-length') or "0"
        for name, value in self.headers.items():
            header_name = 'HTTP_' + name.upper().replace('-', '_')
            env[header_name] = value
        accept = []
        for line in self.headers.getallmatchingheaders('accept'):
            if line[:1] in "\t\n\r ":
                accept.append(line.strip())
            else:
                accept = accept + line[7:].split(',')
        env['HTTP_ACCEPT'] = ','.join(accept)
        co = filter(None, self.headers.getheaders('cookie'))
        if co:
            env['HTTP_COOKIE'] = ', '.join(co)
        return env

    def process(self, env):
        request = HTTPRequest(self.rfile, env)
        response = get_publisher().process_request(request)
        try:
            self.send_response(response.get_status_code(),
                               response.get_reason_phrase())
            response.write(self.wfile, include_status=False)
        except IOError, err:
            print "IOError while sending response ignored: %s" % err

    def do_POST(self):
        return self.process(self.get_cgi_env('POST'))

    def do_GET(self):
        return self.process(self.get_cgi_env('GET'))


def run(create_publisher, host='', port=80):
    """Runs a simple, single threaded, synchronous HTTP server that
    publishes a Quixote application.
    """
    httpd = HTTPServer((host, port), HTTPRequestHandler)
    publisher = create_publisher()
    httpd.serve_forever()


if __name__ == '__main__':
    from quixote.server.util import main
    main(run)
