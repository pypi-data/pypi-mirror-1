# -*- coding: utf-8 -*-
import re
from django import template

QUERYSET_METHODS = [
    'count',
]

def _order_by(queryset, value):
    args = value.split(',')
    return queryset.order_by(*args)

def _offset(queryset, value):
    value = int(value)
    return queryset[value:]

def _limit(queryset, value):
    value = int(value)
    return queryset[:value]

QUERYSET_OPTIONS_CALLBACK = {
    'order_by': _order_by,
    'offset': _offset,
    'limit': _limit,
}

def _in(value):
    return value.split(',')

QUERYSET_LOOKUP_CALLBACK = {
    'in': _in,
}


class ValidationError(Exception):
    pass


def parse_queryset_option_value(key, value):
    '''
    Options that get parsed:

    datetime(now)
    datetime(2009-02-23 03:10:59)
    '''
    for lookup in QUERYSET_OPTIONS_CALLBACK:
        if key.endswith('__%s' % lookup):
            return key, QUERYSET_OPTIONS_CALLBACK[key](value)
    if value.startswith('datetime(') and value.endswith(')'):
        from datetime import datetime
        value = value[len('datetime('):-1]
        if value == 'now':
            value = datetime.now()
        else:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%s')
    elif value == 'now':
        value = datetime.now()
    return key, value


RE_PATTERNS = {}
RE_PATTERNS['var'] = r'(?:[a-zA-Z]+[_a-zA-Z0-9]*)'
RE_PATTERNS['string'] = r"""(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')"""
RE_PATTERNS['num'] = r'(?:\d*\.\d+|\d+\.\d*|\d+)'

RE_PATTERNS['option'] = r'(%(var)s)=(%(string)s|%(num)s),?' % RE_PATTERNS

RE_OPTION = re.compile(RE_PATTERNS['option'])


def parse_queryset_options(string):
    '''
    >>> parse_queryset_options('order_by="-created,-pub_date",title__exact="Hello world!",pub_date__lte=datetime(now)')
    [['order_by', '-created'], ['title__exact', 'Hello world!'], ['pub_date__lte', datetime.now()]
    '''
    options = []
    while string:
        m = RE_OPTION.match(string)
        if m:
            string = string[m.end():]
            key, value = m.groups()
            if (value[0] == value[-1] == '"' or
                value[0] == value[-1] == "'"):
                value = value[1:-1]
            options.append([key, value])
        else:
            raise ValueError('Unsupported syntax: %s' % string)
    return options


def apply_lookup_callback(key, value):
    for lookup in QUERYSET_LOOKUP_CALLBACK:
        if key.endswith('__%s' % lookup):
            return QUERYSET_LOOKUP_CALLBACK[lookup](value)
    return value


def apply_queryset_options(queryset, options, callbacks=None):
    if callbacks is None:
        callbacks = {}
    for key, value in options:
        key = str(key)
        if key in callbacks:
            queryset = callbacks[key](queryset, value)
        elif key in QUERYSET_OPTIONS_CALLBACK:
            queryset = QUERYSET_OPTIONS_CALLBACK[key](queryset, value)
        else:
            if value.startswith('-'):
                value = apply_lookup_callback(key, value[1:])
                queryset = queryset.exclude(**{key: value})
            else:
                value = apply_lookup_callback(key, value)
                queryset = queryset.filter(**{key: value})
    return queryset


class QuerysetOptionNode(template.Node):
    queryset = None

    def __init__(self, options):
        self.options = options

    def render(self, context):
        raise NotImplementedError

    def get_query_set(self):
        return apply_queryset_options(
            self.queryset, self.options, self.option_callbacks)

    @classmethod
    def parse_options(cls, tokens):
        if tokens[1] != 'using':
            return [], tokens[1:]
        options = parse_queryset_options(tokens[2])
        return options, tokens[3:]

    @classmethod
    def parse_tokens(cls, tokens):
        return tokens

    @classmethod
    def parse(cls, parser, token):
        tokens = token.split_contents()
        options, tokens = cls.parse_options(tokens)
        args = cls.parse_tokens(tokens)
        return cls(options, *args)


class GetModelsNode(QuerysetOptionNode):
    def __init__(self, options, as_var):
        self.options = options
        self.as_var = as_var

    @classmethod
    def parse_tokens(cls, tokens):
        if tokens[0] != 'as':
            raise template.TemplateSyntaxError(u'Second argument must be "as"')
        return [tokens[1]]

    def render(self, context):
        context[self.as_var] = self.get_query_set()
        return ''


class DisplayModelsNode(QuerysetOptionNode):
    def __init__(self, options, with_var):
        self.options = options
        self.template_name = with_var

    @classmethod
    def parse_tokens(cls, tokens):
        if tokens[0] != 'with':
            raise template.TemplateSyntaxError(u'Second argument must be "with"')
        template_name = tokens[1]
        if (template_name[0] == template_name[-1] == '"' or
            template_name[0] == template_name[-1] == "'"):
            template_name = template_name[1:-1]
        else:
            template_name = template.Variable(template_name)
        return [template_name]

    def render(self, context):
        if isinstance(self.template_name, template.Variable):
            template_name = self.template_name.resolve(context)
        else:
            template_name = self.template_name
        context.push()
        context['object_list'] = self.get_query_set()
        t = template.loader.render_to_string(template_name, context)
        context.pop()
        return t


class FilterModelsNode(QuerysetOptionNode):
    def __init__(self, options, queryset_var, as_var):
        self.options = options
        self.queryset_var = template.Variable(queryset_var)
        self.as_var = as_var

    @classmethod
    def parse_tokens(cls, tokens):
        if tokens[0] != 'as':
            raise template.TemplateSyntaxError(u'Third argument must be "as"')
        return [tokens[1]]

    @classmethod
    def parse(cls, parser, token):
        tokens = token.split_contents()
        queryset_var = tokens[1]
        del tokens[1]
        options, tokens = cls.parse_options(tokens)
        args = cls.parse_tokens(tokens)
        return cls(options, queryset_var, *args)

    def render(self, context):
        self.queryset = self.queryset_var.resolve(context)
        m1 = self.queryset.model
        m2 = self.model
        if not issubclass(m1, m2) and m1 != m2:
            raise Exception('Only subclasses allowed')
        context[self.as_var] = self.get_query_set()
        return ''


def get_models(queryset, queryset_options=None):
    QS = queryset
    class cls(GetModelsNode):
        queryset = QS
        option_callbacks = queryset_options
    return cls.parse


def display_models(queryset, queryset_options=None):
    QS = queryset
    class cls(DisplayModelsNode):
        queryset = QS
        option_callbacks = queryset_options
    return cls.parse


def filter_models(model, queryset_options=None):
    M = model
    class cls(FilterModelsNode):
        model = M
        option_callbacks = queryset_options
    return cls.parse
