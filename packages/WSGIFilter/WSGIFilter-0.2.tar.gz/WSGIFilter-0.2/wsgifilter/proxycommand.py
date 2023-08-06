"""
This implements the basic framework for making an HTTP proxy app from
your filter.

This is the basic pattern::

    def main(args=None):
        if args is None:
            args = sys.argv[1:]
        parser = make_basic_optparse('MyPackage')
        parser.add_option('--foo',
                          dest='foo')
        options, args = parser.parse_args(args)
        wsgi_middleware = make_my_foo_filter(
            options.foo)
        run_proxy_command(options, args, wsgi_middleware, parser)

Note that ``wsgi_middleware`` should be a callable that takes one
argument (the application being wrapped) and returns a WSGI
application that wraps the given application.
"""

import sys
import re
import optparse
import pkg_resources
import textwrap
import urlparse
from wsgifilter import proxyapp
from wsgifilter.relocateresponse import RelocateMiddleware

__all__ = ['make_basic_optparser', 'run_proxy_command',
           'run_proxy']

scheme_re = re.compile(r'^[a-z]+:', re.I)

def make_basic_optparser(
    distro_name,
    help=None,
    usage='%prog [OPTIONS] REMOTE [SERVER]\n\n%(help)s',
    ):
    """
    Creates a parser that parses the options for the run_proxy()
    function.  You may modify the parser this returns, to add
    option appropriate for building your WSGI middleware.
    """
    distro = pkg_resources.get_distribution(distro_name)
    usage = usage.replace('%prog', '\000 prog \000')
    usage = usage % {'help': help or ''}
    usage = usage.replace('\000 prog \000', '%prog')
    parser = optparse.OptionParser(
        version=str(distro),
        usage=usage)
    parser.add_option(
        '--transparent',
        help="Do not rewrite the Host header when passing the request on",
        action='store_true',
        dest='transparent')
    parser.add_option(
        '--debug',
        help="Show tracebacks when an error occurs (use twice for fancy/dangerous traceback)",
        action="count",
        dest="debug")
    parser.add_option(
        '--request-log',
        help="Show an apache-style log of requests (use twice for more logging)",
        action="count",
        dest="request_log",
        default=0)
    parser.add_option(
        '--rewrite',
        help="Rewrite all headers and links",
        action="store_true",
        dest="rewrite")
    return parser

def run_proxy_command(
    options, args, wsgi_middleware, parser=None):
    """
    Run the proxy command, using the options and args and the WSGI
    middleware
    """
    msg = None
    if not args:
        msg = 'You must provide the remote URL'
    elif len(args) > 2:
        msg = 'Too many arguments (%s): you may only provide a remote URL and server host.' % (' '.join(args[2:]))
        msg = textwrap.fill(msg)
    if msg:
        print msg
        if parser is not None:
            parser.print_usage()
        sys.exit(2)
    if len(args) == 1:
        args.append('http://localhost:8080')
    remote, server = args
    if not scheme_re.search(remote):
        remote = 'http://' + remote
    if not scheme_re.search(server):
        server = 'http://' + server
    run_proxy(remote, server, wsgi_middleware,
              transparent=options.transparent,
              debug=options.debug,
              request_log=options.request_log,
              rewrite=options.rewrite,
              )

def run_proxy(remote, server, wsgi_middleware,
              transparent=False, debug=0, request_log=0,
              rewrite=False):
    # just in case...
    pkg_resources.require('Paste')
    from paste import httpserver
    app = proxyapp.ForcedProxy(
        remote=remote,
        force_host=not transparent)
    if request_log > 1:
        app = proxyapp.DebugHeaders(app)
    if rewrite:
        app = RelocateMiddleware(
            app, old_href=remote)
    if request_log:
        from paste.translogger import TransLogger
        app = TransLogger(app)
    if debug:
        if debug > 1:
            from paste.evalexception.middleware import EvalException
            app = EvalException(app)
        else:
            from paste.exceptions.errormiddleware import ErrorMiddleware
            app = ErrorMiddleware(app, debug=True)
    app = wsgi_middleware(app)
    print 'Serving on    %s' % server
    print 'Remote server %s' % remote
    server_parsed = urlparse.urlsplit(server, 'http')
    if server_parsed[0] != 'http':
        raise ValueError('Only http: is currently supported for the server')
    if ((server_parsed[2] and server_parsed[2] != '/')
        or server_parsed[4]):
        raise ValueError('You may not give a path or query string for the server argument (%r)' % server)
    try:
        httpserver.serve(app, host=server_parsed[1])
    except KeyboardInterrupt:
        print 'Exiting.'
        sys.exit()
    
