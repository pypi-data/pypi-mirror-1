import unittest
from described_routes import ResourceTemplate, ResourceTemplates

data = \
    [
        {
            'name':               'users',
            'uri_template':       'http://example.com/users{-prefix|.|format}',
            'optional_params':    ['format'],
            'options':            ['GET', 'POST'],
            'resource_templates': [
                {
                    'name':               'new_user',
                    'rel':                'new',
                    'uri_template':       'http://example.com/users/new{-prefix|.|format}',
                    'optional_params':    ['format'],
                    'options':            ['GET'],
                },
                {
                    'name':               'user',
                    'uri_template':       'http://example.com/users/{user_id}{-prefix|.|format}',
                    'params':             ['user_id'],
                    'optional_params':    ['format'],
                    'options':            ['GET', 'PUT', 'DELETE'],
                    'resource_templates': [
                        {
                            'name':            'edit_user',
                            'rel':             'edit',
                            'uri_template':    'http://example.com/users/{user_id}/edit{-prefix|.|format}',
                            'params':          ['user_id'],
                            'optional_params': ['format'],
                            'options':         ['GET']
                        },
                        {
                            'name':            'user_articles',
                            'rel':             'articles',
                            'uri_template':    'http://example.com/users/{user_id}/articles{-prefix|.|format}',
                            'params':          ['user_id'],
                            'optional_params': ['format'],
                            'options':         ['GET', 'POST'],
                            'resource_templates': [
                                {
                                    'name':               'user_article',
                                    'uri_template':       'http://example.com/users/{user_id}/articles/{article_id}{-prefix|.|format}',
                                    'params':             ['user_id', 'article_id'],
                                    'optional_params':    ['format'],
                                    'options':            ['GET', 'PUT', 'DELETE']
                                }
                            ]
                        }
                    ]
                },
            ]
        },
        {
            'name':          'test_with_no_uri_template',
            'path_template': '/path'
        }
    ]    
resource_templates = ResourceTemplates(data)
params= {'user_id': 'dojo', 'format': 'json'}


def find_by_name(name):
    return resource_templates.all_by_name()[name]


class TestResourceTemplate(unittest.TestCase):
    def test_find_by_rel(self):
        user = find_by_name('user')
        edit_user = find_by_name('edit_user')
        self.assertEqual([edit_user], user.find_by_rel('edit'))
        
    def test_uri_for(self):
        user = find_by_name('user')
        self.assertEqual('http://example.com/users/dojo.json', user.uri_for(params))
        
    def test_uri_based_on_path(self):
        user = find_by_name('test_with_no_uri_template')
        self.assertEqual('http://example.com/base/path', user.uri_for({}, 'http://example.com/base'))
        
    def test_partial_expand(self):
        user_articles = find_by_name('user_articles')
        self.assertEqual(
            {
                'name':            'user_articles',
                'rel':             'articles',
                'uri_template':    'http://example.com/users/dojo/articles.json',
                'options':         ['GET', 'POST'],
                'resource_templates': [
                    {
                        'name':               'user_article',
                        'uri_template':       'http://example.com/users/dojo/articles/{article_id}.json',
                        'params':             ['article_id'],
                        'options':            ['GET', 'PUT', 'DELETE']
                    }
                ]
            },
            user_articles.partial_expand(params).to_py())
    
    def test_positional_params(self):
        user_articles = find_by_name('user_articles')
        user_article = find_by_name('user_article')
        self.assertEqual(['user_id', 'article_id','format'], user_article.positional_params(None))
        self.assertEqual(['article_id','format'], user_article.positional_params(user_articles))

    def test_str(self):
        user_articles = find_by_name('user_articles')
        self.assertEqual(
                'user_articles{user_id} user_articles GET, POST        http://example.com/users/{user_id}/articles{-prefix|.|format}\n' +
                '  {article_id}         user_article  GET, PUT, DELETE http://example.com/users/{user_id}/articles/{article_id}{-prefix|.|format}\n',
                 str(user_articles))

    def test_parent(self):
        user_articles = find_by_name('user_articles')
        self.assertEqual('user', user_articles.parent.name)
        self.assertEqual('users', user_articles.parent.parent.name)
        self.assertEqual(None, user_articles.parent.parent.parent)
