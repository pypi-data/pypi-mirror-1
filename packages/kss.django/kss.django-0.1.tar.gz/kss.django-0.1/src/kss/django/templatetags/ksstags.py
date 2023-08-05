from django.core.urlresolvers import reverse
from django import template
from django.conf import settings
from kss.base import javascript

register = template.Library()

@register.tag
def kss_js(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag accepts no arguments" % token.contents.split()[0]
    return KSSJavascriptNode()

class KSSJavascriptNode(template.Node):
    def render(self, context):
        return '<script type="text/javascript" src="%s"></script>' % reverse(
            'kss.js')


@register.tag
def kss_extra_scripts(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag accepts no arguments" % token.contents.split()[0]
    return KSSExtraScriptsNode()

class KSSExtraScriptsNode(template.Node):
    def render(self, context):
        extra_scripts = javascript.extra_scripts().keys()
        return '\n'.join(
            ['<script type="text/javascript" src="%s"></script>' % reverse(
            'kss_extra_scripts', args=[script]) for script in extra_scripts])




@register.tag
def kss_base_url(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag accepts no arguments" % token.contents.split()[0]
    return KSSBaseURL()

class KSSBaseURL(template.Node):
    def render(self, context):
        return '<link rel="kss-base-url" href="%s" />' % getattr(
            settings, 'KSS_BASE_URL', '')
