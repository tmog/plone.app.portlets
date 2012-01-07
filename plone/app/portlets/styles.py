from zope.interface import Invalid
import re


# Styles formatting validator for control panel config
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
        raise Exception()

    # Check for empty CSS class part
    if not css:
        raise InvalidCssClassError()

    # Check for CSS class validity; a style can have multiple CSS classes
    # so we first need to split them
    for cls in css.split():
        if not _is_valid_css_class(cls):
            raise InvalidCssClassError()

    return css, title


def _is_valid_css_class(string):
    """Check if string is a valid CSS class.
    http://stackoverflow.com/questions/448981/what-characters-are-valid-in-css-class-names

    :param string: String to check for validity.
    :type string: string

    :rtype: boolean
    :return: True if string is a valid CSS class, False otherwise

    >>> from hexagonit.portletstyle import _is_valid_css_class

    Valid classes
    >>> _is_valid_css_class('foo')
    True
    >>> _is_valid_css_class('-single-dash')
    True
    >>> _is_valid_css_class('_underscore')
    True
    >>> _is_valid_css_class('numbered123')
    True

    Invalid classes
    >>> _is_valid_css_class('x')
    False
    >>> _is_valid_css_class('--double-dash')
    False
    >>> _is_valid_css_class('123leading-numbers')
    False
    """
    exp = re.compile('^-?[_a-zA-Z][_a-zA-Z0-9-]+$')
    if exp.match(string):
        return True
    return False
