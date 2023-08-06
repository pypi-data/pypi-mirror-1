"""
This file contains the real image processing code: request json object
validation that needs to retreive a url to ensure valid srcURL, put a
placeholder to ensure valid dstURL, generating placeholder images,
image rescaling, svg rasterization.
"""

from __future__ import with_statement
import os
import shutil
import socket
import urllib
import urllib2
import Image, ImageFile, ImageFont, ImageDraw
import cairo
import rsvg
import pycurl
import tempfile
from pkg_resources import resource_filename
from imgserve.utils import *


GETSIZES_TIMEOUT = 30 # in seconds
socket.setdefaulttimeout(GETSIZES_TIMEOUT)

UPLOAD_CONNECT_TIMEOUT = 10 # inseconds
UPLOAD_TIMEOUT = 30


PLACEHOLDER_TEXT = 'Image being processed'
FAIL_TEXT = 'Image Processing failed'
FONT_FILE = resource_filename(__name__, 'arial.ttf')
FONT_SIZE = 16

# Some servers (upload.wikimedia.org for instance) refuse to serve
# files if user agent string is not a commonly known browser
USER_AGENT = 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'


def http_200_ok(header_string):
    """
    Parse the header string, return True if it represents a HTTP 200
    OK.
    """
    first_line = header_string.split('\n')[0]
    if not first_line:
        return False

    try:
        protocol, code, msg = first_line.split(' ', 2)
    except:
        return False

    return protocol.startswith('HTTP/') and code == '200'


def retrieve(url):
    """
    Retrieve a remote file from `url`, use the file name from `url`.
    If things go wrong, return None.
    """
    filename = os.path.split(url)[1]
    if not filename:
        garbage, suffix = get_filename_parts_from_url(url)
        filepath = make_filepath(suffix='.' + suffix)
    else:
        filepath = make_filepath(filename)
    f = open(filepath, 'wb')

    retrieved_headers = Storage()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, str(url))
    c.setopt(pycurl.WRITEFUNCTION, f.write)
    c.setopt(pycurl.HEADERFUNCTION, retrieved_headers.store)
    try:
        c.perform()
    except:
        success = False
    else:
        success = True
    finally:
        c.close()
        f.close()

    # Delete the local file if retrieval failed, or http reponse
    # indicates a failure
    if not success or \
           (url.startswith('http') and \
            not retrieved_headers.is_empty() and \
            not http_200_ok(retrieved_headers.contents)):
        clean_filepath(filepath)
        return None

    return filepath


def generate_placeholder(width, height, filepath, text):
    """
    Generates a placeholder of appropirate size with `text` rendering
    in the middle, and save the file to `filepath`, return True if
    success, False otherwise.
    """
    image = Image.new('RGB', (width, height), 'white')
    font = ImageFont.truetype(FONT_FILE, FONT_SIZE)
    draw = ImageDraw.Draw(image)
    size = draw.textsize(text, font=font)
    x, y = (width - size[0])/2, (height - size[1])/2
    draw.text((x, y), text, font=font, fill='black')

    fmt = os.path.splitext(filepath)[1][1:].upper()
    if fmt == 'JPG':
        fmt = 'JPEG'

    try:
        image.save(filepath, fmt)
    except:
        return_val = False
    else:
        return_val = True
    return return_val


class Storage:
    """
    This class is for pycurl to store http reponse headers to a
    string.
    """
    def __init__(self):
        self.contents = ''

    def store(self, buf):
        self.contents += buf

    def is_empty(self):
        """Returns True if the content is empty."""
        return len(self.contents) == 0


class Upload:
    def __init__(self):
        self._curl = pycurl.Curl()

    def _curl_perform(self):
        """
        Utility method to perform curl upload action.  Return True if
        successful, otherwise False.
        """
        self._curl.setopt(pycurl.CONNECTTIMEOUT, UPLOAD_CONNECT_TIMEOUT)
        self._curl.setopt(pycurl.TIMEOUT, UPLOAD_TIMEOUT)
        try:
            self._curl.perform()
        except:
            return_val = False
        else:
            return_val = True
        finally:
            self._curl.close() # is _curl usable after close? need
                               # test
        return return_val

    def _ftp_upload(self, url, filepath, args):
        """
        Upload file to FTP `url`.
        """
        def upload_func(url, read_cb, size, args):
            self._curl.reset()
            self._curl.setopt(pycurl.URL, str(url))
            self._curl.setopt(pycurl.UPLOAD, 1)
            self._curl.setopt(pycurl.READFUNCTION, read_cb)
            self._curl.setopt(pycurl.INFILESIZE, size)
            return self._curl_perform()

        size = os.path.getsize(filepath)
        with open(filepath) as f:
            return_val = upload_func(url, f.read, size, args)
        return return_val

    def _http_post_upload(self, url, filepath, args):
        """
        Upload file to `url` with HTTP Post.
        """
        pf = [(str(args['field_file']),
               (pycurl.FORM_FILE, str(filepath)))]
        self._curl.reset()
        self._curl.setopt(pycurl.URL, str(url))
        self._curl.setopt(pycurl.HTTPPOST, pf)
        return self._curl_perform()

    def _http_put_upload(self, url, filepath, args):
        """
        Upload file to `url` with HTTP Put.
        """
        self._curl.reset()
        # TODO: not implemented yet.
        return self._curl_perform()

    def _file_upload(self, url, filepath, args):
        """
        Move file to local `url`.  It is ugly to deal with local file
        with such a mess, this is making API uniform, maybe change
        this in the future.
        """
        url = url[7:] # get rid of 'file://' prefix
        try:
            # Create all intermediate dirs
            dirname = os.path.dirname(url)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            shutil.copyfile(filepath, url)
        except IOError:
            return_val = False
        else:
            return_val = True
        return return_val

    def upload(self, url, filepath, args):
        """
        A dispatcher based on protocol indicated by `url`.
        """
        if url.startswith('ftp'):
            return self._ftp_upload(url, filepath, args)
        elif url.startswith('http'):
            return self._http_post_upload(url, filepath, args)
        elif url.startswith('file'):
            return self._file_upload(url, filepath, args)


def getsizes(url):
    """
    Download `url` just enough for PIL to determine its dimension,
    return a tuple of file size and image dimension, image dimension
    itself is a width, height tuple, None if can't be determined
    """
    req = urllib2.Request(url=url, headers={'User-Agent': USER_AGENT})
    filelike = urllib2.urlopen(req)

    if url.startswith('http'):
        size = filelike.info().get("content-length")
        size = int(size)
    else:
        size = None

    # Download just enough to determine image dimension
    p = ImageFile.Parser()
    ok_flag = False
    while True:
        data = filelike.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            ok_flag = True
            break
    filelike.close()
    if ok_flag:
        return size, p.image.size

    return size, None


def slow_check(req):
    """
    Do smart request object validation.  Validate srcURL by
    downloading part of the file to determine the image demension,
    download the whole file if it's svg, validate dstURL by uploading
    a placeholder image.
    """

    # Save typing
    op = req['operationType']
    arg_width = req['args']['width']
    arg_height = req['args']['height']

    data = None

    # Test if srcURL is valid
    if op == 'resize':
        try:
            size, dimension = getsizes(req['srcURL'])
        except (urllib2.URLError, OSError, IOError):
            return (False, 201)

        if not dimension:
            return (False, 202)
        width, height = dimension

        # Only downscale
        if not (width >= arg_width and height >= arg_height):
            return (False, 203)

    # If it's svg, download the whole file
    elif op == 'rasterize':
        filepath = retrieve(req['srcURL'])
        if not filepath:
            return (False, 201)

        # TODO: Validate svg file here, return 204 if invalid

        # Return saved filepath for later use to avoid downloading
        # again
        data = filepath

    # Test if dstURL is valid by uploading placeholder
    fp = make_filepath(get_dst_filename(req['dstURL']))
    upload_url = get_upload_dst_url(req['dstURL'])
    generate_placeholder(arg_width, arg_height, fp, PLACEHOLDER_TEXT)
    return_val = Upload().upload(upload_url, fp, req['args'])
    clean_filepath(fp)
    if not return_val:
        # Delete retrieved file
        if 'filepath' in locals():
            clean_filepath(filepath)
        return (False, 205)

    return (True, data)


def get_dst_filename(dst_url):
    if dst_url.startswith('http'):
        garbage, filename = dst_url.rsplit(':', 1)
    else:
        garbage, filename = os.path.split(dst_url)
    return filename


def get_upload_dst_url(dst_url):
    url = dst_url
    if dst_url.startswith('http'):
        url, garbage = dst_url.rsplit(':', 1)
    return url


def rescale(im, size):
    dst_width, dst_height = size
    src_width, src_height = im.size
    src_ratio = float(src_width) / float(src_height)
    dst_ratio = float(dst_width) / float(dst_height)

    if dst_ratio < src_ratio:
        crop_height = src_height
        crop_width = crop_height * dst_ratio
        x_offset = float(src_width - crop_width) / 2
        y_offset = 0
    else:
        crop_width = src_width
        crop_height = crop_width / dst_ratio
        x_offset = 0
        y_offset = int(float(src_height - crop_height) / 3)
    im = im.crop((x_offset, y_offset,
                  x_offset + int(crop_width), y_offset + int(crop_height)))
    im = im.resize((dst_width, dst_height), Image.ANTIALIAS)
    return im


def work(i_queue, o_queue):
    """
    This is the worker process target function.  First a request
    object is taken off from input queue, in which all request have
    already passed the quick check previously before they are put into
    the input queue, the request object then go through slow check
    process, reply object is generated and put into the output queue
    regardless of whether the request passes the slow check.  However,
    if the request passed the slow check successfully, the heavy work
    is followed, otherwise, next request from the input queue will be
    poped and go through the same process.
    """
    for req_id, req in iter(i_queue.get, None):
        # Slow check the request object from input queue
        valid, data = slow_check(req)
        if valid:
            reply_data = req['dstURL'] # reply with a substituted
                                       # dstURL
        else:
            reply_data = data # error code

        # Put the reply into output queue
        which = {True: 'valid', False: 'invalid'}[valid]
        o_queue.put((req_id, make_reply(which, reply_data)))
        #i_queue.task_done()

        # If request failed to go through the slow check process, go
        # to next iteration
        if not valid:
            continue

        # Start real image processing work
        width, height = req['args']['width'], req['args']['height']

        dst_filename = get_dst_filename(req['dstURL'])
        dst_filepath = make_filepath(dst_filename)

        if req['operationType'] == 'rasterize':
            filepath = data # filepath of downloaded svg file

            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            ctx = cairo.Context(surface)
            try:
                svg = rsvg.Handle(file=filepath)
                ctx.scale(float(width)/svg.props.width,
                          float(height)/svg.props.height)
                svg.render_cairo(ctx)
            except:
                generate_placeholder(width, height, dst_filepath, FAIL_TEXT)
            else:
                surface.write_to_png(dst_filepath)
                del svg
                del surface
                del ctx

        elif req['operationType'] == 'resize':
            filepath = retrieve(req['srcURL'])
            if not filepath:
                generate_placeholder(width, height, dst_filepath, FAIL_TEXT)

            try:
                im = Image.open(filepath)
                im = rescale(im, (width, height))
            except:
                generate_placeholder(width, height, dst_filepath, FAIL_TEXT)
            else:
                im.save(dst_filepath, im.format)
                del im

        # Upload to destination url
        upload_url = get_upload_dst_url(req['dstURL'])
        Upload().upload(upload_url, dst_filepath, req['args'])

        # Clean downloaded and generated file
        clean_filepath(dst_filepath)
        if filepath:
            clean_filepath(filepath)

    # Put None back to i_queue to notify next worker process to quit
    #i_queue.task_done()
    i_queue.put(None)
