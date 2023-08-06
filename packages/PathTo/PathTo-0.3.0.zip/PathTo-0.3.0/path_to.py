"""
Resource-oriented client APIs generated dynamically from auto-discovered or locally-configured metadata.

Initialise from a server that supports auto-discovery via link headers (see the DescribedRoutes package)::

    app = open_app('http://example.com/users/', http)

Initialize from a ``described_routes.ResourceTemplates`` object or from a list/dict structure from which
a ``ResourceTemplates`` object can be constructed::

    app = Application(templates)

Later examples assume this kind of structure::

    >>> print str(app.resource_templates).rstrip()
    users              users         GET, POST        http://example.com/users{.format}
      new              new_user      GET              http://example.com/users/new{.format}
      {user_id}        user          GET, PUT, DELETE http://example.com/users/{user_id}{.format}
        edit           edit_user     GET              http://example.com/users/{user_id}/edit{.format}
        articles       user_articles GET, POST        http://example.com/users/{user_id}/articles{.format}
          {article_id} user_article  GET, PUT, DELETE http://example.com/users/{user_id}/articles/{article_id}{.format}

Chaining, indexing, following relationships::

    >>> print app.users['dojo'].edit
    http://example.com/users/dojo/edit

Positional and named parameters::

    >>> print app.user_article('dojo', 'foo', format='json')
    http://example.com/users/dojo/articles/foo.json

Parameter dictionaries::

    >>> print app.user_article({'user_id': 'dojo', 'article_id': 'foo', 'format': 'json'})
    http://example.com/users/dojo/articles/foo.json

Parameter inheritance::

    >>> Application(templates, params=dict(format='json')).users.uri
    'http://example.com/users.json'
    >>> Application(templates, format='json').users.uri
    'http://example.com/users.json'
    >>> Application(templates).with_params(format='json').users.uri
    'http://example.com/users.json'
"""

import re
import httplib2
import logging

from described_routes import ResourceTemplates
import link_header

try:
    import json
except ImportError:
    import simplejson as json


#__all__ = ['open_app', 'Application', 'Path', 'Response', 'NotFound',
#           'NoLinkFound', 'NoDescriptionFound', 'UnexpectedStatus']


log = logging.getLogger(__name__)

META = ["ResourceTemplate", "ResourceTemplates"]
RE_COLON = re.compile(' *: *')
MAX_HOPS = 3


class NotFound(Exception):
    """Base Exception class for discovery failures"""
    def __init__(self, msg, uri, hops):
        Exception.__init__(self, msg % (uri, hops))
        self.uri = uri
        self.hops = hops

        
class NoLinkFound(NotFound):
    """Couldn't find the expected link header"""
    def __init__(self, uri, hops):
        NotFound.__init__(self,
                          "no link found at [%s] after %d hops",
                          uri, hops)


class NoDescriptionFound(NotFound):
    """Couldn't find the app description after given number of link hops"""
    def __init__(self, uri, hops):
        NotFound.__init__(self,
                          "no app description found at [%s] after %d hops",
                          uri, hops)


class UnexpectedStatus(Exception):
    def __init__(self, method, uri, response, content, expected_status):
        Exception.__init__(self, "%s %s failed, got status %s, expected %s" %
                                 (method, uri, response.status, expected_status))
        self.method = method
        self.uri = uri
        self.response = response
        self.status = response.status
        self.content = content
        self.expected_status = expected_status


def open_app(uri, base=None, http=None, headers=None, params=None,
             application_class=None, **more_params):
    """
    "Discover" a server application by following link headers at the given URI,
    create a client application proxy.
    
    Link headers of interest have a ``meta`` attribute of "ResourceTemplate"
    or "ResourceTemplates"  The target URI has a ``rel`` containing "self"; to
    reach this it will if necessary follow links that have ``rel`` attributes
    of "describedby" or "index".
    
    The ``ResourceTemplates`` description of the application will be retrieved
    from the target URI and converted from JSON.  From this description an
    ``Application`` object (or object returned by ``application_class``) is
    created and returned.
    
    Arguments (all optional except for ``uri``)::
    
    ``uri``
        The initial URI at which the discovery process starts.
        
    ``base``
        A default base URI to pass through to the created application
        
    ``http``
        A ``httplib2.Http`` object (or equivalent).  One will be created if
        none is supplied; it is used both for the discovery process and to
        pass through to the created application
        
    ``headers``
        Default headers to pass through to the created application
        
    ``params``
        Default params to pass through to the created application
        
    ``application_class``
        The class of the created application, defaults to ``Application``.
        
    Any extra keyword arguments are passed on to the created application.
    """
    def get_links(uri):
        for method in ['HEAD', 'GET']:
            log.debug("request %s %s", method, uri)
            response, content = http.request(uri, method=method)
            if response.status == 200:
                break;
        if response.status != 200:
            raise UnexpectedStatus(method, uri, response, content, 200)
        links = response.get('link', None)
        if links:
            return link_header.parse(links.rstrip()).links
        else:
            return []    
    
    def find_app_description_uri(uri):
        for hop in range(MAX_HOPS):
            for link in get_links(uri):
                if getattr(link, 'meta', '') in META:
                    if link.rel in ['describedby', 'index']:
                        uri = link.href
                        break
                    elif link.rel == 'self':
                        return link.href
            else:
                raise NoLinkFound(uri, hop)
        raise NoDescriptionFound(uri, hop)

    if not http:
        http = httplib2.Http()

    description_uri = find_app_description_uri(uri)
    log.debug("request %s %s", 'GET', description_uri)
    response, body = http.request(description_uri, method='GET',
                                  headers=dict(accept='application/json'))
    if response.status != 200:
        raise UnexpectedStatus(method, uri, response, content, expected_status)

    return (application_class or Application)(
                                    resource_templates=json.loads(body),
                                    http=http, base=base, headers=headers,
                                    params=params, **more_params)

    
class Path(object):
    """A client-side proxy to a server-side resource, identified by a resource
    template and params.  Path objects are not usually constructed directly,
    but are generated by navigating the application's structure as defined
    by its resource template.
    
    Example::
        
        >>> user = app.users['dojo']
        >>> type(user)
        <class 'path_to.Path'>
        >>> user.resource_template.name
        'user'
        >>> user.resource_template.uri_template
        'http://example.com/users/{user_id}{.format}'
        >>> user.params
        {'user_id': 'dojo'}
        >>> user.uri
        'http://example.com/users/dojo'
    """
    
    def __init__(self, parent, resource_template, params):
        """Initialize a new Path object with `parent` (another Path),
        `resource_template` and `params`.
        
        A root object `self.application` is inherited from the parent.
        `self.uri` is generated from the resource template and params.
        """
        self.parent = parent
        self.resource_template = resource_template
        self.params = params
        
        if parent:
            self.application = parent.application
        else:
            self.application = None
        
        if self.resource_template:
            self.uri = self.resource_template.uri_for(self.params, self.application.base)
        else:
            self.uri = None

    def with_params(self, *args, **kwargs):
        """Create a new object of the same type but with additional params.
        
        Example::

            >>> user = app.users['dojo']
            >>> user.params
            {'user_id': 'dojo'}
            >>> user.with_params(format='json').params
            {'user_id': 'dojo', 'format': 'json'}
        """
        return type(self)(self, self.resource_template, self._make_child_params(None, args, kwargs))
        
    def _make_child_params(self, resource_template, args, kwargs):
        child_params = dict(self.params)
        if args and isinstance(args[-1], dict):
            args = list(args)
            while args and isinstance(args[-1], dict):
                child_params.update(args.pop())
        if args and resource_template:
            child_params.update(dict(zip(resource_template.positional_params(self.resource_template), args)))
        child_params.update(kwargs)
        return child_params

    def child(self, rel, *args, **kwargs):
        """Creates a child object matching the given rel, args and kwargs.
        
        Example::
        
            >>> user = app.child('users').child(None, 'dojo', format='json')
            >>> user.resource_template.name
            'user'
            >>> user.params
            {'user_id': 'dojo', 'format': 'json'}
            
        This is equivalent to:

            >>> user = app.users['dojo'].with_params(format='json')
        """
        for rt in self._candidate_child_templates(rel):
            child_params = self._make_child_params(rt, args, kwargs)
            if not [param for param in rt.params if param not in child_params]:
                return self.child_class_for(rt, child_params)(self, rt, child_params)
        else:
            raise LookupError(
                    "can't find child resource template of %s with rel %s, args %s, kwargs %s" %
                    (repr(self), repr(rel), repr(args), repr(kwargs)))
                                
    def _candidate_child_templates(self, rel):
        return self.resource_template.find_by_rel(rel)
        
    def child_class_for(self, resource_template, params):
        """Determines the class of new child objects with given
        `resource_template` and `params`; override as necessary.   The default
        implementation is delegated to `self.application`, the root object.
        """
        return self.application.child_class_for(resource_template, params)
                
    def __str__(self):
        return str(self.uri)

    def __getitem__(self, *args):
        """Index into a collection resource, matching the given args to the
        params of the member resource.
        
        Example:
        
            >>> user = app.users['dojo']
            >>> user.params
            {'user_id': 'dojo'}
        """
        if args and isinstance(args[0], tuple):
            args = args[0]
        return self.child(None, *args)
        
    def __getattr__(self, attr):
        """Fill in missing properties as either child resources or as callables
        that will collect missing params required by child resources.
        
        Examples::

            >>> type(app.users)
            <class 'path_to.Path'>
            >>> type(app.user)
            <type 'function'>
            >>> app.foo
            Traceback (most recent call last):
            AttributeError: foo
        """
        if self._candidate_child_templates(attr):
            try:
                return self.child(attr)
            except LookupError:
                return lambda *args, **kwargs: self.child(attr, *args, **kwargs)
        else:
            raise AttributeError, attr

    def __call__(self, *args, **kwargs):
        return self.with_params(*args, **kwargs)
        
    def get(self, headers=None, expected_status=None):
        """Perform a GET request on ``self.uri`` with optional `headers` and
        `expected_response` (see ``Application.request``)"""
        return self.application.request(method='GET', uri=self.uri, body='',
                                        headers=headers,
                                        expected_status=expected_status)
        
    def head(self, headers=None, expected_status=None):
        """Perform a HEAD request on ``self.uri`` with optional `headers` and
        `expected_response` (see ``Application.request``)"""
        return self.application.request(method='HEAD', uri=self.uri, body='',
                                        headers=headers,
                                        expected_status=expected_status)

    def delete(self, headers=None, expected_status=None):
        """Perform a DELETE request on ``self.uri`` with optional `headers` and
        `expected_response` (see ``Application.request``)"""
        return self.application.request(method='DELETE', uri=self.uri, body='',
                                        headers=headers,
                                        expected_status=expected_status)

    def put(self, body='', headers=None, expected_status=None):
        """Perform a PUT request on ``self.uri`` with optional `headers` and
        `expected_response` (see ``Application.request``)"""
        return self.application.request(method='PUT', uri=self.uri, body=body,
                                        headers=headers,
                                        expected_status=expected_status)

    def post(self, body='', headers=None, expected_status=None):
        """Perform a POST request on ``self.uri`` with optional `headers` and
        `expected_response` (see ``Application.request``)"""
        return self.application.request(method='POST', uri=self.uri, body=body,
                                        headers=headers,
                                        expected_status=expected_status)


class Application(Path):
    """A client-side proxy to a server-side application; the root from which
    child Path objects descend"""
    def __init__(self, resource_templates, parent=None, params=None, http=None,
                 base=None, headers=None, **more_params):
        """Initialize a new Application object.
        
        Arguments (all optional except for ``resource_templates``)::
        
        ``resource_templates``
            A ResourceTemplates object or a list object from which a
            ResourceTemplates object can be initialized.
        
        ``parent``
            Usually ``None``, but will be set when one ``Application`` object
            is derived from another via ``Application.with_params()``.
            
        ``params``
            A dict of parameters that will be inherited by child ``Path``
            objects.
            
        ``http``
            A ``httplib2.Http`` (or equivalent) object through which server
            requests will be made.
            
        ``base``
            The base URI of the application.  This will be used in the
            generation of URIs when ``ResourceTemplate`` objects have
            a ``path_template`` defined but no ``uri_template``.
        
        ``headers``
            Default headers to send on server requests.
        
        Any extra keyword arguments are merged into to the new object's ``params``.
        """
        Path.__init__(self, parent, None, dict(params or {}, **more_params))
        if isinstance(resource_templates, ResourceTemplates):
            self.resource_templates = resource_templates
        else:
            self.resource_templates = ResourceTemplates(resource_templates)

        self.http = http
        self.base = base
        self.headers = headers or {}

        if self.application is None:
            self.application = self

        self.default_class = parent.default_class if parent else Path
        
    def with_params(self, *args, **kwargs):
        """Create a new object of the same type but with additional params.
        
        Example::

            >>> app.with_params(format='json').params
            {'format': 'json'}
        """
        return type(self)(resource_templates=self.resource_templates,
                          parent=self,
                          params=self._make_child_params(None, args, kwargs),
                          http=self.http)


    def _candidate_child_templates(self, rel):
        if rel in self.resource_templates.all_by_name():
            return [self.resource_templates.all_by_name().get(rel)]
        else:
            return []

    def child_class_for(self, resource_template, params):
        """Specify the class of new child objects.  Override as necessary;
        the default implementation returns ``self.default_class`` which is set
        on initialization to ``Path``.
        """
        return self.default_class
        
    def uri(self):
        """Returns the application's base URI"""
        return self.base

    def request(self, method, uri, body='', headers=None, expected_status=None):
        """Perform a server request, returning a ``Response`` object.
        
        Arguments::
        
        ``method``
            The HTTP method, e.g. "POST"
        
        ``uri``
            The URI of the request
        
        ``body`` (optional)
            The request body.  A body of a string type will be sent as-is;
            other types will be converted to JSON.
            
        ``headers`` (optional)
            A dict of headers to send, overriding the default ``self.headers``
            
        ``expected_status``
            If provided, the response status is compared to this value and an
            ``UnexpectedStatus`` exception raised if they differ.
        """
        if self.application is not self:
            return self.application.request(method, uri, body, headers, expected_status)

        log.debug("request %s %s", method, uri)
        if headers is None:
            headers = self.headers

        if not isinstance(body, (str, unicode)):
            body = json.dumps(body)

        response, content = self.http.request(uri, method=method,
                                              headers=headers, body=body)

        if expected_status and response.status != expected_status:
            raise UnexpectedStatus(method, uri, response, content,
                                   expected_status)

        if 'set-cookie' in response:
            self.headers = dict(cookie=response['set-cookie'])

        return Response(response, content)


class Response(object):
    """The result of a server request"""
    def __init__(self, response, content):
        """Initialize with the  ``response``and ``content`` values returned
        by a server request.
        """
        self.response = response
        self.content = content
        self._parsed = None
    
    @property
    def parsed(self):
        """The content parsed with ``json.loads``, memoized.
        
        Example::
        
            >>> Response(None, '{"foo": "bar"}').parsed['foo']
            u'bar'
        """
        if not self._parsed:
          self._parsed = json.loads(self.content)
        return self._parsed


# For doctests:

templates = [
    {
        'name':               'users',
        'uri_template':       'http://example.com/users{.format}',
        'optional_params':    ['format'],
        'options':            ['GET', 'POST'],
        'resource_templates': [
            {
                'name':               'new_user',
                'rel':                'new',
                'uri_template':       'http://example.com/users/new{.format}',
                'optional_params':    ['format'],
                'options':            ['GET'],
            },
            {
                'name':               'user',
                'uri_template':       'http://example.com/users/{user_id}{.format}',
                'params':             ['user_id'],
                'optional_params':    ['format'],
                'options':            ['GET', 'PUT', 'DELETE'],
                'resource_templates': [
                    {
                        'name':            'edit_user',
                        'rel':             'edit',
                        'uri_template':    'http://example.com/users/{user_id}/edit{.format}',
                        'params':          ['user_id'],
                        'optional_params': ['format'],
                        'options':         ['GET']
                    },
                    {
                        'name':            'user_articles',
                        'rel':             'articles',
                        'uri_template':    'http://example.com/users/{user_id}/articles{.format}',
                        'params':          ['user_id'],
                        'optional_params': ['format'],
                        'options':         ['GET', 'POST'],
                        'resource_templates': [
                            {
                                'name':               'user_article',
                                'uri_template':       'http://example.com/users/{user_id}/articles/{article_id}{.format}',
                                'params':             ['user_id', 'article_id'],
                                'optional_params':    ['format'],
                                'options':            ['GET', 'PUT', 'DELETE']
                            }
                        ]
                    }
                ]
            }
        ]
    }
]

app = Application(templates, http=None)

