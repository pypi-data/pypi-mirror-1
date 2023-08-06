from described_routes import uri_template

class ResourceTemplate(object):
    """
    Dynamic, framework-neutral metadata describing path/URI structures natively in Python and through
    JSON, YAML and XML representations.

    Purpose: to define and support a metadata format capable of being generated dynamically from web
    applications, describing the URI structure of the application in its entirety or of specific resources
    and their related subresources.  In a very lightweight manner - focussed only on resource identification -
    it aims to cover a spectrum ranging from application description languages (cf WSDL and WADL) through to
    more dynamic, hyperlinked interaction (cf REST and HATEOAS).
    """
    def __init__(self, d={}, parent=None, **kwargs):
        """
        Initialize a ResourceTemplate from a dict &/or keyword arguments, all of which are optional.  For example:

            user_articles = ResourceTemplate(
                                {
                                    'name':                'user_articles',
                                    'rel':                 'articles',
                                    'uri_template':        'http://example.com/users/{user_id}/articles{-prefix|.|format}',
                                    'path_template':       '/users/{user_id}/articles{-prefix|.|format}',
                                    'params':              ['user_id'],
                                    'optional_params':     ['format'],
                                    'options':             ['GET', 'POST']
                                },
                                resource_templates = [user_article, new_user_article])

        The resource_templates parameter can be a ResourceTemplates object, an array of ResourceTemplate objects
        or an array of hashes.  This last option makes it easy to initialize a whole hierarchy directly from deserialised JSON or YAML
        objects, e.g.:

            user_articles = ResourceTemplate(json.parse(json))
            user_articles = ResourceTemplate(yaml.load(yaml))
        """
        d = dict(d, **kwargs)

        for attr in ('name', 'rel', 'uri_template', 'path_template'):
            setattr(self, attr, d.get(attr))
        
        for attr in ('params', 'optional_params', 'options'):
            setattr(self, attr, d.get(attr, []))

        self.resource_templates = ResourceTemplates(
                                            d.get('resource_templates', []),
                                            self)
        self.parent = parent
        
    def to_py(self, base=None):
        """
        Convert to a dict, perhaps for a further conversion to JSON or YAML.
        """        
        pairs = [(attr, getattr(self, attr))
                 for attr in ('name', 'rel', 'uri_template', 'path_template',
                              'params', 'optional_params', 'options')] + \
                [('resource_templates', self.resource_templates.to_py())]
        return dict((attr, value) for attr, value in pairs if value)

    def __str__(self):
        """
        Text report
        """
        return str(ResourceTemplates([self]))


    def positional_params(self, parent):
        """
        Returns params and any optional_params in order, removing the supplied parent's params
        """
        
        all_params = self.params + self.optional_params
        if parent:
            return [p for p in all_params if p not in parent.params]
        else:
            return all_params


    def uri_template_for_base(self, base):
        """
        Returns this template's URI template or one constructed from the given base and path template.
        """
        if self.uri_template:
            return self.uri_template
        elif base and self.path_template:
            return base + self.path_template
            
    def uri_for(self, actual_params, base=None):
        """
        Returns an expanded URI template with template variables filled from the given params hash.
        Raises KeyError if params doesn't contain all mandatory params.
        """
        missing_params = [p for p in self.params if p not in actual_params]
        if missing_params:
            raise KeyError('missing params ' + ', '.join(missing_params))
            
        t = self.uri_template_for_base(base)
        if not t:
            raise RuntimeError('uri_template_for_base(%s) is None; path_template=%s' % (repr(base), repr(self.path_template)))
        
        return uri_template.sub(t, actual_params)
        
    def path_for(self, actual_params):
        """
        Returns an expanded path template with template variables filled from the given params hash.
        Raises KeyError if params doesn't contain all mandatory params.
        """
        missing_params = [p for p in self.params if p not in actual_params]
        if missing_params:
            raise KeyError('missing params ' + ', '.join(missing_params))

        if not self.path_template:
            raise RuntimeError('path_template is None')

        return uri_template.sub(path_template, actual_params)
    
    def partial_expand(self, actual_params):
        """
        Return a new resource template with the path_template &/or uri_template partially expanded with the given params        
        """
        return type(self)(
                    name               = self.name,
                    rel                = self.rel,
                    uri_template       = self.partial_expand_uri_template(self.uri_template,  actual_params),
                    path_template      = self.partial_expand_uri_template(self.path_template, actual_params),
                    params             = [p for p in self.params if p not in actual_params],
                    optional_params    = [p for p in self.optional_params if p not in actual_params],
                    options            = self.options,
                    resource_templates = self.resource_templates.partial_expand(actual_params))

    def partial_expand_uri_template(self, ut, actual_params):
        """
        Partially expand a URI template
        """
        if ut:
            return uri_template.sub(ut, actual_params, partial=True)
  
    def find_by_rel(self, rel):
        """
        Find member ResourceTemplate objects with the given rel
        """
        return [t for t in self.resource_templates if t.rel == rel]


"""
A list of ResourceTemplate objects.
"""
class ResourceTemplates(list):
    def __init__(self, collection=[], parent=None):
        """
        Initialize a ResourceTemplates object (a new collection of ResourceTemplate objects) from given collection of
        ResourceTemplates or hashes
        """
        super(ResourceTemplates, self).__init__()
        if collection:
            for rt in collection:
                if isinstance(rt, ResourceTemplate):
                    self.append(rt)
                elif isinstance(rt, dict):
                    self.append(ResourceTemplate(rt, parent))
                else:
                    raise TypeError(repr(rt) + " is neither a ResourceTemplate nor a dict")

    def to_py(self):
        """
        Convert member ResourceTemplate objects to array of hashes equivalent to their JSON or YAML representations
        """
        return [t.to_py() for t in self]
        
    def all_by_name(self):
        """
        Get a dict of all named ResourceTemplate objects contained in the supplied collection, keyed by name
        """
        d = {}
        for rt in self:
            if rt.name:
                d[rt.name] = rt
            d.update(rt.resource_templates.all_by_name())

        return d

    def to_table(self, parent_template=None, indent=''):
        """
        For to_text()
        """
        table = []        
        for rt in self:
            if parent_template:
                link = rt.rel or ''
                new_params = [p for p in rt.params if p not in parent_template.params]
            else:
                link = rt.name
                new_params = rt.params
            table.append([
                indent + link + ', '.join(['{' + p + '}' for p in new_params]),
                rt.name or '',
                ', '.join(rt.options),
                rt.uri_template or rt.path_template])
            table.extend(rt.resource_templates.to_table(rt, indent + '  '))

        return table

    def __str__(self):
        """
        Text report
        """
        table = self.to_table()
        
        for col in range(3):
            col_width = max([len(row[col]) for row in table])
            for row in table:
                row[col] = row[col].ljust(col_width)
        
        return '\n'.join([' '.join(row) for row in table] + [''])
        
    def partial_expand(self, actual_params):
        """
        Partially expand the path_template or uri_template of the given resource templates with the given params,
        returning new resource templates
        """
        return type(self)([rt.partial_expand(actual_params) for rt in self])
