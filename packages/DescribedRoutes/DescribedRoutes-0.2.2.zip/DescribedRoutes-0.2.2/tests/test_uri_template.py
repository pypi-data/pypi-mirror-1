import unittest

from described_routes.uri_template import sub


# Acknowledgement: the first set of unit tests is based on Joe Gregorio's (in turn based on examples in his v3 spec)
# Note: the commented-out examples aren't yets supported (see "Limitations")

TESTDATA = [
    ('/path/to/{foo}',                          {},                            '/path/to/'),
    ('/path/to/{foo}',                          {'foo': 'barney'},             '/path/to/barney'),
#   ('/path/to/{foo=wilma}',                    {},                            '/path/to/wilma'),
#   ('/path/to/{foo=wilma}',                    {'foo': 'barney'},             '/path/to/barney'),
    ('/path/to/{foo}',                          {'foo': 'barney'},             '/path/to/barney'),

    ('/path/to/{-prefix|&|foo}',                {},                            '/path/to/'),
#   ('/path/to/{-prefix|&|foo=wilma}',          {},                            '/path/to/&wilma'),
#   ('/path/to/{-prefix||foo=wilma}',           {},                            '/path/to/wilma'),
#   ('/path/to/{-prefix|&|foo=wilma}',          {'foo': 'barney'},             '/path/to/&barney'),
#   ('/path/to/{-prefix|&|foo}',                {'foo': ['wilma', 'barney']},  '/path/to/&wilma&barney'),
    ('/path/to/{-prefix|&|foo}',                {'foo': 'barney'},             '/path/to/&barney'),

    ('/path/to/{-suffix|/|foo}',                {},                            '/path/to/'),
#   ('/path/to/{-suffix|#|foo=wilma}',          {},                            '/path/to/wilma#'),
#   ('/path/to/{-suffix|&?|foo=wilma}',         {'foo': 'barney'},             '/path/to/barney&?'),
#   ('/path/to/{-suffix|&|foo}',                {'foo': ['wilma', 'barney']},  '/path/to/wilma&barney&'),
    ('/path/to/{-suffix|&?|foo}',               {'foo': 'barney'},             '/path/to/barney&?'),

    ('/path/to/{-join|/|foo}',                  {},                            '/path/to/'),
    ('/path/to/{-join|/|foo,bar}',              {},                            '/path/to/'),
    ('/path/to/{-join|&|q,num}',                {},                            '/path/to/'),
#   ('/path/to/{-join|#|foo=wilma}',            {},                            '/path/to/foo=wilma'),
#   ('/path/to/{-join|#|foo=wilma,bar}',        {},                            '/path/to/foo=wilma'),
#   ('/path/to/{-join|#|foo=wilma,bar=barney}', {},                            '/path/to/foo=wilma#bar=barney'),
#   ('/path/to/{-join|&?|foo=wilma}',           {'foo': 'barney'},             '/path/to/foo=barney'),
    ('/path/to/{-join|&?|foo}',                 {'foo': 'barney'},             '/path/to/foo=barney'),

    ('/path/to/{-list|/|foo}',                  {},                            '/path/to/'),
    ('/path/to/{-list|/|foo}',                  {'foo': ['a', 'b']},           '/path/to/a/b'),
    ('/path/to/{-list||foo}',                   {'foo': ['a', 'b']},           '/path/to/ab'),
    ('/path/to/{-list|/|foo}',                  {'foo': ['a']},                '/path/to/a'),
    ('/path/to/{-list|/|foo}',                  {'foo': []},                   '/path/to/'),

    ('/path/to/{-opt|&|foo}',                   {},                            '/path/to/'),
    ('/path/to/{-opt|&|foo}',                   {'foo': 'fred'},               '/path/to/&'),
    ('/path/to/{-opt|&|foo}',                   {'foo': []},                   '/path/to/'),
    ('/path/to/{-opt|&|foo}',                   {'foo': ['a']},                '/path/to/&'),
    ('/path/to/{-opt|&|foo,bar}',               {'foo': ['a']},                '/path/to/&'),
    ('/path/to/{-opt|&|foo,bar}',               {'bar': 'a'},                  '/path/to/&'),
    ('/path/to/{-opt|&|foo,bar}',               {},                            '/path/to/'),

    ('/path/to/{-neg|&|foo}',                   {},                            '/path/to/&'),
    ('/path/to/{-neg|&|foo}',                   {'foo': 'fred'},               '/path/to/'),
    ('/path/to/{-neg|&|foo}',                   {'foo': []},                   '/path/to/&'),
    ('/path/to/{-neg|&|foo}',                   {'foo': ['a']},                '/path/to/'),
    ('/path/to/{-neg|&|foo,bar}',               {'bar': 'a'},                  '/path/to/'),
    ('/path/to/{-neg|&|foo,bar}',               {'bar': []},                   '/path/to/&'),

    ('/path/to/{foo}',                          {'foo': ' '},                  '/path/to/%20'),
    ('/path/to/{-list|&|foo}',                  {'foo': ['&', '&', '|', '_']}, '/path/to/%26&%26&%7C&_'),

    ('/path/to{.format}',                       {},                            '/path/to'),
    ('/path/to{.format}',                       {'format': ''},                '/path/to.'),
    ('/path/to{.format}',                       {'format': 'mp3'},             '/path/to.mp3')]

t = '/{foo}-{foo=def}-{-opt|opt|foo}-{-neg|neg|foo}{-prefix|pre|foo}-{-suffix|suf|foo}&{-join|&|foo,bar,baz}'
PARTIAL_PARAMS = [
    {'foo': 'FOO', 'bar': 'BAR', 'baz': 'BAZ'},
    {'bar': 'BAR', 'baz': 'BAZ'},
    {'foo': 'FOO', 'baz': 'BAZ'},
    {'foo': 'FOO', 'bar': 'BAR'},
    {'foo': 'FOO'},
    {'bar': 'BAR'},
    {'baz': 'BAZ'}]
    

class TestUriTemplates(unittest.TestCase):
    def test_operators(self):
        for template, params, expected in TESTDATA:
            print template, params
            self.assertEqual(expected, sub(template, params), " ".join(["testing", repr(template), repr(params)]))
    
    def test_partial(self):
        for params in PARTIAL_PARAMS:
            expected = sub(t, params)
            self.assertEqual(expected, sub(sub(t, {}, partial=True), params), "testing (1) " + repr(params))
            self.assertEqual(expected, sub(sub(t, params, partial=True), {}), "testing (2) " + repr(params))
