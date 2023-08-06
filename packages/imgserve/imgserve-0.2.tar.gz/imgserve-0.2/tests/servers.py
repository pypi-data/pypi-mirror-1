import os, sys
import threading
import posixpath
import SimpleHTTPServer
import BaseHTTPServer
import httplib
import urllib
import cgi

from BaseHTTPServer import HTTPServer
from pyftpdlib import ftpserver


class BaseServer():
    """
    Base class for providing an interface for server classes
    """
    def __init__(self):
        raise NotImplementedError("Should have implemented __init__")

    def get_url(self):
        raise NotImplementedError("Should have implemented get_url method")

    def start(self):
        raise NotImplementedError("Should have implemented start method")

    def terminate(self):
        raise NotImplementedError("Should have implemented stop method")


class ImgFileServer(BaseServer):
    def __init__(self, path):
        self.url = 'file://' + path

    def get_url(self):
        return self.url

    def start(self):
        pass

    def terminate(self):
        pass


class ImgFTPServer(BaseServer):
    def __init__(self, path, host, port, user, passwd):
        self.url = {}
        self.host = host
        self.port = port

        # create a ftp server instance
        self.authorizer = ftpserver.DummyAuthorizer()
        self.add_user(user, passwd, path)
        ftp_handler = ftpserver.FTPHandler
        ftp_handler.authorizer = self.authorizer
        address = (self.host, self.port)
        self.ftpd = ftpserver.FTPServer(address, ftp_handler)

    def add_user(self, user, passwd, path):
        self.authorizer.add_user(user, passwd, path, perm="elradfmw")
        self.url[user] = 'ftp://%s:%s@%s:%d' % (user, passwd,
                                                self.host, self.port)

    def get_url(self, user):
        return self.url[user]

    def start(self):
        self.thread = threading.Thread(target=self.ftpd.serve_forever)
        self.thread.start()

    def terminate(self):
        self.ftpd.close_all()
        self.thread.join()


class ImgHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """
    HTTP request handler with QUIT stopping the server, and handling
    POST uploading
    """
    def log_message(self, format, *args):
        # we override this to suppress logging
        pass

    def translate_path(self, path):
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = self.server.path
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def do_GET(self):
        try:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        except:
            pass

    def do_QUIT(self):
        """send 200 OK response, and set server.stop to True"""
        self.send_response(200)
        self.end_headers()
        self.server.stop = True

    def do_POST(self):
        """Save the uploaded file"""
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        if 'field_file' not in form.keys():
            return
        item = form['field_file']
        if not item.filename:
            return

        fout =file(os.path.join(self.server.path, item.filename), 'wb')
        while True:
            chunk = item.file.read(102400)
            if not chunk: break
            fout.write (chunk)
        fout.close()

        self.send_response(200)
        self.end_headers()


class ImgHTTPServer(HTTPServer):
    """http server that can be stopped"""
    def __init__(self, path, host, port):
        self.url = 'http://%s:%d' % (host, port)
        self.path = path
        HTTPServer.__init__(self, (host, port), ImgHTTPRequestHandler)

    def get_url(self):
        return self.url

    def serve_forever(self):
        """Handle one request at a time until stopped."""
        self.stop = False
        while not self.stop:
            self.handle_request()

    def start(self):
        self.thread = threading.Thread(target=self.serve_forever)
        self.thread.start()

    def terminate(self):
        """send QUIT request to http server running on localhost:<port>"""
        conn = httplib.HTTPConnection(self.url.split('://', 1)[1])
        conn.request("QUIT", "/")
        conn.getresponse()
        self.thread.join()
        self.socket.close()
