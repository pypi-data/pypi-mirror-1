"""
Simple, regexp-based implementation of the draft URI Templates spec (v6 or thereabouts).

Features:

1) A partial expansion mode inspired by sporkonger/addressable (rubygem)
2) Overridable quoting of special charactors
3) An implementation of the proposed {.format} expansion, equivalent to {-prefix|.|format}

Usage:

>>> import uri_template
>>> uri_template.sub("http://example.com/users/{user_id}{.format}", {'user_id': 'dojo'})
'http://example.com/users/dojo'

Limitations:

There are two specified features not supported in this initial version:
1) default values (e.g. {foo=FOO})
2) list-valued parameters to the prefix and suffix operators, e.g. uri_template.sub("/path-to{-suffix|/|foo}", {'foo': ['a', 'b']})

Author:

Mike Burrows (asplake), email mailto:mjb@asplake.co.uk, website http://positiveincline.com (see articles tagged uri[http://positiveincline.com/?tag=uri])
"""

import urllib
import re


__all__ = ['sub']


EXPANSION_RE = re.compile(r'{([-.])?([^}]+)}')


def sub(template, params, encoding=urllib.quote, partial=False):
    """Expand a URI Template using the supplied params:
    
    >>> sub('/entries/{entry_id}{.format}', dict(entry_id='1'))
    '/entries/1'
    >>> sub('/entries/{entry_id}{.format}', dict(entry_id='1', format='json'))
    '/entries/1.json'
    
    Provide a callable ``encoding`` (overriding the default ``urllib.quote``)
    to change how values are encoded:
    
    >>> sub('/entries/{entry_id}', dict(entry_id='frist post'))
    '/entries/frist%20post'
    >>> sub('/entries/{entry_id}', dict(entry_id='frist post'), encoding=lambda v: v)
    '/entries/frist post'
    
    Partially expand a template to produce another:
    
    >>> sub('/entries/{entry_id}{.format}', dict(format='json'), partial=True)
    '/entries/{entry_id}.json'
    """
    return re.sub(EXPANSION_RE, lambda match: matched(match, params, encoding, partial), template)

def matched(match, params, encoding, partial):
    lead, body = match.groups()
    if lead == '-': # leading '-' 
        operator, arg, operands = re.split(r'\|', body)
        variables = re.split(',', operands)
        return operators[operator](arg, variables, params, encoding, partial)
    elif lead == '.':
        variables = re.split(',', body)
        return operators['prefix']('.', variables, params, encoding, partial)
    else:
        return operators['variable'](body, params, encoding, partial)

def single_variable(variables):
    if len(variables) != 1:
        raise TypeError('-prefix takes exactly one variable, given %s' % ','.join(variables))
    return variables[0]
    
def encoded_lookup(params, variable, encoding):
    return encoding(params[variable])

operators = {}

def operator(name):
    def save_operator(func):
        operators[name] = func
        return func
    return save_operator

@operator('variable')
def do_variable(variable, params, encoding, partial):
    if variable in params:
        return encoded_lookup(params, variable, encoding)
    elif partial:
        return '{%s}' % variable
    else:
        return ''

@operator('opt')
def op_opt(arg, variables, params, encoding, partial):
    if [variable for variable in variables if variable in params and params[variable] != []]:
        return arg
    elif partial:
        return '{-opt|%s|%s}' % (arg, ','.join(variables))
    else:
        return ''

@operator('neg')
def op_neg(arg, variables, params, encoding, partial):
    if [variable for variable in variables if variable in params and params[variable] != []]:
        return ''
    elif partial:
        return '{-neg|%s|%s}' % (arg, ','.join(variables))
    else:
        return arg

@operator('prefix')
def op_prefix(prefix, variables, params, encoding, partial):
    variable = single_variable(variables)
    if variable in params:
        return prefix + encoded_lookup(params, variable, encoding)
    elif partial:
        return '{-prefix|%s|%s}' % (prefix, variable)
    else:
        return ''

@operator('suffix')
def op_suffix(suffix, variables, params, encoding, partial):
    variable = single_variable(variables)
    if variable in params:
        return encoded_lookup(params, variable, encoding) + suffix
    elif partial:
        return '{-suffix|%s|%s}' % (suffix, variable)
    else:
        return ''

@operator('join')
def op_join(separator, variables, params, encoding, partial):
    if not partial:
        return separator.join(variable + '=' + encoded_lookup(params, variable, encoding) for variable in variables if variable in params)
    else:
        buf = ''
        deferred = []
        filled = False
        for variable in variables:
            if variable in params:
                if deferred:
                    if filled:
                        if len(deferred) == 1:
                            buf += '{-prefix|%s%s=|%s}' % (separator, deferred[0], deferred[0])
                        else:
                            buf += '{-opt|%s|%s}{-join|%s|%s}' % (separator, ','.join(deferred), separator, ','.join(deferred))
                    else:
                        buf += '{-join|%s|%s}{-opt|%s|%s}' % (separator, ','.join(deferred), separator, ','.join(deferred))
                    deferred = []
                if filled:
                    buf += separator
                buf += '%s=%s' % (variable, encoded_lookup(params, variable, encoding))
                filled = True
            else:
                deferred.append(variable)
        if deferred:
            if filled:
                if len(deferred) == 1:
                    buf += '{-prefix|%s%s=|%s}' % (separator, deferred[0], deferred[0])
                else:
                    buf += '{-opt|%s|%s}{-join|%s|%s}' % (separator, ','.join(deferred), separator, ','.join(deferred))
            else:
                buf += '{-join|%s|%s}' % (separator, ','.join(deferred))
        return buf

@operator('list')
def op_list(separator, variables, params, encoding, partial):
    variable = single_variable(variables)
    if variable in params:
        return separator.join(map(encoding, params[variable]))
    elif partial:
        return '{-list|%s|%s}' % (separator, variable)
    else:
        ''
