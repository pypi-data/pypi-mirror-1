import socket
import urllib2

from django import template
from django.conf import settings
from django.core import exceptions
from django.utils import safestring


register = template.Library()


class HttpResponseProxy(dict):
    def __init__(self, status_code, headers, content):
        self.status_code = str(status_code)
        for header_name, header_value in headers.items():
            self[header_name.lower().replace('-', '_')] = header_value
        self.content = safestring.mark_safe(content)


class VssiNode(template.Node):
    def __init__(self, request_path, asvar):
        self.request_path = request_path
        self.asvar = asvar

    def render(self, context):
        if 'request' not in context:
            raise exceptions.ImproperlyConfigured((
                    'vssi requires the django.core.context_processors.request'
                    ' template context processor'))
        request = context['request']
        url = 'http://'
        if request.is_secure():
            url = 'https://'
        url += request.get_host()

        if self.request_path.startswith('/'):
            url += self.request_path
        else:
            url += request.path + self.request_path

        try:
            r = urllib2.urlopen(url)
            response = HttpResponseProxy(
                status_code=r.code,
                headers=dict(r.info().items()),
                content=r.read())
            if self.asvar:
                context[self.asvar] = response
                return u''
            else:
                return response.content

        except urllib2.HTTPError:
            pass
        except urllib2.URLError:
            pass
        except socket.error:
            pass

        return safestring.mark_safe(getattr(
            settings, 'VIRTUALSSI_ERROR_MESSAGE',
            u'<!-- error while processing include: %s -->' % self.request_path))


@register.tag
def vssi(parser, token):
    tokens = token.split_contents()
    tag, tokens = tokens[0], tokens[1:]
    if len(tokens) not in (1, 3):
        raise template.TemplateSyntaxError(
            '%s tag got the wrong number of arguments' % tag)
    if len(tokens) == 1:
        request_path = tokens[0]
        asvar = None
    else:
        request_path, x, asvar = tokens
    if request_path[0] in ('"', "'") and request_path[-1] in ('"', "'"):
        request_path = request_path[1:-1]
    return VssiNode(request_path, asvar)
