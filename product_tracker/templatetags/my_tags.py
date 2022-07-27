from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Returns encoded URL parameters with specified query parameters added to existing parameters
    """
    d = context['request'].GET.copy()
    # print('context copy = ' + str(list(d.items())))
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()