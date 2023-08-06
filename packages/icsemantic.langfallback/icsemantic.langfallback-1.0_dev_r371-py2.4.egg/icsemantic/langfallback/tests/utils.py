# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: utils.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
import os, sys
import glob

from Globals import package_home

def list_functionaltests(folder):
    home = package_home(globals())
    return [folder + '/' + os.path.basename(filename) for filename in
            glob.glob(os.path.sep.join([home, folder + '/*.txt']))]

def cleanup_folder(folder):
    """
    """
    folder.manage_delObjects(folder.objectIds())

class Five:
    version = '1.4.4'

def http(request_string, handle_errors=True):
    """
    MONKEYPATCH: Fix https://bugs.launchpad.net/zope3/+bug/98437
    TODO: try to really fix this... ask Martin Aspeli,
    talk in the zope channel, etc...

    Execute an HTTP request string via the publisher

    This is used for HTTP doc tests.
    """
    import urllib
    import rfc822
    from cStringIO import StringIO
    from ZPublisher.Response import Response
    from ZPublisher.Test import publish_module
    from AccessControl.SecurityManagement import getSecurityManager
    from AccessControl.SecurityManagement import setSecurityManager
    import transaction
    from Testing.ZopeTestCase.zopedoctest.functional import HTTPHeaderOutput, \
                                                        split_header, \
                                                        sync, \
                                                        DocResponseWrapper

    # Save current Security Manager
    old_sm = getSecurityManager()

    # Commit work done by previous python code.
    transaction.commit()

    # Discard leading white space to make call layout simpler
    request_string = request_string.lstrip()

    # Split off and parse the command line
    l = request_string.find('\n')
    command_line = request_string[:l].rstrip()
    request_string = request_string[l+1:]
    method, path, protocol = command_line.split()
    path = urllib.unquote(path)

    instream = StringIO(request_string)

    env = {"HTTP_HOST": 'nohost',
           "HTTP_REFERER": 'http://nohost/plone',
           "REQUEST_METHOD": method,
           "SERVER_PROTOCOL": protocol,
           }

    p = path.split('?')
    if len(p) == 1:
        env['PATH_INFO'] = p[0]
    elif len(p) == 2:
        [env['PATH_INFO'], env['QUERY_STRING']] = p
    else:
        raise TypeError, ''

    header_output = HTTPHeaderOutput(
        protocol, ('x-content-type-warning', 'x-powered-by',
                   'bobo-exception-type', 'bobo-exception-file',
                   'bobo-exception-value', 'bobo-exception-line'))

    headers = [split_header(header)
               for header in rfc822.Message(instream).headers]

    # Store request body without headers
    instream = StringIO(instream.read())

    for name, value in headers:
        name = ('_'.join(name.upper().split('-')))
        if name not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            name = 'HTTP_' + name
        env[name] = value.rstrip()

    if env.has_key('HTTP_AUTHORIZATION'):
        env['HTTP_AUTHORIZATION'] = auth_header(env['HTTP_AUTHORIZATION'])

    outstream = StringIO()
    response = Response(stdout=outstream, stderr=sys.stderr)

    publish_module('Zope2',
                   response=response,
                   stdin=instream,
                   environ=env,
                   debug=not handle_errors,
                  )
    header_output.setResponseStatus(response.getStatus(), response.errmsg)
    header_output.setResponseHeaders(response.headers)
    header_output.appendResponseHeaders(response._cookie_list())
    header_output.appendResponseHeaders(response.accumulated_headers.splitlines())

    # Restore previous security manager, which may have been changed
    # by calling the publish method above
    setSecurityManager(old_sm)

    # Sync connection
    sync()

    return DocResponseWrapper(response, outstream, path, header_output)
