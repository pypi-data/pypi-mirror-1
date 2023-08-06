"""
This file contains a http server that receives json request from
users, and code for json request parsing, quick nonblocking
validation, reply object creation.
"""
from __future__ import with_statement

import os
import sys
import time
import uuid
from pprint import pprint
from cogen.web import wsgi
from cogen.common import *
from cogen.web.async import SynchronousInputMiddleware
from imgserve.utils import get_filename_parts_from_url, make_reply
from imgserve import version


if sys.version_info >= (2, 6):
    import json
else:
    import simplejson as json

# Allowed operation types
OPS = ('rasterize', 'resize')

# Allowed file extention in srcURL for different operations
EXTENTIONS = {
    'rasterize': ('svg',),
    'resize': ('png', 'gif', 'jpg', 'jpeg'),
    }

# Required args for different operations, keyed by operation
REQUIRED_ARGS = {
    'rasterize': {
        'width': int,
        'height': int,
        },
    'resize': {
        'width': int,
        'height': int,
        },
    }

assert set(EXTENTIONS.keys()) == set(REQUIRED_ARGS.keys()) == set(OPS)

# Supported protocols (prefix) for source and destination URL
SRC_PREFIXES = ('http', 'ftp', 'file')
DST_PREFIXES = ('http', 'ftp', 'file')

# Required extra args for different protocols (URL prefix as key)
EXTRA_ARGS = {
    'http': {
        'field_file': (str, unicode)
        },
    'ftp': {},
    'file': {},
    }

assert set(EXTRA_ARGS.keys()) == set(DST_PREFIXES)


def quick_check(req):
    """
    Do basic nonblocking validation for request object, return a tuple
    where the first element is a boolean value that tells whether the
    request is valid, the second element is a error code if invalid,
    None if valid.

    See README for more description about request format
    specification.
    """
    # Test if all keys are present
    if not set(req.keys()) == \
           set(['operationType', 'args', 'srcURL', 'dstURL']):
        return (False, 101)

    op = req['operationType']

    # Test if operationType is in predefined set
    if op not in OPS:
        return (False, 102)

    # Test if args is of type dict
    if not isinstance(req['args'], dict):
        return (False, 103)

    # Test if srcURL is not empty
    if not req['srcURL']:
        return (False, 104)

    # Test if dstURL is not empty
    if not req['dstURL']:
        return (False, 105)

    # Test if required args received is subset of required args
    req_args = set(req['args'].keys())
    required_args = set(REQUIRED_ARGS[op].keys())
    if not required_args.issubset(req_args):
        return (False, 106)

    # Test if required args received are of right types
    for arg in required_args:
        if not isinstance(req['args'][arg], REQUIRED_ARGS[op][arg]):
            return (False, 107)

    # Test if operation type and srcURL file extention match
    src_basename, src_ext = get_filename_parts_from_url(req['srcURL'])
    if src_ext.lower() not in EXTENTIONS[op]:
        return (False, 108)

    # Substitute dstURL variables
    substitute_maps = (
        ('{$width}', str(req['args']['width'])),
        ('{$height}', str(req['args']['height'])),
        ('{$basename}', src_basename),
        ('{$ext}', src_ext)
        )
    # Only substitude the string after colon, so that only filename
    # part of HTTP Post URL is processed
    prefix, sub_body = req['dstURL'].rsplit(':', 1)
    for token, value in substitute_maps:
        sub_body = sub_body.replace(token, value)
    req['dstURL'] = prefix + ':' + sub_body

    # Test if srcURL and dstURL protocols are supported
    src_prefix = req['srcURL'].split(':', 1)[0]
    dst_prefix = req['dstURL'].split(':', 1)[0]
    if src_prefix not in SRC_PREFIXES:
        return (False, 109)
    if dst_prefix not in DST_PREFIXES:
        return (False, 110)

    # Test if extra args are present for the dstURL protocol
    extra_args = set(EXTRA_ARGS[dst_prefix].keys())
    if not extra_args.issubset(req_args):
        return (False, 111)

    # Test if extra args are of right types
    for arg in extra_args:
        if isinstance(EXTRA_ARGS[dst_prefix], list):
            bool_list = map(lambda x: isinstance(req['args'][arg], x),
                            EXTRA_ARGS[dst_prefix]),
            correct = reduce(lambda (x, y): x and y, bool_list)
        else:
            correct = isinstance(req['args'][arg], EXTRA_ARGS[dst_prefix][arg])
        if not correct:
            return (False, 112)

    # Test if file extention from srcURL and new file name match
    dst_basename, dst_ext = get_filename_parts_from_url(req['dstURL'])
    compare_target = {'rasterize': 'png', 'resize': src_ext}
    if dst_ext.lower() != compare_target[op]:
        return (False, 113)

    return (True, None)


def load_json(environ):
    """
    Convert a WSGI environ of json request to a python dict.
    """
    entity = environ['wsgi.input'].read()

    # Test if the string is empty
    if not entity:
        return None

    # Test if the string is json valid
    try:
        req = json.loads(entity)
    except:
        return None
    else:
        return req


def reply_json(start_response, reply):
    """
    Make a json reply that is used by our tiny WSGI application.
    """
    body = json.dumps(reply)
    start_response('200 OK', [('Content-Type','text/html')])
    return [body]


def get_worker_reply(i_queue, o_queue, req):
    """
    Dispatch request to worker process, and get the result back.
    """
    # Generate a id so that we know if a item input queue and that in
    # output queue matches
    req_id = uuid.uuid1()

    # Enqueue (id, request) tuple
    i_queue.put((req_id, req))

    # Polling output queue for matching task result
    temp_buf = []
    sleep = .5
    while True:
        reply = o_queue.get()
        if reply[0] == req_id:
            break
        temp_buf.append(reply)
        time.sleep(sleep)
        sleep *= 2

    if temp_buf:
        for reply in temp_buf:
            o_queue.put(reply)

    return reply[1]


def httpserv(host, port, i_queue, o_queue):
    """
    Start the http server.
    """
    @SynchronousInputMiddleware
    def http_handler(environ, start_response):
        """
        WSGI request handler that do othe real work of receiving json
        request from users.
        """
        # Ignore requests that are not POST
        if environ['REQUEST_METHOD'] != 'POST':
            start_response('404 OK', [('Content-Type','text/html')])
            return ["404 Not Found - %s %s" %
                    (version.NAME, version.VERSION['version'])]

        print "Got a request from %s, %s" % (environ['REMOTE_ADDR'],
                                             environ['HTTP_USER_AGENT'])

        # Check if json request is grammatically good
        req = load_json(environ)

        if not req:
            return reply_json(start_response, make_reply('parse'))

        # Print reqeust content to log file
        pprint(req)

        # Quick check, and substitute variables in dstURL with real
        # values
        valid, data = quick_check(req)
        if not valid:
            error_code = data
            return reply_json(start_response, make_reply('invalid', error_code))

        print "Passing the request to a worker process"
        reply = get_worker_reply(i_queue, o_queue, req)

        return reply_json(start_response, reply)

    m = Scheduler()
    server = wsgi.WSGIServer((host, port), http_handler, m)
    m.add(server.serve)
    try:
        m.run()
    except (KeyboardInterrupt, SystemExit):
        return
