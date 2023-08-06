import unittest
from routes import Mapper

from described_routes.routes import (_normalized_path, _methods, _options,
                                     _params, _route_cmp, _rel, make_tree,
                                     make_resource_templates,
                                     DescribedRoutesMiddleware)
from described_routes.routes import json


STR_RTS = """\
root              root                    /
entries           entries                 /entries
  {entry_id}      entry         GET, POST /entries/{entry_id}
    details       entry_details           /entries/{entry_id}/details
      {detail_id} entry_detail            /entries/{entry_id}/details/{detail_id}
    edit          edit_entry              /entries/{entry_id}/edit
things            things                  /things
  {thing_id}      thing                   /things/{thing_id}
"""

ENTRY_STR = """\
entry           entry         GET, POST /entries/1
  details       entry_details           /entries/1/details
    {detail_id} entry_detail            /entries/1/details/{detail_id}
  edit          edit_entry              /entries/1/edit
"""

ENTRY_PYTHON = {
    'name': 'entry',
    'path_template': '/entries/1',
    'options': ['GET', 'POST'],
    'resource_templates': [
        {
            'name': 'entry_details',
            'rel': 'details',
            'path_template': '/entries/1/details',
            'resource_templates': [
                {
                    'name': 'entry_detail',
                    'path_template': '/entries/1/details/{detail_id}',
                    'params': ['detail_id'],
                }
            ],
        },
        {
            'name': 'edit_entry',
            'rel': 'edit',
            'path_template': '/entries/1/edit',
        }
    ]
}

def make_mapper():
    mapper = Mapper(explicit=True)
    mapper.minimization = False
    mapper.connect('root',          '/')
    mapper.connect('entries',       '/entries')
    mapper.connect('entry',         '/entries/{entry_id}', conditions=dict(method='GET'))
    mapper.connect(None,            '/entries/{entry_id}', conditions=dict(method='POST'))
    mapper.connect('edit_entry',    '/entries/{entry_id}/edit')
    mapper.connect('entry_details', '/entries/{entry_id}/details')
    mapper.connect('entry_detail',  '/entries/{entry_id}/details/{detail_id}')
    mapper.connect('things',        '/things')
    mapper.connect('thing',         '/things/{id}', controller='thing')
    mapper.connect(None,            '/un-named')
    return mapper

def _find_route(mapper, route_name):
    return [route for route in mapper.matchlist if route.name == route_name][0]


class TestRoutes(unittest.TestCase):
    
    def setUp(self):
        self.mapper = make_mapper()
        
    def test_normalized_path(self):
        # Unchanged
        self.assertEqual('/entries/{entry_id}/details/{detail_id}',
                         _normalized_path(_find_route(self.mapper, 'entry_detail')))
        # Unchanged
        self.assertEqual('/things/{thing_id}',
                         _normalized_path(_find_route(self.mapper, 'thing')))
    
    def test_methods(self):
        self.assertEqual(['GET'],
                         _methods(_find_route(self.mapper, 'entry')))

    def test_options(self):
        self.assertEqual([],
                         _options([_find_route(self.mapper, 'entries')]))
        self.assertEqual(['GET', 'POST'],
                         _options([_find_route(self.mapper, 'entry'),
                                   _find_route(self.mapper, None)]))

    def test_params(self):
        self.assertEqual([],
                         _params(_find_route(self.mapper, 'entries')))
        self.assertEqual(['entry_id', 'detail_id'],
                         _params(_find_route(self.mapper, 'entry_detail')))

    def test_route_cmp(self):
        # same
        self.assertEqual(0,
                         _route_cmp(_find_route(self.mapper, 'entries'),
                                    _find_route(self.mapper, 'entries')))
        # differ by path
        self.assertEqual(-1,
                         _route_cmp(_find_route(self.mapper, 'entries'),
                                    _find_route(self.mapper, 'entry')))
        # differ by methods
        self.assertEqual(-1,
                         _route_cmp(_find_route(self.mapper, 'entry'),
                                    _find_route(self.mapper, None)))

    def test_rel(self):
        self.assertEqual('entries',
                         _rel(_find_route(self.mapper, 'entries'),
                              _find_route(self.mapper, 'root')))
        self.assertEqual(None,
                         _rel(_find_route(self.mapper, 'entry'),
                              _find_route(self.mapper, 'entries')))
        self.assertEqual('edit',
                         _rel(_find_route(self.mapper, 'edit_entry'),
                              _find_route(self.mapper, 'entry')))
        self.assertEqual('details',
                         _rel(_find_route(self.mapper, 'entry_details'),
                              _find_route(self.mapper, 'entry')))

    def test_make_tree(self):
        tree = make_tree(sorted(self.mapper.matchlist, cmp=_route_cmp))
        self.assertEqual(['root', 'entries', 'things'],
                         [toplevel['name'] for toplevel in tree])
        self.assertEqual('entry',
                         tree[1]['resource_templates'][0]['name'])
        self.assertEqual('entry_details',
                         tree[1]['resource_templates'][0]['resource_templates'][0]['name'])
        self.assertEqual('entry_detail',
                         tree[1]['resource_templates'][0]['resource_templates'][0]['resource_templates'][0]['name'])

    def test_make_tree_with_root_has_children(self):
        tree = make_tree(sorted(self.mapper.matchlist, cmp=_route_cmp),
                         root_has_children=True)
        self.assertEqual(['root'],
                         [toplevel['name'] for toplevel in tree])
        self.assertEqual('entries',
                         tree[0]['resource_templates'][0]['name'])
        self.assertEqual('entry',
                         tree[0]['resource_templates'][0]['resource_templates'][0]['name'])

    def test_make_resource_templates(self):
        rts = make_resource_templates(self.mapper)
        self.assertEqual(['root', 'entries', 'things'],
                         [toplevel.name for toplevel in rts])
        self.assertEqual('entry',
                         rts[1].resource_templates[0].name)
        self.assertEqual('entry_details',
                         rts[1].resource_templates[0].resource_templates[0].name)
        self.assertEqual('entry_detail',
                         rts[1].resource_templates[0].resource_templates[0].resource_templates[0].name)
                         
        self.assertEqual(STR_RTS, str(rts))


    def test_make_resource_templates_with_base(self):
        base = 'http://example.com/'
        rts = make_resource_templates(self.mapper, base=base)
        self.assertEqual('http://example.com/entries', rts[1].uri_template)
        

class TestDescribedRoutesMiddleware(unittest.TestCase):
    
    def setUp(self):
        self.mapper = make_mapper()
        self.middleware = DescribedRoutesMiddleware(self.app, self.mapper)
        self.status = self.response_headers = None
    
    def app(self, environ, start_response):
        start_response("200 OK", [('App-Header', 'Header-Value')])
        return ["Content"]
    
    def _start_response(self, status, response_headers, exc_info=None):
        self.status = status
        self.response_headers = response_headers

    def test_headers(self):
        body = self.middleware({'PATH_INFO': '/entries/1',
                                'HTTP_HOST': 'example.com',
                                'routes.route': _find_route(self.mapper, 'entry'),
                                'wsgiorg.routing_args': (None, {'entry_id': '1'})},
                                self._start_response)
        self.assertEqual(['Content'], body)
        self.assertEqual('200 OK', self.status)        
        self.assertEqual([('App-Header', 'Header-Value'),
                          ('Link', '<http://example.com/described_routes/entry?entry_id=1>; meta=ResourceTemplate; rel=describedby')],
                         self.response_headers)

    def test_headers_for_unknown_route(self):
        body = self.middleware({'PATH_INFO': '/entries/1'},
                                self._start_response)
        self.assertEqual(['Content'], body)
        self.assertEqual('200 OK', self.status)        
        self.assertEqual([('App-Header', 'Header-Value')],
                         self.response_headers)
        
    def test_serve_txt(self):
        body = self.middleware({'PATH_INFO': '/described_routes.txt'},
                                self._start_response)
        self.assertEqual([STR_RTS], body)
        self.assertEqual('200 OK', self.status)        
        self.assertEqual([('Content-Type', 'text/plain'),
                          ('Link', '</described_routes>; meta=ResourceTemplates; rel=self')],
                         self.response_headers)

        body = self.middleware({'PATH_INFO': '/described_routes/entry.txt',
                                'QUERY_STRING': 'entry_id=1'},
                                self._start_response)
        self.assertEqual([ENTRY_STR], body)
        self.assertEqual('200 OK', self.status)        
        self.assertEqual([('Content-Type', 'text/plain'),
                          ('Link', '</described_routes>; meta=ResourceTemplates; rel=index')],
                         self.response_headers)

    def test_serve_json(self):
        body = self.middleware({'PATH_INFO': '/described_routes/entry.json',
                                'QUERY_STRING': 'entry_id=1'},
                                self._start_response)
        self.assertEqual(ENTRY_PYTHON, json.loads(body[0]))
        self.assertEqual('200 OK', self.status)        
        self.assertEqual([('Content-Type', 'application/json'),
                          ('Link', '</described_routes>; meta=ResourceTemplates; rel=index')],
                         self.response_headers)
