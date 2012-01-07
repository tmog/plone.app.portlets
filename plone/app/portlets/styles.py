# -*- coding: utf-8 -*-
from plone.app.portlets import PloneMessageFactory as _
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import Invalid
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import logging
import re

logger = logging.getLogger(__name__)
RE_CSS_CLASS = re.compile('^-?[_a-zA-Z][_a-zA-Z0-9-]+$')


class InvalidCssClassError(ValueError):
    """An exception thrown when a style does not have a valid CSS class."""


class EmptyLineError(ValueError):
    """An exception thrown when a line is empty or contains only whitespace."""


def styles_formatting(styles):
    """Iterate over all styles and check that they can be successfully parsed.
    Ignore empty lines.

    :param styles: List of pipe-delimited styles in "ccs|title" format.
    :type styles: list

    :rtype: boolean
    :return: True if all styles are correcty formatted
    """
    for index, style in enumerate(styles, 1):
        try:
            parse_style(style)
        except EmptyLineError:
            continue
        except InvalidCssClassError:
            raise Invalid("Style %i does not have a valid CSS class: %s" % (index, style))
        except:
            raise Invalid("Style %i is not correctly formatted: %s" % (index, style))
    return True


def parse_style(style):
    """Parse pipe-delimited style into a css part and a title part.

    :param style: Pipe-delimited style in "ccs|title" format.
    :type style: string

    :rtype: tuple of strings
    :return: A pair of strings representing css class for a style and it's title
    """
    # ignore empty lines
    if not style.strip():
        raise EmptyLineError()

    css, title = style.split("|", 1)
    css.strip()
    title.strip()

    # Check for empty title part
    if not title:
        raise ValueError

    # Check for empty CSS class part
    if not css:
        raise InvalidCssClassError()

    # Check for CSS class validity; a style can have multiple CSS classes
    # so we first need to split them
    for cls in css.split():
        if not is_valid_css_class(cls):
            raise InvalidCssClassError()

    return css, title


def is_valid_css_class(string):
    """Check if string is a valid CSS class.
    http://stackoverflow.com/questions/448981/what-characters-are-valid-in-css-class-names

    :param string: String to check for validity.
    :type string: string

    :rtype: boolean
    :return: True if string is a valid CSS class, False otherwise
    """
    return RE_CSS_CLASS.match(string) is not None


class StylesVocabulary(object):
    """Vocabulary factory of portlet styles read from control panel registry."""
    implements(IVocabularyFactory)

    def __call__(self, context):
        registry = getUtility(IRegistry)
        try:
            styles = registry['plone.app.portlets.browser.interfaces.IPortletStyles.portlet_styles']
        except KeyError:
            # if portlet_styles field is not found in plone.app.registry, just
            # return an empty list -> probably the product is registered (zcml)
            # but not installed (GenericSetup)
            styles = []

        # always have the default "default style" option available, which is effectively a no-op
        terms = [SimpleTerm(title=_(u"Default style"), value=" ")]

        # add styles from the control panel, but filter out invalid ones
        for style in styles:

            try:
                css, title = parse_style(style)
            except EmptyLineError:
                continue
            except InvalidCssClassError:
                logger.warn("Filtered out a style because it doesn't have a valid CSS class: '%s'" % style)
                continue
            except:
                logger.warn("Filtered out a style because it cannot be parsed: '%s'" % style)
                continue

            terms.append(SimpleTerm(title=title, value=css))

        # if a portlet has a style assigned that is no longer listed in
        # portlet_styles, than we need to add it to the drop-down menu,
        # so it's still possible to select it
        if hasattr(context, 'portlet_style') and not context.portlet_style in [t.value for t in terms]:
            terms.append(SimpleTerm(
                    title=context.portlet_style,
                    value=context.portlet_style,
                ))

        return SimpleVocabulary(terms)


StylesVocabularyFactory = StylesVocabulary()
