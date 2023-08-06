# urlminer.py
#
# Copyright (c) 2009 Stephen Day
#
# This module is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
#

import re
import warnings
from wsgiref.util import application_uri
from urlparse import urljoin
from urllib import quote

VALID_CLASS_ATTRIBUTES =  ['children', 'pattern', 'path_nodes']

HTTP_REDIRECT_CODES = {300: 'Multiple Choices',
                       301: 'Moved Permanently',
                       302: 'Found',
                       303: 'See Other',
                       304: 'Not Modified',
                       305: 'Use Proxy',
                       307: 'Temporary Redirect'}


class _metaclass(type):
    """
    This class compiles Resource `pattern`s and guesses `path_nodes` values if needed.

    It also limits allowed attribute names to prevent bugs due to spelling errors
    (see VALID_CLASS_ATTRIBUTES).
    """

    def __init__(cls, name, bases, classdict):
        super(_metaclass, cls).__init__(name, bases, classdict)
        for k in classdict:
            if isinstance(classdict[k], (basestring,list,tuple,re._pattern_type)):
                if not(k.endswith('_') or k in VALID_CLASS_ATTRIBUTES):
                    raise AttributeError("'%s' is not a legal class attribute name. Fix spelling, postfix with an underscore, "+
                                         "or update VALID_CLASS_ATTRIBUTES" % k)
        if cls.pattern is not None:
            if isinstance(cls.pattern, basestring):
                cls._compiled_pattern = re.compile(cls.pattern)
            else:
                cls._compiled_pattern = cls.pattern
            if hasattr(cls,'path_nodes'):
                if cls._compiled_pattern.pattern.count('/') and cls.path_nodes < 2:
                    raise Exception("'path_nodes' must be > 1 as the pattern for '%s' contains at least one '/'" % name)
            else:
                cls.path_nodes = cls._compiled_pattern.pattern.count('/') + 1
                if cls.path_nodes > 1 and cls._compiled_pattern.pattern.count('|'):
                    warnings.warn("The value of 'pattern' looks complex and 'path_nodes' for '%s' was not specified, guessing value: %s" % (name, cls.path_nodes))


class Resource(object):
    """Base resource class. A Resource object is a regular WSGI
    application that is initialized with a couple of optional parameters. 

    Resource must be sub-classed to provide any useful functionality
    (otherwise objects return only 404s). Subclasses can provide methods with
    names corresponding HTTP methods (e.g., GET, POST, etc). These methods
    must themselves be WSGI application. Alternatively, Resource.index()
    (another WSGI application) can be overridden or extended.

    Usually, you will create subclasses of Resource for each actual
    resource being served, and a final subclass for the root of your
    application. Normally this "root" subclass is the only one that your
    code will call directly.
    """

    children = []
    "Subclasses of Resource that will be searched in __call__ if PATH_INFO is not empty."
    
    pattern = None
    """Regexp pattern that is used by the "parent" to determine if this class should be called.
    Can be a string or compiled regular expression. Also see _match_path_info()."""
    
    __metaclass__ = _metaclass
    
    def __init__(self,parent_app=None,match_object=None):
        """"This class is usually instantiated by the __call__ method of its "parent",
        except when at the application root.
        """
        
        self.parent = parent_app
        self.mo = match_object
            
    def __call__(self, environ, start_response):
        """Routes incomming request to another WSGI application based on the values of PATH_INFO
        and self.children, updating PATH_INFO and SCRIPT_NAME if needed.

        If PATH_INFO is empty, call self.index().
        Else, try and match with each of the patterns of the children and call one.
        Else, call self.default().
        """
        
        if environ.get('PATH_INFO','') == '':
            return self.index(environ, start_response)
        else:
            for App in self.children:
                mo = _match_path_info(App._compiled_pattern, environ['PATH_INFO'],App.path_nodes)
                if mo:
                    environ['SCRIPT_NAME'] = environ['SCRIPT_NAME'] + environ['PATH_INFO'][:mo.end()]
                    environ['PATH_INFO'] = environ['PATH_INFO'][mo.end():]
                    return App(self,mo)(environ, start_response)
            else:
                return self.default(environ, start_response)

    @property
    def path_arg(self):
        "The entire matching string of self.mo"
        return self.mo.group(0)

    @property
    def named_args(self):
        "A dictionary of named groups in self.mo"
        return self.mo.groupdict()

    def default(self,environ, start_response):
        """Checks if PATH_INFO is '/' and calls self.index (if at server root) or
        redirects to the de-slashed url. If PATH_INFO is not '/', return a 404 resonse.
        """
        
        if environ.get('PATH_INFO','') == '/':
            if environ['SCRIPT_NAME'] == '':
                environ['PATH_INFO'], environ['SCRIPT_NAME'] = environ['SCRIPT_NAME'], environ['PATH_INFO']
                return self.index(environ, start_response)
            else:
                location = quote(environ['SCRIPT_NAME'])#application_uri(environ)
                if environ.get('QUERY_STRING'):
                   location += '?' + environ['QUERY_STRING']
                return redirect(location,status='301 Moved Permanently')(environ, start_response)
        else:
            return self.not_found(environ, start_response)

    def index(self, environ, start_response):
        """Route the request to another WSGI application based on the REQUEST_METHOD.

        If REQUEST_METHOD matches a method name, use that, otherwise return a 404 resonse.
        """

        try:
            method = getattr(self, environ['REQUEST_METHOD'].upper())
        except AttributeError:
            method = self.not_found
        return method(environ, start_response)

    def not_found(self, environ, start_response):
        status = '404 Not Found'
        response_headers = [('Content-type','text/plain')]
        start_response(status,response_headers)
        return ["The request URL doesn't map to any resource."]    


def redirect(location, status):
    """Return a WSGI application that does a HTTP redirect.

    :parameters:
      location
        The url for the redirect. May be a relative url, in which case it will
        be transformed to an absolute url. The value should made url-safe before
        it is passed in.
      status
        The full HTTP status code (e.g., "303 See Other"). The int values 301, 302,
        and 303 may also be supplied, in which case they will be converted to
        appropriate string values (see HTTP_REDIRECT_CODES).
	"""

    if isinstance(status, int):
        status = str(status) + ' ' + HTTP_REDIRECT_CODES[status]
    def func(environ, start_response):
        abs_location = urljoin(application_uri(environ),location)
        response_headers = [('Content-Type', 'text/html'), ('Location', abs_location)]
        start_response(status, response_headers)
        return ["""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html><head><title>Redirecting</title></head><body><p>Redirecting to <a href="%s">%s</a> ...</p></body></html>"""
                % (abs_location,abs_location)]
    return func
        

def _xfind(char,string,occurence):
    """Return the index of the n'th occurence of a character in a string.

    >>> _xfind ('/','/foo/bar/',2)
    4
    >>> _xfind ('/','/foo/bar/',4)
    >>>

    """

    start = 0
    for x in range(occurence):
        i = string.find(char,start)
        if i == -1:
            return None
        start=i+1
    return i


def _match_path_info(path_regexp,path_info,path_nodes):
    """Try to match a regular expression to a variable segment of PATH_INFO.

    :parameters:
      path_regexp
        The compiled regular expression to match against path_info. The pattern
        should not include the leading or trailing slashes of the path segment
        to match. The regexp can include slashes, if slashes are included,
        `path_nodes` must be > 1.
      path_info
        The value of PATH_INFO. The first character must be '/' or a ValueError will
        be raised.
      path_nodes
        The number of "path nodes" included in the match, where a path node is
        what is contained between two slashes, or the last slash and the end
        of the string. Path nodes can be empty, so the path "/" contains one node. 

    >>> _match_path_info(re.compile("foo"),"/foo",1).group(0)
    'foo'
    >>> _match_path_info(re.compile("foo"),"/foo/bar",1).group(0)
    'foo'
    >>> _match_path_info(re.compile("foo"),"/foobar",1) is None
    True
    >>> _match_path_info(re.compile("foo"),"/fo",1) is None
    True
    >>> _match_path_info(re.compile("foo/bar"),"/foo/bar",2).group(0)
    'foo/bar'
    >>> _match_path_info(re.compile(""),"/foo",1) is None
    True
    >>> _match_path_info(re.compile(""),"/",1).group(0)
    ''

    """

    index = _xfind('/',path_info,path_nodes+1)
    if index is None:
        if _xfind('/',path_info,path_nodes) is not None:
            index = len(path_info)
        elif path_info.startswith('/'):
            return None
        else:
            raise ValueError("path_info must start with a '/'")
    mo = path_regexp.match(path_info,1,index)
    if mo and mo.end() == index:
        return mo
    
      
def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()    
