import os
import urllib2
import urlparse
import simplejson
import shutil
import copy
import Image

from nose.tools import *
from servers import ImgFTPServer, ImgHTTPServer, ImgFileServer


SERVICE_URL = 'http://localhost:8602'
HOST = '127.0.0.1'
DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(DIR, 'data')
SRC_DIR = os.path.join(DIR, 'src_dir')
DST_DIR = os.path.join(DIR, 'dst_dir')
SRC_PROTOS = {
    'http': {
        'loader': ImgHTTPServer,
        'host': HOST,
        'path': SRC_DIR,
        'port': 8088,
        },
    'ftp': {
        'loader': ImgFTPServer,
        'host': HOST,
        'path': SRC_DIR,
        'port': 2121,
        'user': 'user_src',
        'passwd': 'pass_src',
        },
    'file': {
        'loader': ImgFileServer,
        'path': SRC_DIR,
        }
    }
DST_PROTOS = {
    'http': {
        'loader': ImgHTTPServer,
        'host': HOST,
        'path': DST_DIR,
        'port': 8089,
        },
    'ftp': {
        'loader': ImgFTPServer,
        'host': HOST,
        'path': DST_DIR,
        'port': 2121,
        'user': 'user_dst',
        'passwd': 'pass_dst',
        },
    'file': {
        'loader': ImgFileServer,
        'path': DST_DIR,
        }
    }
URL = {
    'srcURL': {
        'http': 'http://' + SRC_PROTOS['http']['host'] + ':' + \
                 str(SRC_PROTOS['http']['port']),
        'ftp': 'ftp://' + SRC_PROTOS['ftp']['user'] + ':' + \
               SRC_PROTOS['ftp']['passwd'] + '@' + \
               SRC_PROTOS['ftp']['host'] + ':' + \
               str(SRC_PROTOS['ftp']['port']),
        'file': 'file://' + SRC_DIR
        },
    'dstURL': {
        'http': 'http://' + DST_PROTOS['http']['host'] + ':' + \
                 str(DST_PROTOS['http']['port']),
        'ftp': 'ftp://' + DST_PROTOS['ftp']['user'] + ':' + \
               DST_PROTOS['ftp']['passwd'] + '@' + \
               DST_PROTOS['ftp']['host'] + ':' + \
               str(DST_PROTOS['ftp']['port']),
        'file': 'file://' + DST_DIR
        }
    }

EXTS = {
    'rasterize': ('svg',),
    'resize': ('png', 'gif', 'jpg', 'jpeg'),
    }

REQ = {
    'operationType': 'resize',
    'args': {
        'width': 200,
        'height': 120,
    },
    'srcURL': '',
    'dstURL': '',
    }


EXPECTED_REPLY = {
    'parse': {'msg': 'request parse error'},
    'invalid': {'msg': 'request invalid'},
    'valid': {'dstURL': None},
    }

class RequestTypeError(Exception):
    """ Exception raised when request type is unexpected. """

def gen_requests():
    requests = []
    for src_key, dst_key in [(src, dst)
                             for src in SRC_PROTOS
                             for dst in DST_PROTOS]:
        for op in ('rasterize', 'resize'):
            for ext in EXTS[op]:
                req = copy.deepcopy(REQ)
                req['operationType'] = op
                req['srcURL'] = src_key + ':/1_example.' + ext  # PREPARE
                if op == 'rasterize':
                    req['dstURL'] = dst_key + ':/1_result.' + 'png'
                else:
                    req['dstURL'] = dst_key + ':/1_result.' + ext

                if dst_key == 'http':
                    req['args']['field_file'] = 'field_file'
                requests.append(req)
    return requests

REQUESTS = gen_requests()


def send_request(url, request):
    if isinstance(request, dict):
        r = urllib2.Request(url, simplejson.dumps(request))
    elif isinstance(request, str):
        r = urllib2.Request(url, request)
    else:
        raise RequestTypeError("request should be of type str or dict")

    f = urllib2.urlopen(r)
    return simplejson.loads(f.read())


def get_dst_filename(dst_url):
    if dst_url.startswith('http'):
        garbage, filename = dst_url.rsplit(':', 1)
    else:
        garbage, filename = os.path.split(dst_url)
    return filename


def gen_target(req, expected_reply):
    """
    Test generator for source/destination URL server protocol
    combinations
    """
    if isinstance(req, dict):
        for url_key, protos in (('srcURL', SRC_PROTOS), ('dstURL', DST_PROTOS)):
            if not req[url_key]:
                continue

            prefix, path = req[url_key].split(':', 1)

            if prefix not in protos.keys():
                req[url_key] = prefix + '://127.0.0.1' + path
                continue

            if path[1] == '/':
                # test if req[url_key] is a valid url
                continue

            if prefix == 'http' and url_key == 'dstURL':
                req[url_key] = URL[url_key][prefix] + '/:' + path[1:]
            else:
                req[url_key] = URL[url_key][prefix] + path

    try:
        reply = send_request(SERVICE_URL, req)
    except urllib2.HTTPError:
        ok_(False)
        return

    if 'dstURL' not in reply.keys():
        # For invalid requests, we should get the right error code
        eq_(reply, expected_reply)
    else:
        # For valid requests, we should get the result image right
        filename = get_dst_filename(reply['dstURL'])
        garbage, ext = os.path.splitext(filename)
        filepath = os.path.join(DST_DIR, filename)
        assert_true(os.path.exists(filepath))
        im = Image.open(filepath)

        if ext == '.jpg': ext = '.jpeg'
        ok_(im.mode in ('P', 'RGB', 'RGBA'))
        eq_((im.format, im.size), (ext[1:].upper(), (req['args']['width'],
                                                     req['args']['height'])))

SERVERS = []


def setup():
    if not os.path.exists(SRC_DIR):
        shutil.copytree(DATA_DIR, SRC_DIR)
    if not os.path.exists(DST_DIR):
        os.mkdir(DST_DIR)

    items = filter(lambda x: x[0] != 'file',
                   SRC_PROTOS.items() + DST_PROTOS.items())
    for k, v in items:
        dv = copy.deepcopy(v)
        loader = dv['loader']
        if k == 'ftp':
            # Reuse existing ImgFTPServer instance, because there is a
            # bug in pyftpdlib, later created server overrides earlier
            # path.
            s = None
            for server in SERVERS:
                if server.__class__ == loader:
                    s = server
            if s:
                s.add_user(dv['user'], dv['passwd'], dv['path'])
                continue
        del dv['loader']
        SERVERS.append(loader(**dv))

    for server in SERVERS:
        server.start()


def teardown():
    for server in SERVERS:
        server.terminate()
    shutil.rmtree(SRC_DIR)
    shutil.rmtree(DST_DIR)


def test_request_parse_error():
    expected_reply = EXPECTED_REPLY['parse']
    raw_req = '{wrongsyntax}}'
    yield gen_target, raw_req, expected_reply


def test_request_lack_key():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 101
    for req in copy.deepcopy(REQUESTS):
        del req['args']
        yield gen_target, req, expected_reply


def test_request_undefined_operationtype():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 102
    for req in copy.deepcopy(REQUESTS):
        req['operationType'] = 'unknown_operation'
        yield gen_target, req, expected_reply


def test_request_wrong_args_type():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 103
    for req in copy.deepcopy(REQUESTS):
        req['args'] = 'I am not a dict'
        yield gen_target, req, expected_reply


def test_request_srcurl_empty():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 104
    for req in copy.deepcopy(REQUESTS):
        req['srcURL'] = ''
        yield gen_target, req, expected_reply


def test_request_dsturl_empty():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 105
    for req in copy.deepcopy(REQUESTS):
        req['dstURL'] = ''
        yield gen_target, req, expected_reply


def test_request_insufficient_args():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 106
    for req in copy.deepcopy(REQUESTS):
        del req['args']['height']
        yield gen_target, req, expected_reply


def test_request_args_wrong_type():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 107
    for req in copy.deepcopy(REQUESTS):
        req['args']['height'] = 'not a int'
        yield gen_target, req, expected_reply


def test_request_srcurl_ext_notallowed():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 108
    for req in copy.deepcopy(REQUESTS):
        req['srcURL'] = req['srcURL'].rsplit('.', 1)[0] + '.tiff'
        yield gen_target, req, expected_reply


def test_request_srcurl_unsupported_protocol():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 109
    for req in copy.deepcopy(REQUESTS):
        req['srcURL'] = 'gopher:' + req['srcURL'].split(':', 1)[1]
        yield gen_target, req, expected_reply


def test_request_dsturl_unsupported_protocol():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 110
    for req in copy.deepcopy(REQUESTS):
        req['dstURL'] = 'gopher:' + req['dstURL'].split(':', 1)[1]
        yield gen_target, req, expected_reply


def test_request_insufficient_extra_args():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 111
    for req in copy.deepcopy(REQUESTS):
        if req['dstURL'] != 'http':
            continue
        del req['args']['field_file']
        yield gen_target, req, expected_reply


def test_request_extra_args_wrong_type():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 112
    for req in copy.deepcopy(REQUESTS):
        if req['dstURL'] != 'http':
            continue
        req['args']['field_file'] = 5
        yield gen_target, req, expected_reply


def test_request_srcurl_dsturl_ext_unmatch_1():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 113
    for req in copy.deepcopy(REQUESTS):
        dst_basename, dst_ext = req['dstURL'].rsplit('.', 1)
        if dst_ext == 'jpg':
            continue
        req['dstURL'] = dst_basename + '.jpg'
        yield gen_target, req, expected_reply


def test_request_srcurl_dsturl_ext_unmatch_2():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 113
    for req in copy.deepcopy(REQUESTS):
        if req['operationType'] != 'rasterize':
            continue
        dst_basename, dst_ext = req['dstURL'].rsplit('.', 1)
        req['dstURL'] = dst_basename + '.jpg'
        yield gen_target, req, expected_reply


def test_request_srcurl_file_nonexist():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 201
    for req in copy.deepcopy(REQUESTS):
        url, filename = req['srcURL'].rsplit('/', 1)
        src_basename, src_ext = filename.rsplit('.', 1)
        req['srcURL'] = url + '/nonexist.' + src_ext
        yield gen_target, req, expected_reply


def test_request_srcurl_host_nonexist():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 201
    for req in copy.deepcopy(REQUESTS):
        if req['srcURL'].startswith('file'):
            continue
        t = list(urlparse.urlparse(req['srcURL']))
        t[1] = 'adfgeqerweg.org'
        req['srcURL'] = urlparse.urlunparse(t)
        yield gen_target, req, expected_reply


def test_request_srcurl_cant_get_dimension():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 202
    for req in copy.deepcopy(REQUESTS):
        if req['operationType'] != 'resize':
            continue
        url, filename = req['srcURL'].rsplit('/', 1)
        src_basename, src_ext = filename.rsplit('.', 1)
        req['srcURL'] = url + '/actually_a_txt.' +  src_ext # PREPARE
        yield gen_target, req, expected_reply


def test_request_srcurl_too_small():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 203
    for req in copy.deepcopy(REQUESTS):
        if req['srcURL'].endswith('.svg'):
            continue
        url, filename = req['srcURL'].rsplit('/', 1)
        src_basename, src_ext = filename.rsplit('.', 1)
        req['srcURL'] = url + '/too_small.' +  src_ext # PREPARE
        yield gen_target, req, expected_reply


def test_request_dsturl_invalid_1():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 205
    for req in copy.deepcopy(REQUESTS):
        if req['dstURL'].startswith('file'):
            continue
        t = list(urlparse.urlparse(req['dstURL']))
        t[1] = 'adfgeqerweg.org'
        req['dstURL'] = urlparse.urlunparse(t)
        prefix, path = os.path.split(req['dstURL'])
        req['dstURL'] = prefix + ":" + path
        yield gen_target, req, expected_reply


def test_request_dsturl_invalid_2():
    expected_reply = EXPECTED_REPLY['invalid']
    expected_reply['code'] = 205
    for req in copy.deepcopy(REQUESTS):
        if req['dstURL'].split(':')[0] != 'ftp':
            continue
        req['dstURL'] = 'ftp://user_dst:wrong_passwd@' + HOST + ':2121' + \
                        req['dstURL'].split(':')[1]
        yield gen_target, req, expected_reply


def test_request_ok():
    expected_reply = EXPECTED_REPLY['valid']
    for req in copy.deepcopy(REQUESTS):
        yield gen_target, req, expected_reply
