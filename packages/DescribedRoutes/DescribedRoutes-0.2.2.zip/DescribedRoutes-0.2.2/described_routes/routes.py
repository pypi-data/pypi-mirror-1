'''Support for Routes-based frameworks, e.g. Pylons'''

import sys
import re
from described_routes import ResourceTemplates
from link_header import format_link

if sys.version >= '2.6':
    import urlparse
    parse_qsl = urlparse.parse_qsl
else:
    import cgi
    parse_qsl = cgi.parse_qsl
    
try:
    import json
except ImportError:
    import simplejson as json

from described_routes import ResourceTemplates


__all__ = ['DescribedRoutesMiddleware', 'make_resource_templates']


RE_PARAM = re.compile(r'{[^}.][^}]+}')
RE_OPTIONAL_PARAM = re.compile(r'{\.[^}]+}')
RE_PARAM_WITH_REQS = re.compile(r'{(\w+):[^}]+}')


def _normalized_path(route):
    path = RE_PARAM_WITH_REQS.sub(lambda m: '{%s}' % m.group(1), route.routepath)
    if '{id}' in path and 'controller' in route.defaults:
        return path.replace('{id}', '{%s_id}' % route.defaults['controller'])
    return path

def _methods(route):   
    if route.conditions:
        method = route.conditions.get('method', '')
        return method if isinstance(method, list) else [method]
    else:
        return []

def _options(routes):
    METHODS = ['GET', 'PUT', 'POST', 'DELETE']
    def method_index(m):
        return METHODS.index(m) if m in METHODS else len(METHODS)
    return sorted(
                reduce(set.__or__, [set(_methods(route)) for route in routes]),
                key=method_index)
                
def _params(route):
    return [m[1:-1] for m in re.findall(RE_PARAM, _normalized_path(route))]

def _optional_params(route):
    return [m[2:-1] for m in re.findall(RE_OPTIONAL_PARAM, _normalized_path(route))]

def _route_cmp(route1, route2):
    return (cmp(_path_parts(_normalized_path(route1)),
                _path_parts(_normalized_path(route2))) or
            cmp('GET' not in _methods(route1), 'GET' not in _methods(route2)) or
            cmp(_methods(route1), _methods(route2)))

def _path_parts(path):
    if path.endswith('{.format}'):
        return (path[:-9], path[-9:])
    else:
        return (path, '')

def _rel(route, parent):
    if parent:
        if _params(route) != _params(parent):
            return None
        rlen = len(route.name)
        plen = len(parent.name)
        if rlen > plen + 1:
            if route.name.endswith(parent.name) and \
               not route.name[-(plen + 1)].isalnum():
                return route.name[:-(plen + 1)]
            elif route.name.startswith(parent.name) and \
                 not route.name[plen].isalnum():
                return route.name[plen + 1:]
        return route.name
    return None

def make_tree(sorted_routes, base='', root_has_children=False, parent=None):
    def partition(sorted_routes):
        exemplar = sorted_routes[0]
        path = _normalized_path(exemplar)
        stripped = _path_parts(path)[0]
        
        i = 1
        while (i < len(sorted_routes) and 
               _normalized_path(sorted_routes[i]) == path):
            i += 1
        same = sorted_routes[0:i]

        if stripped == '/' and not root_has_children:
            children, remainder = [], sorted_routes[i:]
        else:
            j = i
            while (j < len(sorted_routes) and 
                   _normalized_path(sorted_routes[j]).startswith(stripped)):
                j += 1
            children, remainder = sorted_routes[i:j], sorted_routes[j:]

        return exemplar, path, same, children, remainder

    def partitions(sorted_routes):
        while sorted_routes:
            exemplar, path, same, children, sorted_routes = partition(sorted_routes)
            if exemplar.name:
                yield exemplar, path, same, children
                
    return [dict(name=exemplar.name,
                 rel=_rel(exemplar, parent),
                 path_template=path,
                 options=_options(same),
                 params=_params(exemplar),
                 optional_params=_optional_params(exemplar),
                 resource_templates=make_tree(children, base, parent=exemplar),
                 **(dict(uri_template=base + path) if base else {}))
            for exemplar, path, same, children in partitions(sorted_routes)]

def make_resource_templates(mapper, base='', root_has_children=False):
    '''Convert a ``routes.Mapper`` to a ``ResourceTemplates`` object'''
    sorted_routes = sorted(mapper.matchlist, cmp=_route_cmp)
    return ResourceTemplates(make_tree(sorted_routes, base=base.rstrip('/'),
                                       root_has_children=root_has_children))
    

class DescribedRoutesMiddleware(object):
    """Serve ``ResourceTemplates`` and ``ResourceTemplate`` metadata; decorate
    regular resources with link headers"""
    
    def __init__(self, app, mapper, path='/described_routes', root_has_children=False):
        """Initialize ``DescribedRoutesMiddleware``.  It should be placed
        in the wsgi middleware stack between the ``RoutesMiddleWare`` and
        the main application.  In a Pylons app, the relevant section of
        ``config/middleware.py`` should look something like this::

                ...
                app = PylonsApp()
                app = DescribedRoutesMiddleware(app, config['routes.map'])
                app = RoutesMiddleware(app, config['routes.map'])
                ...

        By default, ``ResourceTemplates`` and ``ResourceTemplate`` data will
        be served at /described_routes. This can be overridden with the
        ``path`` parameter.
        """
        self.app = app
        self.pattern = re.compile(r'^%s(/([^/]+?)??)??(\.((json)|(txt)))?$' % path)
        self.mapper = mapper
        self.path = path
        self.root_has_children = root_has_children
        self.templates_cache = {}
        
    def __call__(self, environ, start_response):
        match = re.match(self.pattern, environ['PATH_INFO'])
        if match:
            return self.serve(environ, start_response,
                              route_name=match.group(2),
                              format=match.group(4))
        else:
            def _start_response(status, response_headers, exc_info=None):
                return start_response(status,
                                      response_headers + self.headers(environ),
                                      exc_info)
            return self.app(environ, _start_response)
            
    def headers(self, environ):
        """Describe an application resource with a link header"""
        try:
            route_name = environ['routes.route'].name
            base = _base(environ)
            if self.get_resource_template(route_name, base):
                query_string = environ.get('QUERY_STRING', '')
                routing_args = environ.get('wsgiorg.routing_args', (None, {}))[1]
                
                params = '&'.join("%s=%s" % (key, value)
                                  for key, value in routing_args.items()
                                  if key not in ['controller', 'action'])
                href = base + self.path + '/' + route_name
                if params:
                    href += '?' + params
                    if query_string:
                        href += '&' + query_string
                elif query_string:
                    href += '?' + query_string

                return [('Link', format_link(href, rel='describedby',
                                             meta='ResourceTemplate'))]
        except Exception:
            pass
        return []

    def serve(self, environ, start_response, route_name, format):
        """Serve ``ResourceTemplates`` and ``ResourceTemplate`` metadata at
        ``self.path`` (/resource_templates by default).
        
        ``ResourceTemplates`` data describing the whole application will be
        served at ``/described_routes`` by default.  ``ResourceTemplate`` data
        describing a resource named 'foo' will be served at
        ``/described_routes/foo``.  In both cases, routing parameters may be
        supplied, resulting in partially expanded templates, e.g. at
        ``/described_routes?format=json``.
        
        Data will be served in json format if the path has a .json extension
        or if the Accept header includes 'application/json' or if there is no
        Accept header at all.  Otherwise a tabular text format is served.
        """
        base = _base(environ)
        if route_name:
            target = self.get_resource_template(route_name, base)
            if target:
                rel = 'index'
            else:
                start_response('404 Not Found', [])
                return []
        else:
            target = self.get_resource_templates(base)
            rel = "self"

        params = dict(parse_qsl(environ.get('QUERY_STRING', '')))
        expanded = target.partial_expand(params) if params else target
        
        if not format:
            if 'application/json' in environ.get('HTTP_ACCEPT', 'application/json'):
                format = 'json'
            else:
                format = 'txt'
    
        if format == 'json':
            content_type = 'application/json'
            body = json.dumps(expanded.to_py())
        else:
            content_type = 'text/plain'
            body = str(expanded)

        start_response('200 OK',
                       [('Content-Type', content_type),
                        ('Link', format_link(base + self.path, rel=rel,
                                             meta='ResourceTemplates'))])
        return [body]

    def get_resource_template(self, route_name, base):
        return self._load_resource_templates(base)[2].get(route_name, None)
        
    def get_resource_templates(self, base):
        return self._load_resource_templates(base)[1]

    def _load_resource_templates(self, base):
        if base in self.templates_cache:
            cached = self.templates_cache[base]
            if self.mapper.matchlist[-1] is cached[0]:
                return cached
        resource_templates = make_resource_templates(
                                    self.mapper, base=base,
                                    root_has_children=self.root_has_children)
        resource_templates_by_name = resource_templates.all_by_name()
        last_route = self.mapper.matchlist[-1]
        cached = last_route, resource_templates, resource_templates_by_name
        self.templates_cache[base] = cached
        return cached
        

def _base(environ):
    http_host = environ.get('HTTP_HOST', '')
    if http_host:
        return 'http://' + http_host + environ.get('SCRIPT_NAME', '')
    else:
        return ''
