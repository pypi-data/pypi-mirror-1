# -*- coding: utf-8 -*-
import os
import re
from django import template
from django.test import TestCase
from django.conf import settings
from django_templatequery.templatetags.query_tags import QueryNode
from django_templatequery import parser
from django_templatequery.tests import KeyValue


class QuersetMethodParserTest(TestCase):
    def test_var_regex(self):
        var = re.compile('^' + parser.RE_VARIABLE + '$')
        self.assertTrue(var.match('_'))
        self.assertTrue(var.match('foo'))
        self.assertTrue(var.match('foo1'))
        self.assertTrue(var.match('foo2bar'))
        self.assertTrue(var.match('_foo3bar'))
        self.assertTrue(var.match('foo_bar_'))
        self.assertFalse(var.match('1'))
        self.assertFalse(var.match('2foo'))
        self.assertFalse(var.match('foo.bar'))
        self.assertFalse(var.match('.foo'))
        self.assertFalse(var.match('foo.'))

    def test_tvar_regex(self):
        tvar = re.compile('^' + parser.RE_TEMPLATE_VARIABLE + '$')
        self.assertTrue(tvar.match('foo'))
        self.assertTrue(tvar.match('foo1'))
        self.assertTrue(tvar.match('foo2bar'))
        self.assertTrue(tvar.match('foo_bar'))
        self.assertTrue(tvar.match('foo_bar_'))
        self.assertFalse(tvar.match('_'))
        self.assertFalse(tvar.match('_foo'))
        self.assertFalse(tvar.match('1'))
        self.assertFalse(tvar.match('2foo'))
        # dot notation
        self.assertTrue(tvar.match('foo.bar'))
        self.assertFalse(tvar.match('.foo'))
        self.assertFalse(tvar.match('foo.'))
        self.assertFalse(tvar.match('foo.2'))
        self.assertFalse(tvar.match('foo.1bar'))
        self.assertFalse(tvar.match('foo..bar'))
        self.assertFalse(tvar.match('foo.bar.'))

    def test_string_regex(self):
        string = re.compile('^' + parser.RE_STRING + '$')
        self.assertTrue(string.match(r'""'))
        self.assertTrue(string.match(r'"foo"'))
        self.assertTrue(string.match(r'"foo bar"'))
        self.assertTrue(string.match(r'''"foo bar 'hello'"'''))
        self.assertTrue(string.match(r'"\t"'))
        self.assertTrue(string.match(r'"\""'))
        self.assertTrue(string.match(r'"foo\"bar\"spam"'))
        self.assertTrue(string.match(r'"foo\\\"bar\\\\\"spam"'))
        self.assertFalse(string.match(r'"'))
        self.assertFalse(string.match(r'"foo'))
        self.assertFalse(string.match(r'"\"'))
        self.assertFalse(string.match(r'"\"'))
        self.assertFalse(string.match(r'foo"bar"'))
        self.assertFalse(string.match(r'foo"bar"'))
        self.assertFalse(string.match(r'"\\""'))
        self.assertFalse(string.match(r'"foo\\"bar"'))
        self.assertTrue(string.match(r"''"))
        self.assertTrue(string.match(r"'foo'"))
        self.assertTrue(string.match(r"'foo bar'"))
        self.assertTrue(string.match(r"""'foo bar "hello"'"""))
        self.assertTrue(string.match(r"'\t'"))
        self.assertTrue(string.match(r"'\''"))
        self.assertTrue(string.match(r"'foo\'bar\'spam'"))
        self.assertTrue(string.match(r"'foo\\\'bar\\\\\'spam'"))
        self.assertFalse(string.match(r"'"))
        self.assertFalse(string.match(r"'foo"))
        self.assertFalse(string.match(r"'\'"))
        self.assertFalse(string.match(r"'\'"))
        self.assertFalse(string.match(r"foo'bar'"))
        self.assertFalse(string.match(r"foo'bar'"))
        self.assertFalse(string.match(r"'\\''"))
        self.assertFalse(string.match(r"'foo\\'bar'"))

    def test_numeric_regex(self):
        string = re.compile('^' + parser.RE_NUMERIC + '$')
        self.assertTrue(string.match(r'1'))
        self.assertTrue(string.match(r'123'))
        self.assertTrue(string.match(r'1.0'))
        self.assertTrue(string.match(r'.0'))
        self.assertTrue(string.match(r'0.'))
        self.assertTrue(string.match(r'123.455'))
        self.assertFalse(string.match(r'.'))
        self.assertFalse(string.match(r'1.a'))
        self.assertFalse(string.match(r'1a'))
        self.assertFalse(string.match(r'a1'))

    def test_tokenize_function(self):
        string = ' hello, world!'
        tokens = tuple(parser.tokenize(string))
        expected_tokens = tuple([parser.Token(x) for x in (
            'hello',',','world','!'
        )])
        self.assertEqual(tokens,expected_tokens)

        string = ' filter(field=foo.bar, name="this is a string!?") . order_by()'
        tokens = tuple(parser.tokenize(string))
        expected_tokens = tuple([parser.Token(x) for x in (
            'filter','(','field','=','foo.bar',',','name','=','"this is a string!?"',')',
            '.','order_by','(',')'
        )])
        self.assertEqual(tokens,expected_tokens)

        string = 'filter(field=1.2) .2 3.!'
        tokens = tuple(parser.tokenize(string))
        expected_tokens = tuple([parser.Token(x) for x in (
            'filter','(','field','=','1.2',')','.2','3.','!'
        )])
        self.assertEqual(tokens,expected_tokens)

    def test_parser_function(self):
        string = 'filter(field=value, athor_field="string")'
        parsed = parser.parse_query_string(string)
        expected = (['filter', [], {'field':'VARIABLE: value','athor_field':'string'}],)
        parsed[0][2]['field'] = 'VARIABLE: %s' % parsed[0][2]['field'].var
        self.assertEqual(parsed,expected)

        string = 'filter(field=foo.bar, athor_field="string").order_by().only("name")'
        parsed = parser.parse_query_string(string)
        expected = (
            ['filter', [], {'field':'VARIABLE: foo.bar','athor_field':'string'}],
            ['order_by', [], {}],
            ['only', ['name'],{}],
        )
        parsed[0][2]['field'] = 'VARIABLE: %s' % parsed[0][2]['field'].var
        self.assertEqual(parsed,expected)

        string = 'filter(1.2, name=.3).all()'
        parsed = parser.parse_query_string(string)
        expected = (
            ['filter', [1.2], {'name':0.3}],
            ['all', [],{}],
        )
        self.assertEqual(parsed,expected)


class TestTemplateTag(TestCase):
    def setUp(self):
        self.original_template_dirs = settings.TEMPLATE_DIRS
        settings.TEMPLATE_DIRS = (
            os.path.join(os.path.dirname(__file__), 'templates'),)
        KeyValue.objects.create(key='foo',value=0)
        KeyValue.objects.create(key='bar',value=50)
        KeyValue.objects.create(key='spam',value=100)
        KeyValue.objects.create(key='egg',value=200)


    def tearDown(self):
        settings.TEMPLATE_DIRS = self.original_template_dirs

    @staticmethod
    def render_template(template_string, context=None):
        t = template.Template(template_string)
        return t.render(template.Context(context))

    def test_parse_std(self):
        tag_name, tokens, queryset, queryset_methods = QueryNode.parse_std([
            'tagname',
            'django_templatequery.KeyValue',
            'all()',
            'as',
            'foo'])
        self.assertEqual(list(queryset),list(KeyValue.objects.all()))
        self.assertEqual(queryset_methods,(
            ['all', [], {}],))
        self.assertEqual(list(tokens),['as','foo'])

        tag_name, tokens, queryset, queryset_methods = QueryNode.parse_std([
            'tagname',
            'django_templatequery.KeyValue',
            'all()',
            'using',
            'big',
            'as',
            'foo'])
        self.assertEqual(list(queryset),list(KeyValue.big.all()))

        self.assertRaises(template.TemplateSyntaxError, QueryNode.parse_std, [
            'tagname',
            '1invalidapp.Bar',
            'all()',
            'as',
            'foo'])
        self.assertRaises(template.TemplateSyntaxError, QueryNode.parse_std, [
            'tagname',
            'django_templatequery.KeyValue',
            'Invalid" queryset methods"',
            'as',
            'foo'])
        self.assertRaises(template.TemplateSyntaxError, QueryNode.parse_std, [
            'tagname',
            'django_templatequery.KeyValue',
            'all()',
            'using',
            'unkown_manager'])

    def test_displayquery_tag(self):
        rendered = self.render_template(
            '{% load query_tags %}'
            '{% displayquery django_templatequery.KeyValue all() with "list.html" %}'
        )
        self.assertEqual(rendered,"foo=0\nbar=50\nspam=100\negg=200\n")

        rendered = self.render_template(
            '{% load query_tags %}'
            '{% displayquery django_templatequery.KeyValue all() using big with "list.html" %}'
        )
        self.assertEqual(rendered,"spam=100\negg=200\n")

        rendered = self.render_template(
            '{% load query_tags %}'
            '{% displayquery django_templatequery.KeyValue get(pk=1) with "detail.html" %}'
        )
        self.assertEqual(rendered,"foo=0\n")

        rendered = self.render_template(
            '{% load query_tags %}'
            '{% displayquery django_templatequery.KeyValue get(pk=1) with template_name %}',
            {'template_name': 'detail.html'}
        )
        self.assertEqual(rendered,"foo=0\n")

        self.assertRaises(
            template.TemplateSyntaxError,
            self.render_template,
            '{% load query_tags %}'
            '{% displayquery django_templatequery.KeyValue all() notwith "list.html" %}'
        )
        self.assertRaises(
            template.TemplateSyntaxError,
            self.render_template,
            '{% load query_tags %}'
            '{% displayquery django_templatequery.KeyValue all() with %}'
        )
        self.assertRaises(
            template.TemplateSyntaxError,
            self.render_template,
            '{% load query_tags %}'
            '{% displayquery django_templatequery.KeyValue all() with "list.html" too many arguments %}'
        )

    def test_loadquery_tag(self):
        rendered = self.render_template(
            '{% load query_tags %}'
            '{% loadquery django_templatequery.KeyValue all() as object_list %}'
            '{{ object_list }}'
        )
        self.assertEqual(rendered,"[foo=0, bar=50, spam=100, egg=200]")

        rendered = self.render_template(
            '{% load query_tags %}'
            '{% loadquery django_templatequery.KeyValue all() using big as object_list %}'
            '{{ object_list }}'
        )
        self.assertEqual(rendered,"[spam=100, egg=200]")

        self.assertRaises(
            template.TemplateSyntaxError,
            self.render_template,
            '{% load query_tags %}'
            '{% loadquery django_templatequery.KeyValue all() notas object_list %}'
        )
        self.assertRaises(
            template.TemplateSyntaxError,
            self.render_template,
            '{% load query_tags %}'
            '{% loadquery django_templatequery.KeyValue all() %}'
        )
        self.assertRaises(
            template.TemplateSyntaxError,
            self.render_template,
            '{% load query_tags %}'
            '{% loadquery django_templatequery.KeyValue all() as object_list too many arguments %}'
        )

    def test_usequery_tag(self):
        rendered = self.render_template(
            '{% load query_tags %}'
            '{% usequery django_templatequery.KeyValue all() as object_list %}'
            '{{ object_list.0.key }} ... {{ object_list }}'
            '{% endusequery %}'
        )
        self.assertEqual(rendered,"foo ... [foo=0, bar=50, spam=100, egg=200]")

        rendered = self.render_template(
            '{% load query_tags %}'
            '{% usequery django_templatequery.KeyValue get(pk=1) as object %}'
                '{{ object }} {{ object.key|upper }} '
                '{% if object.value %}true{% else %}false{% endif %}'
            '{% endusequery %}'
        )
        self.assertEqual(rendered,"foo=0 FOO false")

        self.assertRaises(
            template.TemplateSyntaxError,
            self.render_template,
            '{% load query_tags %}'
            '{% usequery django_templatequery.KeyValue all() notas object_list %}'
            '{% endusequery %}'
        )
        self.assertRaises(
            template.TemplateSyntaxError,
            self.render_template,
            '{% load query_tags %}'
            '{% usequery django_templatequery.KeyValue all() as object_list '
            'too many arguments %}'
            '{% endusequery %}'
        )
        self.assertRaises(
            template.TemplateSyntaxError,
            self.render_template,
            '{% load query_tags %}'
            '{% usequery django_templatequery.KeyValue all() %}'
            '{% endusequery %}'
        )
        self.assertRaises(
            template.TemplateSyntaxError,
            self.render_template,
            '{% load query_tags %}'
            '{% usequery django_templatequery.KeyValue all() as object_list %}'
            'Template'
        )
