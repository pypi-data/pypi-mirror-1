# -*- coding: utf-8 -*-
import re
from django import template


RE_VARIABLE = r'(?:[_a-zA-Z]+[_a-zA-Z0-9]*)'
RE_TEMPLATE_VARIABLE = r'(?:[a-zA-Z]+(?:[_a-zA-Z0-9]|\.[a-zA-Z])*)'
RE_STRING = r"""(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')"""
RE_NUMERIC = r'(?:\d*\.\d+|\d+\.\d*|\d+)'

RE_PATTERNS = {
    'var': RE_VARIABLE,
    'tvar': RE_TEMPLATE_VARIABLE,
    'string': RE_STRING,
    'num': RE_NUMERIC,
}

RE_MATCH_METHOD_NAME = re.compile(
    r'^\s*\.?\s*(%(var)s)\s*\((.*)$' % RE_PATTERNS)
RE_MATCH_METHOD_ARGUMENTS = re.compile(
    r'^\s*((?:(?:%(var)s\s*=\s*%(tvar)s|%(string)s|%(num)s))|(?:%(tvar)s|%(string)s|%(num)s))?\s*([),])(.*)$' % RE_PATTERNS)
RE_MATCH_NAMED_ARGUMENT = re.compile(
    r'^(%(var)s)\s*=\s*(%(tvar)s|%(string)s|%(num)s)$' % RE_PATTERNS)


class TemplateQuerySyntaxError(Exception):
    pass

RE_TOKEN = re.compile(
    r'^\s*(%(tvar)s|%(string)s|%(var)s|%(num)s|.)\s*(.*)$' % RE_PATTERNS)

class Token(object):
    RE_VARIABLE = re.compile(RE_VARIABLE)
    RE_STRING = re.compile(RE_STRING)
    RE_TEMPLATE_VARIABLE = re.compile(RE_TEMPLATE_VARIABLE)
    RE_NUMERIC = re.compile(RE_NUMERIC)

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return u'<Token: %s>' % self.token

    def __unicode__(self):
        return self.token

    def __eq__(self, athor):
        if not isinstance(athor, Token):
            return False
        return self.token == athor.token

    def is_var(self):
        return bool(self.RE_VARIABLE.match(self.token))

    def is_tvar(self):
        return bool(self.RE_TEMPLATE_VARIABLE.match(self.token))

    def is_string(self):
        return bool(self.RE_STRING.match(self.token))

    def is_numeric(self):
        return bool(self.RE_NUMERIC.match(self.token))


def tokenize(query_string):
    while query_string:
        m = RE_TOKEN.match(query_string)
        token, query_string = m.groups()
        yield Token(token)

def get_argument_representation(token):
    string = token.token
    if token.is_numeric():
        if '.' in string:
            return float(string)
        else:
            return int(string)
    if string[0] == string[-1] == '"' or string[0] == string[-1] == "'":
        return string[1:-1]
    else:
        return template.Variable(string)

def get_template_variable(string):
    if string[0] == string[-1] == '"' or string[0] == string[-1] == "'":
        return string[1:-1]
    else:
        return template.Variable(string)

def parse_query_string(query_string):
    '''
    filter(name=foo.bar).order_by().only("name")

    returns

    ('filter', (("name",'foo.bar'),)),
    ('order_by', (),),
    ('only', ((None, "name"),))
    '''
    tokens = tokenize(query_string)
    def parse_method(tokens):
        method = [None, [], {}]
        try:
            token = tokens.next()
        except StopIteration:
            return None
        try:
            if not token.is_var():
                raise TemplateQuerySyntaxError('Expected valid python name instead of "%s"' % token)
            method[0] = token.token
            token = tokens.next()
            if token.token != '(':
                raise TemplateQuerySyntaxError('Expected "(" instead of "%s"' % token)
            argtokens = []
            while True:
                token = tokens.next()
                if token.token == ')':
                    break
                argtokens.append(token)
            method_args = []
            while argtokens:
                if len(argtokens) >= 3 and argtokens[1].token == '=':
                    kw, arg = argtokens[0], argtokens[2]
                    if not kw.is_var():
                        raise TemplateQuerySyntaxError('Expected valid python name instead of "%s"' % kw)
                    if not arg.is_tvar() and not arg.is_string() and not arg.is_numeric():
                        raise TemplateQuerySyntaxError('Expected string, number or template variable instead of "%s"' % arg)
                    method[2][kw.token] = get_argument_representation(arg)
                    argtokens = argtokens[3:]
                else:
                    arg = argtokens[0]
                    if not arg.is_tvar() and not arg.is_string() and not arg.is_numeric():
                        raise TemplateQuerySyntaxError('Expected string, number or template variable instead of "%s"' % arg)
                    method[1].append(get_argument_representation(arg))
                    argtokens = argtokens[1:]
                if argtokens and not argtokens[0].token == ',':
                    raise TemplateQuerySyntaxError('Expected "," instead of "%s"' % argtokens[0].token)
                argtokens = argtokens[1:]
            return method
        except StopIteration:
            raise TemplateQuerySyntaxError('Unexpected end of tokens.')

    methods = []
    while True:
        method = parse_method(tokens)
        if method is None:
            break
        methods.append(method)
        try:
            token = tokens.next()
        except StopIteration:
            break
        if token.token != '.':
            raise TemplateQuerySyntaxError('Expected "." after method call instead of "%s"' % token)

    return tuple(methods)
