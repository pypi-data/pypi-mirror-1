import re

from django import template

from cart.models import Cart

register = template.Library()

class GetCartNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        request = context['request']
        context[self.var_name] = Cart.objects.get_for_session(request.session)
        return ''


@register.tag(name='get_cart')
def do_get_cart(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    var_name = m.group(1)
    return GetCartNode(var_name)
