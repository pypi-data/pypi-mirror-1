from django.template import Library
from django.template import Node
from django.template import TemplateSyntaxError
from emencia.django.links.models import Link

register = Library()

class LatestContentNode(Node):
    def __init__(self, num, varname):
        self.num = int(num)
        self.varname = varname
        self.model = Link

    def render(self, context):
        language = context['request'].LANGUAGE_CODE
        query = self.model.published.filter(language=language)
        if self.num == -1:
            context[self.varname] = query.all()
        else:
            context[self.varname] = query.all()[:self.num]
        if self.num == 1:
            context[self.varname] = context[self.varname][0]
        return ''

@register.tag
def get_latest_links(parser, token):
    bits = token.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError, "get_latest_links tag takes exactly four arguments"
    if bits[2] != 'as':
        raise TemplateSyntaxError, "third argument to get_latest tag must be 'as'"
    return LatestContentNode(bits[1], bits[3])
