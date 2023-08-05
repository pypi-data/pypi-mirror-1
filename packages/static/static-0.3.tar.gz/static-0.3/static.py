#!/usr/bin/env python2.4
"""static - A stupidly simple WSGI way to serve static (or mixed) content.

(See the docstrings of the various functions and classes.)

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
import string
from os import path, stat


from wsgiref import util


try: from pkg_resources import resource_filename, Requirement
except: pass

try: import kid
except: pass


class MagicError(Exception): pass


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
        if environ['REQUEST_METHOD'] == 'GET':
            return [self.message]
        else:
            return [""]


class Cling(object):
    """A stupidly simple way to serve static content via WSGI.
    
    Serve the file of the same path as PATH_INFO in self.datadir.
    
    Look up the Content-type in self.content_types by extension
    or use 'text/plain' if the extension is not found.

    Serve up the contents of the file or delegate to self.not_found.
    """

    block_size = 16 * 4096
    index_file = 'index.html'
    not_found = StatusApp('404 Not Found')
    not_modified = StatusApp('304 Not Modified', "")
    moved_permanently = StatusApp('301 Moved Permanently')
    method_not_allowed = StatusApp('405 Method Not Allowed')

    def __init__(self, root, **kw):
        """Just set the root and any other attribs passes via **kw."""
        self.root = root
        for k, v in kw.iteritems():
            setattr(self, k, v)

    def __call__(self, environ, start_response):
        """Respond to a request when called in the usual WSGI way."""
        if environ['REQUEST_METHOD'] not in ('GET', 'HEAD'):
            return self.method_not_allowed(environ, start_response)
        path_info = environ.get('PATH_INFO', '')
        full_path = self._full_path(path_info)
        if path.isdir(full_path):
            if full_path[-1] <> '/' or full_path == self.root:
                location = util.request_uri(environ, include_query=False) + '/'
                if environ.get('QUERY_STRING'):
                    location += '?' + environ.get('QUERY_STRING')
                headers = [('Location', location)]
                return self.moved_permanently(environ, start_response, headers)
            else:
                full_path = self._full_path(path_info + self.index_file)
        content_type = self._guess_type(full_path)
        try:
            etag, last_modified = self._conditions(full_path, environ)
            headers = [('Date', rfc822.formatdate(time.time())),
                       ('Last-Modified', last_modified),
                       ('ETag', etag)]
            if_modified = environ.get('HTTP_IF_MODIFIED_SINCE')
            if if_modified and (rfc822.parsedate(if_modified)
                                >= rfc822.parsedate(last_modified)):
                return self.not_modified(environ, start_response, headers)
            if_none = environ.get('HTTP_IF_NONE_MATCH')
            if if_none and (if_none == '*' or etag in if_none):
                return self.not_modified(environ, start_response, headers)
            file_like = self._file_like(full_path)
            headers.append(('Content-Type', content_type))
            start_response("200 OK", headers)
            if environ['REQUEST_METHOD'] == 'GET':
                return self._body(full_path, environ, file_like)
            else:
                return ['']
        except (IOError, OSError), e:
            return self.not_found(environ, start_response)

    def _full_path(self, path_info):
        """Return the full path from which to read."""
        return self.root + path_info

    def _guess_type(self, full_path):
        """Guess the mime type using the mimetypes module."""
        return mimetypes.guess_type(full_path)[0] or 'text/plain'

    def _conditions(self, full_path, environ):
        """Return a tuple of etag, last_modified by mtime from stat."""
        mtime = stat(full_path).st_mtime
        return str(mtime), rfc822.formatdate(mtime)

    def _file_like(self, full_path):
        """Return the appropriate file object."""
        return open(full_path)

    def _body(self, full_path, environ, file_like):
        """Return an iterator over the body of the response."""
        way_to_send = environ.get('wsgi.file_wrapper', iter_and_close)
        return way_to_send(file_like, self.block_size)


def iter_and_close(file_like, block_size):
    """Yield file contents by block then close the file."""
    while 1:
        try:
            block = file_like.read(block_size)
            if block: yield block
            else: raise StopIteration
        except StopIteration, si:
            file_like.close()
            return 


def cling_wrap(package_name, dir_name, **kw):
    """Return a Cling that serves from the given package and dir_name.
    
    This uses pkg_resources.resource_filename which is not the
    recommended way, since it extracts the files. 
    
    I think this works fine unless you have some _very_ serious 
    requirements for static content, in which case you probably 
    shouldn't be serving it through a WSGI app, IMHO. YMMV.
    """
    resource = Requirement.parse(package_name)
    return Cling(resource_filename(resource, dir_name), **kw)
 

class Shock(Cling):
    """A stupidly simple way to serve up mixed content.
    
    Serves static content just like Cling (it's superclass)
    except that it process content with the first matching
    magic from self.magics if any apply.

    See Cling and classes with "Magic" in their names in this module.

    If you are using Shock with the StringMagic class for instance:

    shock = Shock('/data', magics=[StringMagic(food='cheese')])
    
    Let's say you have a file called /data/foo.txt.stp containing one line:

    "I love to eat $food!"
    
    When you do a GET on /foo.txt you will see this in your browser:

    "I love to eat cheese!"

    This is really nice if you have a color variable in your css files or
    something trivial like that. It seems silly to create or change a 
    handful of objects for a couple of dynamic bits of text.
    """

    magics = ()

    def _match_magic(self, full_path):
        """Return the first magic that matches this path or None."""
        for magic in self.magics:
            if magic.matches(full_path):
                return magic

    def _full_path(self, path_info):
        """Return the full path from which to read."""
        full_path = self.root + path_info
        if path.exists(full_path):
            return full_path
        else:
            for magic in self.magics: 
                if path.exists(magic.new_path(full_path)):
                    return magic.new_path(full_path)
            else:
                return full_path

    def _guess_type(self, full_path):
        """Guess the mime type magically or using the mimetypes module."""
        magic = self._match_magic(full_path)
        if magic is not None:
            return (mimetypes.guess_type(magic.old_path(full_path))[0] 
                    or 'text/plain')
        else:
            return mimetypes.guess_type(full_path)[0] or 'text/plain'

    def _conditions(self, full_path, environ):
        """Return Etag and Last-Modified values defaults to now for both."""
        magic = self._match_magic(full_path)
        if magic is not None:
            return magic.conditions(full_path, environ)
        else:
            mtime = stat(full_path).st_mtime
            return str(mtime), rfc822.formatdate(mtime)

    def _file_like(self, full_path):
        """Return the appropriate file object."""
        magic = self._match_magic(full_path)
        if magic is not None:
            return magic.file_like(full_path)
        else:
            return open(full_path)

    def _body(self, full_path, environ, file_like):
        """Return an iterator over the body of the response."""
        magic = self._match_magic(full_path)
        if magic is not None:
            return magic.body(environ, file_like)
        else:
            way_to_send = environ.get('wsgi.file_wrapper', iter_and_close)
            return way_to_send(file_like, self.block_size)


class BaseMagic(object):
    """Base class for magic file handling.

    Really a do nothing if you were to use this directly.
    
    In a strait forward case you would just override .extension and body().
    (See StringMagic in this module for a simple example of subclassing.)

    In a more complex case you may need to override many or all methods.
    """

    extension = ''

    def exists(self, full_path):
        """Check that self.new_path(full_path) exists."""
        if path.exists(self.new_path(full_path)):
            return self.new_path(full_path)

    def new_path(self, full_path):
        """Add the self.extension to the path."""
        return full_path + self.extension

    def old_path(self, full_path):
        """Remove self.extension from path or raise MagicError."""
        if self.matches(full_path):
            return full_path[:-len(self.extension)]
        else:
            raise MagicError, "Path does not match this magic."

    def matches(self, full_path):
        """Check that path ends with self.extension."""
        if full_path.endswith(self.extension):
            return full_path

    def conditions(self, full_path, environ):
        """Return Etag and Last-Modified values (based on mtime)."""
        mtime = int(time.time())
        return str(mtime), rfc822.formatdate(mtime)

    def file_like(self, full_path):
        """Return a file object for path."""
        return open(full_path)

    def body(self, environ, file_like):
        """Return an iterator over the body of the response."""
        return [file_like.read()]


class StringMagic(BaseMagic):
    """Magic to replace variables in file contents using string.Template.
    
    Using this requires Python2.4.
    """

    extension = '.stp'
    safe = False

    def __init__(self, **variables):
        """Keyword arguments populate self.variables."""
        self.variables = variables

    def body(self, environ, file_like):
        """Pass environ and self.variables in to template.
        
        self.variables overrides environ so that suprises in environ don't
        cause unexpected output if you are passing a value in explicitly.
        """
        variables = environ.copy()
        variables.update(self.variables)
        template = string.Template(file_like.read())
        if self.safe is True:
            return [template.safe_substitute(variables)]
        else:
            return [template.substitute(variables)]


class KidMagic(StringMagic):
    """Like StringMagic only using the Kid templating language.
    
    Using this requires Kid: http://kid.lesscode.org/
    """
    
    extension = '.kid'
    
    def body(self, environ, full_path):
        """Pass environ and **self.variables into the template."""
        template = kid.Template(file=full_path, 
                                environ=environ, 
                                **self.variables)
        return [template.serialize()]


if __name__ == '__main__':

    #app = Cling('testdata')
    magics = StringMagic(title="String Test"), KidMagic(title="Kid Test")
    app = Shock('testdata', magics=magics)
    
    try:
        from wsgiref.simple_server import make_server
        make_server('localhost', 9999, app).serve_forever()
    except KeyboardInterrupt, ki:
        print "Cio, baby!"

