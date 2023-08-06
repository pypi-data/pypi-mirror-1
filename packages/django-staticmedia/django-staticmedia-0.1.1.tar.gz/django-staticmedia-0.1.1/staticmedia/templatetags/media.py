"""
Template tag for dynamically loading static media.
"""

from django import template
from django.core.cache import cache

import staticmedia


register = template.Library()


class MediaNode(template.Node):
    """
    Finds the first instance of the static media on the filesystem.

    See `staticmedia.resolve` docstring.

    This tag uses the cache framework as medias are unlikely to change
    very often, and templates will redundantly call specific static
    media (i.e. a button image).
    """
    def __init__(self, base_url, asvar=None):
        self.base_url = base_url
        self.asvar = asvar

    def render(self, context):
        """
        Return the dynamic media url directly or as a context variable
        """
        base_url = self.base_url.resolve(context)
        # use caching framework to save the media path
        media_url = cache.get('media:%s' % base_url)
        if not media_url:
            media_url = staticmedia.resolve(base_url)
            if media_url:
                cache.set('media:%s' % base_url, media_url)

        if self.asvar:
            context[self.asvar] = media_url or u''
            return u''
        else:
            return media_url or u''


@register.tag
def media(parser, token):
    """
    {% media %} tag

    Viable forms:
        {% media 'path/to/resource' %}
        {% media 'path/to/resource' as <context_variable> %}

        Where the first just returns the url and the second loads it
        into a template context variable.
    """
    tokens = token.split_contents()

    if len(tokens) > 4:
        raise template.TemplateSyntaxError(
            '%s tag given wrong number of arguments' % tokens[0])
    if len(tokens) == 1:
        raise template.TemplateSyntaxError(
            '%s tag takes 1 or 3 arguments: \'x\', or \'x as y\'')
    if not (tokens[1][0] == tokens[1][-1] and tokens[1][0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            '%s tag\'s argument should be in quotes' % tokens[0])

    base_url = parser.compile_filter(tokens[1])
    if len(tokens) == 4:
        asvar = tokens[3]
    else:
        asvar = None

    return MediaNode(base_url, asvar)
