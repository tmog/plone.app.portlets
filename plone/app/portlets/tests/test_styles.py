# -*- coding: utf-8 -*-
from plone.app.portlets.styles import EmptyLineError
from plone.app.portlets.styles import InvalidCssClassError
from plone.app.portlets.styles import is_valid_css_class
from plone.app.portlets.styles import parse_style
from plone.app.portlets.styles import styles_formatting
from zope.interface import Invalid
import unittest


class TestStyleUtilities(unittest.TestCase):
    """Tests for the style configuration helpers."""

    def test_parse_valid_style(self):
        self.assertEquals(parse_style('foo|Foo style'), ('foo', 'Foo style'))
        self.assertEquals(parse_style('bar|Bär style'), ('bar', 'Bär style'))

    def test_parse_valid_multiple_style(self):
        self.assertEquals(parse_style('foo bar baz|Multistyle'), ('foo bar baz', 'Multistyle'))

    def test_parse_empty_style(self):
        self.assertRaises(EmptyLineError, lambda: parse_style(''))

    def test_parse_empty_title(self):
        self.assertRaises(ValueError, lambda: parse_style('foo|'))

    def test_parse_empty_css_class(self):
        self.assertRaises(InvalidCssClassError, lambda: parse_style('|foo'))

    def test_parse_invalid_css_class(self):
        self.assertRaises(InvalidCssClassError, lambda: parse_style('2nd|foo'))

    def test_formatting_valid_styles(self):
        self.failUnless(styles_formatting(['foo|faz', 'bar|baz']))

    def test_formatting_empty_lines_are_ignored(self):
        self.failUnless(styles_formatting(['foo|bar', '  ']))

    def test_formatting_invalid_css_class(self):
        self.assertRaises(Invalid, lambda: styles_formatting(['2nd|foo']))

    def test_valid_css_class(self):
        self.failUnless(is_valid_css_class('foo'))
        self.failUnless(is_valid_css_class('foo-bar'))
        self.failUnless(is_valid_css_class('foo_bar'))
        self.failUnless(is_valid_css_class('-foo123'))

    def test_invalid_css_class(self):
        self.failIf(is_valid_css_class('2foo'))
        self.failIf(is_valid_css_class('.foo'))
        self.failIf(is_valid_css_class('-2foo'))
