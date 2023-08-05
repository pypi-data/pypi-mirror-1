# (c) 2005 Ian Bicking, Clark C. Evans and contributors
# This module is part of the Python Paste Project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
"""
This module handles sending static content such as in-memory data or
files.  At this time it has cache helpers and understands the
if-modified-since request header.
"""

import os, time, mimetypes
from httpexceptions import *
from httpheaders import *

CACHE_SIZE = 4096
BLOCK_SIZE = 4096 * 16

__all__ = ['DataApp','FileApp']

class DataApp(object):
    """
    Returns an application that will send content in a single chunk,
    this application has support for setting cashe-control and for
    responding to conditional (or HEAD) requests.

    Constructor Arguments:

        ``content``     the content being sent to the client

        ``headers``     the headers to send /w the response

        The remaining ``kwargs`` correspond to headers, where the
        underscore is replaced with a dash.  These values are only
        added to the headers if they are not already provided; thus,
        they can be used for default values.  Examples include, but
        are not limited to:

            ``content_type``
            ``content_encoding``
            ``content_location``

    ``cache_control()``

        This method provides validated construction of the ``Cache-Control``
        header as well as providing for automated filling out of the
        ``EXPIRES`` header for HTTP/1.0 clients.

    ``set_content()``

        This method provides a mechanism to set the content after the
        application has been constructed.  This method does things
        like changing ``Last-Modified`` and ``Content-Length`` headers.

    """
    def __init__(self, content, headers=None, **kwargs):
        assert isinstance(headers,(type(None),list))
        self.expires = None
        self.content = None
        self.content_length = None
        self.last_modified = 0
        self.headers = headers or []
        for (k,v) in kwargs.items():
            header = get_header(k)
            header.update(self.headers,v)
        ACCEPT_RANGES.update(self.headers,bytes=True)
        if not CONTENT_TYPE(self.headers):
            CONTENT_TYPE.update(self.headers)
        if content:
            self.set_content(content)

    def cache_control(self, **kwargs):
        self.expires = CACHE_CONTROL.apply(self.headers, **kwargs) or None
        return self

    def set_content(self, content):
        assert content is not None
        self.last_modified = time.time()
        self.content = content
        self.content_length = len(content)
        LAST_MODIFIED.update(self.headers, time=self.last_modified)
        return self

    def content_disposition(self, **kwargs):
        CONTENT_DISPOSITION.apply(self.headers, **kwargs)
        return self

    def __call__(self, environ, start_response):
        headers = self.headers[:]
        if self.expires is not None:
            EXPIRES.update(headers, delta=self.expires)

        try:
            client_clock = IF_MODIFIED_SINCE.parse(environ)
            if client_clock >= int(self.last_modified):
                # horribly inefficient, n^2 performance, yuck!
                for head in list_headers(entity=True):
                    head.delete(headers)
                start_response('304 Not Modified',headers)
                return [''] # empty body
        except HTTPBadRequest, exce:
            return exce.wsgi_application(environ, start_response)

        (lower,upper) = (0, self.content_length - 1)
        range = RANGE.parse(environ)
        if range and 'bytes' == range[0] and 1 == len(range[1]):
            (lower,upper) = range[1][0]
            upper = upper or (self.content_length - 1)
            if upper >= self.content_length or lower > upper:
                return HTTPRequestRangeNotSatisfiable((
                  "Range request was made beyond the end of the content,\r\n"
                  "which is %s long.\r\n  Range: %s\r\n") % (
                     self.content_length, RANGE(environ))
                ).wsgi_application(environ, start_response)

        content_length = upper - lower + 1
        CONTENT_RANGE.update(headers, first_byte=lower, last_byte=upper,
                            total_length = self.content_length)
        CONTENT_LENGTH.update(headers, content_length)
        if content_length == self.content_length:
            start_response('200 OK', headers)
        else:
            start_response('206 Partial Content', headers)
        if self.content is not None:
            return [self.content[lower:upper+1]]
        assert self.__class__ != DataApp, "DataApp must call set_content"
        return (lower, content_length)

class FileApp(DataApp):
    """
    Returns an application that will send the file at the given
    filename.  Adds a mime type based on ``mimetypes.guess_type()``.
    See DataApp for the arguments beyond ``filename``.
    """

    def __init__(self, filename, headers=None, **kwargs):
        self.filename = filename
        content_type, content_encoding = mimetypes.guess_type(self.filename)
        if content_type and 'content_type' not in kwargs:
            kwargs['content_type'] = content_type
        if content_encoding and 'content_encoding' not in kwargs:
            kwargs['content_encoding'] = content_encoding
        DataApp.__init__(self, None, headers, **kwargs)

    def update(self, force=False):
        stat = os.stat(self.filename)
        if not force and stat.st_mtime == self.last_modified:
            return
        if stat.st_size < CACHE_SIZE:
            fh = open(self.filename,"rb")
            self.set_content(fh.read())
            fh.close()
        else:
            self.content = None
            self.content_length = stat.st_size
        self.last_modified = stat.st_mtime

    def __call__(self, environ, start_response):
        if 'max-age=0' in CACHE_CONTROL(environ).lower():
            self.update(force=True) # RFC 2616 13.2.6
        else:
            self.update()
        if not self.content:
            try:
                file = open(self.filename, 'rb')
            except (IOError, OSError), e:
                exc = HTTPForbidden(
                    'You are not permitted to view this file (%s)' % e)
                return exc.wsgi_application(
                    environ, start_response)
        retval = DataApp.__call__(self, environ, start_response)
        if isinstance(retval,list):
            # cached content, exception, or not-modified
            return retval
        (lower, content_length) = retval
        file.seek(lower)
        return _FileIter(file, size=content_length)

class _FileIter:

    def __init__(self, file, block_size=None, size=None):
        self.file = file
        self.size = size
        self.block_size = block_size or BLOCK_SIZE

    def __iter__(self):
        return self

    def next(self):
        chunk_size = self.block_size
        if self.size is not None:
            if chunk_size > self.size:
                chunk_size = self.size
            self.size -= chunk_size
        data = self.file.read(chunk_size)
        if not data:
            raise StopIteration
        return data

    def close(self):
        self.file.close()

