# -*- coding: utf-8 -*-
from django.db.models.query import QuerySet
from django.db import models
from django import template
from django.template import loader
from django_templatequery.parser import (
    parse_query_string, get_template_variable, TemplateQuerySyntaxError)

register = template.Library()


class QueryNode(template.Node):
    def __init__(self, queryset, queryset_methods):
        self.queryset = queryset
        self.queryset_methods = queryset_methods

    def resolve(self, var, context):
        if isinstance(var, template.Variable):
            return var.resolve(context)
        else:
            return var

    def get_query_set(self, context):
        qs = self.queryset
        for method_name, args, kwargs in self.queryset_methods:
            assert isinstance(qs, QuerySet), \
                'Excpected an queryset instead of "%s"' % qs
            assert hasattr(qs, method_name), \
                'Unkown queryset method "%s"' % method_name
            nargs, nkwargs = [], {}
            for arg in args:
                nargs.append(self.resolve(arg, context))
            for k, v in kwargs.items():
                nkwargs[str(k)] = self.resolve(v, context)
            qs = getattr(qs, method_name)(*nargs, **nkwargs)
        return qs

    @classmethod
    def parse_std(cls, tokens):
        tag_name, tokens = tokens[0], tokens[1:]
        appmodel, query_string, tokens =  tokens[0], tokens[1], tokens[2:]
        try:
            queryset_methods = parse_query_string(query_string)
        except TemplateQuerySyntaxError, e:
            raise template.TemplateSyntaxError('Invalid querymethod calls "%s"' % query_string)
        # load model
        model = models.get_model(*appmodel.split('.',1))
        if model is None:
            raise template.TemplateSyntaxError(
                u'Cannot find model "%s"' % appmodel)
        # get manager
        if len(tokens) >= 2 and tokens[0] == 'using':
            manager = tokens[1]
            tokens = tokens[2:]
        else:
            manager = '_default_manager'
        if not hasattr(model, manager) or \
            not isinstance(getattr(model, manager), models.Manager):
            raise template.TemplateSyntaxError(
                u'Cannot access manager "%s" on model "%s"' %
                (manager, appmodel))
        queryset = getattr(model, manager).all()
        return tag_name, tokens, queryset, queryset_methods


class DisplayQueryNode(QueryNode):
    """
    Usage::
        {% displayquery <app>.<model> <query methods> [using <manager>] as
             <template_name> %}

    Examples::
        {% displayquery auth.User filter(username__startswith="a").only("username")
            with "auth/user_list.html" %}

        {% displayquery blog.Entry get(slug=object_slug) using public
            with template_name %}
    """
    def __init__(self, queryset, queryset_methods, template_name):
        super(DisplayQueryNode, self).__init__(queryset, queryset_methods)
        self.template = template_name

    def render(self, context):
        template_context = {}
        qs = self.get_query_set(context)
        if isinstance(qs, QuerySet):
            template_context['object_list'] = qs
        else:
            template_context['object'] = qs
        return loader.render_to_string(
            self.resolve(self.template, context), template_context)

    @classmethod
    def parse(cls, parser, tokens):
        tokens = tokens.split_contents()
        tag_name, tokens, queryset, queryset_methods = cls.parse_std(tokens)
        try:
            with_, template_name = tokens
        except ValueError:
            raise template.TemplateSyntaxError(u'Wrong number of arguments')
        if with_ != 'with':
            raise template.TemplateSyntaxError(
                u'Excpected "with" instead of "%s"' % with_)
        template_name = get_template_variable(template_name)
        return cls(queryset, queryset_methods, template_name)


class LoadQueryNode(QueryNode):
    """
    Usage::
        {% loadquery <app>.<model> <query methods> [using <manager>] as <template_variable> %}

    Examples::
        {% loadquery auth.User filter(username__startswith="a").only("username") as object_list %}

        {% loadquery blog.Entry get(slug=object_slug) using public as entry %}
    """
    def __init__(self, queryset, queryset_methods, as_var):
        super(LoadQueryNode, self).__init__(queryset, queryset_methods)
        self.as_var = as_var

    def render(self, context):
        context[self.as_var] = self.get_query_set(context)
        return ''

    @classmethod
    def parse(cls, parser, tokens):
        tokens = tokens.split_contents()
        tag_name, tokens, queryset, queryset_methods = cls.parse_std(tokens)
        try:
            as_, as_var = tokens
        except ValueError:
            raise template.TemplateSyntaxError(u'Too many arguments')
        if as_ != 'as':
            raise template.TemplateSyntaxError(u'Excpected "as" instead of "%s"' % as_)
        return cls(queryset, queryset_methods, as_var)


class UseQueryNode(QueryNode):
    """
    Usage::
        {% usequery <app>.<model> <query methods> [using <manager>]
            as <template_variable> %}
            Template code that will be rendered with <template_variable>
            in its context.
        {% endusequery %}

    Examples::
        {% usequery auth.User filter(username__startswith="a").only("username")
            as object_list %}
            <ul>{% for object in object_list %}
                <li>{{ object }}</li>
            {% endfor %}</ul>
        {% endusequery %}

        {% usequery blog.Entry get(slug=object_slug) using public as entry %}
            {% include "display_entry.html" %}
        {% endusequery %}
    """
    def __init__(self, queryset, queryset_methods, as_var, nodelist):
        super(UseQueryNode, self).__init__(queryset, queryset_methods)
        self.as_var = as_var
        self.nodelist = nodelist

    def render(self, context):
        context.push()
        context[self.as_var] = self.get_query_set(context)
        output = self.nodelist.render(context)
        context.pop()
        return output

    @classmethod
    def parse(cls, parser, tokens):
        tokens = tokens.split_contents()
        tag_name, tokens, queryset, queryset_methods = cls.parse_std(tokens)
        try:
            as_, as_var = tokens
        except ValueError:
            raise template.TemplateSyntaxError(u'Too many arguments')
        if as_ != 'as':
            raise template.TemplateSyntaxError(u'Excpected "as" instead of "%s"' % as_)

        # get template content until endusequery
        nodelist = parser.parse(('end%s' % tag_name,))
        parser.delete_first_token()

        return cls(queryset, queryset_methods, as_var, nodelist)


register.tag('displayquery', DisplayQueryNode.parse)
register.tag('loadquery', LoadQueryNode.parse)
register.tag('usequery', UseQueryNode.parse)
