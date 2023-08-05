#!/usr/bin/env python2.4
"""static - A stupidly simple WSGI way to serve static files.

(See the docstring of static.Cling.)

Copyright (C) 2006 Luke Arno - http://lukearno.com/

This program is free software; you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by the 
Free Software Foundation; either version 2 of the License, or (at your 
option) any later version.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to:

The Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, 
Boston, MA  02110-1301, USA.

Luke Arno can be found at http://lukearno.com/

"""

import mimetypes
import rfc822
import time
from os import path, stat


class StatusApp:
    """A WSGI app that just returns the given status."""
    
    def __init__(self, status, message=None):
        self.status = status
        if message is None:
            self.message = status
        else:
            self.message = message
        
    def __call__(self, environ, start_response, headers=[]):
        start_response(self.status, headers)
        return [self.message]


class Cling(object):
    """A _stupidly_ simple way to serve static content via WSGI."""

    block_size = 16 * 4096
    index_file = 'index.html'
    not_found = StatusApp('404 Not Found')
    not_modified = StatusApp('304 Not Modified', "")
    moved_permanently = StatusApp('301 Moved Permanently')

    def __init__(self, root, **kw):
        """Just set the root and any other attribs passes via **kw."""
        self.root = root
        for k, v in kw.iteritems():
            setattr(self, k, v)

    def __call__(self, environ, start_response):
        """Serve the file of the same path as PATH_INFO in self.datadir.
        
        Look up the Content-type in self.content_types by extension
        or use 'text/plain' if the extension is not found.

        Serve up the contents of the file or delegate to self.not_found.
        """
        full_path = self.root + environ.get('PATH_INFO', '')
        if path.isdir(full_path):
            if full_path[-1] <> '/' or full_path == self.root:
                location = environ.get('PATH_INFO', '') + '/'
                if environ.get('QUERY_STRING'):
                    location += '?' + environ.get('QUERY_STRING')
                headers = [('Location', location)]
                return self.moved_permanently(environ, start_response, headers)
            else:
                full_path = path.join(full_path, self.index_file)
        content_type = mimetypes.guess_type(full_path)[0] or 'text/plain'
        try:
            mtime = stat(full_path).st_mtime
            last_modified = rfc822.formatdate(mtime)
            headers = [('Date', rfc822.formatdate(time.time())),
                       ('Last-Modified', last_modified),
                       ('ETag', str(mtime))]
            if_modified = environ.get('HTTP_IF_MODIFIED_SINCE')
            if if_modified and (rfc822.parsedate(if_modified)
                                >= rfc822.parsedate(last_modified)):
                return self.not_modified(environ, start_response, headers)
            if_none = environ.get('HTTP_IF_NONE_MATCH')
            if if_none and (if_none == '*' or str(mtime) in if_none):
                return self.not_modified(environ, start_response, headers)
            fp = open(full_path)
            headers.append(('Content-Type', content_type))
            start_response("200 OK", headers)
            way_to_send = environ.get('wsgi.file_wrapper', iter_and_close)
            return way_to_send(fp, self.block_size)
        except (IOError, OSError), e:
            return self.not_found(environ, start_response)


def iter_and_close(fp, block_size):
    """Yield file contents by block then close the file."""
    while 1:
        try:
            block = fp.read(block_size)
            if block: yield block
            else: raise StopIteration
        except StopIteration, si:
            fp.close()
            return 


def cling_wrap(package_name, dir_name, **kw):
    """Return a Cling that serves from the given package and dir_name.
    
    This uses pkg_resources.resource_filename which is not the
    recommended way, since it extracts the files. 
    
    I think this works fine unless you have some _very_ serious 
    requirements for static content, in which case you probably 
    shouldn't be serving it through a WSGI app, IMHO. YMMV.
    """
    from pkg_resources import resource_filename, Requirement
    resource = Requirement.parse(package_name)
    return Cling(resource_filename(resource, dir_name), **kw)
    


if __name__ == '__main__':
    clingon = Cling('/tmp')
    from wsgiref.simple_server import make_server
    server = make_server('localhost', 9999, clingon)
    try:
        server.serve_forever()
    except KeyboardInterrupt, ki:
        print "Cio, baby!"
    
